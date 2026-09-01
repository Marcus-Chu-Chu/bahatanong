# Pre-registration - BahaTanong prompt experiment

**Committed before any V2 result exists; the git history of this file is the timestamp.**

- **H1:** Prompt V2 (V1 + two worked tool-use examples + an explicit numeric-grounding
  checklist) improves the overall golden-set pass rate over V1 (baseline: 95.0%).
- **Test:** exact McNemar (two-sided binomial on discordant pairs), alpha = .05,
  paired over the full N=120 golden set.
- **Procedure:** one run per variant, temperature 0, model claude-haiku-4-5,
  same golden.jsonl (frozen at the Task 10 commit), scorer frozen at the Task 11 commit.
- **Secondary metrics (descriptive only, no test):** grounding pass rate, refusal
  accuracy, per-language pass rates, mean tokens per question.
- **Power:** with N=120, the minimum detectable effect is roughly 12pp at
  conventional power; a smaller true effect may return non-significant. The report
  states the observed effect with its p-value either way - a null result is a result.
- **Limitations stated up front:** single run per variant assumes temperature-0
  stability; scorer is deterministic and shared by both arms.
