"""Embed all briefs into a committed ChromaDB index (one collection per language).

Run once: ./.venv/Scripts/python build/02_build_index.py   (~2-4 min on CPU)
"""
import json
import shutil
import sys
from pathlib import Path

import chromadb
import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bahatanong_mcp.paths import BAHAMAP_PROCESSED, DATA_DIR
from bahatanong_mcp.search import CHROMA_DIR, EMBED_MODEL


def main() -> None:
    from sentence_transformers import SentenceTransformer

    briefs = json.loads((BAHAMAP_PROCESSED / "briefs.json").read_text(encoding="utf-8"))
    con = duckdb.connect(str(DATA_DIR / "bahatanong.duckdb"), read_only=True)
    meta_by_pcode = {
        r[0]: {"barangay": r[1], "city": r[2]}
        for r in con.execute("SELECT pcode, barangay, city FROM v_exposure").fetchall()
    }
    assert set(briefs) == set(meta_by_pcode), "briefs.json and v_exposure disagree on pcodes"

    model = SentenceTransformer(EMBED_MODEL)
    shutil.rmtree(CHROMA_DIR, ignore_errors=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    for lang in ("en", "tl"):
        ids, docs, metas = [], [], []
        for pcode, b in sorted(briefs.items()):
            ids.append(f"{pcode}_{lang}")
            docs.append(b[lang])
            metas.append({"pcode": pcode, **meta_by_pcode[pcode]})
        vecs = model.encode(docs, normalize_embeddings=True, show_progress_bar=True).tolist()
        coll = client.create_collection(f"briefs_{lang}", metadata={"hnsw:space": "cosine"})
        for i in range(0, len(ids), 500):  # chroma add() batch cap safety
            coll.add(ids=ids[i:i+500], documents=docs[i:i+500],
                     embeddings=vecs[i:i+500], metadatas=metas[i:i+500])
        print(f"briefs_{lang}: {coll.count()} docs")

    size = sum(f.stat().st_size for f in CHROMA_DIR.rglob("*") if f.is_file())
    print(f"Index size: {size/1e6:.1f} MB")


if __name__ == "__main__":
    main()
