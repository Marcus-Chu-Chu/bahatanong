"""FastMCP stdio server exposing the BahaTanong tool layer.

Run: bahatanong-mcp   (or: python -m bahatanong_mcp.server)

SDK note: the installed `mcp` SDK is 2.x, where `mcp.server.fastmcp.FastMCP`
was renamed to `mcp.server.mcpserver.MCPServer` (same decorator/run API,
mechanical rename only - see the ModuleNotFoundError raised by the old
import path for the migration pointer). pyproject.toml's `mcp>=1.2` has no
upper bound, so CI resolves 2.x too; importing the old path would break there
as well, not just locally.
"""
import json

from mcp.server.mcpserver import MCPServer

from . import tools

mcp = MCPServer("bahatanong")


@mcp.tool()
def run_sql(query: str) -> str:
    """Run one read-only SELECT over the BahaMap atlas (views: v_exposure,
    v_city_league, v_rainfall, data_dictionary). Row cap 200."""
    return json.dumps(tools.run_sql(query), ensure_ascii=False)


@mcp.tool()
def get_schema() -> str:
    """List every queryable view, its columns, and their documented meanings."""
    return json.dumps(tools.get_schema(), ensure_ascii=False)


@mcp.tool()
def search_briefs(query: str, lang: str = "en", k: int = 4) -> str:
    """Semantic search over 1,710 bilingual public-safety briefs. lang: 'en' or 'tl'."""
    return json.dumps(tools.search_briefs(query, lang=lang, k=k), ensure_ascii=False)


@mcp.tool()
def get_brief(pcode: str, lang: str = "en") -> str:
    """Fetch one barangay's brief by PSGC pcode. lang: 'en' or 'tl'."""
    return json.dumps(tools.get_brief(pcode, lang=lang), ensure_ascii=False)


@mcp.tool()
def glossary_lookup(term: str = "") -> str:
    """Define a methodology term (exposure_score, return_period, ...). Empty = list all."""
    return json.dumps(tools.glossary_lookup(term), ensure_ascii=False)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
