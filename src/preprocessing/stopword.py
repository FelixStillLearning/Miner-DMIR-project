def get_stopwords_list():
    # Daftar stopword manual bahasa Indonesia
    return {
        "yang", "untuk", "pada", "ke", "para", "namun", "menurut", "antara", "dia", "dua",
        "ia", "seperti", "jika", "jika", "sehingga", "kembali", "dan", "tidak", "ini", "karena",
        "kepada", "oleh", "saat", "harus", "sementara", "setelah", "belum", "kami", "sekitar",
        "bagi", "serta", "di", "dari", "telah", "sebagai", "masih", "hal", "ketika", "adalah",
        "itu", "dalam", "bisa", "bahwa", "atau", "hanya", "kita", "dengan", "akan", "juga",
        "ada", "mereka", "sudah", "saya", "terhadap", "secara", "agar", "lain", "anda",
        "begitu", "mengapa", "kenapa", "yaitu", "yakni", "daripada", "itulah", "lagi", "maka",
        "tentang", "demi", "dimana", "kemana", "kapan", "sambil", "sebelum", "sesudah", "supaya",
        "guna", "kah", "pun", "sampai", "sedangkan", "selagi", "sementara", "tetapi", "apakah",
        "kecuali", "sebab", "selain", "seolah", "seraya", "seterusnya", "tanpa", "agak", "boleh",
        "dapat", "dsb", "dst", "dll", "dahulu", "dulunya", "anu", "demikian", "tapi", "ingin",
        "juga", "nggak", "mari", "nanti", "melainkan", "oh", "ok", "seharusnya", "sebetulnya",
        "setiap", "setidaknya", "sesuatu", "pasti", "saja", "toh", "ya", "walau", "tolong",
        "tentu", "amat", "apalagi", "bagaimanapun"
    }

def remove_stopwords(tokens):
    stopwords = get_stopwords_list()
    # Filter token yang ada di dalam set stopwords
    filtered_tokens = [word for word in tokens if word.lower() not in stopwords]
    return filtered_tokens

# def tampilkan_hasil_stopword(tokens_asli, tokens_bersih):
#     terhapus = len(tokens_asli) - len(tokens_bersih)
#     print(f"\nJumlah kata sebelum stopword removal: {len(tokens_asli)}")
#     print(f"Jumlah kata setelah stopword removal: {len(tokens_bersih)}")
#     print(f"Jumlah stopword yang terhapus: {terhapus}")
    
#     # Tampilkan preview hasil filter (10 kata pertama)
#     if tokens_bersih:
#         preview = ' '.join(tokens_bersih[:10])
#         if len(tokens_bersih) > 10:
#             preview += "..."
#         print(f"\nPreview hasil filter: {preview}")

# def identifikasi_stopword_terhapus(tokens_asli, tokens_bersih):
#     # Mengidentifikasi kata-kata yang dihapus (stopwords)
#     set_asli = set(tokens_asli)
#     set_bersih = set(tokens_bersih)
#     stopwords_terhapus = list(set_asli - set_bersih)
#     return sorted(stopwords_terhapus)

# def tampilkan_stopword_terhapus(stopwords_terhapus):
#     if not stopwords_terhapus:
#         print("\nTidak ada stopword yang terhapus")
#         return
    
#     print(f"\nDaftar stopword yang terhapus ({len(stopwords_terhapus)} kata):")
#     for kata in stopwords_terhapus:
#         print(f"  - {kata}")