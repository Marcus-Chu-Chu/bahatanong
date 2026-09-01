import json
from pathlib import Path

SHOWCASE = Path("app/showcase.json")


def test_showcase_shape():
    data = json.loads(SHOWCASE.read_text(encoding="utf-8"))
    items = data["items"]
    assert len(items) == 12
    assert sum(1 for i in items if i["lang"] == "tl") >= 5
    for i in items:
        assert i["answer"] and isinstance(i["tool_trace"], list)
    # traces are genuine: at least 10 of 12 called a tool (refusals may call none)
    assert sum(1 for i in items if i["tool_trace"]) >= 10
