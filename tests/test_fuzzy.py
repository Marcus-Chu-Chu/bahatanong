from bahatanong_mcp.fuzzy import find_barangay


def test_exact_name_scores_100():
    top = find_barangay("Malanday")[0]
    assert top["barangay"] == "Malanday" and top["match_score"] == 100


def test_misspelling_finds_target():
    assert any(c["barangay"] == "Manggahan" for c in find_barangay("Mangahan"))


def test_city_qualifier_disambiguates_duplicates():
    # "San Roque" exists in 4 cities - the qualifier must pick the right one.
    top = find_barangay("San Roque Navotas")[0]
    assert (top["barangay"], top["city"]) == ("San Roque", "Navotas")


def test_partial_name_beats_city_token():
    # "San" must surface San-named barangays, not all of San Juan city.
    top = find_barangay("San", limit=5)
    assert all(c["barangay"].startswith("San") for c in top[:3])


def test_returns_at_most_limit():
    assert len(find_barangay("San", limit=3)) == 3
