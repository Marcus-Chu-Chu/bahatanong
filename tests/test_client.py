import os

import pytest

from agent.client import MODEL, make_llm


def test_model_id_is_exact():
    assert MODEL == "claude-haiku-4-5"


def test_missing_key_raises_clear_error(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("agent.client._load_dotenv_once", lambda: None)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        make_llm()


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY") and not os.path.exists(".env"),
                    reason="no key available")
def test_llm_constructs_with_workspace_header():
    llm = make_llm()
    assert llm.temperature == 0
    # Header attached whenever a workspace id is configured (identity-linked key).
    if os.environ.get("ANTHROPIC_WORKSPACE_ID"):
        assert llm.default_headers["anthropic-workspace-id"] == os.environ["ANTHROPIC_WORKSPACE_ID"]
