from bahatanong_mcp.glossary import lookup


def test_exact_term():
    out = lookup("exposure_score")
    assert out["term"] == "exposure_score" and "0.5" in out["definition"]


def test_loose_term_matches():
    assert lookup("return periods")["term"] == "return_period"
    assert lookup("Exposure Score")["term"] == "exposure_score"


def test_no_term_lists_all():
    out = lookup(None)
    assert "exposure_score" in out["terms"] and len(out["terms"]) >= 7


def test_unknown_term_lists_all():
    assert "terms" in lookup("blockchain")


def test_whitespace_query_lists_all():
    assert "terms" in lookup("   ")
