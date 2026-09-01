"""Fuzzy barangay-name resolution for 'did you mean...?' suggestions."""
from functools import lru_cache

from rapidfuzz import fuzz, process

from .db import get_connection


@lru_cache(maxsize=1)
def _catalog() -> list[dict]:
    rows = get_connection().execute(
        "SELECT barangay, city, pcode FROM v_exposure"
    ).fetchall()
    return [{"barangay": b, "city": c, "pcode": p, "label": f"{b} {c}"} for b, c, p in rows]


def find_barangay(name: str, limit: int = 3) -> list[dict]:
    cat = _catalog()
    # Score against "Name City" labels so "Rosario Pasig" disambiguates duplicates,
    # but let a bare exact name still hit 100 via the name-only scorer.
    scored = []
    for entry in cat:
        s = max(
            fuzz.WRatio(name, entry["barangay"]),
            fuzz.WRatio(name, entry["label"]),
        )
        scored.append((s, entry))
    scored.sort(key=lambda t: (-t[0], t[1]["barangay"], t[1]["city"]))
    return [
        {"barangay": e["barangay"], "city": e["city"], "pcode": e["pcode"],
         "match_score": int(s)}
        for s, e in scored[:limit]
    ]
