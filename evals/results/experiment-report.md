# Experiment report - BahaTanong prompt V1 vs V2 (Task 12, M4b)

**Amendment 1 applies to this report.** Pre-registered in `evals/PREREGISTRATION.md`
(commit `436c583`), before any V2 result existed. Post-hoc review then found an
instrumentation bug: `run_agent` stored tool results truncated to 2,000 chars for the
eval trace, while the live grounding validator saw full evidence - so the qualitative
scorer's pcode-in-trace check could fail on answers that were in fact fully grounded.
Confirmed for one V2 item (`qual-001`, target pcode at char 5,260 of a 6,568-char
`search_briefs` result). Amendment 1 (registered in `PREREGISTRATION.md`, commit
`f0f3b06`, before any amended run existed) raised the cap to 8,000 chars
(`agent/graph.py`, commit `36ee5ff`) and re-ran both arms once, unchanged otherwise.
**The amended analysis below is primary.** The original analysis is kept verbatim
afterward for the record, not deleted or silently replaced.

## 1. H1 (restated, verbatim from the pre-registration)

> Prompt V2 (V1 + two worked tool-use examples + an explicit numeric-grounding
> checklist) improves the overall golden-set pass rate over V1 (baseline: 95.0%).

Test: exact McNemar (two-sided binomial on discordant pairs), alpha = .05, paired
over the full N=120 golden set. Same `golden.jsonl` (Task 10 commit), same scorer
(Task 11 commit), one run per variant, temperature 0, model `claude-haiku-4-5`.

## 2. Amended analysis (PRIMARY)

Labels `v1-amended` / `v2-amended`; same prompts (`agent/prompts/v1.md`,
`agent/prompts/v2.md`, byte-identical to the original run - verified by hash), same
golden set and scorer, `agent/graph.py` trace cap raised from 2,000 to 8,000 chars.

| | V1-amended | V2-amended |
|---|---|---|
| Overall pass rate | **93.3%** (112/120) | **87.5%** (105/120) |

- Discordant pairs: b = 12 (V1-amended passed, V2-amended failed), c = 5 (V2-amended
  passed, V1-amended failed)
- Exact McNemar (two-sided): **p = 0.1435**
- delta_pp (V2-amended - V1-amended): **-5.83 pp**

**p = 0.1435 >= alpha = .05: no significant difference detected (MDE ~12pp).** This
is exactly the null-result case the pre-registration described in advance - "the
report states the observed effect with its p-value either way, a null result is a
result" - and per the pre-registration's own rule, that fallback headline is the
correct one to report, with no spin toward either arm.

### Secondary metrics (descriptive only, no test)

| Metric | V1-amended | V2-amended |
|---|---|---|
| Grounding pass rate | 100.0% (120/120) | 98.3% (118/120) |
| Refusal accuracy (refuse-type items) | 66.7% (10/15) | 80.0% (12/15) |
| Pass rate - English | 92.5% (62/67) | 89.6% (60/67) |
| Pass rate - Tagalog | 94.3% (50/53) | 84.9% (45/53) |
| Mean tokens / question (total) | 6,840 | 7,313 |
| Mean tokens / question (in / out) | 6,524 / 316 | 7,011 / 301 |
| Est. cost (full 120-item run) | $0.97 | $1.02 |

By question type (pass/N):

| Type | V1-amended | V2-amended |
|---|---|---|
| aggregation | 20/20 (100%) | 18/20 (90%) |
| comparison | 15/15 (100%) | 15/15 (100%) |
| lookup | 28/30 (93%) | 29/30 (97%) |
| qualitative | 19/20 (95%) | 12/20 (60%) |
| ranking | 20/20 (100%) | 19/20 (95%) |
| refuse | 10/15 (67%) | 12/15 (80%) |

### Where the amended point estimate moved (descriptive - not part of the test; the
### test result above is non-significant, so this is not evidence of an effect)

Recomputed directly from both `results.jsonl` files, item by item:

**b = 12 (V1-amended passed -> V2-amended failed):** 7 of 12 are `qualitative`
items (still the largest single category, down from 9 of 14 pre-amendment - `qual-001`
is no longer in this list, consistent with the confirmed mis-score fix). The rest:
two `aggregation` (`agg-005` en / `agg-006` tl, same missing value 14983.0 as the
original run), one `lookup`, one `ranking`, one `refuse`.

**c = 5 (V2-amended passed -> V1-amended failed):** two `lookup`, three `refuse` -
spread across distinct items with no shared failure reason.

Qualitative pass rate moved from 95.0% (19/20) to 60.0% (12/20) in the amended runs -
smaller than the pre-amendment 100%-to-55% swing (the qual-001 fix and ordinary
run-to-run drift both contributed to V1-amended itself landing at 95% rather than
100%), but still the largest per-category gap between arms.

**Per-language rates *within* the qualitative category** (correcting the original
report's "concentrated in Tagalog" framing, which was read off raw discordant-pair
counts rather than rates normalized by each language's own base N):

| | V1-amended qualitative | V2-amended qualitative | Drop |
|---|---|---|---|
| English (N=8) | 87.5% (7/8) | 50.0% (4/8) | -37.5 pp |
| Tagalog (N=12) | 100.0% (12/12) | 66.7% (8/12) | -33.3 pp |

Both languages drop by a comparable amount in relative terms. The original report's
"concentrated in Tagalog" statement was an artifact of Tagalog having more
qualitative items in the golden set (12 vs 8), not of Tagalog degrading
disproportionately - English degrades slightly *more* on a rate basis. This is
corrected here rather than repeated.

## 3. Original (pre-amendment) analysis - kept for the record, NOT primary

This is the analysis from before the trace-cap fix, preserved verbatim rather than
deleted, per Amendment 1's instruction that both analyses be reported.

> H1 - that prompt V2 (worked examples + grounding checklist) would improve the
> overall pass rate over V1 - is not supported by this experiment. The data show the
> opposite: V2 scored 86.7% (104/120) against V1's 95.0% (114/120), a drop of 8.33
> percentage points that is statistically significant under the pre-registered exact
> McNemar test (b=14, c=4, two-sided p=0.0309, alpha=.05).

| | V1 (original) | V2 (original) |
|---|---|---|
| Overall pass rate | 95.0% (114/120) | 86.7% (104/120) |
| Grounding pass rate | 100.0% (120/120) | 97.5% (117/120) |
| Refusal accuracy | 73.3% (11/15) | 80.0% (12/15) |
| Pass rate - English | 94.0% (63/67) | 89.6% (60/67) |
| Pass rate - Tagalog | 96.2% (51/53) | 83.0% (44/53) |

Discordant pairs: b = 14, c = 4, exact McNemar two-sided **p = 0.0309** (significant),
delta_pp = -8.33.

**Why this analysis is superseded, not trusted as primary:** post-hoc review found
that `run_agent` stored tool results truncated to 2,000 chars for the eval trace
(`agent/graph.py`, pre-fix), while the live grounding validator that actually gated
`result["violations"]` saw the full, untruncated tool output. The qualitative
scorer's check - `item["expect"]["pcode"] in trace and grounded` - reads that same
truncated trace, so an answer could be fully grounded (validator saw everything) and
still score as a qualitative failure (scorer's trace copy was cut off) purely because
the correct pcode string happened to sit past character 2,000 of a `search_briefs`
result. **Confirmed for `qual-001`** (V2, original run): target pcode was at char
5,260 of a 6,568-char search result; the underlying answer was fully grounded.
Correcting that one item's score by hand (without re-running) moves the sensitivity
estimate from p=0.0309 to **p=0.0490** - still under .05, which is why a full rerun
(not a post-hoc rescore) was chosen as the amendment of record: two more items
(`qual-009`, `qual-012`) were flagged as possible further cases but could not be
confirmed the same way, because retrieval itself is not guaranteed deterministic
across process runs (see Limitations) - reconstructing exactly what a past process's
`search_briefs` call would have returned is not reliable after the fact. A real
rerun with the fix in place, rather than arithmetic patching of the old numbers, is
the only way to get a trustworthy count instead of a lower-bound sensitivity note.

Full original discordant-pair detail (by type): b=14 was 9 qualitative, 2
aggregation, 1 lookup, 1 ranking, 1 refuse; c=4 was 2 lookup, 2 refuse. Original
per-type table: aggregation 20/20 vs 18/20, comparison 15/15 vs 15/15, lookup 28/30
vs 29/30, qualitative 20/20 vs 11/20, ranking 20/20 vs 19/20, refuse 11/15 vs 12/15.

## 4. Conclusion (per the amended, primary analysis)

**No significant difference detected between V1 and V2 (exact McNemar, p=0.1435,
alpha=.05; MDE at N=120 is approximately 12pp).** H1 predicted V2 would improve on
V1; the amended data do not support that, but with the instrumentation bug fixed
they also no longer support the original analysis's finding that V2 was
significantly *worse*. The point estimate still numerically favors V1 (93.3% vs
87.5%, delta -5.83pp), and the qualitative-question category remains the largest
single contributor to that gap (95.0% to 60.0%), but at N=120 this specific
experiment cannot distinguish that gap from chance (b=12, c=5 is close enough to
balanced that p is well above .05). The original report's claim that the drop was
"concentrated in Tagalog" is corrected here: normalized by each language's own base
rate, English's qualitative pass rate fell by more (-37.5pp) than Tagalog's
(-33.3pp) - the earlier framing was an artifact of raw discordant-item counts, not
of the actual per-language rates. Grounding, refusal accuracy, and lookup all show
small movements in both directions that are consistent with ordinary run-to-run
noise rather than a real prompt effect. **Recommendation: do not conclude that
prompt V2 either helps or hurts based on this experiment.** The qualitative-category
gap is worth a targeted follow-up (why `search_briefs` retrieval or grounding fails
more often under V2 for these specific items) precisely because it is the one
pattern that recurred across both the original and amended runs even as statistical
significance did not - but that follow-up should be designed and pre-registered as
its own comparison, not read off this one's non-significant point estimate.

## 5. Limitations

- **Single run per arm** (both original and amended) assumes temperature-0
  stability; neither arm was repeated, so ordinary run-to-run variance cannot be
  distinguished from true prompt effects at the individual-item level - only the
  aggregate McNemar result is protected against that by the paired design, and even
  that result can shift between two single runs of the *same* prompt, as it did
  between the original and amended V1 runs (95.0% vs 93.3% - see below).
- **MDE (minimum detectable effect) is approximately 12pp at N=120** under
  conventional power assumptions; a smaller true effect than that may return
  non-significant even if real. The amended p=0.1435 with delta=-5.83pp is
  consistent with either "no real effect" or "a real effect too small for this
  N to detect reliably" - this experiment cannot distinguish those two
  possibilities, and neither should be claimed over the other.
- **Retrieval nondeterminism across processes (HNSW).** `search_briefs` is backed
  by an HNSW approximate-nearest-neighbor index; result ordering/selection for
  near-tied candidates is not guaranteed identical across separate process runs
  even at the same query and temperature-0 model settings. This is visible directly
  in the data: V1-amended (93.3%, 112/120) differs from the original V1 run (95.0%,
  114/120) despite an unchanged prompt, unchanged golden set, and unchanged scorer -
  the only thing that differs is wall-clock run and, for qualitative items,
  whatever the retrieval layer returned that time. This is also why the original
  analysis's two unconfirmed suspects (`qual-009`, `qual-012`) were left as
  "unconfirmable" rather than hand-patched: reconstructing what a *past* process's
  retrieval call would have returned is not reliable, which is itself part of why
  a rerun - not post-hoc rescoring - is the amendment of record.

## Cost accounting

| Run | Est. cost |
|---|---|
| smoke (Task 11, N=10) | $0.07 |
| v1 (original, N=120) | $0.97 |
| v2 (original, N=120) | $1.03 |
| v1-amended (N=120) | $0.97 |
| v2-amended (N=120) | $1.02 |
| **Total** | **$4.06** |

$4.06 is under the coordinator's ~$4.1 estimate and the $5 flag threshold for this
step (and well under the $8 approved budget for the amendment) - no cost concern to
raise before Task 13.
