import docx
import PyPDF2
import nltk # Library nltk
import string # Library string
import re # Library regex
import pandas as pd
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

def generate_tabel(freq_dist):
    for token, frequency in freq_dist.most_common(20):
        print(f"{token:<20} {frequency:>10}")
        
    return freq_dist

def generate_histogram(freq_dist, title="Histogram Frekuensi Token"):

    top_tokens = freq_dist.most_common(20)
    tokens = [token for token, freq in top_tokens]
    frequencies = [freq for token, freq in top_tokens]

    plt.figure(figsize=(12, 6))
    plt.bar(tokens, frequencies, color='steelblue')
    plt.xlabel('Token')
    plt.ylabel('Frekuensi')
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
   

if __name__ == "__main__":    
    nltk.download('punkt')

    # Path File
    file_path_txt = 'docs/tokenizing_test.txt'
    file_path_docx = 'docs/tokenizing_test.docx'
    file_path_pdf = 'docs/tokenizing_test.pdf'

    # Baca file
    text_txt = read_txt(file_path_txt)
    text_docx = read_docx(file_path_docx)
    text_pdf = read_pdf(file_path_pdf)

    # Bersihkan teks
    clean_txt = clean_text(text_txt)
    clean_docx = clean_text(text_docx)
    clean_pdf = clean_text(text_pdf)

    # Tokenisasi
    tokens_txt = tokenizing(clean_txt)
    tokens_docx = tokenizing(clean_docx)
    tokens_pdf = tokenizing(clean_pdf)

    # Hitung frekuensi
    freq_dist_txt = Hitung_frekuensi(tokens_txt)
    freq_dist_docx = Hitung_frekuensi(tokens_docx)
    freq_dist_pdf = Hitung_frekuensi(tokens_pdf)

    # Tampilkan tabel frekuensi
    print("Frekuensi Token dari TXT:")
    generate_tabel(freq_dist_txt)
    print("\nFrekuensi Token dari DOCX:")
    generate_tabel(freq_dist_docx)
    print("\nFrekuensi Token dari PDF:")
    generate_tabel(freq_dist_pdf)

    #Tampilkan Grafik Histogram
    print("\n Histogram Frekuensi Token \n")
    generate_histogram(freq_dist_txt, "Histogram - TXT")
    generate_histogram(freq_dist_docx, "Histogram - DOCX")
    generate_histogram(freq_dist_pdf, "Histogram - PDF")