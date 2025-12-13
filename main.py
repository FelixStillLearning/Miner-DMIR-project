from utils import baca_txt, baca_docx, baca_pdf, bersihkan_text
from tokenizing import tokeninizing, Hitung_frekuensi, tampilkan_frekuensi_kata
from stemming import Stem_tokenizing, tampilkan_hasil_stem, hitung_frekuensi_stem
import os

directory = "/docs"
ekstensi_file = ('.txt', 'docx', 'pdf')

files = [
    (file, os.path.join(directory, file), os.path.splitext(file)[1].lower())
    for file in os.listdir(directory)
    if os.path.isfile(os.path.join(directory, file)) 
    and os.path.splitext(file)[1].lower() in ekstensi_file
]

for idx, (filenamae, filepath, exs) in enumerate(files, 1):
    try:
        if exs == '.txt':
            text = baca_txt(filepath)
        elif exs == '.docx':
            text = baca_docx(filepath)
        elif exs == '.pdf' :
            text == baca_pdf(filepath)

        text_bersih = bersihkan_text()

        tokens = tokeninizing(text_bersih)

        frek_token = Hitung_frekuensi(tokens)

        frek_stem = Stem_tokenizing (frek_token)

        

