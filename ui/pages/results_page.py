"""Halaman hasil pencarian."""
import customtkinter as ctk
from ui.components import create_section_header, create_chip, create_result_card


def render_results_page(app):
    if not app.current_results:
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
            text="Belum ada hasil pencarian",
            font=app.fonts["card_title"],
            text_color=app.colors["text_primary"],
        ).pack(pady=(24, 6))

        ctk.CTkLabel(
            state,
            text="Mulai dari halaman Pencarian untuk melihat hasil.",
            font=app.fonts["body"],
            text_color=app.colors["text_secondary"],
        ).pack(pady=(0, 12))

        ctk.CTkButton(
            state,
            text="Ke Halaman Pencarian",
            command=lambda: app.navigate_to("search"),
            fg_color=app.colors["primary"],
            hover_color="#0d6ecc",
            font=app.fonts["body"],
            width=200,
        ).pack(pady=(0, 22))
        return

    main_scroll = ctk.CTkScrollableFrame(
        app.main_container,
        fg_color="transparent",
        scrollbar_button_color=app.colors["surface_dark"],
    )
    main_scroll.pack(fill="both", expand=True, padx=40, pady=30)
    main_scroll.grid_columnconfigure(0, weight=1)

    header_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
    header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 18))

    create_section_header(
        header_frame,
        "Hasil Pencarian",
        f'"{app.current_query}"',
        f"Menampilkan {len(app.current_results)} dokumen relevan",
        app.colors,
        app.fonts,
        badge="Ranking LM Dirichlet",
    )

    chips = ctk.CTkFrame(header_frame, fg_color="transparent")
    chips.pack(anchor="w")
    create_chip(
        chips,
        f"Dokumen terindeks: {len(app.processed_docs)}",
        app.colors,
        app.fonts,
        image=app.images.get("result"),
    )
    create_chip(
        chips,
        f"Kata kunci: {len(app.current_results[0].get('query_terms', [])) if app.current_results else 0}",
        app.colors,
        app.fonts,
    )
    create_chip(
        chips,
        f"Waktu: {app.current_search_time_ms:.1f} ms",
        app.colors,
        app.fonts,
    )
    create_chip(
        chips,
        "Pratinjau dengan highlight",
        app.colors,
        app.fonts,
        image=app.images.get("highlight"),
    )

    results_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
    results_frame.grid(row=1, column=0, sticky="ew")
    results_frame.grid_columnconfigure(0, weight=1)

    for rank, res in enumerate(app.current_results, 1):
        create_result_card(
            results_frame,
            rank,
            res['metadata']['filename'],
            res['score'],
            res['metadata']['filepath'],
            res.get('preview', ''),
            res.get('query_terms', []),
            raw_score=res.get('raw_score'),
            colors=app.colors,
            fonts=app.fonts,
            images=app.images,
            open_file_cb=app.open_file,
        )
