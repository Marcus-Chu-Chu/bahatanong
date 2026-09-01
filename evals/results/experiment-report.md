# Experiment report - BahaTanong prompt V1 vs V2 (Task 12, M4b)

Pre-registered in `evals/PREREGISTRATION.md` (commit `436c583`), before any V2 result
existed. This report follows that pre-registration exactly, including in the case -
this one - where the result does not confirm H1.

## H1 (restated, verbatim from the pre-registration)

> Prompt V2 (V1 + two worked tool-use examples + an explicit numeric-grounding
> checklist) improves the overall golden-set pass rate over V1 (baseline: 95.0%).

Test: exact McNemar (two-sided binomial on discordant pairs), alpha = .05, paired
over the full N=120 golden set. Same `golden.jsonl` (Task 10 commit), same scorer
(Task 11 commit), one run per variant, temperature 0, model `claude-haiku-4-5`.

## Headline result: H1 is not supported - V2 is significantly WORSE than V1

| | V1 (baseline) | V2 (worked examples + checklist) |
|---|---|---|
| Overall pass rate | **95.0%** (114/120) | **86.7%** (104/120) |

- Discordant pairs: b = 14 (V1 passed, V2 failed), c = 4 (V2 passed, V1 failed)
- Exact McNemar (two-sided): **p = 0.0309**
- delta_pp (V2 - V1): **-8.33 pp**

p = 0.0309 < alpha = .05, so this result **is** statistically significant - but in
the opposite direction from H1. The pre-registration's fallback headline ("no
significant difference detected, MDE ~12pp") does not apply here; that language was
reserved for a null result (p >= .05), and this is not one. The honest headline for
this data is: **adding the worked examples and grounding checklist significantly
reduced the pass rate**, by an amount (8.33pp) inside the study's ~12pp minimum
detectable effect - i.e. the drop is large enough to clear detection at N=120 despite
the study being underpowered for smaller effects.

## Secondary metrics (descriptive only, no test - as pre-registered)

| Metric | V1 | V2 |
|---|---|---|
| Grounding pass rate | 100.0% (120/120) | 97.5% (117/120) |
| Refusal accuracy (refuse-type items) | 73.3% (11/15) | 80.0% (12/15) |
| Pass rate - English | 94.0% (63/67) | 89.6% (60/67) |
| Pass rate - Tagalog | 96.2% (51/53) | 83.0% (44/53) |
| Mean tokens / question (total) | 6,821 | 7,360 |
| Mean tokens / question (in / out) | 6,506 / 316 | 7,057 / 303 |
| Est. cost (full 120-item run) | $0.97 | $1.03 |

By question type (pass/N):

| Type | V1 | V2 |
|---|---|---|
| aggregation | 20/20 (100%) | 18/20 (90%) |
| comparison | 15/15 (100%) | 15/15 (100%) |
| lookup | 28/30 (93%) | 29/30 (97%) |
| qualitative | 20/20 (100%) | 11/20 (55%) |
| ranking | 20/20 (100%) | 19/20 (95%) |
| refuse | 11/15 (73%) | 12/15 (80%) |

## Where the regression concentrated (descriptive - not part of the pre-registered test)

Recomputed directly from both `results.jsonl` files, item by item:

**b = 14 (V1 passed -> V2 failed):** 9 of the 14 (64%) are `qualitative` items, all
failing with the same scorer reason - "target brief not retrieved or ungrounded
numbers" - and 5 of those 9 are Tagalog. The remaining 5: two `aggregation` items
(`agg-005` en / `agg-006` tl - the same expected value, 14983.0, missing in both
language variants of what is evidently the same underlying question), one `lookup`,
one `ranking`, one `refuse`.

**c = 4 (V2 passed -> V1 failed):** two `lookup`, two `refuse` - spread across
distinct items with no shared failure reason, consistent with run-to-run noise on
borderline items rather than a systematic V2 improvement.

Qualitative pass rate alone moved from 100% (20/20) to 55% (11/20) and accounts for
the majority of the net drop. The V2 prompt's appended block includes a worked
example for a qualitative question that ends "then say 'Source: brief - Rosario,
Pasig'" - a rigid two-example demonstration late in a prompt that also adds a
4-point pre-answer checklist. Whether the mechanism is the model over-fitting to the
worked example's phrasing, the added prompt length/checklist crowding out the
`search_briefs` tool call, or something else, is **not established by this data** -
the golden set and scorer were not built to isolate that mechanism, and this is a
single run. This paragraph is an observation about where the numbers moved, not a
causal claim.

## Limitations (restated from the pre-registration)

- Single run per variant assumes temperature-0 stability; neither arm was repeated,
  so ordinary run-to-run variance (e.g. the c=4 items above) cannot be distinguished
  from true prompt effects at the item level - only the aggregate McNemar result is
  protected against that by the paired design.
- The scorer is deterministic and shared by both arms, so it cannot itself have
  introduced the asymmetry.
- With N=120 the pre-registered minimum detectable effect was ~12pp; the observed
  8.33pp effect is smaller than that nominal MDE yet still reached p < .05 here,
  which is expected (MDE is a power-planning heuristic, not a hard detection floor)
  but is a reminder that a non-significant result on a future, similarly sized run
  should not be over-read as "no effect."

## Cost accounting

| Run | Est. cost |
|---|---|
| smoke (Task 11, N=10) | $0.07 |
| v1 (this task, N=120) | $0.97 |
| v2 (this task, N=120) | $1.03 |
| **Total** | **$2.07** |

$2.07 is well under the $5 expected-total checkpoint and the $6 flag threshold from
the task brief - no cost concern to raise before Task 13.

## Conclusion

H1 - that prompt V2 (worked examples + grounding checklist) would improve the
overall pass rate over V1 - is not supported by this experiment. The data show the
opposite: V2 scored 86.7% (104/120) against V1's 95.0% (114/120), a drop of 8.33
percentage points that is statistically significant under the pre-registered exact
McNemar test (b=14, c=4, two-sided p=0.0309, alpha=.05). This is a significant
result, not a null one, so the pre-registration's null-result headline does not
apply; the honest headline is that V2 underperformed V1, driven mostly by a collapse
in the qualitative-question category (100% to 55%, concentrated in Tagalog) with a
smaller contribution from two aggregation items and single items in three other
categories. Grounding pass rate also declined slightly (100.0% to 97.5%). V2 did
edge out V1 on refusal accuracy (73.3% to 80.0%) and lookup (93% to 97%), and the
four items V2 recovered from V1's failures show no shared pattern, consistent with
ordinary noise rather than a real improvement in those categories. Recommendation:
do not adopt prompt V2 as written; if the worked-examples approach is revisited, it
should be tested with the qualitative-item failure mode investigated directly (why
`search_briefs` results or grounding fail for the exact items listed above) rather
than re-run blind, since this experiment was pre-registered for a single comparison
and a second look at the same two arms would no longer be a clean test.
