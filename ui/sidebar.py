"""Sidebar navigasi."""
import customtkinter as ctk


def build_sidebar(app):
    sidebar = ctk.CTkFrame(app, width=250, fg_color=app.colors["surface_dark"])
    sidebar.grid(row=0, column=0, sticky="nsew")
    sidebar.grid_propagate(False)

    # Logo dan judul
    logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    logo_frame.pack(pady=30, padx=20)

    brand_row = ctk.CTkFrame(logo_frame, fg_color="transparent")
    brand_row.pack()

    if app.images.get("logo"):
        ctk.CTkLabel(
            brand_row,
            text="",
            image=app.images["logo"],
            fg_color="transparent",
        ).pack(side="left", padx=(0, 8))

    ctk.CTkLabel(
        brand_row,
        text="MINER",
        font=ctk.CTkFont(family="Poppins", size=28, weight="bold"),
        text_color=app.colors["primary"],
    ).pack(side="left")

    ctk.CTkLabel(
        logo_frame,
        text="Information Retrieval",
        font=app.fonts["subtitle"],
        text_color=app.colors["text_secondary"],
    ).pack()

    # Tombol navigasi
    nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    nav_frame.pack(fill="both", expand=True, padx=15, pady=20)
    app.nav_buttons = {}

    def add_nav_button(name, label):
        btn = ctk.CTkButton(
            nav_frame,
            text=label,
            command=lambda: app.navigate_to(name),
            fg_color=app.colors["primary"] if name == "search" else "transparent",
            hover_color="#0d6ecc" if name == "search" else app.colors["border_dark"],
            font=app.fonts["body"],
            height=45,
            anchor="w",
            corner_radius=10,
            border_width=0 if name == "search" else 1,
            border_color=app.colors["border_dark"] if name != "search" else None,
        )
        btn.pack(fill="x", pady=5)
        app.nav_buttons[name] = btn

    add_nav_button("search", "Pencarian")
    add_nav_button("results", "Hasil Pencarian")
    add_nav_button("documents", "Dokumen")
    add_nav_button("upload", "Upload Dokumen")

    # Statistik bawah
    stats_frame = ctk.CTkFrame(sidebar, fg_color=app.colors["bg_dark"], corner_radius=10)
    stats_frame.pack(side="bottom", fill="x", padx=15, pady=20)

    app.stats_label = ctk.CTkLabel(
        stats_frame,
        text="0 Dokumen\nTala Stemmer",
        font=app.fonts["chip"],
        text_color=app.colors["text_secondary"],
        justify="center",
    )
    app.stats_label.pack(pady=15)

    return sidebar
