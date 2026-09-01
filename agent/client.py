"""ChatAnthropic factory. The Console key is identity-linked: every request must
carry the anthropic-workspace-id header or the API rejects it."""
import os
from functools import lru_cache

from langchain_anthropic import ChatAnthropic

MODEL = "claude-haiku-4-5"  # exact id; never append a date suffix


@lru_cache(maxsize=1)
def _load_dotenv_once() -> None:
    from dotenv import load_dotenv
    load_dotenv()


def make_llm(model: str = MODEL) -> ChatAnthropic:
    _load_dotenv_once()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    headers = {}
    if os.environ.get("ANTHROPIC_WORKSPACE_ID"):
        headers["anthropic-workspace-id"] = os.environ["ANTHROPIC_WORKSPACE_ID"]
    kwargs = dict(model=model, max_tokens=1500, default_headers=headers or None)
    if model.startswith("claude-haiku"):
        kwargs["temperature"] = 0  # temperature is removed on Sonnet 5 - omit there
    return ChatAnthropic(**kwargs)
