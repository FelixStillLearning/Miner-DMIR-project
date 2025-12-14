from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from collections import Counter

factory = StemmerFactory()  
stemmer = factory.create_stemmer()

def Stem_tokenizing(tokens):
    return [stemmer.stem(word) for word in tokens if word]

def hitung_frekuensi_stem(stemmed_tokens):
    freq = {}
    for token in stemmed_tokens:
        freq[token] = freq.get(token, 0) + 1
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))

def tampilkan_hasil_stem(freq_stem):
    for token, count in freq_stem.items():
        print(f"{token}: {count}")

def identifikasi_kata_gagal_stem(tokens_asli, tokens_stem):
    gagal = [original for original, stem in zip(tokens_asli, tokens_stem) 
             if original == stem and len(original) > 3]
    return list(set(gagal))

def tampilkan_kata_gagal_stem(kata_gagal):
    if not kata_gagal:
        print(f"Tidak ada kata yang gagal di-stem")
        return
    
    print(f"\nTotal kata yang tidak/gagal di stem: {len(kata_gagal)} kata")
    for kata in sorted(kata_gagal):
        print(f"{kata}")