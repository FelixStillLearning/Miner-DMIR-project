import docx
import PyPDF2
import nltk
import string
import re
import os
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk import FreqDist 

# Read txt
def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Read docx
def read_docx(file_path):
    doc = docx.Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return '\n'.join(text)

# Read pdf
def read_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

#Cleaning Text
def clean_text(text):
    if not isinstance(text, str):
        text = str(text)

    # Lowercase
    text = text.lower()

    # Hilangkan tanda baca ASCII
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Hilangkan tanda baca Unicode tambahan
    text = re.sub(r'[“”‘’…—–-]', '', text)

    # Hilangkan angka
    text = re.sub(r'\d+', '', text)

    # Hilangkan spasi berlebihan
    text = ' '.join(text.split())
    return text

def tokenizing(text):
    tokens = nltk.tokenize.word_tokenize(text)
    return tokens

def Hitung_frekuensi(tokens):
    frekuensi_tokens = nltk.FreqDist(tokens)
    return frekuensi_tokens

def tampilkan_frekuensi_kata(freq_dist, indent="                                                   "):
    for token, frequency in sorted(freq_dist.items()):
        print(f"{indent}{token} = {frequency}")

def generate_histogram(freq_dist, title="Histogram Frekuensi Token", top_n=20):
    top_tokens = freq_dist.most_common(top_n)
    tokens = [token for token, freq in top_tokens]
    frequencies = [freq for token, freq in top_tokens]

    plt.figure(figsize=(14, 7))
    plt.bar(tokens, frequencies, color='steelblue', edgecolor='navy', alpha=0.7)
    plt.xlabel('Token', fontsize=12, fontweight='bold')
    plt.ylabel('Frekuensi', fontsize=12, fontweight='bold')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
   

if __name__ == "__main__":    
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    print("PROGRAM PEMBACAAN DOKUMEN DAN TOKENIZING")
    
    # Minta input direktori dari user
    directory_input = input("Masukkan path direktori (tekan Enter untuk default): ").strip()
    
    # Jika user tidak memasukkan apa-apa, gunakan direktori default
    if not directory_input:
        directory_input = "docs"
        print(f"\nMenggunakan direktori default: {directory_input}")
    
    # Validasi direktori
    if not os.path.exists(directory_input):
        print(f"\nError: Direktori '{directory_input}' tidak ditemukan!")
        exit()
    
    if not os.path.isdir(directory_input):
        print(f"\nError: '{directory_input}' bukan direktori!")
        exit()
    
    # Ekstensi file yang didukung
    supported_extensions = {'.txt', '.docx', '.pdf'}
    
    # Cari semua file yang didukung
    files = []
    for file in os.listdir(directory_input):
        file_path = os.path.join(directory_input, file)
        if os.path.isfile(file_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in supported_extensions:
                files.append((file, file_path, ext))
    
    if not files:
        print(f"\nTidak ada file TXT, DOCX, atau PDF ditemukan di '{directory_input}'")
        exit()
    
    print(f"Nama path: {os.path.abspath(directory_input)}")
    
    # Proses setiap file
    all_freq_dists = []
    
    for idx, (filename, filepath, ext) in enumerate(files, 1):
        print(f"                  ({idx}). {filename}")
        
        try:
            # Baca file berdasarkan ekstensi
            if ext == '.txt':
                text = read_txt(filepath)
            elif ext == '.docx':
                text = read_docx(filepath)
            elif ext == '.pdf':
                text = read_pdf(filepath)
            
            # Cleaning dan tokenizing
            cleaned_text = clean_text(text)
            tokens = tokenizing(cleaned_text)
            freq_dist = Hitung_frekuensi(tokens)
            
            # Simpan untuk visualisasi nanti
            all_freq_dists.append((filename, freq_dist))
            
            # Tampilkan frekuensi kata
            print("                        Mengandung kata:")
            if len(freq_dist) > 0:
                tampilkan_frekuensi_kata(freq_dist)
            else:
                print("                                                   (tidak ada kata ditemukan)")
            
            print()
            
        except Exception as e:
            print(f"                        Error membaca file: {e}")
            print()
    
    # Tanya user apakah ingin melihat visualisasi
    print("VISUALISASI DATA")
    
    tampilkan_visualisasi = input("\nApakah Anda ingin melihat histogram? (y/n): ").lower()
    
    if tampilkan_visualisasi == 'y':
        for filename, freq_dist in all_freq_dists:
            if len(freq_dist) > 0:
                generate_histogram(freq_dist, f"Histogram Frekuensi Token - {filename}", top_n=20)
    
    print("PROGRAM SELESAI")