def tokenizing(text):
    if not text:
        return []
    tokens = text.split()
    return tokens

def Hitung_frekuensi(tokens):
    if not tokens:
        return {}
    frekuensi_token = {}
    for token in tokens :
        frekuensi_token[token] = frekuensi_token.get(token, 0) + 1
    return dict(sorted(frekuensi_token.items(),key=lambda x: x[1], reverse=True))

def tampilkan_frekuensi_kata(freq_dist):
    if not freq_dist:
        print(f"(tidak ada data)")
    for token, frequency in sorted(freq_dist.items()):
        print(f"{token} = {frequency}")