"""Helper untuk tampilan: highlight dan snippet pratinjau."""
import re
import os
from src.utils.utils import baca_txt, baca_docx, baca_pdf


def highlight_text(text: str, query_terms):
    """Highlight term kueri dengan tanda ()."""
    highlighted = text
    for term in query_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        highlighted = pattern.sub(f"({term.upper()})", highlighted)
    return highlighted


def get_preview_snippet(filepath: str, query_terms, max_length: int = 200):
    """Ambil potongan teks dengan konteks term kueri."""
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

    except Exception:
        return "[Preview tidak tersedia]"
