"""Helper untuk memuat aset gambar UI."""
from pathlib import Path
from PIL import Image, ImageDraw
import customtkinter as ctk


def _load_rounded_image(path: Path, size, radius=8):
    img = Image.open(path).convert("RGBA").resize(size, Image.LANCZOS)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), (size[0], size[1])], radius=radius, fill=255)
    img.putalpha(mask)
    return img


def load_images(base_dir: Path):
    """Muat aset PNG jika tersedia; abaikan jika gagal."""
    assets = {
        "logo": ("logo.png", (34, 34)),
        "stop": ("StopFix.png", (22, 22)),
        "highlight": ("highlight_preview_Fix.png", (22, 22)),
        "result": ("resultFix.png", (26, 26)),
        "upload": ("uploadFix.png", (72, 72)),
    }

    images = {}
    for key, (filename, size) in assets.items():
        path = base_dir / filename
        if not path.exists():
            images[key] = None
            continue
        try:
            if key == "logo":
                img = _load_rounded_image(path, size, radius=8)
                images[key] = ctk.CTkImage(light_image=img, size=size)
            else:
                images[key] = ctk.CTkImage(light_image=Image.open(path), size=size)
        except Exception:
            images[key] = None
    return images
