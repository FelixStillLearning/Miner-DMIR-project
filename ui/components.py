"""Komponen UI reuseable untuk MINER."""
import customtkinter as ctk


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
