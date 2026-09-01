"""Run the real agent on 12 curated questions; save full traces for the app's
Showcase tab. Runs AFTER the agent exists (Task 13) - not with the Task 2/3 builds.

Run: ./.venv/Scripts/python build/03_build_showcase.py   (~$0.25)
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent.client import MODEL
from agent.graph import run_agent

PROMPT = "agent/prompts/v1.md"  # the experiment outcome: V2 refuted (Task 12) - V1 ships
OUT = Path("app/showcase.json")

QUESTIONS = [
    ("Which barangay in Marikina has the most residents inside the 25-year flood zone?", "en"),
    ("Aling barangay sa Marikina ang may pinakamaraming residenteng nakatira sa loob ng 25-year flood zone?", "tl"),
    ("What are the top 5 most flood-exposed barangays in Metro Manila?", "en"),
    ("Ano ang sitwasyon ng baha sa Rosario, Pasig?", "tl"),
    ("How many NCR residents in total are estimated to live inside the 25-year flood zone?", "en"),
    ("Ilan lahat ang tinatayang residente ng Taguig na nasa loob ng 25-year flood zone?", "tl"),
    ("Which city has the highest share of its population in the flood zone?", "en"),
    ("Paano dapat maghanda sa baha ang mga taga-Tumana, Marikina?", "tl"),
    ("Based on the yearly rainfall data, are days of extreme rainfall becoming more frequent in Metro Manila?", "en"),
    ("What does 'exposure score' mean in this atlas?", "en"),
    ("Babaha ba bukas sa Marikina?", "tl"),
    ("Compare flood exposure between Malanday and Manggahan.", "en"),
]


def main() -> None:
    items = []
    for q, lang in QUESTIONS:
        print(f"-> {q}")
        r = run_agent(q, prompt_path=PROMPT)
        assert r["language"] == lang, f"language detect mismatch on {q!r}"
        assert r["violations"] == [], f"ungrounded showcase answer on {q!r} - fix before shipping"
        items.append({"question": q, "lang": lang, "answer": r["answer"],
                      "tool_trace": r["tool_trace"], "usage": r["usage"]})
    OUT.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt": PROMPT, "model": MODEL, "items": items,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {OUT} with {len(items)} items")


if __name__ == "__main__":
    main()
