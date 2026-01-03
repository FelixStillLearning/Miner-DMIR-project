import re

PARTIKEL = ("lah", "kah", "pun")
SANDANG = ("nya", "ku", "mu")
SUFFIX = ("kan", "an", "i")

SPECIAL_PREFIX = (
    (re.compile(r"^meny([aiueo].*)$"), lambda m: "s" + m.group(1)),
    (re.compile(r"^mem([aiueo].*)$"), lambda m: "p" + m.group(1)),
    (re.compile(r"^mem([^aiueo].*)$"), lambda m: m.group(1)),
    (re.compile(r"^peny([aiueo].*)$"), lambda m: "s" + m.group(1)),
    (re.compile(r"^pem([aiueo].*)$"), lambda m: "p" + m.group(1)),
    (re.compile(r"^pem([^aiueo].*)$"), lambda m: m.group(1)),
)

MIN_ROOT_LEN = 2
MIN_SYLLABLES = 2 
VOWELS = set("aiueo")


def _count_syllables(word: str) -> int:
    """Hitung jumlah suku kata berdasarkan jumlah vokal."""
    return sum(1 for c in word if c in VOWELS)


def _is_valid_root(word: str) -> bool:
    """Cek apakah word valid sebagai root (panjang + suku kata cukup)."""
    return len(word) >= MIN_ROOT_LEN and _count_syllables(word) >= MIN_SYLLABLES


def _apply_special_prefix(word):
    """Substitusi khusus sesuai aturan Tala untuk meny/mem/peny/pem + vokal."""
    for pattern, repl in SPECIAL_PREFIX:
        m = pattern.match(word)
        if m:
            new = repl(m)
            if len(new) >= MIN_ROOT_LEN:
                return new, True
    return word, False


def _remove_suffix(word, removed_prefixes=None):
    if removed_prefixes is None:
        removed_prefixes = []
    
    for suf in SUFFIX:
        if word.endswith(suf):
            candidate = word[: -len(suf)]
            if not _is_valid_root(candidate):
                continue
            
            if suf == "kan" and any(p in removed_prefixes for p in ["ke", "peng"]):
                continue
            if suf == "an" and any(p in removed_prefixes for p in ["di", "meng", "ter"]):
                continue
            if suf == "i" and any(p in removed_prefixes for p in ["ber", "ke", "peng"]):
                continue
            
            return candidate, True
    return word, False


def _remove_particle(word):
    for p in PARTIKEL:
        if word.endswith(p):
            candidate = word[: -len(p)]
            if len(candidate) >= MIN_ROOT_LEN:
                return candidate, True
    return word, False


def _remove_sandang(word):
    for s in SANDANG:
        if word.endswith(s):
            candidate = word[: -len(s)]
            if len(candidate) >= MIN_ROOT_LEN:
                return candidate, True
    return word, False


def _remove_prefix1(word):
    new, changed = _apply_special_prefix(word)
    if changed:
        if word.startswith("meny") or word.startswith("mem"):
            return new, True, "meng"
        elif word.startswith("peny") or word.startswith("pem"):
            return new, True, "peng"

    if word.startswith("meng") and len(word) - 4 >= MIN_ROOT_LEN:
        return word[4:], True, "meng"
    if word.startswith("men") and len(word) - 3 >= MIN_ROOT_LEN:
        return word[3:], True, "meng"
    if word.startswith("me") and len(word) - 2 >= MIN_ROOT_LEN:
        return word[2:], True, "meng"

    if word.startswith("peng") and len(word) - 4 >= MIN_ROOT_LEN:
        return word[4:], True, "peng"
    if word.startswith("pen") and len(word) - 3 >= MIN_ROOT_LEN:
        return word[3:], True, "peng"

    if word.startswith("di") and len(word) - 2 >= MIN_ROOT_LEN:
        return word[2:], True, "di"
    if word.startswith("ter") and len(word) - 3 >= MIN_ROOT_LEN:
        return word[3:], True, "ter"
    if word.startswith("ke") and len(word) - 2 >= MIN_ROOT_LEN:
        return word[2:], True, "ke"

    return word, False, None


def _remove_prefix2(word):
    if word.startswith("belajar"):
        return word[3:], True, "ber"
    if word.startswith("pelajar"):
        return word[3:], True, "per"
    
    if word.startswith("be"):
        rest = word[2:]
        if len(rest) >= MIN_ROOT_LEN and len(rest) > 2:
            if rest[0] not in VOWELS and rest[1:3] == "er":
                return rest, True, "ber"
    
    if word.startswith("ber") and len(word) - 3 >= MIN_ROOT_LEN:
        return word[3:], True, "ber"
    if word.startswith("per") and len(word) - 3 >= MIN_ROOT_LEN:
        return word[3:], True, "per"
    if word.startswith("pel") and len(word) - 3 >= MIN_ROOT_LEN:
        return word[3:], True, "per"
    if word.startswith("pe") and len(word) - 2 >= MIN_ROOT_LEN:
        return word[2:], True, "per"
    if word.startswith("bel") and len(word) - 3 >= MIN_ROOT_LEN:
        return word[3:], True, "ber"
    
    return word, False, None


def stem_tala_word(word: str) -> str:
    if not word or len(word) < MIN_ROOT_LEN:
        return word

    original = word
    removed_prefixes = []

    word, changed = _remove_particle(word)
    word, changed = _remove_sandang(word)
    
    word, changed, prefix1 = _remove_prefix1(word)
    if prefix1:
        removed_prefixes.append(prefix1)

    temp_word, suf_changed = _remove_suffix(word, removed_prefixes)
    if suf_changed:
        word = temp_word
        word, changed, prefix2 = _remove_prefix2(word)
        if prefix2:
            removed_prefixes.append(prefix2)
    else:
        word, changed, prefix2 = _remove_prefix2(word)
        if prefix2:
            removed_prefixes.append(prefix2)
        word, _ = _remove_suffix(word, removed_prefixes)

    if not _is_valid_root(word):
        return original
    
    return word


def Stem_Tala_tokenizing(tokens):
    return [stem_tala_word(tok) for tok in tokens if tok]


# def hitung_frekuensi_stem_tala(stemmed_tokens):
#     freq = {}
#     for token in stemmed_tokens:
#         freq[token] = freq.get(token, 0) + 1
#     return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))


# def tampilkan_hasil_stem_tala(freq_stem):
#     for token, count in freq_stem.items():
#         print(f"{token}: {count}")


# def identifikasi_kata_gagal_stem_tala(tokens_asli, tokens_stem):
#     gagal = [original for original, stem in zip(tokens_asli, tokens_stem) if original == stem and len(original) > 3]
#     return list(set(gagal))


# def tampilkan_kata_gagal_stem_tala(kata_gagal):
#     if not kata_gagal:
#         print("Tidak ada kata yang gagal di-stem (Tala)")
#         return
#     print(f"\nTotal kata yang tidak/gagal di stem (Tala): {len(kata_gagal)} kata")
#     for kata in sorted(kata_gagal):
#         print(kata)
