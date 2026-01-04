"""Pipeline utilitas untuk preprocessing dan indexing dokumen."""
import os
from src.utils.utils import baca_txt, baca_docx, baca_pdf, bersihkan_text, tokenizing
from src.preprocessing.stopword import remove_stopwords
from src.preprocessing.tala_stemmer import Stem_Tala_tokenizing
from src.indexing.inverted_index import InvertedIndex
from src.query.query_processor import QueryProcessor
from src.retrieval.retrieval_engine import RetrievalEngine

SUPPORTED_EXT = {".txt", ".docx", ".pdf"}


def _read_file(filepath, ext):
    if ext == ".txt":
        return baca_txt(filepath)
    if ext == ".docx":
        return baca_docx(filepath)
    if ext == ".pdf":
        return baca_pdf(filepath)
    raise ValueError(f"Ekstensi tidak didukung: {ext}")


def preprocess_text(text):
    """Bersihkan, tokenisasi, hapus stopword, dan stemming Tala."""
    clean_text = bersihkan_text(text)
    tokens = tokenizing(clean_text)
    tokens_no_stop = remove_stopwords(tokens)
    tokens_stem = Stem_Tala_tokenizing(tokens_no_stop)
    return tokens_stem, tokens, tokens_no_stop, clean_text


def process_directory(directory, ekstensi_file=None, progress_cb=None):
    """Proses seluruh dokumen dalam folder menjadi daftar dokumen terproses."""
    ekstensi = ekstensi_file or SUPPORTED_EXT
    files = [
        (file, os.path.join(directory, file), os.path.splitext(file)[1].lower())
        for file in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, file))
        and os.path.splitext(file)[1].lower() in ekstensi
    ]

    processed_docs = []
    total = len(files)

    for idx, (filename, filepath, ext) in enumerate(files, 1):
        try:
            raw_text = _read_file(filepath, ext)
            tokens_stem, tokens_raw, tokens_no_stop, clean_text = preprocess_text(raw_text)
            
            # Hitung kata dasar unik
            unique_stems = set(tokens_stem)
            
            # Hitung frekuensi kata dasar (untuk tabel)
            from collections import Counter
            stem_freq = Counter(tokens_stem)
            # Sort by frequency descending
            stem_freq_sorted = sorted(stem_freq.items(), key=lambda x: x[1], reverse=True)

            processed_docs.append({
                "id": idx,
                "tokens": tokens_stem,
                "metadata": {
                    "filename": filename,
                    "filepath": filepath,
                },
                "stats": {
                    "tokens": len(tokens_raw),
                    "after_stopword": len(tokens_no_stop),
                    "after_stem": len(tokens_stem),
                    "unique_stems": len(unique_stems),
                },
                "preprocessing": {
                    "raw_text": raw_text[:2000],  # Simpan 2000 karakter pertama
                    "clean_text": clean_text[:2000],
                    "tokens_raw": tokens_raw[:100],  # Simpan 100 token pertama
                    "tokens_no_stop": tokens_no_stop[:100],
                    "tokens_stem": tokens_stem[:100],
                    "stem_frequency": stem_freq_sorted,  # Full frequency table sorted
                },
            })

            if progress_cb and total:
                progress_cb(idx, total)
        except Exception as exc:  # pragma: no cover - hanya logging
            print(f"Error processing {filename}: {exc}")

    return processed_docs


def build_models(processed_docs):
    """Bangun inverted index, query processor, dan retrieval engine (LM Dirichlet)."""
    inverted_index = InvertedIndex()
    inverted_index.build_index(processed_docs)

    query_processor = QueryProcessor()
    engine = RetrievalEngine(inverted_index)

    return inverted_index, query_processor, engine
