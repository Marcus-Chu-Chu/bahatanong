import pytest

from agent.graph import run_agent

pytestmark = pytest.mark.live


def test_lookup_en():
    out = run_agent("How many residents does Malanday in Marikina have?")
    assert out["language"] == "en" and out["violations"] == []
    assert any(t["tool"] == "run_sql" for t in out["tool_trace"])


def test_qualitative_tl():
    out = run_agent("Ano ang sitwasyon ng baha sa Rosario, Pasig?")
    assert out["language"] == "tl" and out["violations"] == []


def test_forecast_refused():
    out = run_agent("Will it flood in Marikina tomorrow?")
    assert "This is outside what BahaTanong can answer." in out["answer"]
