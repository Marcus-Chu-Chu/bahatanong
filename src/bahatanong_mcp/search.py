"""Vector search over the 1,710x2 bilingual BahaMap briefs (ChromaDB, committed index).

The sentence-transformers model (~470 MB with torch-CPU) is lazy-loaded on the
first query only - importing this module never loads it. The Streamlit showcase
tab therefore never pays the cost; only live questions do.
"""
from functools import lru_cache

import chromadb

from .paths import DATA_DIR

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHROMA_DIR = DATA_DIR / "chroma"


@lru_cache(maxsize=1)
def _client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


@lru_cache(maxsize=1)
def _embedder():
    from sentence_transformers import SentenceTransformer  # heavy import, deferred
    return SentenceTransformer(EMBED_MODEL)


def _collection(lang: str):
    if lang not in ("en", "tl"):
        raise ValueError(f"lang must be 'en' or 'tl', got {lang!r}")
    return _client().get_collection(f"briefs_{lang}")


def search_briefs(query: str, lang: str = "en", k: int = 4) -> list[dict]:
    vec = _embedder().encode([query], normalize_embeddings=True).tolist()
    res = _collection(lang).query(query_embeddings=vec, n_results=k)
    out = []
    for i, doc in enumerate(res["documents"][0]):
        meta = res["metadatas"][0][i]
        out.append({
            "pcode": meta["pcode"], "barangay": meta["barangay"],
            "city": meta["city"], "lang": lang, "text": doc,
            "distance": round(res["distances"][0][i], 4),
        })
    return out


def get_brief_text(pcode: str, lang: str) -> dict | None:
    res = _collection(lang).get(ids=[f"{pcode}_{lang}"])
    if not res["ids"]:
        return None
    meta = res["metadatas"][0]
    return {"pcode": meta["pcode"], "barangay": meta["barangay"],
            "city": meta["city"], "lang": lang, "text": res["documents"][0]}
