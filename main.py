from src.utils.utils import *
from src.preprocessing.tokenizing import *
from src.preprocessing.stopword import *
from src.preprocessing.tala_stemmer import *
import os

directory = "data/raw"
ekstensi_file = {'.txt', '.docx', '.pdf'}

files = [
    (file, os.path.join(directory, file), os.path.splitext(file)[1].lower())
    for file in os.listdir(directory)
    if os.path.isfile(os.path.join(directory, file)) 
    and os.path.splitext(file)[1].lower() in ekstensi_file
]

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
        
        print("\nFrekuensi Token:")
        tampilkan_frekuensi_kata(frek_token)

        # Stopword removal sebelum stemming
        tokens_bersih = remove_stopwords(tokens)
        print("\nHasil Stopword Removal:")
        tampilkan_hasil_stopword(tokens, tokens_bersih)
        stopwords_terhapus = identifikasi_stopword_terhapus(tokens, tokens_bersih)
        tampilkan_stopword_terhapus(stopwords_terhapus)

        # Stemming menggunakan Algoritma Tala
        token_stem = Stem_Tala_tokenizing(tokens_bersih)
        frek_stem = hitung_frekuensi_stem_tala(token_stem)

        print("\nHasil Stemming:")
        print(f"\nJumlah kata yang di-stem: {sum(a != b for a, b in zip(tokens, token_stem))}")
        for asal, stem in zip(tokens_bersih, token_stem):
            if asal != stem:
                print(f"'{asal}' -> '{stem}'")
        tampilkan_hasil_stem_tala(frek_stem)
        kata_gagal = identifikasi_kata_gagal_stem_tala(tokens_bersih, token_stem)
        tampilkan_kata_gagal_stem_tala(kata_gagal)

        
    except Exception as e:
        print(f"Error: {e}")