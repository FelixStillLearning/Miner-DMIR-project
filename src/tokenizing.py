def tokenizing(text):
    tokens = text.split()

def Hitung_frekuensi(tokens):
    frekuensi_token = {}
    for token in tokens :
        frekuensi_token[token] = frekuensi_token.get(token, 0) + 1
    return dict(sorted(frekuensi_token.items(),key=lambda x: x[1], reverse=True))

def tampilkan_frekuensi_kata(freq_dist, indent="                                                   "):
    for token, frequency in sorted(freq_dist.items()):
        print(f"{indent}{token} = {frequency}")