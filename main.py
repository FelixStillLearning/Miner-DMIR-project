from src.utils import baca_txt, baca_docx, baca_pdf, bersihkan_text
from src.tokenizing import tokenizing, Hitung_frekuensi, tampilkan_frekuensi_kata
from src.stemming import Stem_tokenizing, tampilkan_hasil_stem
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
        if exs == '.txt':
            text = baca_txt(filepath)
        elif exs == '.docx':
            text = baca_docx(filepath)
        elif exs == '.pdf':
            text = baca_pdf(filepath) 

        text_bersih = bersihkan_text(text)  

        tokens = tokenizing(text_bersih)  

        frek_token = Hitung_frekuensi(tokens)
        print("\nFrekuensi Token:")
        tampilkan_frekuensi_kata(frek_token)

        tokens_stem = Stem_tokenizing(tokens) 
        print("\nHasil Stemming:")
        tampilkan_hasil_stem(tokens_stem)
        
    except Exception as e:
        print(f"Error: {e}")