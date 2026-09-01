"""Run the golden set through the agent and write results + a report.

Usage:
  ./.venv/Scripts/python evals/run_evals.py --prompt agent/prompts/v1.md --label v1
  ./.venv/Scripts/python evals/run_evals.py --prompt agent/prompts/v1.md --label smoke --subset 10
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent.client import MODEL
from agent.graph import run_agent
from evals.scoring import score_item

GOLDEN = Path(__file__).parent / "golden.jsonl"
RESULTS = Path(__file__).parent / "results"
PRICE_IN, PRICE_OUT = 1.00, 5.00  # claude-haiku-4-5 $/MTok (verify actuals in Console)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--subset", type=int)
    ap.add_argument("--model", default=MODEL)
    args = ap.parse_args()

    items = [json.loads(l) for l in GOLDEN.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.subset:
        items = items[:: max(1, len(items) // args.subset)][: args.subset]

    outdir = RESULTS / args.label
    outdir.mkdir(parents=True, exist_ok=True)
    rows, tok_in, tok_out = [], 0, 0
    t0 = time.time()
    for n, item in enumerate(items, 1):
        try:
            result = run_agent(item["question"], prompt_path=args.prompt, model=args.model)
        except Exception as e:  # API failure -> scored as fail, run continues
            result = {"answer": f"[RUN ERROR] {e}", "violations": [], "tool_trace": [],
                      "language": item["lang"], "retried": False,
                      "usage": {"input_tokens": 0, "output_tokens": 0}}
        score = score_item(item, result)
        rows.append({"item": item, "result": result, "score": score})
        tok_in += result["usage"]["input_tokens"]
        tok_out += result["usage"]["output_tokens"]
        print(f"[{n}/{len(items)}] {item['id']} {'PASS' if score['passed'] else 'FAIL':4} "
              f"({score['reason'][:60]})")

    (outdir / "results.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

    cost = tok_in / 1e6 * PRICE_IN + tok_out / 1e6 * PRICE_OUT
    scores = [r["score"] for r in rows]
    overall = sum(s["passed"] for s in scores) / len(scores)
    grounded = sum(s["grounded"] for s in scores) / len(scores)
    by_type = {t: (sum(s["passed"] for s in scores if s["type"] == t),
                   sum(1 for s in scores if s["type"] == t))
               for t in Counter(s["type"] for s in scores)}
    by_lang = {g: (sum(s["passed"] for s in scores if s["lang"] == g),
                   sum(1 for s in scores if s["lang"] == g))
               for g in ("en", "tl")}

    lines = [
        f"# Eval report - {args.label}", "",
        f"- Prompt: `{args.prompt}` | Model: `{args.model}` | N = {len(items)}",
        f"- **Overall pass rate: {overall:.1%}** | Grounding pass rate: {grounded:.1%}",
        f"- Tokens: {tok_in:,} in / {tok_out:,} out | Est. cost: ${cost:.2f} "
        f"| Wall: {time.time()-t0:.0f}s", "",
        "| Type | Passed | N |", "|---|---|---|",
        *[f"| {t} | {p}/{n} | {p/n:.0%} |" for t, (p, n) in sorted(by_type.items())],
        "", "| Lang | Passed | N |", "|---|---|---|",
        *[f"| {g} | {p}/{n} | {p/n:.0%} |" for g, (p, n) in by_lang.items() if n],
        "", "## Failures", "",
        *[f"- `{s['id']}` ({s['type']}/{s['lang']}): {s['reason']}"
          for s in scores if not s["passed"]],
    ]
    (outdir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nOverall {overall:.1%} | grounded {grounded:.1%} | ${cost:.2f} -> {outdir}")


if __name__ == "__main__":
    main()
