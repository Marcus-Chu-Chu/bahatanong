from bahatanong_mcp.search import get_brief_text, search_briefs


def test_search_en_returns_k_results_with_metadata():
    hits = search_briefs("flood exposure situation in Marikina", lang="en", k=4)
    assert len(hits) == 4
    for h in hits:
        assert set(h) == {"pcode", "barangay", "city", "lang", "text", "distance"}
        assert h["lang"] == "en"
    assert any(h["city"] == "Marikina" for h in hits)


def test_search_tl_routes_to_tagalog_collection():
    # k=10 + city-level assertion: HNSW approximate search is nondeterministic at
    # tight rank boundaries (verified flaky at k=4), so assert with a wide margin.
    hits = search_briefs("baha sa Rosario Pasig", lang="tl", k=10)
    assert all(h["lang"] == "tl" for h in hits)
    assert any(h["city"] == "Pasig" for h in hits)


def test_get_brief_text_roundtrip():
    some = search_briefs("Malanday", lang="en", k=1)[0]
    brief = get_brief_text(some["pcode"], "tl")
    assert brief is not None and brief["lang"] == "tl" and len(brief["text"]) > 100


def test_unknown_pcode_returns_none():
    assert get_brief_text("PH00000000", "en") is None
