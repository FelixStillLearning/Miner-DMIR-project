def tokenizing(text):
    return text.split() if text else []

def Hitung_frekuensi(tokens):
    freq = {}
    for token in tokens:
        freq[token] = freq.get(token, 0) + 1
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))

def tampilkan_frekuensi_kata(freq_dist):
    for token, count in freq_dist.items():
        print(f"  {token}: {count}")