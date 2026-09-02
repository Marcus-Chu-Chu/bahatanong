"""BahaTanong - hybrid demo: precomputed Showcase (free, instant) + capped Live agent."""
import datetime as dt
import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.limits import DAILY_CAP, check  # noqa: E402

st.set_page_config(page_title="BahaTanong", layout="centered")
SHOWCASE = json.loads((ROOT / "app" / "showcase.json").read_text(encoding="utf-8"))


def _secret(name: str, default: str = "") -> str:
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


@st.cache_resource
def _daily_counter() -> dict:
    return {"date": None, "count": 0}


def _today_count() -> int:
    c = _daily_counter()
    today = dt.date.today().isoformat()
    if c["date"] != today:
        c["date"], c["count"] = today, 0
    return c["count"]


st.title("BahaTanong")
st.caption(
    "*Baha* (flood) + *tanong* (question): ask the "
    "[BahaMap](https://bahamap-ftq9fcw37j2maqlib3msmo.streamlit.app) Metro Manila "
    "flood atlas anything, in English or Tagalog. Every number is validated against "
    "the data before you see it. "
    "[GitHub](https://github.com/Marcus-Chu-Chu/bahatanong)"
)

tab_show, tab_live = st.tabs(["Showcase (instant)", "Live agent"])


def _render_showcase(item: dict) -> None:
    with st.chat_message("user"):
        st.write(item["question"])
    with st.chat_message("assistant"):
        st.write(item["answer"])
        with st.expander("See the tools it called"):
            for t in item["tool_trace"]:
                st.code(f"{t['tool']}({json.dumps(t['args'], ensure_ascii=False)})", language="text")
                st.text((t["result"] or "")[:800])


with tab_show:
    st.write("Twelve real agent runs, replayed with their genuine tool traces. Browsing them costs nothing.")
    for lang, heading in (("en", "English"), ("tl", "Tagalog")):
        items = [i for i in SHOWCASE["items"] if i["lang"] == lang]
        st.subheader(heading)
        pick = st.selectbox(
            f"Pick a question ({heading})", range(len(items)),
            format_func=lambda idx, items=items: items[idx]["question"],
            key=f"showcase_{lang}",
        )
        _render_showcase(items[pick])
    st.caption(f"Generated {SHOWCASE['generated_at'][:10]} · {SHOWCASE['model']} · "
               f"prompt {SHOWCASE['prompt']}")

with tab_live:
    kill = _secret("BAHATANONG_KILL_SWITCH")
    if kill:
        st.info("The live agent is paused right now - the Showcase tab has 12 real runs.")
    elif not _secret("ANTHROPIC_API_KEY"):
        st.warning("No API key configured; live mode is off in this deployment.")
    else:
        st.session_state.setdefault("live_count", 0)
        st.session_state.setdefault("history", [])
        for role, text in st.session_state.history:
            with st.chat_message(role):
                st.write(text)
        q = st.chat_input("Ask about Metro Manila flood exposure (EN or TL)...")
        if q:
            ok, msg = check(st.session_state.live_count, _today_count())
            if not ok:
                st.warning(msg)
            else:
                import os
                os.environ.setdefault("ANTHROPIC_API_KEY", _secret("ANTHROPIC_API_KEY"))
                if _secret("ANTHROPIC_WORKSPACE_ID"):
                    os.environ.setdefault("ANTHROPIC_WORKSPACE_ID", _secret("ANTHROPIC_WORKSPACE_ID"))
                from agent.graph import run_agent  # deferred: first call loads the embedder lazily
                with st.chat_message("user"):
                    st.write(q)
                with st.chat_message("assistant"), st.spinner("Querying the atlas..."):
                    try:
                        r = run_agent(q)
                        st.write(r["answer"])
                        with st.expander("Tool trace"):
                            for t in r["tool_trace"]:
                                st.code(f"{t['tool']}({json.dumps(t['args'], ensure_ascii=False)})",
                                        language="text")
                    except Exception:
                        st.error("Something went wrong talking to the agent - try again, "
                                 "or use the Showcase tab.")
                        r = None
                if r:
                    st.session_state.history += [("user", q), ("assistant", r["answer"])]
                    st.session_state.live_count += 1
                    _daily_counter()["count"] = _today_count() + 1
        st.caption(f"5 questions per visitor · {DAILY_CAP} per day across all visitors · "
                   "answers are validated against the atlas before display")
