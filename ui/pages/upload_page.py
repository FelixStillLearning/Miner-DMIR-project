"""Halaman upload dokumen."""
import customtkinter as ctk
from ui.components import create_section_header, create_panel


def render_upload_page(app):
    container = ctk.CTkFrame(app.main_container, fg_color="transparent")
    container.pack(fill="both", expand=True, padx=60, pady=40)

    create_section_header(
        container,
        "Upload Dokumen",
        "Baru",
        "Tambahkan folder berisi dokumen untuk langsung diindeks",
        app.colors,
        app.fonts,
        badge="Indexer",
    )

    content_row = ctk.CTkFrame(container, fg_color="transparent")
    content_row.pack(fill="both", expand=True)
    content_row.grid_columnconfigure((0, 1), weight=1, uniform="upload")

    upload_area = ctk.CTkFrame(
        content_row,
        fg_color=app.colors["surface_dark"],
        corner_radius=16,
        border_width=2,
        border_color=app.colors["border_dark"],
        height=340,
    )
    upload_area.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
    upload_area.grid_propagate(False)

    upload_content = ctk.CTkFrame(upload_area, fg_color="transparent")
    upload_content.place(relx=0.5, rely=0.5, anchor="center")

    if app.images.get("upload"):
        ctk.CTkLabel(upload_content, text="", image=app.images["upload"], fg_color="transparent").pack()

    ctk.CTkLabel(
        upload_content,
        text="Pilih Folder Dokumen",
        font=app.fonts["card_title"],
        text_color=app.colors["text_primary"],
    ).pack(pady=10)

    ctk.CTkLabel(
        upload_content,
        text="Format: .txt, .docx, .pdf",
        font=app.fonts["body"],
        text_color=app.colors["text_secondary"],
    ).pack(pady=4)

    ctk.CTkButton(
        upload_content,
        text="Browse Folder",
        command=app.browse_and_index,
        fg_color=app.colors["primary"],
        hover_color="#0d6ecc",
        font=app.fonts["body"],
        width=200,
        height=48,
        corner_radius=10,
    ).pack(pady=18)

    guide_panel = ctk.CTkFrame(content_row, fg_color="transparent")
    guide_panel.grid(row=0, column=1, sticky="nsew", padx=(14, 0))
    guide_panel.grid_rowconfigure(1, weight=1)

    create_panel(
        guide_panel,
        "Tips Upload",
        "1) Gunakan folder dengan nama deskriptif.\n2) Pastikan file tidak terkunci.\n3) Hindari karakter spesial ekstrem pada nama file.",
        app.colors,
        app.fonts,
        icon="",
    )

    create_panel(
        guide_panel,
        "Status Indexer",
        "Progress bar akan bergerak otomatis selama pemrosesan. Anda tetap bisa menavigasi halaman lain sementara proses berjalan.",
        app.colors,
        app.fonts,
        icon="",
    )

    app.upload_progress_frame = ctk.CTkFrame(container, fg_color="transparent")
    app.upload_progress_frame.pack(pady=24)

    app.upload_status = ctk.CTkLabel(
        app.upload_progress_frame,
        text="",
        font=app.fonts["body"],
        text_color=app.colors["text_secondary"],
    )
    app.upload_status.pack()

    app.upload_progress = ctk.CTkProgressBar(
        app.upload_progress_frame,
        width=420,
        height=10,
        progress_color=app.colors["primary"],
    )
    app.upload_progress.set(0)
