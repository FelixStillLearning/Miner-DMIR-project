
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import subprocess
import platform
import time
from pathlib import Path
from ui.theme import COLORS, build_fonts
from ui.sidebar import build_sidebar
from ui.pages.search_page import render_search_page
from ui.pages.results_page import render_results_page
from ui.pages.upload_page import render_upload_page
from ui.pages.documents_page import render_documents_page
from ui.assets import load_images
from src.pipeline import process_directory, build_models, SUPPORTED_EXT

# Import backend helpers
from src.utils.view_helpers import get_preview_snippet

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MinerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("MINER - Mining Information Retrieval")
        self.geometry("1400x900")
        
        # Theme
        self.colors = COLORS.copy()
        self.fonts = build_fonts()
        
        # Backend components
        self.inverted_index = None
        self.query_processor = None
        self.engine = None
        self.processed_docs = []
        self.current_query = ""
        self.current_results = []
        self.current_search_time_ms = 0.0

        # Assets
        self.images = {}
        # Ikon kini berada di ui/Icon1 relatif terhadap akar proyek
        base_dir = Path(__file__).resolve().parent / "ui" / "Icon1"
        self.images = load_images(base_dir)
        
        # Current page
        self.current_page = "search"
        
        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create Sidebar Navigation
        build_sidebar(self)
        
        # Create Main Content Container
        self.main_container = ctk.CTkFrame(self, fg_color=self.colors["bg_dark"])
        self.main_container.grid(row=0, column=1, sticky="nsew")
        
        # Show search page by default
        render_search_page(self)

    def clear_main_container(self):
        """Hapus seluruh konten utama sebelum memuat halaman baru."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def navigate_to(self, page):
        """Navigate to different pages"""
        self.current_page = page
        
        # Update button styles
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == page:
                btn.configure(
                    fg_color=self.colors["primary"],
                    hover_color="#0d6ecc",
                    font=self.fonts["body"],
                    border_width=0
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=self.colors["border_dark"],
                    font=self.fonts["body"],
                    border_width=1,
                    border_color=self.colors["border_dark"]
                )
        
        # Clear main container
        self.clear_main_container()
        
        # Show appropriate page
        if page == "search":
            render_search_page(self)
        elif page == "results":
            render_results_page(self)
        elif page == "documents":
            render_documents_page(self)
        elif page == "upload":
            render_upload_page(self)
    
    def perform_search(self):
        """Perform search and navigate to results"""
        if not self.engine:
            messagebox.showwarning("Warning", "Silakan index dokumen terlebih dahulu!\nGunakan halaman Upload.")
            return
        
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Masukkan query pencarian!")
            return
        
        try:
            # Loading indicator
            if hasattr(self, "search_button") and self.search_button.winfo_exists():
                self.search_button.configure(state="disabled", text="Mencari…")
            if hasattr(self, "search_status") and self.search_status.winfo_exists():
                self.search_status.configure(text="Sedang mencari…")

            start = time.perf_counter()
            # Process query
            q_vector, q_tokens = self.query_processor.transform_query(query)

            # Search dengan LM Dirichlet
            results = self.engine.search(q_vector, top_k=20)

            elapsed_ms = (time.perf_counter() - start) * 1000
            self.current_search_time_ms = elapsed_ms

            # Normalisasi skor untuk tampilan (0-1) sambil simpan raw log-prob
            if results:
                raw_scores = [r['score'] for r in results]
                min_s, max_s = min(raw_scores), max(raw_scores)
                denom = (max_s - min_s) if max_s != min_s else 1.0
                for res in results:
                    res['raw_score'] = res['score']
                    res['score'] = (res['score'] - min_s) / denom
                    # keep hits for display
                    res['hits'] = res.get('hits', 0)

            # Add previews
            for res in results:
                preview = get_preview_snippet(
                    res['metadata']['filepath'],
                    q_tokens,
                    max_length=200
                )
                res['preview'] = preview
                res['query_terms'] = q_tokens
            
            # Store results
            self.current_query = query
            self.current_results = results
            
            # Navigate to results page
            self.navigate_to("results")
            
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")
        finally:
            if hasattr(self, "search_button") and self.search_button.winfo_exists():
                self.search_button.configure(state="normal", text="Cari")
            if hasattr(self, "search_status") and self.search_status.winfo_exists():
                self.search_status.configure(text="")
    
    def browse_and_index(self):
        """Browse folder and index documents"""
        folder = filedialog.askdirectory(title="Pilih Folder Dokumen")
        if not folder:
            return
        
        # Run in thread
        thread = threading.Thread(target=self.index_documents, args=(folder,))
        thread.daemon = True
        thread.start()
    
    def index_documents(self, directory):
        """Index documents from directory"""
        try:
            # Thread-safe UI update
            self.after(0, lambda: self.upload_status.configure(text="Memproses dokumen..."))
            self.after(0, lambda: self.upload_progress.pack(pady=10))
            self.after(0, lambda: self.upload_progress.set(0.3))
            
            def progress_cb(current, total):
                progress = 0.3 + (0.4 * current / total)
                self.after(0, lambda p=progress: self.upload_progress.set(p))

            self.processed_docs = process_directory(directory, SUPPORTED_EXT, progress_cb)

            if not self.processed_docs:
                self.after(0, lambda: messagebox.showwarning("Warning", "Tidak ada dokumen yang ditemukan!"))
                return

            self.after(0, lambda: self.upload_progress.set(0.7))

            # Gunakan default mu=2000; dapat diubah bila perlu
            self.inverted_index, self.query_processor, self.engine = build_models(self.processed_docs)
            
            self.after(0, lambda: self.upload_progress.set(1.0))
            
            # Thread-safe UI updates
            doc_count = len(self.processed_docs)
            self.after(0, lambda: self.upload_status.configure(
                text=f"{doc_count} dokumen berhasil diindeks!",
                text_color=self.colors["success"]
            ))
            
            # Update stats
            self.after(0, lambda: self.stats_label.configure(text=f"{doc_count} Dokumen\nTala Stemmer"))
            
            # Update doc count label if the widget still exists (only on search page)
            def _update_doc_count():
                if hasattr(self, 'doc_count_label') and self.doc_count_label.winfo_exists():
                    self.doc_count_label.configure(text=f"Status: {doc_count} Dokumen Terindeks")

            self.after(0, _update_doc_count)
            
            self.after(0, lambda: messagebox.showinfo("Success", f"{doc_count} dokumen berhasil diindeks!"))
            
        except Exception as e:
            self.after(0, lambda: self.upload_status.configure(
                text=" Error saat indexing",
                text_color=self.colors["danger"]
            ))
            self.after(0, lambda err=e: messagebox.showerror("Error", f"Indexing failed: {str(err)}"))
    
    def open_file(self, filepath):
        """Open file with default application"""
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', filepath])
            else:
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka file: {str(e)}")
    

def main():
    app = MinerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
