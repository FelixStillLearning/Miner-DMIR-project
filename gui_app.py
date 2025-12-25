"""
MINER - Mining Information Retrieval
Desktop GUI Application for Document Search using VSM and Tala Stemmer
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from pathlib import Path
import threading

# Import backend modules
from src.utils.utils import *
from src.preprocessing.tokenizing import *
from src.preprocessing.stopword import *
from src.preprocessing.tala_stemmer import *
from src.feature_extraction.tfidf import TFIDF
from src.indexing.inverted_index import InvertedIndex
from src.query.query_processor import QueryProcessor
from src.retrieval.retrieval_engine import RetrievalEngine


class MinerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MINER - Mining Information Retrieval")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        # Backend components
        self.tfidf_model = None
        self.inverted_index = None
        self.query_processor = None
        self.engine = None
        self.processed_docs = []
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="🔍 MINER", 
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Mining Information Retrieval - Tala Stemmer & VSM",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle_label.pack()
        
        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # === INDEXING SECTION ===
        indexing_frame = tk.LabelFrame(
            main_frame,
            text="📂 Document Indexing",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        indexing_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Folder selection
        folder_frame = tk.Frame(indexing_frame, bg="#f0f0f0")
        folder_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            folder_frame,
            text="Folder:",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.folder_path = tk.StringVar(value="data/raw")
        folder_entry = tk.Entry(
            folder_frame,
            textvariable=self.folder_path,
            font=("Arial", 10),
            width=50
        )
        folder_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_btn = tk.Button(
            folder_frame,
            text="Browse",
            command=self.browse_folder,
            bg="#3498db",
            fg="white",
            font=("Arial", 9),
            cursor="hand2"
        )
        browse_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        index_btn = tk.Button(
            folder_frame,
            text="🔄 Index Documents",
            command=self.start_indexing,
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            padx=15
        )
        index_btn.pack(side=tk.LEFT)
        
        # Status
        self.status_label = tk.Label(
            indexing_frame,
            text="Status: Ready",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        self.status_label.pack(anchor=tk.W, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            indexing_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(fill=tk.X, pady=5)
        
        # === SEARCH SECTION ===
        search_frame = tk.LabelFrame(
            main_frame,
            text="🔍 Search Documents",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Search input
        search_input_frame = tk.Frame(search_frame, bg="#f0f0f0")
        search_input_frame.pack(fill=tk.X, pady=5)
        
        self.query_entry = tk.Entry(
            search_input_frame,
            font=("Arial", 12),
            width=60
        )
        self.query_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=5)
        self.query_entry.bind('<Return>', lambda e: self.search_documents())
        
        search_btn = tk.Button(
            search_input_frame,
            text="Search",
            command=self.search_documents,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            padx=20
        )
        search_btn.pack(side=tk.LEFT)
        
        # Query info
        self.query_info = tk.Label(
            search_frame,
            text="",
            font=("Arial", 9, "italic"),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        self.query_info.pack(anchor=tk.W, pady=5)
        
        # === RESULTS SECTION ===
        results_frame = tk.LabelFrame(
            main_frame,
            text="📄 Search Results",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            font=("Courier New", 10),
            wrap=tk.WORD,
            bg="white",
            fg="#2c3e50"
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            
    def start_indexing(self):
        # Run indexing in separate thread to prevent UI freeze
        thread = threading.Thread(target=self.index_documents)
        thread.daemon = True
        thread.start()
        
    def index_documents(self):
        try:
            self.progress.start()
            self.status_label.config(text="Status: Indexing documents...", fg="#e67e22")
            
            directory = self.folder_path.get()
            if not os.path.exists(directory):
                messagebox.showerror("Error", f"Folder tidak ditemukan: {directory}")
                return
                
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
                    # Read file
                    if exs == '.txt':
                        text = baca_txt(filepath)
                    elif exs == '.docx':
                        text = baca_docx(filepath)
                    elif exs == '.pdf':
                        text = baca_pdf(filepath)
                    
                    # Preprocessing
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
                    print(f"Error processing {filename}: {e}")
            
            # Build VSM
            self.tfidf_model = TFIDF()
            corpus_tokens = [doc['tokens'] for doc in self.processed_docs]
            self.tfidf_model.calculate_idf(corpus_tokens)
            
            self.inverted_index = InvertedIndex()
            self.inverted_index.build_index(self.processed_docs, self.tfidf_model)
            
            self.query_processor = QueryProcessor(self.tfidf_model)
            self.engine = RetrievalEngine(self.inverted_index, self.tfidf_model)
            
            # Update UI
            self.progress.stop()
            self.status_label.config(
                text=f"Status: ✓ {len(self.processed_docs)} documents indexed successfully",
                fg="#27ae60"
            )
            messagebox.showinfo("Success", f"{len(self.processed_docs)} dokumen berhasil diindeks!")
            
        except Exception as e:
            self.progress.stop()
            self.status_label.config(text="Status: Error", fg="#e74c3c")
            messagebox.showerror("Error", f"Indexing failed: {str(e)}")
    
    def search_documents(self):
        if not self.engine:
            messagebox.showwarning("Warning", "Silakan index dokumen terlebih dahulu!")
            return
            
        query = self.query_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Masukkan query pencarian!")
            return
        
        try:
            # Process query
            q_vector, q_tokens = self.query_processor.transform_query(query)
            
            # Update query info
            self.query_info.config(
                text=f"Processed query: {' '.join(q_tokens)}"
            )
            
            # Search
            results = self.engine.search(q_vector, top_k=10)
            
            # Display results
            self.results_text.delete(1.0, tk.END)
            
            if not results:
                self.results_text.insert(tk.END, "Tidak ada dokumen yang ditemukan.\n")
            else:
                self.results_text.insert(
                    tk.END,
                    f"Ditemukan {len(results)} dokumen relevan:\n\n",
                    "header"
                )
                
                for rank, res in enumerate(results, 1):
                    doc_meta = res['metadata']
                    score = res['score']
                    
                    # Color code based on score
                    if score >= 0.7:
                        tag = "high"
                    elif score >= 0.4:
                        tag = "medium"
                    else:
                        tag = "low"
                    
                    result_text = f"{rank}. {doc_meta['filename']}\n"
                    result_text += f"   Score: {score:.4f}\n"
                    result_text += f"   Path: {doc_meta['filepath']}\n\n"
                    
                    self.results_text.insert(tk.END, result_text, tag)
            
            # Configure tags for coloring
            self.results_text.tag_config("header", font=("Arial", 11, "bold"))
            self.results_text.tag_config("high", foreground="#27ae60")
            self.results_text.tag_config("medium", foreground="#f39c12")
            self.results_text.tag_config("low", foreground="#e74c3c")
            
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")


def main():
    root = tk.Tk()
    app = MinerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
