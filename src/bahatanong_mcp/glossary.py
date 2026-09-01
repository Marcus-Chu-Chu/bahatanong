"""Methodology definitions the agent can cite instead of guessing."""
import json
from functools import lru_cache

from .paths import DATA_DIR


@lru_cache(maxsize=1)
def _terms() -> dict:
    return json.loads((DATA_DIR / "glossary.json").read_text(encoding="utf-8"))


def _normalize(s: str) -> str:
    return s.strip().lower().replace(" ", "_").rstrip("s")


def lookup(term: str | None) -> dict:
    terms = _terms()
    if term:
        want = _normalize(term)
        for key in terms:
            if _normalize(key) == want or want in _normalize(key):
                return {"term": key, "definition": terms[key]}
    return {"terms": sorted(terms)}
