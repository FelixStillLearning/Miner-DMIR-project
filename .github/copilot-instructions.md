# Copilot Instructions - Text Mining Pipeline

## Project Overview
Indonesian language text mining project for an academic Data Mining course. Implements a complete NLP preprocessing pipeline: document reading → text cleaning → tokenization → stopword removal → stemming with Tala (rule-based, no dictionary).

## Architecture

### Pipeline Flow (main.py)
Proses dokumen dari `docs/` secara berurutan:
1. **File Reading** (`src/utils/utils.py`): `.txt`, `.docx`, `.pdf`
2. **Text Cleaning** (`bersihkan_text`): lowercase → hapus tanda baca/angka → normalisasi spasi
3. **Tokenization** (`src/preprocessing/tokenizing.py`): split + frekuensi
4. **Stopword Removal** (`src/preprocessing/stopword.py`): filter + tampilkan hasil + stopword terhapus
5. **Stemming (Tala)** (`src/preprocessing/tala_stemmer.py`): stem + frekuensi + identifikasi gagal

### Module Responsibilities
- **src/utils/utils.py**: Document I/O and text cleaning - handles encoding issues and format-specific extraction
- **src/preprocessing/tokenizing.py**: Word splitting and frequency analysis - uses dict-based frequency counting (no NLTK FreqDist)
- **src/preprocessing/stopword.py**: Manual Indonesian stopword list, filtering + hasil tampilan + identifikasi terhapus
- **src/preprocessing/tala_stemmer.py**: Implementasi Tala (rule-based). Langkah: partikel → sandang/kepunyaan → awalan-1 → cabang: akhiran & awalan-2. Analitik: frekuensi stem, identifikasi kata gagal (unchanged >3 chars).

## Critical Patterns

### Function Naming Convention
Mix of snake_case and PascalCase observed:
- Functions: `baca_txt()`, `bersihkan_text()`, `tokenizing()`
- Analysis functions: `Hitung_frekuensi()`, `Stem_tokenizing()` (PascalCase for main operations)
- Display functions: `tampilkan_*()` prefix for console output

### Indonesian Language Processing
- All variable names, comments, and output messages are in Indonesian
- Stopword list is manually curated for Indonesian (not using NLTK)
- Tala stemmer (internal rule-based) digunakan sebagai stemmer utama; tidak menggunakan kamus eksternal.

### Output Format Pattern
All modules follow: operation → display results → identify issues pattern:
```python
# Example from stemming.py
tokens_stem = Stem_tokenizing(tokens)           # Transform
frek_stem = hitung_frekuensi_stem(tokens_stem)  # Analyze
tampilkan_hasil_stem(frek_stem)                 # Display
kata_gagal = identifikasi_kata_gagal_stem(...)  # Identify issues
tampilkan_kata_gagal_stem(kata_gagal)           # Report issues
```

## Known Issues

### Stopword Module Not Integrated
[stopword.py](../src/stopword.py) defines `remove_stopwords()` but it's never called in [main.py](../main.py). Pipeline goes directly from tokenization to stemming.

### Code Duplication
[stopword.py](../src/stopword.py) has `get_stopwords_list()` and `tampilkan_hasil_stopword()` functions duplicated (appears twice with truncation).

## Development Workflow

### Running the Pipeline
```bash
python main.py
```
Processes all `.txt`, `.docx`, `.pdf` files in `docs/` directory automatically.

### Dependencies
Install with: `pip install -r requirements.txt`
- **PySastrawi 1.2.0**: Indonesian stemmer (critical - no alternatives)
- **python-docx 1.1.2**: .docx parsing
- **PyPDF2 3.0.1**: PDF text extraction
- **NLTK 3.9.1**: Listed but not actively used in current implementation
- **matplotlib 3.9.2**: Listed but no visualization code present yet

### Testing Documents
Place test documents in `docs/` directory. Current test file: [docs/tokenizing_test.txt](../docs/tokenizing_test.txt)

## Conventions for New Code

- Use Indonesian for user-facing strings and print statements
- Follow existing display pattern: compute → analyze → print results → identify problems
- For text processing functions, return processed data (don't print directly)
- For display functions (`tampilkan_*`), print to console and return None
- Maintain dictionary-based frequency counting (avoid external frequency classes)
- When adding new stopwords, update the set in `get_stopwords_list()`
