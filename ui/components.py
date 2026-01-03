"""Komponen UI reuseable untuk MINER."""
import customtkinter as ctk
from tkinter import messagebox
from src.utils.view_helpers import highlight_text


def create_section_header(parent, title, accent, subtitle, colors, fonts, badge=None):
    """Header dengan judul besar, aksen, dan subjudul ringkas."""
    header = ctk.CTkFrame(parent, fg_color="transparent")
    header.pack(fill="x", pady=(0, 25))

    title_row = ctk.CTkFrame(header, fg_color="transparent")
    title_row.pack(fill="x")

    ctk.CTkLabel(
        title_row,
        text=title,
        font=fonts["hero"],
        text_color=colors["text_primary"],
    ).pack(side="left")

    ctk.CTkLabel(
        title_row,
        text=accent,
        font=fonts["hero_accent"],
        text_color=colors["primary"],
    ).pack(side="left", padx=(12, 0))

    if badge:
        ctk.CTkLabel(
            title_row,
            text=badge,
            font=fonts["chip"],
            text_color=colors["primary"],
            fg_color=colors["border_dark"],
            corner_radius=8,
            padx=10,
            pady=4,
        ).pack(side="left", padx=(16, 0))

    ctk.CTkLabel(
        header,
        text=subtitle,
        font=fonts["subtitle"],
        text_color=colors["text_secondary"],
        justify="left",
    ).pack(anchor="w", pady=(10, 0))

    return header


def create_chip(parent, text, colors, fonts, icon_text="", fg=None, image=None):
    """Chip stat ringkas untuk status cepat."""
    chip = ctk.CTkFrame(parent, fg_color=fg or colors["surface_dark"], corner_radius=18, height=40)
    chip.pack(side="left", padx=8)
    chip.pack_propagate(False)

    label = ctk.CTkLabel(
        chip,
        text=f"{icon_text} {text}".strip() if icon_text else text,
        font=fonts["chip"],
        text_color=colors["text_primary"],
        anchor="w",
        image=image,
        compound="left",
        padx=6,
    )
    label.pack(padx=14, pady=8)

    return label


def create_panel(parent, title, body, colors, fonts, icon=""):
    """Panel konten ringkas untuk informasi atau tips."""
    panel = ctk.CTkFrame(
        parent,
        fg_color=colors["surface_dark"],
        corner_radius=12,
        border_width=1,
        border_color=colors["border_dark"],
    )
    panel.pack(fill="x", padx=6, pady=6)

    ctk.CTkLabel(
        panel,
        text=f"{icon} {title}" if icon else title,
        font=fonts["card_title"],
        text_color=colors["text_primary"],
        anchor="w",
    ).pack(anchor="w", padx=18, pady=(14, 6))

    ctk.CTkLabel(
        panel,
        text=body,
        font=fonts["body"],
        text_color=colors["text_secondary"],
        justify="left",
        wraplength=780,
        anchor="w",
    ).pack(anchor="w", padx=18, pady=(0, 16))

    return panel


def create_result_card(
    parent,
    rank,
    filename,
    score,
    filepath,
    preview_text,
    query_terms,
    raw_score,
    colors,
    fonts,
    images,
    open_file_cb,
):
    """Kartu hasil untuk LM Dirichlet (score sudah dinormalisasi 0-1)."""
    query_terms = query_terms or []

    if score >= 0.66:
        score_color = colors["success"]
        bar_color = "#27ae60"
    elif score >= 0.33:
        score_color = colors["warning"]
        bar_color = "#f39c12"
    else:
        score_color = colors["text_secondary"]
        bar_color = colors["primary"]

    card = ctk.CTkFrame(
        parent,
        fg_color=colors["surface_dark"],
        corner_radius=12,
        border_width=1,
        border_color=colors["border_dark"],
    )
    card.grid(row=rank - 1, column=0, sticky="ew", pady=8)
    card.grid_columnconfigure(1, weight=1)

    icon = ctk.CTkLabel(card, text="", font=fonts["card_title"], width=32, image=images.get("result"), compound="left")
    icon.grid(row=0, column=0, rowspan=3, padx=20, pady=20)

    content = ctk.CTkFrame(card, fg_color="transparent")
    content.grid(row=0, column=1, sticky="ew", pady=20, padx=(0, 20))

    ctk.CTkLabel(
        content,
        text=f"{rank}. {filename}",
        font=fonts["card_title"],
        text_color=colors["primary"],
        anchor="w",
    ).pack(anchor="w")

    ctk.CTkLabel(
        content,
        text=filepath,
        font=fonts["body"],
        text_color=colors["text_secondary"],
        anchor="w",
    ).pack(anchor="w", pady=(5, 0))

    if preview_text:
        preview_frame = ctk.CTkFrame(content, fg_color=colors["bg_dark"], corner_radius=8)
        preview_frame.pack(fill="x", pady=(10, 0))

        highlighted = highlight_text(preview_text, query_terms)
        ctk.CTkLabel(
            preview_frame,
            text=highlighted,
            font=fonts["body"],
            text_color="#d0d0d0",
            anchor="w",
            wraplength=700,
            justify="left",
        ).pack(padx=15, pady=10, anchor="w")

    ctk.CTkButton(
        card,
        text="Buka",
        command=lambda: open_file_cb(filepath),
        fg_color=colors["border_dark"],
        hover_color=colors["primary"],
        font=fonts["body"],
        width=90,
        height=32,
    ).grid(row=1, column=1, sticky="w", padx=(0, 20), pady=(0, 20))

    score_frame = ctk.CTkFrame(card, fg_color="transparent")
    score_frame.grid(row=0, column=2, rowspan=3, padx=20, pady=20)

    ctk.CTkLabel(
        score_frame,
        text="RELEVANSI",
        font=fonts["label"],
        text_color=colors["text_secondary"],
    ).pack()

    ctk.CTkLabel(
        score_frame,
        text=f"{score:.2f}",
        font=ctk.CTkFont(family="Poppins", size=22, weight="bold"),
        text_color=score_color,
    ).pack(pady=(5, 5))

    progress = ctk.CTkProgressBar(
        score_frame,
        width=100,
        height=8,
        progress_color=bar_color,
        fg_color=colors["border_dark"],
    )
    progress.set(min(max(score, 0), 1))
    progress.pack()

    def show_detail():
        raw_txt = "n/a" if raw_score is None else f"{raw_score:.4f}"
        messagebox.showinfo("Detail Skor", f"Raw score (log-prob): {raw_txt}")

    ctk.CTkButton(
        score_frame,
        text="Detail",
        command=show_detail,
        fg_color=colors["border_dark"],
        hover_color=colors["primary"],
        font=fonts["caption"],
        width=90,
        height=26,
    ).pack(pady=(8, 0))

    return card
