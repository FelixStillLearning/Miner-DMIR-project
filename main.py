from src.utils.utils import *
from src.preprocessing.tokenizing import *
from src.preprocessing.stopword import *
from src.preprocessing.tala_stemmer import *
from src.feature_extraction.tfidf import TFIDF
from src.indexing.inverted_index import InvertedIndex
from src.query.query_processor import QueryProcessor
from src.retrieval.retrieval_engine import RetrievalEngine
import os

directory = "data/raw"
ekstensi_file = {'.txt', '.docx', '.pdf'}

files = [
    (file, os.path.join(directory, file), os.path.splitext(file)[1].lower())
    for file in os.listdir(directory)
    if os.path.isfile(os.path.join(directory, file)) 
    and os.path.splitext(file)[1].lower() in ekstensi_file
]

processed_docs = []

print("=== Preprocessing Documents ===")
for idx, (filename, filepath, exs) in enumerate(files, 1):
    print(f"\n({idx}). Memproses: {filename}")
    
    try:
        #buat bac file
        if exs == '.txt':
            text = baca_txt(filepath)
        elif exs == '.docx':
            text = baca_docx(filepath)
        elif exs == '.pdf':
            text = baca_pdf(filepath) 

        #preprocesing
        text_bersih = bersihkan_text(text)  

        #tokenizing
        tokens = tokenizing(text_bersih)
        frek_token = Hitung_frekuensi(tokens)
        
        # print("\nFrekuensi Token:")
        # tampilkan_frekuensi_kata(frek_token)

        # Stopword removal sebelum stemming
        tokens_bersih = remove_stopwords(tokens)
        # print("\nHasil Stopword Removal:")
        # tampilkan_hasil_stopword(tokens, tokens_bersih)
        # stopwords_terhapus = identifikasi_stopword_terhapus(tokens, tokens_bersih)
        # tampilkan_stopword_terhapus(stopwords_terhapus)

        # Stemming menggunakan Algoritma Tala
        token_stem = Stem_Tala_tokenizing(tokens_bersih)
        
        # Print statistik singkat
        print(f"  Jumlah token asli: {len(tokens)}")
        print(f"  Setelah stopword: {len(tokens_bersih)}")
        print(f"  Setelah stemming: {len(token_stem)}")
        
        # Collect for VSM
        processed_docs.append({
            'id': idx,
            'tokens': token_stem,
            'metadata': {
                'filename': filename,
                'filepath': filepath
            }
        })

    except Exception as e:
        print(f"Error processing {filename}: {e}")

# === VSM Implementation ===
print("\n" + "="*50)
print("Vector Space Model (VSM) Indexing")
print("="*50)

# 1. Transform to TF-IDF
print("Building TF-IDF Model...")
tfidf_model = TFIDF()
corpus_tokens = [doc['tokens'] for doc in processed_docs]
tfidf_model.calculate_idf(corpus_tokens)

# 2. Build Inverted Index
print("Building Inverted Index...")
inverted_index = InvertedIndex()
inverted_index.build_index(processed_docs, tfidf_model)

# 3. Setup Retrieval Engine
query_processor = QueryProcessor(tfidf_model)
engine = RetrievalEngine(inverted_index, tfidf_model)

print(f"Index built successfully with {len(processed_docs)} documents.")

# 4. Search Loop
while True:
    print("\n" + "-"*30)
    query = input("Masukkan query pencarian (ketik 'exit' untuk keluar): ")
    if query.lower() in ('exit', 'quit'):
        break
        
    print(f"Query: '{query}'")
    
    # Process Query
    try:
        q_vector, q_tokens = query_processor.transform_query(query)
        print(f"Query terms: {q_tokens}")
        
        # Search
        results = engine.search(q_vector)
        
        # Display Results
        if not results:
            print("Tidak ada dokumen yang ditemukan.")
        else:
            print(f"\nDitemukan {len(results)} dokumen relevan:")
            for rank, res in enumerate(results, 1):
                doc_meta = res['metadata']
                score = res['score']
                print(f"{rank}. {doc_meta['filename']} (Score: {score:.4f})")
                
    except Exception as e:
        print(f"Error during search: {e}")

print("Terima kasih!")