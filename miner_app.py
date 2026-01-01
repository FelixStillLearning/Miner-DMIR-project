
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import subprocess
import platform
from pathlib import Path
from ui.theme import COLORS, build_fonts
from ui.sidebar import build_sidebar
from ui.pages.search_page import render_search_page
from ui.pages.results_page import render_results_page
from ui.pages.upload_page import render_upload_page
from ui.assets import load_images
from src.pipeline import process_directory, build_models, SUPPORTED_EXT

# Import backend helpers
from src.utils.utils import baca_txt, baca_docx, baca_pdf

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
        self.tfidf_model = None
        self.inverted_index = None
        self.query_processor = None
        self.engine = None
        self.processed_docs = []
        self.current_query = ""
        self.current_results = []

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
        elif page == "upload":
            render_upload_page(self)
    
    def create_result_card_v2(self, parent, rank, filename, score, filepath, preview_text="", query_terms=[]):
        """Enhanced result card for results page"""
        # Determine colors - ADJUSTED for realistic TF-IDF scores
        if score >= 0.3:  # Changed from 0.7
            score_color = self.colors["success"]
            bar_color = "#27ae60"
        elif score >= 0.15:  # Changed from 0.4
            score_color = self.colors["warning"]
            bar_color = "#f39c12"
        else:
            score_color = self.colors["danger"]
            bar_color = "#e74c3c"
        
        # Card
        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["surface_dark"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border_dark"]
        )
        card.grid(row=rank-1, column=0, sticky="ew", pady=8)
        card.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon = ctk.CTkLabel(card, text="", font=self.fonts["card_title"], width=32, image=self.images.get("result"), compound="left")
        icon.grid(row=0, column=0, rowspan=3, padx=20, pady=20)
        
        # Content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=0, column=1, sticky="ew", pady=20, padx=(0, 20))
        
        # Filename
        ctk.CTkLabel(
            content,
            text=f"{rank}. {filename}",
            font=self.fonts["card_title"],
            text_color=self.colors["primary"],
            anchor="w"
        ).pack(anchor="w")
        
        # Path
        ctk.CTkLabel(
            content,
            text=filepath,
            font=self.fonts["body"],
            text_color=self.colors["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(5, 0))
        
        # Preview
        if preview_text:
            preview_frame = ctk.CTkFrame(content, fg_color=self.colors["bg_dark"], corner_radius=8)
            preview_frame.pack(fill="x", pady=(10, 0))
            
            highlighted = self.highlight_text(preview_text, query_terms)
            ctk.CTkLabel(
                preview_frame,
                text=highlighted,
                font=self.fonts["body"],
                text_color="#d0d0d0",
                anchor="w",
                wraplength=700,
                justify="left"
            ).pack(padx=15, pady=10, anchor="w")
        
        # Open button
        ctk.CTkButton(
            card,
            text="Buka",
            command=lambda: self.open_file(filepath),
            fg_color=self.colors["border_dark"],
            hover_color=self.colors["primary"],
            font=self.fonts["body"],
            width=90,
            height=32
        ).grid(row=1, column=1, sticky="w", padx=(0, 20), pady=(0, 20))
        
        # Score
        score_frame = ctk.CTkFrame(card, fg_color="transparent")
        score_frame.grid(row=0, column=2, rowspan=3, padx=20, pady=20)
        
        ctk.CTkLabel(
            score_frame,
            text="RELEVANSI",
            font=self.fonts["label"],
            text_color=self.colors["text_secondary"]
        ).pack()
        
        ctk.CTkLabel(
            score_frame,
            text=f"{score:.2f}",
            font=ctk.CTkFont(family="Poppins", size=22, weight="bold"),
            text_color=score_color
        ).pack(pady=(5, 5))
        
        progress = ctk.CTkProgressBar(
            score_frame,
            width=100,
            height=8,
            progress_color=bar_color,
            fg_color=self.colors["border_dark"]
        )
        progress.set(min(max(score, 0), 1))
        progress.pack()
    
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
            # Process query
            q_vector, q_tokens = self.query_processor.transform_query(query)
            
            # Search
            results = self.engine.search(q_vector, top_k=20)
            
            # Add previews
            for res in results:
                preview = self.get_preview_snippet(
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

            self.tfidf_model, self.inverted_index, self.query_processor, self.engine = build_models(self.processed_docs)
            
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
                text="❌ Error saat indexing",
                text_color=self.colors["danger"]
            ))
            self.after(0, lambda: messagebox.showerror("Error", f"Indexing failed: {str(e)}"))
    
    def highlight_text(self, text, query_terms):
        """Highlight query terms in text"""
        highlighted = text
        for term in query_terms:
            import re
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted = pattern.sub(f"⟪{term.upper()}⟫", highlighted)
        return highlighted
    
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
    
    def get_preview_snippet(self, filepath, query_terms, max_length=200):
        """Get preview snippet from document"""
        try:
            ext = os.path.splitext(filepath)[1].lower()
            if ext == '.txt':
                text = baca_txt(filepath)
            elif ext == '.docx':
                text = baca_docx(filepath)
            elif ext == '.pdf':
                text = baca_pdf(filepath)
            else:
                return ""
            
            text = text.replace('\n', ' ').replace('\r', ' ')
            text = ' '.join(text.split())
            
            best_snippet = ""
            for term in query_terms:
                import re
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 150)
                    snippet = text[start:end]
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(text):
                        snippet = snippet + "..."
                    best_snippet = snippet
                    break
            
            if not best_snippet:
                best_snippet = text[:max_length]
                if len(text) > max_length:
                    best_snippet += "..."
            
            return best_snippet
            
        except Exception as e:
            return f"[Preview tidak tersedia]"


def main():
    app = MinerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
