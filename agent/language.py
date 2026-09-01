"""EN/TL detection via Tagalog marker words - deterministic, no dependencies.

Two-language problem: langdetect-style libs are overkill and nondeterministic on
short questions. Two or more Tagalog function words = Tagalog.
"""
import re

TL_MARKERS = {
    "ang", "ng", "mga", "sa", "ay", "ba", "ito", "iyon", "ano", "alin", "aling",
    "saan", "ilan", "ilang", "sino", "paano", "bakit", "kailan", "magkano",
    "pinaka", "pinakamataas", "pinakamaraming", "pinakamarami", "may", "wala",
    "at", "para", "kung", "naman", "lang", "po", "ninyo", "natin", "namin",
    "barangay", "lungsod", "bayan", "baha", "pagbaha", "ulan", "sitwasyon",
    "apektado", "apektadong", "residente", "paaralan", "tao", "taong",
}
# "barangay"/"baha" alone shouldn't flip English questions; require 2+ hits and
# don't count words that are also common English ("may" is the only overlap risk;
# accepted - it needs a second marker anyway).


def detect(text: str) -> str:
    words = re.findall(r"[a-zA-ZÀ-ÿ'-]+", text.lower())
    hits = sum(1 for w in words if w in TL_MARKERS)
    return "tl" if hits >= 2 else "en"
