"""Deterministic scoring - no LLM judge. Every rule is inspectable and testable."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent.validator import extract_numbers


def _numbers_in(text: str) -> list[float]:
    # Scorer-local extraction WITHOUT the <10 floor (ranks and small counts matter here).
    out = []
    for tok in re.findall(r"\d[\d,]*\.?\d*", text):
        out.append(float(tok.replace(",", "")))
    return out


def _value_present(answer: str, value: float, tolerance: float) -> bool:
    return any(abs(n - value) <= max(tolerance, 1e-9) for n in _numbers_in(answer))


def score_item(item: dict, result: dict) -> dict:
    t, answer = item["type"], result["answer"]
    grounded = result["violations"] == []
    passed, reason = False, ""

    if t in ("lookup", "aggregation"):
        passed = _value_present(answer, item["expect"]["value"], item["expect"]["tolerance"])
        reason = "" if passed else f"expected {item['expect']['value']} not in answer"
    elif t == "ranking":
        pos = []
        low = answer.lower()
        for name in item["expect"]["ordered_names"]:
            i = low.find(name.lower())
            pos.append(i)
        passed = all(p >= 0 for p in pos) and pos == sorted(pos)
        reason = "" if passed else f"names/order mismatch (positions {pos})"
    elif t == "comparison":
        winner = item["expect"]["winner"].lower()
        passed = winner in answer.lower() and _value_present(
            answer, max(item["expect"]["values"]), 0.5)
        reason = "" if passed else "winner or winning value missing"
    elif t == "qualitative":
        trace = json.dumps(result["tool_trace"], ensure_ascii=False)
        passed = item["expect"]["pcode"] in trace and grounded
        reason = "" if passed else "target brief not retrieved or ungrounded numbers"
    elif t == "refuse":
        passed = any(m.lower() in answer.lower() for m in item["expect"]["markers"])
        reason = "" if passed else "no refusal/suggestion marker in answer"

    if t != "refuse" and not grounded:
        passed, reason = False, (reason + "; ungrounded numbers survived").strip("; ")
    return {"id": item["id"], "type": t, "lang": item["lang"],
            "passed": passed, "grounded": grounded, "reason": reason}
