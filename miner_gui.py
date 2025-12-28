"""
MINER - Mining Information Retrieval
Modern Desktop GUI Application inspired by web template design
Using CustomTkinter for modern, elegant UI
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import subprocess
import platform
from pathlib import Path

# Import backend modules
from src.utils.utils import *
from src.preprocessing.tokenizing import *
from src.preprocessing.stopword import *
from src.preprocessing.tala_stemmer import *
from src.feature_extraction.tfidf import TFIDF
from src.indexing.inverted_index import InvertedIndex
from src.query.query_processor import QueryProcessor
from src.retrieval.retrieval_engine import RetrievalEngine

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MinerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("MINER - Mining Information Retrieval")
        self.geometry("1200x800")
        
        # Color scheme matching template
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
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Configure grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # ===== HEADER =====
        self.create_header()
        
        # ===== MAIN CONTENT =====
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(2, weight=1)
        
        # Search Section
        self.create_search_section()
        
        # Stats Section
        self.create_stats_section()
        
        # Results Section
        self.create_results_section()
        
    def create_header(self):
        header = ctk.CTkFrame(self, height=80, fg_color=self.colors["surface_dark"])
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        # Logo and Title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=30, pady=20)
        
        title = ctk.CTkLabel(
            title_frame,
            text="🔍 MINER",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["primary"]
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Mining Information Retrieval - Tala Stemmer & VSM",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_secondary"]
        )
        subtitle.pack(anchor="w")
        
        # Index Button
        self.index_btn = ctk.CTkButton(
            header,
            text="📂 Index Documents",
            command=self.start_indexing,
            fg_color=self.colors["success"],
            hover_color="#229954",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            width=180
        )
        self.index_btn.pack(side="right", padx=30, pady=20)
        
    def create_search_section(self):
        search_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        search_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            search_frame,
            text="Pencarian Dokumen Bahasa Indonesia",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        title.grid(row=0, column=0, pady=(0, 10))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            search_frame,
            text="Mesin pencari pintar menggunakan Algoritma Stemming Tala",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        subtitle.grid(row=1, column=0, pady=(0, 20))
        
        # Search Bar Container
        search_container = ctk.CTkFrame(search_frame, fg_color=self.colors["surface_dark"], corner_radius=12)
        search_container.grid(row=2, column=0, sticky="ew", padx=100)
        search_container.grid_columnconfigure(0, weight=1)
        
        # Search Input
        self.search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="🔍  Masukkan kata kunci pencarian...",
            font=ctk.CTkFont(size=15),
            height=50,
            border_width=0,
            fg_color="transparent"
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(20, 10), pady=10)
        self.search_entry.bind('<Return>', lambda e: self.search_documents())
        
        # Search Button
        search_btn = ctk.CTkButton(
            search_container,
            text="Cari",
            command=self.search_documents,
            fg_color=self.colors["primary"],
            hover_color="#0d6ecc",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100,
            height=40
        )
        search_btn.grid(row=0, column=1, padx=(0, 10), pady=10)
        
    def create_stats_section(self):
        stats_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Status Label
        self.status_label = ctk.CTkLabel(
            stats_frame,
            text="📚 Status: Siap - 0 dokumen terindeks",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_secondary"]
        )
        self.status_label.pack(side="left", padx=10)
        
        # Processed Query Info
        self.query_info = ctk.CTkLabel(
            stats_frame,
            text="",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color=self.colors["text_secondary"]
        )
        self.query_info.pack(side="left", padx=20)
        
    def create_results_section(self):
        # Results Container
        results_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        results_container.grid(row=2, column=0, sticky="nsew")
        results_container.grid_columnconfigure(0, weight=1)
        results_container.grid_rowconfigure(0, weight=1)
        
        # Scrollable Frame for Results
        self.results_scroll = ctk.CTkScrollableFrame(
            results_container,
            fg_color="transparent",
            scrollbar_button_color=self.colors["surface_dark"],
            scrollbar_button_hover_color=self.colors["border_dark"]
        )
        self.results_scroll.grid(row=0, column=0, sticky="nsew")
        self.results_scroll.grid_columnconfigure(0, weight=1)
        
    def create_result_card(self, rank, filename, score, filepath, preview_text="", query_terms=[]):
        """Create a result card with preview and open file button"""
        
        # Determine score color
        if score >= 0.7:
            score_color = self.colors["success"]
            bar_color = "#27ae60"
        elif score >= 0.4:
            score_color = self.colors["warning"]
            bar_color = "#f39c12"
        else:
            score_color = self.colors["danger"]
            bar_color = "#e74c3c"
        
        # Card Frame
        card = ctk.CTkFrame(
            self.results_scroll,
            fg_color=self.colors["surface_dark"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border_dark"]
        )
        card.grid(row=rank-1, column=0, sticky="ew", pady=8, padx=5)
        card.grid_columnconfigure(1, weight=1)
        
        # File Icon
        icon_label = ctk.CTkLabel(
            card,
            text="📄",
            font=ctk.CTkFont(size=32)
        )
        icon_label.grid(row=0, column=0, rowspan=3, padx=20, pady=15)
        
        # Content Frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="ew", pady=15, padx=(0, 20))
        
        # Filename
        filename_label = ctk.CTkLabel(
            content_frame,
            text=f"{rank}. {filename}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["primary"],
            anchor="w"
        )
        filename_label.pack(anchor="w")
        
        # Path
        path_label = ctk.CTkLabel(
            content_frame,
            text=filepath,
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_secondary"],
            anchor="w"
        )
        path_label.pack(anchor="w", pady=(5, 0))
        
        # Preview with Highlighting
        if preview_text:
            preview_frame = ctk.CTkFrame(content_frame, fg_color=self.colors["bg_dark"], corner_radius=8)
            preview_frame.pack(fill="x", pady=(10, 0))
            
            # Create highlighted preview
            highlighted_preview = self.highlight_text(preview_text, query_terms)
            
            preview_label = ctk.CTkLabel(
                preview_frame,
                text=highlighted_preview,
                font=ctk.CTkFont(size=12),
                text_color="#d0d0d0",
                anchor="w",
                wraplength=600,
                justify="left"
            )
            preview_label.pack(padx=15, pady=10, anchor="w")
        
        # Open File Button
        open_btn = ctk.CTkButton(
            card,
            text="📂 Buka File",
            command=lambda: self.open_file(filepath),
            fg_color=self.colors["border_dark"],
            hover_color=self.colors["primary"],
            font=ctk.CTkFont(size=12),
            width=100,
            height=32
        )
        open_btn.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=(0, 15))
        
        # Score Frame
        score_frame = ctk.CTkFrame(card, fg_color="transparent")
        score_frame.grid(row=0, column=2, rowspan=3, padx=20, pady=15)
        
        # Score Label
        score_label = ctk.CTkLabel(
            score_frame,
            text="RELEVANSI",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=self.colors["text_secondary"]
        )
        score_label.pack()
        
        score_value = ctk.CTkLabel(
            score_frame,
            text=f"{score:.2f}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=score_color
        )
        score_value.pack(pady=(5, 5))
        
        # Progress Bar
        progress = ctk.CTkProgressBar(
            score_frame,
            width=100,
            height=8,
            progress_color=bar_color,
            fg_color=self.colors["border_dark"]
        )
        progress.set(score)
        progress.pack()
    
    def highlight_text(self, text, query_terms):
        """Add visual markers for highlighted terms"""
        highlighted = text
        for term in query_terms:
            # Case insensitive replace with highlight markers
            import re
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            highlighted = pattern.sub(f"⟪{term.upper()}⟫", highlighted)
        return highlighted
    
    def open_file(self, filepath):
        """Open file with default application"""
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            messagebox.showerror("Error", f"Tidak dapat membuka file: {str(e)}")
    
    def get_preview_snippet(self, filepath, query_terms, max_length=200):
        """Extract preview snippet from document with context around query terms"""
        try:
            # Read file
            ext = os.path.splitext(filepath)[1].lower()
            if ext == '.txt':
                text = baca_txt(filepath)
            elif ext == '.docx':
                text = baca_docx(filepath)
            elif ext == '.pdf':
                text = baca_pdf(filepath)
            else:
                return ""
            
            # Clean and find best snippet
            text = text.replace('\n', ' ').replace('\r', ' ')
            text = ' '.join(text.split())  # Normalize whitespace
            
            # Try to find snippet containing query terms
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
            
            # If no match, just take beginning
            if not best_snippet:
                best_snippet = text[:max_length]
                if len(text) > max_length:
                    best_snippet += "..."
            
            return best_snippet
            
        except Exception as e:
            return f"[Preview tidak tersedia: {str(e)}]"
        
    def start_indexing(self):
        folder = filedialog.askdirectory(title="Pilih Folder Dokumen")
        if not folder:
            return
            
        # Run in thread
        thread = threading.Thread(target=self.index_documents, args=(folder,))
        thread.daemon = True
        thread.start()
        
    def index_documents(self, directory):
        try:
            self.index_btn.configure(state="disabled", text="⏳ Indexing...")
            self.status_label.configure(text="📂 Memproses dokumen...")
            
            ekstensi_file = {'.txt', '.docx', '.pdf'}
            files = [
                (file, os.path.join(directory, file), os.path.splitext(file)[1].lower())
                for file in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, file)) 
                and os.path.splitext(file)[1].lower() in ekstensi_file
            ]
            
            if not files:
                messagebox.showwarning("Warning", "Tidak ada dokumen yang ditemukan!")
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
                except Exception as e:
                    print(f"Error: {filename}: {e}")
            
            # Build VSM
            self.tfidf_model = TFIDF()
            corpus_tokens = [doc['tokens'] for doc in self.processed_docs]
            self.tfidf_model.calculate_idf(corpus_tokens)
            
            self.inverted_index = InvertedIndex()
            self.inverted_index.build_index(self.processed_docs, self.tfidf_model)
            
            self.query_processor = QueryProcessor(self.tfidf_model)
            self.engine = RetrievalEngine(self.inverted_index, self.tfidf_model)
            
            # Update UI
            self.status_label.configure(
                text=f"✓ {len(self.processed_docs)} dokumen terindeks",
                text_color=self.colors["success"]
            )
            self.index_btn.configure(state="normal", text="📂 Index Documents")
            messagebox.showinfo("Success", f"{len(self.processed_docs)} dokumen berhasil diindeks!")
            
        except Exception as e:
            self.status_label.configure(text="❌ Error saat indexing", text_color=self.colors["danger"])
            self.index_btn.configure(state="normal", text="📂 Index Documents")
            messagebox.showerror("Error", f"Indexing failed: {str(e)}")
    
    def search_documents(self):
        if not self.engine:
            messagebox.showwarning("Warning", "Silakan index dokumen terlebih dahulu!")
            return
            
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Masukkan query pencarian!")
            return
        
        try:
            # Process query
            q_vector, q_tokens = self.query_processor.transform_query(query)
            
            # Update query info
            self.query_info.configure(
                text=f"Query diproses: {' '.join(q_tokens)}"
            )
            
            # Search
            results = self.engine.search(q_vector, top_k=10)
            
            # Clear previous results
            for widget in self.results_scroll.winfo_children():
                widget.destroy()
            
            # Display results
            if not results:
                no_result = ctk.CTkLabel(
                    self.results_scroll,
                    text="Tidak ada dokumen yang ditemukan",
                    font=ctk.CTkFont(size=14),
                    text_color=self.colors["text_secondary"]
                )
                no_result.grid(row=0, column=0, pady=50)
            else:
                for rank, res in enumerate(results, 1):
                    # Get preview snippet
                    preview = self.get_preview_snippet(
                        res['metadata']['filepath'],
                        q_tokens,
                        max_length=200
                    )
                    
                    self.create_result_card(
                        rank,
                        res['metadata']['filename'],
                        res['score'],
                        res['metadata']['filepath'],
                        preview,
                        q_tokens
                    )
            
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")


def main():
    app = MinerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
