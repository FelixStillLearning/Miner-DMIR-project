"""Halaman daftar dokumen dan detail preprocessing."""
import customtkinter as ctk
from ui.components import create_section_header


def render_documents_page(app):
    """Render halaman dokumen dengan tabel dan detail preprocessing."""
    
    if not app.processed_docs:
        # Empty state
        empty_frame = ctk.CTkFrame(app.main_container, fg_color="transparent")
        empty_frame.pack(expand=True)

        state = ctk.CTkFrame(
            empty_frame,
            fg_color=app.colors["surface_dark"],
            corner_radius=12,
            border_width=1,
            border_color=app.colors["border_dark"],
        )
        state.pack(padx=80, pady=40)

        ctk.CTkLabel(
            state,
            text="Belum ada dokumen",
            font=app.fonts["card_title"],
            text_color=app.colors["text_primary"],
        ).pack(pady=(24, 6))

        ctk.CTkLabel(
            state,
            text="Upload folder dokumen terlebih dahulu untuk melihat daftar dan detail preprocessing.",
            font=app.fonts["body"],
            text_color=app.colors["text_secondary"],
            wraplength=400,
        ).pack(pady=(0, 12))

        ctk.CTkButton(
            state,
            text="Ke Halaman Upload",
            command=lambda: app.navigate_to("upload"),
            fg_color=app.colors["primary"],
            hover_color="#0d6ecc",
            font=app.fonts["body"],
            width=200,
        ).pack(pady=(0, 22))
        return

    # Main container dengan 2 panel
    main_frame = ctk.CTkFrame(app.main_container, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=30, pady=20)
    main_frame.grid_columnconfigure(0, weight=2)
    main_frame.grid_columnconfigure(1, weight=3)
    main_frame.grid_rowconfigure(1, weight=1)

    # Header
    header = ctk.CTkFrame(main_frame, fg_color="transparent")
    header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
    
    create_section_header(
        header,
        "Daftar Dokumen",
        f"{len(app.processed_docs)} file",
        "Klik dokumen untuk melihat detail preprocessing",
        app.colors,
        app.fonts,
        badge="Preprocessing",
    )

    # Left panel - Document table
    left_panel = ctk.CTkFrame(main_frame, fg_color=app.colors["surface_dark"], corner_radius=12)
    left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
    
    # Table header
    table_header = ctk.CTkFrame(left_panel, fg_color=app.colors["bg_dark"], corner_radius=8)
    table_header.pack(fill="x", padx=10, pady=10)
    
    headers = ["No", "Filename", "Token", "Stop", "Stem", "Unik"]
    widths = [35, 150, 50, 50, 50, 50]
    
    for i, (h, w) in enumerate(zip(headers, widths)):
        ctk.CTkLabel(
            table_header,
            text=h,
            font=app.fonts["chip"],
            text_color=app.colors["text_secondary"],
            width=w,
            anchor="w" if i == 1 else "center",
        ).pack(side="left", padx=3, pady=8)

    # Scrollable document list
    doc_scroll = ctk.CTkScrollableFrame(
        left_panel,
        fg_color="transparent",
        scrollbar_button_color=app.colors["border_dark"],
    )
    doc_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 10))

    # Store reference to selected doc for detail panel
    app.selected_doc_index = 0
    app.doc_rows = []

    def select_doc(idx):
        app.selected_doc_index = idx
        update_detail_panel()
        # Update row highlighting
        for i, row in enumerate(app.doc_rows):
            if i == idx:
                row.configure(fg_color=app.colors["primary"])
            else:
                row.configure(fg_color="transparent")

    # Create document rows
    for i, doc in enumerate(app.processed_docs):
        row = ctk.CTkFrame(
            doc_scroll,
            fg_color=app.colors["primary"] if i == 0 else "transparent",
            corner_radius=6,
            cursor="hand2",
        )
        row.pack(fill="x", pady=2)
        row.bind("<Button-1>", lambda e, idx=i: select_doc(idx))
        app.doc_rows.append(row)

        stats = doc.get("stats", {})
        filename = doc["metadata"]["filename"]
        # Truncate filename if too long
        display_name = filename[:18] + "..." if len(filename) > 20 else filename

        values = [
            str(i + 1),
            display_name,
            str(stats.get("tokens", 0)),
            str(stats.get("after_stopword", 0)),
            str(stats.get("after_stem", 0)),
            str(stats.get("unique_stems", 0)),
        ]

        for j, (v, w) in enumerate(zip(values, widths)):
            lbl = ctk.CTkLabel(
                row,
                text=v,
                font=app.fonts["body"],
                text_color=app.colors["text_primary"],
                width=w,
                anchor="w" if j == 1 else "center",
            )
            lbl.pack(side="left", padx=3, pady=8)
            lbl.bind("<Button-1>", lambda e, idx=i: select_doc(idx))

    # Right panel - Detail preprocessing
    right_panel = ctk.CTkFrame(main_frame, fg_color=app.colors["surface_dark"], corner_radius=12)
    right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 0))

    # Detail content frame (will be updated)
    app.detail_frame = ctk.CTkScrollableFrame(
        right_panel,
        fg_color="transparent",
        scrollbar_button_color=app.colors["border_dark"],
    )
    app.detail_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def update_detail_panel():
        # Clear existing content
        for widget in app.detail_frame.winfo_children():
            widget.destroy()

        if app.selected_doc_index >= len(app.processed_docs):
            return

        doc = app.processed_docs[app.selected_doc_index]
        preprocessing = doc.get("preprocessing", {})
        stats = doc.get("stats", {})

        # Document title
        ctk.CTkLabel(
            app.detail_frame,
            text=f"{doc['metadata']['filename']}",
            font=app.fonts["card_title"],
            text_color=app.colors["text_primary"],
            anchor="w",
        ).pack(fill="x", pady=(0, 10))

        # Stats summary
        stats_frame = ctk.CTkFrame(app.detail_frame, fg_color=app.colors["bg_dark"], corner_radius=8)
        stats_frame.pack(fill="x", pady=(0, 15))

        stats_text = f"Token Awal: {stats.get('tokens', 0)} → Setelah Stopword: {stats.get('after_stopword', 0)} → Setelah Stemming: {stats.get('after_stem', 0)} | Kata Dasar Unik: {stats.get('unique_stems', 0)}"
        ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=app.fonts["chip"],
            text_color=app.colors["text_secondary"],
            wraplength=500,
        ).pack(padx=10, pady=10)

        # Preprocessing sections
        sections = [
            ("1. Teks Asli (Raw Text)", preprocessing.get("raw_text", "")[:500] + "..."),
            ("2. Setelah Case Folding & Cleaning", preprocessing.get("clean_text", "")[:500] + "..."),
            ("3. Hasil Tokenizing", " | ".join(preprocessing.get("tokens_raw", [])[:30]) + " ..."),
            ("4. Setelah Stopword Removal", " | ".join(preprocessing.get("tokens_no_stop", [])[:30]) + " ..."),
            ("5. Hasil Stemming (Preview)", " | ".join(preprocessing.get("tokens_stem", [])[:30]) + " ..."),
        ]

        for title, content in sections:
            section = ctk.CTkFrame(app.detail_frame, fg_color="transparent")
            section.pack(fill="x", pady=5)

            ctk.CTkLabel(
                section,
                text=title,
                font=app.fonts["body"],
                text_color=app.colors["primary"],
                anchor="w",
            ).pack(fill="x")

            content_box = ctk.CTkTextbox(
                section,
                font=app.fonts["caption"],
                text_color=app.colors["text_secondary"],
                fg_color=app.colors["bg_dark"],
                height=80,
                wrap="word",
                activate_scrollbars=True,
            )
            content_box.pack(fill="x", pady=(5, 10))
            content_box.insert("1.0", content if content else "(Tidak ada data)")
            content_box.configure(state="disabled")

        # Section 6: Tabel Frekuensi Kata Dasar (Full, sorted by frequency)
        freq_section = ctk.CTkFrame(app.detail_frame, fg_color="transparent")
        freq_section.pack(fill="x", pady=5)

        ctk.CTkLabel(
            freq_section,
            text=f"6. Frekuensi Kata Dasar (Total: {stats.get('unique_stems', 0)} kata unik)",
            font=app.fonts["body"],
            text_color=app.colors["primary"],
            anchor="w",
        ).pack(fill="x")

        # Table header for frequency
        freq_header = ctk.CTkFrame(freq_section, fg_color=app.colors["bg_dark"], corner_radius=6)
        freq_header.pack(fill="x", pady=(5, 0))

        ctk.CTkLabel(
            freq_header, text="No", font=app.fonts["chip"],
            text_color=app.colors["text_secondary"], width=40, anchor="center"
        ).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(
            freq_header, text="Kata Dasar", font=app.fonts["chip"],
            text_color=app.colors["text_secondary"], width=200, anchor="w"
        ).pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(
            freq_header, text="Jumlah", font=app.fonts["chip"],
            text_color=app.colors["text_secondary"], width=60, anchor="center"
        ).pack(side="left", padx=5, pady=5)

        # Scrollable frequency table
        freq_scroll = ctk.CTkScrollableFrame(
            freq_section,
            fg_color=app.colors["bg_dark"],
            height=200,
            scrollbar_button_color=app.colors["border_dark"],
        )
        freq_scroll.pack(fill="x", pady=(0, 10))

        stem_freq = preprocessing.get("stem_frequency", [])
        for i, (word, count) in enumerate(stem_freq, 1):
            row = ctk.CTkFrame(freq_scroll, fg_color="transparent")
            row.pack(fill="x")

            ctk.CTkLabel(
                row, text=str(i), font=app.fonts["caption"],
                text_color=app.colors["text_secondary"], width=40, anchor="center"
            ).pack(side="left", padx=5, pady=2)
            ctk.CTkLabel(
                row, text=word, font=app.fonts["caption"],
                text_color=app.colors["text_primary"], width=200, anchor="w"
            ).pack(side="left", padx=5, pady=2)
            ctk.CTkLabel(
                row, text=str(count), font=app.fonts["caption"],
                text_color=app.colors["success"], width=60, anchor="center"
            ).pack(side="left", padx=5, pady=2)

    # Initial detail render
    update_detail_panel()
