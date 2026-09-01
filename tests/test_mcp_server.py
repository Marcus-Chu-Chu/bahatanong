import json
import shutil
import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = [sys.executable, "-m", "bahatanong_mcp.server"]


async def _session():
    params = StdioServerParameters(command=SERVER[0], args=SERVER[1:])
    return stdio_client(params)


async def test_lists_five_tools():
    async with (await _session()) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()
            tools = {t.name for t in (await s.list_tools()).tools}
            assert tools == {"run_sql", "get_schema", "search_briefs", "get_brief", "glossary_lookup"}


async def test_run_sql_roundtrip():
    async with (await _session()) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()
            res = await s.call_tool("run_sql", {"query": "SELECT COUNT(*) AS n FROM v_exposure"})
            payload = json.loads(res.content[0].text)
            assert payload["rows"][0][0] == 1710


async def test_guard_error_surfaces_as_payload_not_crash():
    async with (await _session()) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()
            res = await s.call_tool("run_sql", {"query": "DROP TABLE exposure"})
            assert "error" in json.loads(res.content[0].text)
