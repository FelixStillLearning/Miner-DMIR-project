"""Halaman pencarian."""
import customtkinter as ctk
from ui.components import create_section_header, create_chip, create_panel


def render_search_page(app):
    container = ctk.CTkFrame(app.main_container, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=60, pady=40)

    hero = ctk.CTkFrame(container, fg_color="transparent")
    hero.pack(fill="x", anchor="n")

    create_section_header(
        hero,
        "Pencarian Dokumen",
        "Bahasa Indonesia",
        "Mesin pencari berbasis Tala untuk hasil relevan dan cepat",
        app.colors,
        app.fonts,
    )

    # Search card
    search_card = ctk.CTkFrame(
        hero,
        fg_color=app.colors["surface_dark"],
        corner_radius=16,
        border_width=1,
        border_color=app.colors["border_dark"],
    )
    search_card.pack(fill="x", pady=(0, 22))
    search_card.grid_columnconfigure(0, weight=1)

    search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
    search_inner.grid(row=0, column=0, sticky="ew", padx=18, pady=18)
    search_inner.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        search_inner,
        text="Cari dokumen dengan kata kunci terbaik Anda",
        font=app.fonts["body"],
        text_color=app.colors["text_secondary"],
        anchor="w",
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))

    bar = ctk.CTkFrame(search_inner, fg_color=app.colors["bg_dark"], corner_radius=12)
    bar.grid(row=1, column=0, sticky="ew")
    bar.grid_columnconfigure(0, weight=1)

    app.search_entry = ctk.CTkEntry(
        bar,
        placeholder_text="Masukkan kata kunci pencarian...",
        font=app.fonts["body"],
        height=54,
        border_width=0,
        fg_color="transparent",
    )
    app.search_entry.grid(row=0, column=0, sticky="ew", padx=18, pady=10)
    app.search_entry.bind("<Return>", lambda e: app.perform_search())

    app.search_button = ctk.CTkButton(
        bar,
        text="Cari",
        command=app.perform_search,
        fg_color=app.colors["primary"],
        hover_color="#0d6ecc",
        font=app.fonts["body"],
        width=120,
        height=44,
        corner_radius=10,
    )
    app.search_button.grid(row=0, column=1, padx=10, pady=10)

    app.search_status = ctk.CTkLabel(
        search_inner,
        text="",
        font=app.fonts["caption"],
        text_color=app.colors["text_secondary"],
        anchor="w",
    )
    app.search_status.grid(row=2, column=0, sticky="w", pady=(6, 0))

    chips_frame = ctk.CTkFrame(hero, fg_color="transparent")
    chips_frame.pack(pady=16)
    app.doc_count_label = create_chip(
        chips_frame,
        f"Status: {len(app.processed_docs)} dokumen terindeks",
        app.colors,
        app.fonts,
        image=app.images.get("result"),
    )
    create_chip(chips_frame, "Stemming Tala + Stopword manual", app.colors, app.fonts, image=app.images.get("stop"))
    create_chip(chips_frame, "Format: TXT, DOCX, PDF", app.colors, app.fonts)

    panel_row = ctk.CTkFrame(container, fg_color="transparent")
    panel_row.pack(fill="x", pady=(10, 0))
    panel_row.grid_columnconfigure((0, 1), weight=1, uniform="panel")

    left_panel = ctk.CTkFrame(panel_row, fg_color="transparent")
    left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    right_panel = ctk.CTkFrame(panel_row, fg_color="transparent")
    right_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

    create_panel(
        left_panel,
        "Alur Pencarian",
        "1) Baca & bersihkan dokumen → 2) Tokenisasi → 3) Stopword removal → 4) Stemming Tala → 5) Inverted Index → 6) Pencarian LM (Dirichlet).",
        app.colors,
        app.fonts,
        icon="",
    )

    create_panel(
        right_panel,
        "Tips Kata Kunci",
        "Gunakan 2-4 kata yang spesifik. Sistem akan menyorot istilah yang cocok dan menampilkan pratinjau konteks dari dokumen yang ditemukan.",
        app.colors,
        app.fonts,
        icon="",
    )
