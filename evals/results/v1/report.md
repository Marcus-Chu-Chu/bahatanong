# Eval report - v1

- Prompt: `agent/prompts/v1.md` | Model: `claude-haiku-4-5` | N = 120
- **Overall pass rate: 95.0%** | Grounding pass rate: 100.0%
- Tokens: 780,690 in / 37,871 out | Est. cost: $0.97 | Wall: 555s

| Type | Passed | N |
|---|---|---|
| aggregation | 20/20 | 100% |
| comparison | 15/15 | 100% |
| lookup | 28/30 | 93% |
| qualitative | 20/20 | 100% |
| ranking | 20/20 | 100% |
| refuse | 11/15 | 73% |

| Lang | Passed | N |
|---|---|---|
| en | 63/67 | 94% |
| tl | 51/53 | 96% |

## Failures

- `look-005` (lookup/en): expected 8744.0 not in answer
- `look-024` (lookup/tl): expected 6.0 not in answer
- `ref-003` (refuse/en): no refusal/suggestion marker in answer
- `ref-006` (refuse/en): no refusal/suggestion marker in answer
- `ref-008` (refuse/en): no refusal/suggestion marker in answer
- `ref-011` (refuse/tl): no refusal/suggestion marker in answer
