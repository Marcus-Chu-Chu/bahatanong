# Eval report - v2-amended

- Prompt: `agent/prompts/v2.md` | Model: `claude-haiku-4-5` | N = 120
- **Overall pass rate: 87.5%** | Grounding pass rate: 98.3%
- Tokens: 841,351 in / 36,168 out | Est. cost: $1.02 | Wall: 526s

| Type | Passed | N |
|---|---|---|
| aggregation | 18/20 | 90% |
| comparison | 15/15 | 100% |
| lookup | 29/30 | 97% |
| qualitative | 12/20 | 60% |
| ranking | 19/20 | 95% |
| refuse | 12/15 | 80% |

| Lang | Passed | N |
|---|---|---|
| en | 60/67 | 90% |
| tl | 45/53 | 85% |

## Failures

- `look-006` (lookup/tl): expected 6445.0 not in answer
- `rank-012` (ranking/tl): names/order mismatch (positions [143, 274, -1, 78, -1])
- `agg-005` (aggregation/en): expected 14983.0 not in answer; ungrounded numbers survived
- `agg-006` (aggregation/tl): expected 14983.0 not in answer; ungrounded numbers survived
- `qual-008` (qualitative/tl): target brief not retrieved or ungrounded numbers
- `qual-009` (qualitative/tl): target brief not retrieved or ungrounded numbers
- `qual-011` (qualitative/tl): target brief not retrieved or ungrounded numbers
- `qual-012` (qualitative/tl): target brief not retrieved or ungrounded numbers
- `qual-014` (qualitative/en): target brief not retrieved or ungrounded numbers
- `qual-017` (qualitative/en): target brief not retrieved or ungrounded numbers
- `qual-018` (qualitative/en): target brief not retrieved or ungrounded numbers
- `qual-020` (qualitative/en): target brief not retrieved or ungrounded numbers
- `ref-005` (refuse/en): no refusal/suggestion marker in answer
- `ref-006` (refuse/en): no refusal/suggestion marker in answer
- `ref-011` (refuse/tl): no refusal/suggestion marker in answer
