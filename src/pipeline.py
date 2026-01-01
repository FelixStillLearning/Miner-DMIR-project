"""Pipeline utilitas untuk preprocessing dan indexing dokumen."""
import os
from src.utils.utils import baca_txt, baca_docx, baca_pdf, bersihkan_text
from src.preprocessing.tokenizing import tokenizing
from src.preprocessing.stopword import remove_stopwords
from src.preprocessing.tala_stemmer import Stem_Tala_tokenizing
from src.feature_extraction.tfidf import TFIDF
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
    return tokens_stem, tokens, tokens_no_stop


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
            tokens_stem, tokens_raw, tokens_no_stop = preprocess_text(raw_text)

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
                },
            })

            if progress_cb and total:
                progress_cb(idx, total)
        except Exception as exc:  # pragma: no cover - hanya logging
            print(f"Error processing {filename}: {exc}")

    return processed_docs


def build_models(processed_docs):
    """Bangun TF-IDF, inverted index, query processor, dan retrieval engine."""
    tfidf_model = TFIDF()
    corpus_tokens = [doc["tokens"] for doc in processed_docs]
    tfidf_model.calculate_idf(corpus_tokens)

    inverted_index = InvertedIndex()
    inverted_index.build_index(processed_docs, tfidf_model)

    query_processor = QueryProcessor(tfidf_model)
    engine = RetrievalEngine(inverted_index, tfidf_model)

    return tfidf_model, inverted_index, query_processor, engine
