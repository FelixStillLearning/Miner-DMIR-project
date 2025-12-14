from src.utils import *
from src.tokenizing import *
from src.stemming import *
import os

directory = "docs"
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

        #stemming pake sastarawi
        token_stem = Stem_tokenizing(tokens)
        frek_stem = hitung_frekuensi_stem(token_stem)

        print("\nHasil Stemming:")
        print(f"\nJumlah kata yang di-stem: {sum(a != b for a, b in zip(tokens, token_stem))}")
        for asal, stem in zip(tokens, token_stem):
            if asal != stem:
                print(f"'{asal}' -> '{stem}'")
        tampilkan_hasil_stem(frek_stem)
        kata_gagal = identifikasi_kata_gagal_stem(tokens, token_stem)
        tampilkan_kata_gagal_stem(kata_gagal)

        
    except Exception as e:
        print(f"Error: {e}")