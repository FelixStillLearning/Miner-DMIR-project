"""Palet warna dan font untuk MINER UI."""
import customtkinter as ctk

# Warna utama aplikasi
COLORS = {
    "primary": "#137fec",
    "bg_dark": "#101922",
    "surface_dark": "#1c2630",
    "border_dark": "#2a3744",
    "text_primary": "#ffffff",
    "text_secondary": "#9dabb9",
    "success": "#27ae60",
    "warning": "#f39c12",
    "danger": "#e74c3c",
}


def build_fonts():
    """Bangun kumpulan font yang konsisten."""
    return {
        "hero": ctk.CTkFont(family="Poppins", size=44, weight="bold"),
        "hero_accent": ctk.CTkFont(family="Poppins", size=44, weight="bold"),
        "subtitle": ctk.CTkFont(family="Poppins", size=15),
        "chip": ctk.CTkFont(family="Poppins", size=13),
        "body": ctk.CTkFont(family="Poppins", size=14),
        "card_title": ctk.CTkFont(family="Poppins", size=18, weight="bold"),
        "label": ctk.CTkFont(family="Poppins", size=12, weight="bold"),
        "caption": ctk.CTkFont(family="Poppins", size=11),
    }
