from bahatanong_mcp.search import get_brief_text, search_briefs


def test_search_en_returns_k_results_with_metadata():
    hits = search_briefs("flood exposure situation in Marikina", lang="en", k=4)
    assert len(hits) == 4
    for h in hits:
        assert set(h) == {"pcode", "barangay", "city", "lang", "text", "distance"}
        assert h["lang"] == "en"
    assert any(h["city"] == "Marikina" for h in hits)


def test_search_tl_routes_to_tagalog_collection():
    hits = search_briefs("baha sa Rosario Pasig", lang="tl", k=4)
    assert all(h["lang"] == "tl" for h in hits)
    # Relaxed per task-3-brief.md Step 5: multilingual MiniLM does not surface
    # Rosario itself in the top-4 for this short query (verified present and
    # correctly indexed; see task-3-report.md for the inspected top-4 hits).
    # A Pasig barangay does appear, so the retrieval set is sane.
    assert any(h["city"] == "Pasig" for h in hits)


def test_get_brief_text_roundtrip():
    some = search_briefs("Malanday", lang="en", k=1)[0]
    brief = get_brief_text(some["pcode"], "tl")
    assert brief is not None and brief["lang"] == "tl" and len(brief["text"]) > 100


def test_unknown_pcode_returns_none():
    assert get_brief_text("PH00000000", "en") is None
