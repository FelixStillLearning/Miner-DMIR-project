
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageOps

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

        # Font presets untuk konsistensi UI
        self.fonts = {
            "hero": ctk.CTkFont(family="Poppins", size=44, weight="bold"),
            "hero_accent": ctk.CTkFont(family="Poppins", size=44, weight="bold"),
            "subtitle": ctk.CTkFont(family="Poppins", size=15),
            "chip": ctk.CTkFont(family="Poppins", size=13),
            "body": ctk.CTkFont(family="Poppins", size=14),
            "card_title": ctk.CTkFont(family="Poppins", size=18, weight="bold"),
            "label": ctk.CTkFont(family="Poppins", size=12, weight="bold")
        }
        
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
        self.load_images()
        
        # Current page
        self.current_page = "search"
        
        # Setup UI
        self.setup_ui()

    def load_images(self):
        """Load PNG assets (Fix variants) for UI icons."""
        base_dir = Path(__file__).resolve().parent / "Icon1"
        assets = {
            "logo": ("logo.png", (34, 34)),
            "stop": ("StopFix.png", (22, 22)),
            "highlight": ("highlight_preview_Fix.png", (22, 22)),
            "result": ("resultFix.png", (26, 26)),
            "upload": ("uploadFix.png", (72, 72)),
        }
        for key, (filename, size) in assets.items():
            path = base_dir / filename
            if path.exists():
                try:
                    if key == "logo":
                        img = self._load_rounded_image(path, size, radius=8)
                        self.images[key] = ctk.CTkImage(light_image=img, size=size)
                    else:
                        self.images[key] = ctk.CTkImage(light_image=Image.open(path), size=size)
                except Exception:
                    self.images[key] = None
            else:
                self.images[key] = None

    def _load_rounded_image(self, path: Path, size, radius=8):
        """Load image and apply rounded corners."""
        img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
        mask = Image.new("L", size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), (size[0], size[1])], radius=radius, fill=255)
        img.putalpha(mask)
        return img
        
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

    def clear_main_container(self):
        """Hapus seluruh konten utama sebelum memuat halaman baru."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def create_section_header(self, parent, title, accent, subtitle, badge=None):
        """Header dengan judul besar, aksen, dan subjudul ringkas."""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 25))

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x")

        ctk.CTkLabel(
            title_row,
            text=title,
            font=self.fonts["hero"],
            text_color=self.colors["text_primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            title_row,
            text=accent,
            font=self.fonts["hero_accent"],
            text_color=self.colors["primary"]
        ).pack(side="left", padx=(12, 0))

        if badge:
            ctk.CTkLabel(
                title_row,
                text=badge,
                font=self.fonts["chip"],
                text_color=self.colors["primary"],
                fg_color=self.colors["border_dark"],
                corner_radius=8,
                padx=10,
                pady=4
            ).pack(side="left", padx=(16, 0))

        ctk.CTkLabel(
            header,
            text=subtitle,
            font=self.fonts["subtitle"],
            text_color=self.colors["text_secondary"],
            justify="left"
        ).pack(anchor="w", pady=(10, 0))

        return header

    def create_chip(self, parent, text, icon_text="", fg=None, image=None):
        """Chip stat ringkas untuk status cepat."""
        chip = ctk.CTkFrame(parent, fg_color=fg or self.colors["surface_dark"], corner_radius=18, height=40)
        chip.pack(side="left", padx=8)
        chip.pack_propagate(False)

        label = ctk.CTkLabel(
            chip,
            text=f"{icon_text} {text}".strip() if icon_text else text,
            font=self.fonts["chip"],
            text_color=self.colors["text_primary"],
            anchor="w",
            image=image,
            compound="left",
            padx=6
        )
        label.pack(padx=14, pady=8)

        return label

    def create_panel(self, parent, title, body, icon=""):
        """Panel konten ringkas untuk informasi atau tips."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=self.colors["surface_dark"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border_dark"]
        )
        panel.pack(fill="x", padx=6, pady=6)

        ctk.CTkLabel(
            panel,
            text=f"{icon} {title}" if icon else title,
            font=self.fonts["card_title"],
            text_color=self.colors["text_primary"],
            anchor="w"
        ).pack(anchor="w", padx=18, pady=(14, 6))

        ctk.CTkLabel(
            panel,
            text=body,
            font=self.fonts["body"],
            text_color=self.colors["text_secondary"],
            justify="left",
            wraplength=780,
            anchor="w"
        ).pack(anchor="w", padx=18, pady=(0, 16))

        return panel 
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        sidebar = ctk.CTkFrame(self, width=250, fg_color=self.colors["surface_dark"])
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Logo and Title
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=30, padx=20)
        
        brand_row = ctk.CTkFrame(logo_frame, fg_color="transparent")
        brand_row.pack()

        if self.images.get("logo"):
            ctk.CTkLabel(
                brand_row,
                text="",
                image=self.images["logo"],
                fg_color="transparent"
            ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            brand_row,
            text="MINER",
            font=ctk.CTkFont(family="Poppins", size=28, weight="bold"),
            text_color=self.colors["primary"]
        ).pack(side="left")
        
        subtitle = ctk.CTkLabel(
            logo_frame,
            text="Information Retrieval",
            font=self.fonts["subtitle"],
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
            text="Pencarian",
            command=lambda: self.navigate_to("search"),
            fg_color=self.colors["primary"],
            hover_color="#0d6ecc",
            font=self.fonts["body"],
            height=45,
            anchor="w",
            corner_radius=10
        )
        self.nav_buttons["search"].pack(fill="x", pady=5)
        
        # Results Button
        self.nav_buttons["results"] = ctk.CTkButton(
            nav_frame,
            text="Hasil Pencarian",
            command=lambda: self.navigate_to("results"),
            fg_color="transparent",
            hover_color=self.colors["border_dark"],
            font=self.fonts["body"],
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
            text="Upload Dokumen",
            command=lambda: self.navigate_to("upload"),
            fg_color="transparent",
            hover_color=self.colors["border_dark"],
            font=self.fonts["body"],
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
            text="0 Dokumen\nTala Stemmer",
            font=self.fonts["chip"],
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
            self.show_search_page()
        elif page == "results":
            self.show_results_page()
        elif page == "upload":
            self.show_upload_page()
    
    def show_search_page(self):
        """Page 1: Search Page (matching pencarian_dokumen.html)"""
        container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=60, pady=40)

        hero = ctk.CTkFrame(container, fg_color="transparent")
        hero.pack(fill="x", anchor="n")

        self.create_section_header(
            hero,
            "Pencarian Dokumen",
            "Bahasa Indonesia",
            "Mesin pencari berbasis Tala untuk hasil relevan dan cepat"
        )

        # Search card
        search_card = ctk.CTkFrame(hero, fg_color=self.colors["surface_dark"], corner_radius=16, border_width=1, border_color=self.colors["border_dark"])
        search_card.pack(fill="x", pady=(0, 22))
        search_card.grid_columnconfigure(0, weight=1)

        search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        search_inner.grid(row=0, column=0, sticky="ew", padx=18, pady=18)
        search_inner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            search_inner,
            text="Cari dokumen dengan kata kunci terbaik Anda",
            font=self.fonts["body"],
            text_color=self.colors["text_secondary"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        bar = ctk.CTkFrame(search_inner, fg_color=self.colors["bg_dark"], corner_radius=12)
        bar.grid(row=1, column=0, sticky="ew")
        bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            bar,
            placeholder_text="Masukkan kata kunci pencarian...",
            font=self.fonts["body"],
            height=54,
            border_width=0,
            fg_color="transparent"
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=18, pady=10)
        self.search_entry.bind('<Return>', lambda e: self.perform_search())

        search_btn = ctk.CTkButton(
            bar,
            text="Cari",
            command=self.perform_search,
            fg_color=self.colors["primary"],
            hover_color="#0d6ecc",
            font=self.fonts["body"],
            width=120,
            height=44,
            corner_radius=10
        )
        search_btn.grid(row=0, column=1, padx=10, pady=10)

        # Status chips
        chips_frame = ctk.CTkFrame(hero, fg_color="transparent")
        chips_frame.pack(pady=16)
        self.doc_count_label = self.create_chip(chips_frame, f"Status: {len(self.processed_docs)} dokumen terindeks", image=self.images.get("result"))
        self.create_chip(chips_frame, "Stemming Tala + Stopword manual", image=self.images.get("stop"))
        self.create_chip(chips_frame, "Format: TXT, DOCX, PDF")

        # Info panels
        panel_row = ctk.CTkFrame(container, fg_color="transparent")
        panel_row.pack(fill="x", pady=(10, 0))
        panel_row.grid_columnconfigure((0, 1), weight=1, uniform="panel")

        left_panel = ctk.CTkFrame(panel_row, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right_panel = ctk.CTkFrame(panel_row, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.create_panel(
            left_panel,
            "Alur Pencarian",
            "1) Baca & bersihkan dokumen → 2) Tokenisasi → 3) Stopword removal → 4) Stemming Tala → 5) TF-IDF & Inverted Index → 6) Pencarian berbasis cosinus.",
            icon=""
        )

        self.create_panel(
            right_panel,
            "Tips Kata Kunci",
            "Gunakan 2-4 kata yang spesifik. Sistem akan menyorot istilah yang cocok dan menampilkan pratinjau konteks dari dokumen yang ditemukan.",
            icon=""
        )
    
    def show_results_page(self):
        """Page 2: Results Page (matching hasil_pencarian_dokumen.html)"""
        if not self.current_results:
            # Show empty state
            empty_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
            empty_frame.pack(expand=True)
            
            state = ctk.CTkFrame(empty_frame, fg_color=self.colors["surface_dark"], corner_radius=12, border_width=1, border_color=self.colors["border_dark"])
            state.pack(padx=80, pady=40)

            ctk.CTkLabel(
                state,
                text="Belum ada hasil pencarian",
                font=self.fonts["card_title"],
                text_color=self.colors["text_primary"]
            ).pack(pady=(24, 6))
            
            ctk.CTkLabel(
                state,
                text="Mulai dari halaman Pencarian untuk melihat hasil.",
                font=self.fonts["body"],
                text_color=self.colors["text_secondary"]
            ).pack(pady=(0, 16))

            ctk.CTkButton(
                state,
                text="Ke Halaman Pencarian",
                command=lambda: self.navigate_to("search"),
                fg_color=self.colors["primary"],
                hover_color="#0d6ecc",
                font=self.fonts["body"],
                width=200
            ).pack(pady=(0, 22))
            
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
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 18))

        self.create_section_header(
            header_frame,
            "Hasil Pencarian",
            f'"{self.current_query}"',
            f"Menampilkan {len(self.current_results)} dokumen relevan",
            badge="Ranking Cosine"
        )

        chips = ctk.CTkFrame(header_frame, fg_color="transparent")
        chips.pack(anchor="w")
        self.create_chip(chips, f"Dokumen terindeks: {len(self.processed_docs)}", image=self.images.get("result"))
        self.create_chip(chips, f"Kata kunci: {len(self.current_results[0].get('query_terms', [])) if self.current_results else 0}")
        self.create_chip(chips, "Pratinjau dengan highlight", image=self.images.get("highlight"))
        
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

        self.create_section_header(
            container,
            "Upload Dokumen",
            "Baru",
            "Tambahkan folder berisi dokumen untuk langsung diindeks",
            badge="Indexer"
        )

        content_row = ctk.CTkFrame(container, fg_color="transparent")
        content_row.pack(fill="both", expand=True)
        content_row.grid_columnconfigure((0, 1), weight=1, uniform="upload")

        # Upload Area
        upload_area = ctk.CTkFrame(
            content_row,
            fg_color=self.colors["surface_dark"],
            corner_radius=16,
            border_width=2,
            border_color=self.colors["border_dark"],
            height=340
        )
        upload_area.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        upload_area.grid_propagate(False)

        upload_content = ctk.CTkFrame(upload_area, fg_color="transparent")
        upload_content.place(relx=0.5, rely=0.5, anchor="center")

        if self.images.get("upload"):
            ctk.CTkLabel(
                upload_content,
                text="",
                image=self.images["upload"],
                fg_color="transparent"
            ).pack()

        ctk.CTkLabel(
            upload_content,
            text="Pilih Folder Dokumen",
            font=self.fonts["card_title"],
            text_color=self.colors["text_primary"]
        ).pack(pady=10)

        ctk.CTkLabel(
            upload_content,
            text="Format: .txt, .docx, .pdf",
            font=self.fonts["body"],
            text_color=self.colors["text_secondary"]
        ).pack(pady=4)

        ctk.CTkButton(
            upload_content,
            text="Browse Folder",
            command=self.browse_and_index,
            fg_color=self.colors["primary"],
            hover_color="#0d6ecc",
            font=self.fonts["body"],
            width=200,
            height=48,
            corner_radius=10
        ).pack(pady=18)

        # Guidance
        guide_panel = ctk.CTkFrame(content_row, fg_color="transparent")
        guide_panel.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
        guide_panel.grid_rowconfigure(1, weight=1)

        self.create_panel(
            guide_panel,
            "Tips Upload",
            "1) Gunakan folder dengan nama deskriptif.\n2) Pastikan file tidak terkunci.\n3) Hindari karakter spesial ekstrem pada nama file.",
            icon=""
        )

        self.create_panel(
            guide_panel,
            "Status Indexer",
            "Progress bar akan bergerak otomatis selama pemrosesan. Anda tetap bisa menavigasi halaman lain sementara proses berjalan.",
            icon=""
        )

        # Progress
        self.upload_progress_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.upload_progress_frame.pack(pady=24)

        self.upload_status = ctk.CTkLabel(
            self.upload_progress_frame,
            text="",
            font=self.fonts["body"],
            text_color=self.colors["text_secondary"]
        )
        self.upload_status.pack()

        self.upload_progress = ctk.CTkProgressBar(
            self.upload_progress_frame,
            width=420,
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
                text=f"{doc_count} dokumen berhasil diindeks!",
                text_color=self.colors["success"]
            ))
            
            # Update stats
            self.after(0, lambda: self.stats_label.configure(text=f"{doc_count} Dokumen\nTala Stemmer"))
            
            # Update doc count label if exists
            if hasattr(self, 'doc_count_label'):
                self.after(0, lambda: self.doc_count_label.configure(text=f"Status: {doc_count} Dokumen Terindeks"))
            
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
