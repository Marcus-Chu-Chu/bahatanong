"""Numeric grounding validator, ported from BahaMap pipeline/grounding.py.

BahaMap validated brief numbers against a payload dict; BahaTanong validates
answer numbers against the raw tool-result strings from this turn (SQL results,
brief texts). Same extraction semantics, same +/-0.5 tolerance, same lessons:
numbers inside strings (e.g. the name "Barangay 176") legitimize themselves.
"""
import re

RP_LABELS = {5.0, 25.0, 100.0}


def extract_numbers(text: str) -> list[float]:
    out = []
    for tok in re.findall(r"\d+(?:,\d+)*(?:\.\d+)?", text):
        val = float(tok.replace(",", ""))
        if val < 10 or val in RP_LABELS:
            continue
        if 1900 <= val <= 2100 and val == int(val) and "." not in tok and "," not in tok:
            continue  # year
        out.append(val)
    return out


def validate_answer(text: str, evidence: list[str]) -> list[float]:
    allowed: set[float] = set()
    for ev in evidence:
        allowed.update(extract_numbers(ev))
    return [n for n in extract_numbers(text)
            if not any(abs(n - a) <= 0.5 for a in allowed)]
