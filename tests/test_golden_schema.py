import json
from collections import Counter
from pathlib import Path

GOLDEN = Path("evals/golden.jsonl")


def _items():
    return [json.loads(ln) for ln in GOLDEN.read_text(encoding="utf-8").splitlines() if ln.strip()]


def test_counts_and_distribution():
    items = _items()
    assert len(items) == 120
    types = Counter(i["type"] for i in items)
    assert types == {"lookup": 30, "ranking": 20, "aggregation": 20,
                     "comparison": 15, "qualitative": 20, "refuse": 15}
    langs = Counter(i["lang"] for i in items)
    assert langs["tl"] >= 40


def test_ids_unique_and_expect_shapes():
    items = _items()
    assert len({i["id"] for i in items}) == 120
    for i in items:
        e = i["expect"]
        match i["type"]:
            case "lookup" | "aggregation":
                assert set(e) == {"value", "tolerance"}
            case "ranking":
                assert e["ordered_names"]
            case "comparison":
                assert set(e) == {"winner", "values"}
            case "qualitative":
                assert e["pcode"].startswith("PH") or e["pcode"][0].isdigit()
            case "refuse":
                assert e["markers"]
