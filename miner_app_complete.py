"""
MINER - Mining Information Retrieval
Complete Multi-Page Desktop Application
Matching Web Template Design (3 Pages: Search, Results, Upload)
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# Import backend modules
from src.utils.utils import *
from src.preprocessing.tokenizing import *
from src.preprocessing.stopword import *
from src.preprocessing.tala_stemmer import *
from src.feature_extraction.tfidf import TFIDF
from src.indexing.inverted_index import InvertedIndex
from src.query.query_processor import QueryProcessor
from src.retrieval.retrieval_engine import RetrievalEngine

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MinerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("MINER - Mining Information Retrieval")
        self.geometry("1400x900")
        
        # Color scheme
        self.colors = {
            "primary": "#137fec",
            "bg_dark": "#101922",
            "surface_dark": "#1c2630",
            "border_dark": "#2a3744",
            "text_primary": "#ffffff",
            "text_secondary": "#9dabb9",
            "success": "#27ae60",
            "warning": "#f39c12",
            "danger": "#e74c3c"
        }
        
        # Backend components
        self.tfidf_model = None
        self.inverted_index = None
        self.query_processor = None
        self.engine = None
        self.processed_docs = []
        self.current_query = ""
        self.current_results = []
        
        # Current page
        self.current_page = "search"
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Create Sidebar Navigation
        self.create_sidebar()
        
        # Create Main Content Container
        self.main_container = ctk.CTkFrame(self, fg_color=self.colors["bg_dark"])
        self.main_container.grid(row=0, column=1, sticky="nsew")
        
        # Show search page by default
        self.show_search_page()
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = ctk.CTkFrame(self, width=250, fg_color=self.colors["surface_dark"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Logo and Title
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=30, padx=20)
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🔍 MINER",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["primary"]
        )
        logo_label.pack()
        
        subtitle = ctk.CTkLabel(
            logo_frame,
            text="Information Retrieval",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        subtitle.pack()
        
        # Navigation Buttons
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=15, pady=20)
        
        self.nav_buttons = {}
        
        # Search Button
        self.nav_buttons["search"] = ctk.CTkButton(
            nav_frame,
            text="🏠  Pencarian",
            command=lambda: self.navigate_to("search"),
            fg_color=self.colors["primary"],
            hover_color="#0d6ecc",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            anchor="w",
            corner_radius=10
        )
        self.nav_buttons["search"].pack(fill="x", pady=5)
        
        # Results Button
        self.nav_buttons["results"] = ctk.CTkButton(
            nav_frame,
            text="📄  Hasil Pencarian",
            command=lambda: self.navigate_to("results"),
            fg_color="transparent",
            hover_color=self.colors["border_dark"],
            font=ctk.CTkFont(size=14),
            height=45,
            anchor="w",
            border_width=1,
            border_color=self.colors["border_dark"],
            corner_radius=10
        )
        self.nav_buttons["results"].pack(fill="x", pady=5)
        
        # Upload Button
        self.nav_buttons["upload"] = ctk.CTkButton(
            nav_frame,
            text="📤  Upload Dokumen",
            command=lambda: self.navigate_to("upload"),
            fg_color="transparent",
            hover_color=self.colors["border_dark"],
            font=ctk.CTkFont(size=14),
            height=45,
            anchor="w",
            border_width=1,
            border_color=self.colors["border_dark"],
            corner_radius=10
        )
        self.nav_buttons["upload"].pack(fill="x", pady=5)
        
        # Stats at bottom
        stats_frame = ctk.CTkFrame(sidebar, fg_color=self.colors["bg_dark"], corner_radius=10)
        stats_frame.pack(side="bottom", fill="x", padx=15, pady=20)
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="📚 0 Dokumen\n⚡ Tala Stemmer",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"],
            justify="center"
        )
        self.stats_label.pack(pady=15)
    
    def navigate_to(self, page):
        """Navigate to different pages"""
        self.current_page = page
        
        # Update button styles
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == page:
                btn.configure(
                    fg_color=self.colors["primary"],
                    hover_color="#0d6ecc",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    border_width=0
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    hover_color=self.colors["border_dark"],
                    font=ctk.CTkFont(size=14),
                    border_width=1,
                    border_color=self.colors["border_dark"]
                )
        
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
        
        # Show appropriate page
        if page == "search":
            self.show_search_page()
        elif page == "results":
            self.show_results_page()
        elif page == "upload":
            self.show_upload_page()
    
    def show_search_page(self):
        """Page 1: Search Page (matching pencarian_dokumen.html)"""
        container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=60, pady=40)
        
        # Center content
        center_frame = ctk.CTkFrame(container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.4, anchor="center")
        
        # Title
        title = ctk.CTkLabel(
            center_frame,
            text="Pencarian Dokumen",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        title.pack(pady=(0, 10))
        
        title2 = ctk.CTkLabel(
            center_frame,
            text="Bahasa Indonesia",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=self.colors["primary"]
        )
        title2.pack(pady=(0, 20))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            center_frame,
            text="Mesin pencari pintar yang menggunakan Algoritma Stemming Tala\nuntuk hasil yang presisi dan relevan.",
            font=ctk.CTkFont(size=16),
            text_color=self.colors["text_secondary"],
            justify="center"
        )
        subtitle.pack(pady=(0, 40))
        
        # Search Bar
        search_container = ctk.CTkFrame(center_frame, fg_color=self.colors["surface_dark"], corner_radius=15, height=70)
        search_container.pack(fill="x", padx=50)
        search_container.pack_propagate(False)
        
        search_inner = ctk.CTkFrame(search_container, fg_color="transparent")
        search_inner.pack(fill="both", expand=True, padx=5, pady=5)
        search_inner.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(
            search_inner,
            placeholder_text="🔍  Masukkan kata kunci pencarian...",
            font=ctk.CTkFont(size=16),
            height=60,
            border_width=0,
            fg_color="transparent"
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=20)
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        search_btn = ctk.CTkButton(
            search_inner,
            text="Cari",
            command=self.perform_search,
            fg_color=self.colors["primary"],
            hover_color="#0d6ecc",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=120,
            height=50,
            corner_radius=10
        )
        search_btn.grid(row=0, column=1, padx=10)
        
        # Stats chips
        chips_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        chips_frame.pack(pady=30)
        
        chip1 = ctk.CTkFrame(chips_frame, fg_color=self.colors["surface_dark"], corner_radius=20, height=40)
        chip1.pack(side="left", padx=10)
        chip1.pack_propagate(False)
        
        self.doc_count_label = ctk.CTkLabel(
            chip1,
            text=f"📚 Status: {len(self.processed_docs)} Dokumen Terindeks",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_primary"]
        )
        self.doc_count_label.pack(padx=20, pady=8)
        
        chip2 = ctk.CTkFrame(chips_frame, fg_color=self.colors["surface_dark"], corner_radius=20, height=40)
        chip2.pack(side="left", padx=10)
        chip2.pack_propagate(False)
        
        ctk.CTkLabel(
            chip2,
            text="⚡ Powered by Tala Stemming",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_primary"]
        ).pack(padx=20, pady=8)
    
    def show_results_page(self):
        """Page 2: Results Page (matching hasil_pencarian_dokumen.html)"""
        if not self.current_results:
            # Show empty state
            empty_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
            empty_frame.pack(expand=True)
            
            ctk.CTkLabel(
                empty_frame,
                text="Belum ada hasil pencarian",
                font=ctk.CTkFont(size=20),
                text_color=self.colors["text_secondary"]
            ).pack()
            
            ctk.CTkLabel(
                empty_frame,
                text="Gunakan halaman Pencarian untuk mencari dokumen",
                font=ctk.CTkFont(size=14),
                text_color=self.colors["text_secondary"]
            ).pack(pady=10)
            
            return
        
        # Main container with scrolling
        main_scroll = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color="transparent",
            scrollbar_button_color=self.colors["surface_dark"]
        )
        main_scroll.pack(fill="both", expand=True, padx=40, pady=30)
        main_scroll.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        title = ctk.CTkLabel(
            header_frame,
            text=f'Hasil Pencarian: "{self.current_query}"',
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors["text_primary"],
            anchor="w"
        )
        title.pack(anchor="w")
        
        stats = ctk.CTkLabel(
            header_frame,
            text=f"⏱️ Menampilkan {len(self.current_results)} dokumen",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_secondary"],
            anchor="w"
        )
        stats.pack(anchor="w", pady=5)
        
        # Results
        results_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        results_frame.grid(row=1, column=0, sticky="ew")
        results_frame.grid_columnconfigure(0, weight=1)
        
        for rank, res in enumerate(self.current_results, 1):
            self.create_result_card_v2(
                results_frame,
                rank,
                res['metadata']['filename'],
                res['score'],
                res['metadata']['filepath'],
                res.get('preview', ''),
                res.get('query_terms', [])
            )
    
    def show_upload_page(self):
        """Page 3: Upload Page (matching upload_dokumen_baru.html)"""
        container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=60, pady=40)
        
        # Center content
        center_frame = ctk.CTkFrame(container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.4, anchor="center")
        
        # Title
        title = ctk.CTkLabel(
            center_frame,
            text="📤 Upload Dokumen Baru",
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        title.pack(pady=(0, 20))
        
        subtitle = ctk.CTkLabel(
            center_frame,
            text="Tambahkan dokumen baru ke dalam sistem untuk diindeks",
            font=ctk.CTkFont(size=16),
            text_color=self.colors["text_secondary"]
        )
        subtitle.pack(pady=(0, 40))
        
        # Upload Area
        upload_area = ctk.CTkFrame(
            center_frame,
            fg_color=self.colors["surface_dark"],
            corner_radius=15,
            border_width=2,
            border_color=self.colors["border_dark"],
            width=600,
            height=300
        )
        upload_area.pack()
        upload_area.pack_propagate(False)
        
        upload_content = ctk.CTkFrame(upload_area, fg_color="transparent")
        upload_content.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            upload_content,
            text="📁",
            font=ctk.CTkFont(size=60)
        ).pack()
        
        ctk.CTkLabel(
            upload_content,
            text="Pilih Folder Dokumen",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text_primary"]
        ).pack(pady=10)
        
        ctk.CTkLabel(
            upload_content,
            text="Format: .txt, .docx, .pdf",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        ).pack(pady=5)
        
        browse_btn = ctk.CTkButton(
            upload_content,
            text="Browse Folder",
            command=self.browse_and_index,
            fg_color=self.colors["primary"],
            hover_color="#0d6ecc",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=200,
            height=50,
            corner_radius=10
        )
        browse_btn.pack(pady=20)
        
        # Progress
        self.upload_progress_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        self.upload_progress_frame.pack(pady=30)
        
        self.upload_status = ctk.CTkLabel(
            self.upload_progress_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        self.upload_status.pack()
        
        self.upload_progress = ctk.CTkProgressBar(
            self.upload_progress_frame,
            width=400,
            height=10,
            progress_color=self.colors["primary"]
        )
        self.upload_progress.set(0)
    
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
        icon = ctk.CTkLabel(card, text="📄", font=ctk.CTkFont(size=32))
        icon.grid(row=0, column=0, rowspan=3, padx=20, pady=20)
        
        # Content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.grid(row=0, column=1, sticky="ew", pady=20, padx=(0, 20))
        
        # Filename
        ctk.CTkLabel(
            content,
            text=f"{rank}. {filename}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["primary"],
            anchor="w"
        ).pack(anchor="w")
        
        # Path
        ctk.CTkLabel(
            content,
            text=filepath,
            font=ctk.CTkFont(size=11),
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
                font=ctk.CTkFont(size=12),
                text_color="#d0d0d0",
                anchor="w",
                wraplength=700,
                justify="left"
            ).pack(padx=15, pady=10, anchor="w")
        
        # Open button
        ctk.CTkButton(
            card,
            text="📂 Buka",
            command=lambda: self.open_file(filepath),
            fg_color=self.colors["border_dark"],
            hover_color=self.colors["primary"],
            font=ctk.CTkFont(size=12),
            width=90,
            height=32
        ).grid(row=1, column=1, sticky="w", padx=(0, 20), pady=(0, 20))
        
        # Score
        score_frame = ctk.CTkFrame(card, fg_color="transparent")
        score_frame.grid(row=0, column=2, rowspan=3, padx=20, pady=20)
        
        ctk.CTkLabel(
            score_frame,
            text="RELEVANSI",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack()
        
        ctk.CTkLabel(
            score_frame,
            text=f"{score:.2f}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=score_color
        ).pack(pady=(5, 5))
        
        progress = ctk.CTkProgressBar(
            score_frame,
            width=100,
            height=8,
            progress_color=bar_color,
            fg_color=self.colors["border_dark"]
        )
        progress.set(score)
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
            self.after(0, lambda: self.upload_status.configure(text="⏳ Memproses dokumen..."))
            self.after(0, lambda: self.upload_progress.pack(pady=10))
            self.after(0, lambda: self.upload_progress.set(0.3))
            
            ekstensi_file = {'.txt', '.docx', '.pdf'}
            files = [
                (file, os.path.join(directory, file), os.path.splitext(file)[1].lower())
                for file in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, file)) 
                and os.path.splitext(file)[1].lower() in ekstensi_file
            ]
            
            if not files:
                self.after(0, lambda: messagebox.showwarning("Warning", "Tidak ada dokumen yang ditemukan!"))
                return
            
            self.processed_docs = []
            
            for idx, (filename, filepath, exs) in enumerate(files, 1):
                try:
                    if exs == '.txt':
                        text = baca_txt(filepath)
                    elif exs == '.docx':
                        text = baca_docx(filepath)
                    elif exs == '.pdf':
                        text = baca_pdf(filepath)
                    
                    text_bersih = bersihkan_text(text)
                    tokens = tokenizing(text_bersih)
                    tokens_bersih = remove_stopwords(tokens)
                    token_stem = Stem_Tala_tokenizing(tokens_bersih)
                    
                    self.processed_docs.append({
                        'id': idx,
                        'tokens': token_stem,
                        'metadata': {
                            'filename': filename,
                            'filepath': filepath
                        }
                    })
                    
                    # Thread-safe progress update
                    progress = 0.3 + (0.4 * idx / len(files))
                    self.after(0, lambda p=progress: self.upload_progress.set(p))
                    
                except Exception as e:
                    print(f"Error: {filename}: {e}")
            
            self.after(0, lambda: self.upload_progress.set(0.7))
            
            # Build VSM
            self.tfidf_model = TFIDF()
            corpus_tokens = [doc['tokens'] for doc in self.processed_docs]
            self.tfidf_model.calculate_idf(corpus_tokens)
            
            self.inverted_index = InvertedIndex()
            self.inverted_index.build_index(self.processed_docs, self.tfidf_model)
            
            self.query_processor = QueryProcessor(self.tfidf_model)
            self.engine = RetrievalEngine(self.inverted_index, self.tfidf_model)
            
            self.after(0, lambda: self.upload_progress.set(1.0))
            
            # Thread-safe UI updates
            doc_count = len(self.processed_docs)
            self.after(0, lambda: self.upload_status.configure(
                text=f"✓ {doc_count} dokumen berhasil diindeks!",
                text_color=self.colors["success"]
            ))
            
            # Update stats
            self.after(0, lambda: self.stats_label.configure(text=f"📚 {doc_count} Dokumen\n⚡ Tala Stemmer"))
            
            # Update doc count label if exists
            if hasattr(self, 'doc_count_label'):
                self.after(0, lambda: self.doc_count_label.configure(text=f"📚 Status: {doc_count} Dokumen Terindeks"))
            
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
