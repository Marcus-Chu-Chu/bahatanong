"""BahaTanong LangGraph agent: agent -> tools loop -> grounding validate -> respond.

run_agent() is the single public entry point used by the Streamlit app, the eval
harness, and the showcase builder.
"""
import json
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from bahatanong_mcp import tools as T

from .client import MODEL, make_llm
from .language import detect
from .validator import validate_answer

MAX_RETRIES = 1
LANG_NAMES = {"en": "English", "tl": "Tagalog"}

CAVEAT = {
    "en": "\n\n(Note: I could not verify some figures against the atlas, so I have removed them.)",
    "tl": "\n\n(Paunawa: may mga bilang na hindi ko na-verify sa atlas, kaya inalis ko ang mga ito.)",
}


@tool
def run_sql(query: str) -> str:
    """Run one read-only SELECT over v_exposure, v_city_league, v_rainfall, or
    data_dictionary. Row cap 200. Call get_schema first if unsure of columns."""
    return json.dumps(T.run_sql(query), ensure_ascii=False)


@tool
def get_schema() -> str:
    """List every queryable view, its columns, and documented meanings."""
    return json.dumps(T.get_schema(), ensure_ascii=False)


@tool
def search_briefs(query: str, lang: str = "en", k: int = 4) -> str:
    """Semantic search over 1,710 bilingual public-safety briefs ('en' or 'tl')."""
    return json.dumps(T.search_briefs(query, lang=lang, k=k), ensure_ascii=False)


@tool
def get_brief(pcode: str, lang: str = "en") -> str:
    """Fetch one barangay's public-safety brief by PSGC pcode."""
    return json.dumps(T.get_brief(pcode, lang=lang), ensure_ascii=False)


@tool
def glossary_lookup(term: str = "") -> str:
    """Define a methodology term (exposure_score, return_period, ...). Empty = list."""
    return json.dumps(T.glossary_lookup(term), ensure_ascii=False)


TOOLS = [run_sql, get_schema, search_briefs, get_brief, glossary_lookup]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    retries: int
    violations: list


def load_prompt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def build_graph(llm, system_prompt: str, language: str):
    llm_tools = llm.bind_tools(TOOLS)
    system = SystemMessage(system_prompt.replace("{language_name}", LANG_NAMES[language]))

    def agent_node(state: AgentState):
        return {"messages": [llm_tools.invoke([system] + state["messages"])]}

    def route_after_agent(state: AgentState):
        last = state["messages"][-1]
        return "tools" if getattr(last, "tool_calls", None) else "validate"

    def validate_node(state: AgentState):
        answer = state["messages"][-1].content
        evidence = [m.content for m in state["messages"] if m.type == "tool"]
        violations = validate_answer(answer if isinstance(answer, str) else str(answer), evidence)
        if violations and state["retries"] < MAX_RETRIES:
            feedback = HumanMessage(
                "[VALIDATOR] These numbers do not appear in any tool result this turn: "
                f"{violations}. Re-answer using ONLY numbers exactly as returned by the "
                "tools (re-query if needed). Do not apologize; just answer correctly."
            )
            return {"messages": [feedback], "retries": state["retries"] + 1,
                    "violations": violations}
        if violations:  # second failure: strip to caveat instead of shipping bad numbers
            # Use the QUESTION's language (closure param) - detecting from the bad
            # answer could disagree with the "language" field run_agent reports.
            fixed = AIMessage(
                ("I can only share what I could verify against the atlas."
                 if language == "en"
                 else "Ang maibabahagi ko lang ay ang na-verify ko sa atlas.")
                + CAVEAT[language]
            )
            return {"messages": [fixed], "violations": violations}
        return {"violations": []}

    def route_after_validate(state: AgentState):
        if state["violations"] and state["retries"] <= MAX_RETRIES and \
           state["messages"][-1].type == "human":
            return "agent"
        return END

    g = StateGraph(AgentState)
    g.add_node("agent", agent_node)
    g.add_node("tools", ToolNode(TOOLS))
    g.add_node("validate", validate_node)
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", route_after_agent, {"tools": "tools", "validate": "validate"})
    g.add_edge("tools", "agent")
    g.add_conditional_edges("validate", route_after_validate, {"agent": "agent", END: END})
    return g.compile()


def run_agent(question: str, prompt_path: str = "agent/prompts/v1.md",
              model: str = MODEL) -> dict:
    lang = detect(question)
    graph = build_graph(make_llm(model), load_prompt(prompt_path), lang)
    state = graph.invoke(
        {"messages": [HumanMessage(question)], "retries": 0, "violations": []},
        config={"recursion_limit": 25},
    )
    trace, by_id, usage = [], {}, {"input_tokens": 0, "output_tokens": 0}
    for m in state["messages"]:
        if m.type == "ai":
            meta = getattr(m, "usage_metadata", None) or {}
            usage["input_tokens"] += meta.get("input_tokens", 0)
            usage["output_tokens"] += meta.get("output_tokens", 0)
            for tc in getattr(m, "tool_calls", []) or []:
                entry = {"tool": tc["name"], "args": tc["args"], "result": None}
                trace.append(entry)
                by_id[tc["id"]] = entry
        elif m.type == "tool":
            # Match by tool_call_id - positional fill misattributes results when
            # one AI turn makes parallel tool calls (ToolNode emits in call order,
            # but a reversed scan pairs them backwards).
            entry = by_id.get(getattr(m, "tool_call_id", None))
            if entry is not None:
                content = m.content if isinstance(m.content, str) else str(m.content)
                # 8000, not 2000: the qualitative scorer checks pcode presence in
                # this trace, and a k=10 search_briefs result runs ~6.5k chars -
                # a 2000 cap silently mis-scored grounded answers (T12 amendment).
                entry["result"] = content[:8000]
    answer = state["messages"][-1].content
    return {"answer": answer if isinstance(answer, str) else str(answer),
            "language": lang, "tool_trace": trace,
            "violations": state["violations"], "retried": state["retries"] > 0,
            "usage": usage}
