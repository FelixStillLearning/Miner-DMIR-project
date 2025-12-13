from sastrawi.stem import stemmerFActory
from collections import Counter

factory = stemmerFActory()
stemmer = factory.create_stemmer()

def Stem_tokenizing(tokens):
    kata_stemmed = [stemmer.stem(word) for word in tokens]
    return [word for word in kata_stemmed if word]

def hitung_frekuensi_stem(stemmed_tokens):
    return Counter(stemmed_tokens)

def tampilkan_hasil_stem(frekuensi_stem, indent=""):
    for i,j in sorted(frekuensi_stem.items()):
        print(f"{indent}{Stem_tokenizing}={frekuensi_stem}")
