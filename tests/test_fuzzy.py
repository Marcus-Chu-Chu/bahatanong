from bahatanong_mcp.fuzzy import find_barangay


def test_exact_name_scores_100():
    top = find_barangay("Malanday")[0]
    assert top["barangay"] == "Malanday" and top["match_score"] == 100


def test_misspelling_finds_target():
    assert any(c["barangay"] == "Manggahan" for c in find_barangay("Mangahan"))


def test_city_qualifier_helps():
    top = find_barangay("Rosario Pasig")[0]
    assert (top["barangay"], top["city"]) == ("Rosario", "Pasig")


def test_returns_at_most_limit():
    assert len(find_barangay("San", limit=3)) == 3
