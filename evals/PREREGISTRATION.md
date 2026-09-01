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

## Amendment 1 - 2026-09-01 (before amended runs)

Post-hoc review of the original analysis found an instrumentation bug, not a model
or scorer-logic issue: run_agent stored tool results truncated to 2,000 chars, while
the live grounding validator saw full evidence - so the qualitative pcode check
could fail on answers that were in fact fully grounded (confirmed for one V2 item,
qual-001; corrected-p sensitivity: 0.0309 -> 0.0490). Amendment: raise the stored-trace
cap to 8,000 chars (covers a k=10 search_briefs payload) and rerun BOTH arms once,
same procedure otherwise (same golden set, scorer logic, model, temperature 0).
Both the original and amended analyses will be reported; the amended analysis is
primary. Retrieval nondeterminism across processes (HNSW) is added as a stated
limitation - post-hoc reconstruction of retrieved sets is not reliable, which is
itself part of why the rerun (not post-hoc rescoring) is the amendment of record.
