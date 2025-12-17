import re

# Implementasi dasar Algoritma Tala (rule-based, tanpa kamus)
# Urutan langkah: partikel -> sandang/kepunyaan -> awalan1 -> (cabang) akhiran & awalan2

PARTIKEL = ("lah", "kah", "pun")
SANDANG = ("nya", "ku", "mu")
PREFIX1 = ("ber", "bel", "be", "per", "pel", "pe")
PREFIX2 = ("di", "ter", "ke")
SUFFIX = ("kan", "an", "i")

# Pola khusus konsonan pengganti sesuai aturan Tala
# menyX -> sX, menya/menyi/menyu/menye/menyo -> s..., memX -> pX, pen(y) -> s..., pemX -> pX
SPECIAL_PREFIX = (
    (re.compile(r"^(menya|menyi|menyu|menye|menyo|meny)(.*)$"), lambda m: "s" + m.group(2)),
    (re.compile(r"^(mema|memi|memu|meme|memo|mem)(.*)$"), lambda m: "p" + m.group(2)),
    (re.compile(r"^(penya|penyi|penyu|penye|penyo|peny)(.*)$"), lambda m: "s" + m.group(2)),
    (re.compile(r"^(pema|pemi|pemu|peme|pemo|pem)(.*)$"), lambda m: "p" + m.group(2)),
)

MIN_ROOT_LEN = 2


def _remove_suffix(word):
    for suf in SUFFIX:
        if word.endswith(suf) and len(word) - len(suf) >= MIN_ROOT_LEN:
            return word[: -len(suf)], True
    return word, False


def _remove_particle(word):
    for p in PARTIKEL:
        if word.endswith(p) and len(word) - len(p) >= MIN_ROOT_LEN:
            return word[: -len(p)], True
    return word, False


def _remove_sandang(word):
    for s in SANDANG:
        if word.endswith(s) and len(word) - len(s) >= MIN_ROOT_LEN:
            return word[: -len(s)], True
    return word, False


def _remove_prefix1(word):
    for pre in PREFIX1:
        if word.startswith(pre) and len(word) - len(pre) >= MIN_ROOT_LEN:
            return word[len(pre) :], True
    return word, False


def _apply_special_prefix(word):
    for pattern, repl in SPECIAL_PREFIX:
        m = pattern.match(word)
        if m:
            new = repl(m)
            if len(new) >= MIN_ROOT_LEN:
                return new, True
    return word, False


def _remove_prefix2(word):
    # Special replacements first
    new, changed = _apply_special_prefix(word)
    if changed:
        return new, True
    # Generic di/ter/ke
    for pre in PREFIX2:
        if word.startswith(pre) and len(word) - len(pre) >= MIN_ROOT_LEN:
            return word[len(pre) :], True
    return word, False


def stem_tala_word(word: str) -> str:
    if not word or len(word) < MIN_ROOT_LEN:
        return word

    original = word
    changed_any = False

    # 1) Hilangkan partikel
    word, changed = _remove_particle(word)
    changed_any = changed_any or changed

    # 2) Hilangkan sandang/kepunyaan
    word, changed = _remove_sandang(word)
    changed_any = changed_any or changed

    # 3) Hilangkan awalan 1
    word, changed = _remove_prefix1(word)
    changed_any = changed_any or changed

    # 4) Cabang aturan
    # Cabang A: jika penghilangan akhiran memungkinkan, lakukan akhiran lalu awalan2
    temp_word, suf_changed = _remove_suffix(word)
    if suf_changed:
        word = temp_word
        word, _ = _remove_prefix2(word)
    else:
        # Cabang B: awalan2 dulu, lalu akhiran
        word, _ = _remove_prefix2(word)
        word, _ = _remove_suffix(word)

    # Final: jika hasil terlalu pendek, kembalikan asal
    if len(word) < MIN_ROOT_LEN:
        return original
    return word


def Stem_Tala_tokenizing(tokens):
    return [stem_tala_word(tok) for tok in tokens if tok]


def hitung_frekuensi_stem_tala(stemmed_tokens):
    freq = {}
    for token in stemmed_tokens:
        freq[token] = freq.get(token, 0) + 1
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))


def tampilkan_hasil_stem_tala(freq_stem):
    for token, count in freq_stem.items():
        print(f"{token}: {count}")


def identifikasi_kata_gagal_stem_tala(tokens_asli, tokens_stem):
    gagal = [original for original, stem in zip(tokens_asli, tokens_stem) if original == stem and len(original) > 3]
    return list(set(gagal))


def tampilkan_kata_gagal_stem_tala(kata_gagal):
    if not kata_gagal:
        print("Tidak ada kata yang gagal di-stem (Tala)")
        return
    print(f"\nTotal kata yang tidak/gagal di stem (Tala): {len(kata_gagal)} kata")
    for kata in sorted(kata_gagal):
        print(kata)
