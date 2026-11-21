# -*- coding: utf-8 -*-
"""
hindi_normalizer.py - Pre-TTS Hindi text normalizer (reusable, mandatory before any OmniVoice call).

Converts English/Devanagari digits, years, decimals, percentages and ALL-CAPS acronyms
into pure Hindi words so the TTS never has to guess how to read "1947" or "LAPD".

    normalize_hindi("यह कहानी 1947 के लॉस एंजिल्स की है।")
    -> "यह कहानी उन्नीस सौ सैंतालीस के लॉस एंजिल्स की है।"
"""
import re

UNITS = [
    "शून्य", "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ",
    "दस", "ग्यारह", "बारह", "तेरह", "चौदह", "पंद्रह", "सोलह", "सत्रह", "अठारह", "उन्नीस",
    "बीस", "इक्कीस", "बाईस", "तेईस", "चौबीस", "पच्चीस", "छब्बीस", "सत्ताईस", "अट्ठाईस", "उनतीस",
    "तीस", "इकतीस", "बत्तीस", "तैंतीस", "चौंतीस", "पैंतीस", "छत्तीस", "सैंतीस", "अड़तीस", "उनतालीस",
    "चालीस", "इकतालीस", "बयालीस", "तैंतालीस", "चौवालीस", "पैंतालीस", "छियालीस", "सैंतालीस", "अड़तालीस", "उनचास",
    "पचास", "इक्यावन", "बावन", "तिरपन", "चौवन", "पचपन", "छप्पन", "सत्तावन", "अट्ठावन", "उनसठ",
    "साठ", "इकसठ", "बासठ", "तिरसठ", "चौंसठ", "पैंसठ", "छियासठ", "सड़सठ", "अड़सठ", "उनहत्तर",
    "सत्तर", "इकहत्तर", "बहत्तर", "तिहत्तर", "चौहत्तर", "पचहत्तर", "छिहत्तर", "सतहत्तर", "अठहत्तर", "उन्यासी",
    "अस्सी", "इक्यासी", "बयासी", "तिरासी", "चौरासी", "पचासी", "छियासी", "सत्तासी", "अट्ठासी", "नवासी",
    "नब्बे", "इक्यानवे", "बानवे", "तिरानवे", "चौरानवे", "पंचानवे", "छियानवे", "सत्तानवे", "अट्ठानवे", "निन्यानवे",
]
assert len(UNITS) == 100

LETTERS = {
    "A": "ए", "B": "बी", "C": "सी", "D": "डी", "E": "ई", "F": "एफ", "G": "जी", "H": "एच",
    "I": "आई", "J": "जे", "K": "के", "L": "एल", "M": "एम", "N": "एन", "O": "ओ", "P": "पी",
    "Q": "क्यू", "R": "आर", "S": "एस", "T": "टी", "U": "यू", "V": "वी", "W": "डब्ल्यू",
    "X": "एक्स", "Y": "वाई", "Z": "ज़ेड",
}

_DEV_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def number_to_hindi(n: int) -> str:
    """0 .. 99,99,99,999 -> Hindi words (Indian numbering: हज़ार / लाख / करोड़)."""
    if n < 0:
        return "ऋण " + number_to_hindi(-n)
    if n < 100:
        return UNITS[n]
    if n < 1000:
        h, r = divmod(n, 100)
        return UNITS[h] + " सौ" + (" " + number_to_hindi(r) if r else "")
    if n < 100000:
        t, r = divmod(n, 1000)
        return number_to_hindi(t) + " हज़ार" + (" " + number_to_hindi(r) if r else "")
    if n < 10000000:
        l, r = divmod(n, 100000)
        return number_to_hindi(l) + " लाख" + (" " + number_to_hindi(r) if r else "")
    c, r = divmod(n, 10000000)
    return number_to_hindi(c) + " करोड़" + (" " + number_to_hindi(r) if r else "")


def year_to_hindi(y: int) -> str:
    """1100-1999 -> 'उन्नीस सौ सैंतालीस' (spoken-year style); 2000+ -> normal number style."""
    if 1100 <= y <= 1999:
        hi, lo = divmod(y, 100)
        return UNITS[hi] + " सौ" + (" " + UNITS[lo] if lo else "")
    return number_to_hindi(y)


def _num_token(m):
    raw = m.group(0)
    pct = raw.endswith("%")
    s = raw.rstrip("%").replace(",", "")
    if "." in s:
        a, b = s.split(".", 1)
        out = number_to_hindi(int(a or 0)) + " दशमलव " + " ".join(UNITS[int(d)] for d in b)
    else:
        n = int(s)
        out = year_to_hindi(n) if (len(s) == 4 and 1100 <= n <= 1999) else number_to_hindi(n)
    return out + (" प्रतिशत" if pct else "")


_NUM_RE = re.compile(r"(?<![A-Za-z0-9])\d[\d,]*(?:\.\d+)?%?")
_ACR_RE = re.compile(r"(?<![A-Za-z])[A-Z]{2,6}(?![A-Za-z])")


def _acr_token(m):
    return " ".join(LETTERS[c] for c in m.group(0))


def normalize_hindi(text: str) -> str:
    """Digits/years/acronyms -> pure Hindi words. Whitespace normalised. Idempotent."""
    t = text.translate(_DEV_DIGITS)
    t = _NUM_RE.sub(_num_token, t)
    t = _ACR_RE.sub(_acr_token, t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def word_count(text: str) -> int:
    return len([w for w in re.split(r"\s+", text.strip()) if w])


def leftover_latin(text: str):
    """Latin words that the TTS may mispronounce (report to the script author)."""
    return re.findall(r"[A-Za-z][A-Za-z\-']*", text)


if __name__ == "__main__":
    for sample in ["यह कहानी 1947 के लॉस एंजिल्स की है।", "LAPD ने 3 लोगों को 12.5% बढ़त पर 2016 में पकड़ा", "कीमत 1,50,000 रुपये"]:
        print(sample, "->", normalize_hindi(sample))
