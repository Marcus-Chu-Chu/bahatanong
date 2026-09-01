import json

from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage

from agent.graph import build_graph, load_prompt


class BindableFake(FakeMessagesListChatModel):
    def bind_tools(self, tools, **kwargs):
        return self


def test_grounded_flow_ends_clean():
    # Turn 1: model "calls" run_sql; turn 2: grounded answer.
    fake = BindableFake(responses=[
        AIMessage(content="", tool_calls=[{
            "name": "run_sql", "id": "t1",
            "args": {"query": "SELECT barangay, population FROM v_exposure WHERE rank_ncr = 1"},
        }]),
        AIMessage(content="PLACEHOLDER - filled below"),
    ])
    graph = build_graph(fake, load_prompt("agent/prompts/v1.md"), language="en")
    # First run once to learn the real population, then rebuild with a grounded answer.
    state = graph.invoke({"messages": [("user", "Most exposed barangay?")], "retries": 0})
    evidence = [m.content for m in state["messages"] if m.type == "tool"]
    pop = json.loads(evidence[0])["rows"][0][1]

    fake2 = BindableFake(responses=[
        AIMessage(content="", tool_calls=[{
            "name": "run_sql", "id": "t1",
            "args": {"query": "SELECT barangay, population FROM v_exposure WHERE rank_ncr = 1"},
        }]),
        AIMessage(content=f"The most exposed barangay has {pop:,} residents. Source: v_exposure"),
    ])
    graph2 = build_graph(fake2, load_prompt("agent/prompts/v1.md"), language="en")
    state2 = graph2.invoke({"messages": [("user", "Most exposed barangay?")], "retries": 0})
    assert state2["violations"] == []
    assert state2["retries"] == 0


def test_ungrounded_answer_triggers_exactly_one_retry():
    bad = AIMessage(content="It has 999,999 residents. Source: v_exposure")
    fake = BindableFake(responses=[bad, bad])  # keeps hallucinating on retry
    graph = build_graph(fake, load_prompt("agent/prompts/v1.md"), language="en")
    state = graph.invoke({"messages": [("user", "Most exposed barangay?")], "retries": 0})
    assert state["retries"] == 1
    assert state["violations"] == [999999.0]
    # Final answer must carry the could-not-verify caveat, not the raw hallucination.
    assert "could not verify" in state["messages"][-1].content.lower()
