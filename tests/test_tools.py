from bahatanong_mcp import tools


def test_run_sql_happy_path():
    out = tools.run_sql("SELECT barangay, city FROM v_exposure ORDER BY rank_ncr LIMIT 3")
    assert out["row_count"] == 3 and out["columns"] == ["barangay", "city"]


def test_run_sql_guard_error_is_dict_with_hint():
    out = tools.run_sql("DROP TABLE exposure")
    assert "error" in out and "SELECT" in out["hint"]


def test_run_sql_bad_column_returns_error_dict():
    out = tools.run_sql("SELECT no_such_column FROM v_exposure")
    assert "error" in out  # duckdb binder error relayed, not raised


def test_get_schema_lists_all_views():
    out = tools.get_schema()
    assert set(out["views"]) == {"v_exposure", "v_city_league", "v_rainfall"}
    assert all(c["description"] for cols in out["views"].values() for c in cols)


def test_search_briefs_wraps_results():
    out = tools.search_briefs("flooding near the Marikina river", lang="en", k=3)
    assert len(out["results"]) == 3


def test_get_brief_unknown_pcode_suggests():
    out = tools.get_brief("PH99999999", lang="en")
    assert "error" in out and len(out["suggestions"]) == 0  # pcode lookup: no name to fuzz


def test_get_brief_by_pcode_roundtrip():
    pcode = tools.run_sql("SELECT pcode FROM v_exposure WHERE rank_ncr = 1")["rows"][0][0]
    out = tools.get_brief(pcode, lang="tl")
    assert out["lang"] == "tl" and len(out["text"]) > 100


def test_glossary_tool():
    assert tools.glossary_lookup("return_period")["term"] == "return_period"
    assert "terms" in tools.glossary_lookup("")


def test_never_raise_on_malformed_inputs():
    # The trust boundary: garbage input must come back as a dict, never an exception.
    assert "terms" in tools.glossary_lookup(123)  # coerced to "123", no match -> list
    out = tools.get_brief(12345, lang="en")
    assert "error" in out and "12345" in out["error"]
    assert isinstance(tools.search_briefs(None, lang="xx"), dict)


def test_get_schema_never_raises(monkeypatch):
    def boom():
        raise RuntimeError("db gone")
    monkeypatch.setattr(tools, "get_connection", boom)
    assert tools.get_schema() == {"error": "RuntimeError: db gone"}
