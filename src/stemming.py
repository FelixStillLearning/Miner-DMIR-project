from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from collections import Counter

factory = StemmerFactory()  
stemmer = factory.create_stemmer()

def Stem_tokenizing(tokens):
    kata_stemmed = [stemmer.stem(word) for word in tokens]
    return [word for word in kata_stemmed if word]

def tampilkan_hasil_stem(tokens_stem, indent="   "):
    for token in tokens_stem:
        print(f"{indent}{token}")