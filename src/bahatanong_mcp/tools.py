"""The shared tool layer. Three consumers call these exact functions:
the FastMCP server (server.py), the LangGraph agent (agent/graph.py), and evals.

Contract: always return a JSON-serializable dict; never raise.
"""
from . import fuzzy, glossary, search
from .db import get_connection
from .guard import GuardError, run_guarded

_GUARD_HINT = (
    "Only a single SELECT statement over v_exposure, v_city_league, v_rainfall, "
    "or data_dictionary is allowed (row cap 200). Rewrite the query."
)


def run_sql(query: str) -> dict:
    try:
        # Per-call cursor: DuckDB connections aren't safe for concurrent execute,
        # and the 5s interrupt must target only this query, not other sessions'.
        cols, rows = run_guarded(get_connection().cursor(), query)
        return {"columns": cols, "rows": [list(r) for r in rows], "row_count": len(rows)}
    except GuardError as e:
        return {"error": f"Blocked by SQL guard: {e}", "hint": _GUARD_HINT}
    except Exception as e:  # duckdb binder/exec errors -> repairable feedback
        return {"error": f"{type(e).__name__}: {e}", "hint": _GUARD_HINT}


def get_schema() -> dict:
    try:
        rows = get_connection().cursor().execute(
            "SELECT view_name, column_name, description FROM data_dictionary ORDER BY view_name"
        ).fetchall()
        views: dict[str, list] = {}
        for view, col, desc in rows:
            views.setdefault(view, []).append({"column": col, "description": desc})
        return {
            "views": views,
            "notes": "1,710 NCR barangays; percentages are 0-100; flood zones are Project "
                     "NOAH scenarios, not history. Use glossary_lookup for definitions.",
        }
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def search_briefs(query: str, lang: str = "en", k: int = 4) -> dict:
    try:
        return {"results": search.search_briefs(query, lang=lang, k=int(k))}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def get_brief(pcode: str, lang: str = "en") -> dict:
    try:
        pcode = str(pcode)  # trust boundary: callers may hand us JSON numbers
        brief = search.get_brief_text(pcode, lang)
        if brief is not None:
            return brief
        return {"error": f"No brief for pcode {pcode!r}.",
                "suggestions": fuzzy.find_barangay(pcode) if not pcode.upper().startswith("PH") else []}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}", "suggestions": []}


def glossary_lookup(term: str = "") -> dict:
    try:
        term = str(term) if term is not None else ""
        return glossary.lookup(term or None)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
