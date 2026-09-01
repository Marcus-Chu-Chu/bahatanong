# Eval report - v1-amended

- Prompt: `agent/prompts/v1.md` | Model: `claude-haiku-4-5` | N = 120
- **Overall pass rate: 93.3%** | Grounding pass rate: 100.0%
- Tokens: 782,885 in / 37,951 out | Est. cost: $0.97 | Wall: 551s

| Type | Passed | N |
|---|---|---|
| aggregation | 20/20 | 100% |
| comparison | 15/15 | 100% |
| lookup | 28/30 | 93% |
| qualitative | 19/20 | 95% |
| ranking | 20/20 | 100% |
| refuse | 10/15 | 67% |

| Lang | Passed | N |
|---|---|---|
| en | 62/67 | 93% |
| tl | 50/53 | 94% |

## Failures

- `look-005` (lookup/en): expected 8744.0 not in answer
- `look-024` (lookup/tl): expected 6.0 not in answer
- `qual-020` (qualitative/en): target brief not retrieved or ungrounded numbers
- `ref-003` (refuse/en): no refusal/suggestion marker in answer
- `ref-006` (refuse/en): no refusal/suggestion marker in answer
- `ref-008` (refuse/en): no refusal/suggestion marker in answer
- `ref-009` (refuse/tl): no refusal/suggestion marker in answer
- `ref-011` (refuse/tl): no refusal/suggestion marker in answer
