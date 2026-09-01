from evals.scoring import score_item

R = lambda answer, violations=[]: {"answer": answer, "violations": violations,
                                   "tool_trace": [], "language": "en",
                                   "usage": {"input_tokens": 0, "output_tokens": 0}}


def test_lookup_exact_pass_and_fail():
    item = {"id": "x", "type": "lookup", "lang": "en", "question": "?",
            "expect": {"value": 52961.0, "tolerance": 0}}
    assert score_item(item, R("Malanday has 52,961 residents. Source: v_exposure"))["passed"]
    assert not score_item(item, R("It has 52,000 residents."))["passed"]


def test_lookup_tolerance_window():
    item = {"id": "x", "type": "lookup", "lang": "en", "question": "?",
            "expect": {"value": 62.4, "tolerance": 1.0}}
    assert score_item(item, R("About 62.4% of its land."))["passed"]
    assert score_item(item, R("Roughly 63.0% of its land."))["passed"]
    assert not score_item(item, R("Roughly 65% of its land."))["passed"]


def test_ranking_requires_names_in_order():
    item = {"id": "x", "type": "ranking", "lang": "en", "question": "?",
            "expect": {"ordered_names": ["Rosario", "Malanday", "Santo Niño"]}}
    assert score_item(item, R("1. Rosario 2. Malanday 3. Santo Niño"))["passed"]
    assert not score_item(item, R("1. Malanday 2. Rosario 3. Santo Niño"))["passed"]
    assert not score_item(item, R("Rosario and Santo Niño top the list"))["passed"]


def test_comparison_winner_named():
    item = {"id": "x", "type": "comparison", "lang": "en", "question": "?",
            "expect": {"winner": "Manggahan", "values": [61437.0, 22000.0]}}
    assert score_item(item, R("Manggahan has more, with 61,437 vs 22,000."))["passed"]
    assert not score_item(item, R("They are about equal."))["passed"]


def test_qualitative_needs_retrieved_pcode_and_grounding():
    item = {"id": "x", "type": "qualitative", "lang": "tl", "question": "?",
            "expect": {"pcode": "PH1234"}}
    good = R("Ayon sa brief...")
    good["tool_trace"] = [{"tool": "search_briefs", "args": {}, "result": '{"pcode": "PH1234"}'}]
    assert score_item(item, good)["passed"]
    bad = R("Ayon sa brief...", violations=[999.0])
    bad["tool_trace"] = good["tool_trace"]
    assert not score_item(item, bad)["passed"]


def test_refuse_markers():
    item = {"id": "x", "type": "refuse", "lang": "en", "question": "?",
            "expect": {"markers": ["This is outside what BahaTanong can answer.", "Did you mean"]}}
    assert score_item(item, R("Sorry - This is outside what BahaTanong can answer."))["passed"]
    assert score_item(item, R("Did you mean Talon Dos?"))["passed"]
    assert not score_item(item, R("Here is my forecast: heavy flooding."))["passed"]


def test_rp_label_boilerplate_cannot_satisfy_expected_value():
    item = {"id": "x", "type": "lookup", "lang": "en", "question": "?",
            "expect": {"value": 100.0, "tolerance": 1.0}}
    wrong = R("About 45% lies in the zone; under the 100-year scenario it's ~52%.")
    assert not score_item(item, wrong)["passed"]
    right = R("100.0% of its land lies in the 25-year Medium/High flood zone.")
    assert score_item(item, right)["passed"]


def test_zero_expected_accepts_word_forms():
    item = {"id": "x", "type": "lookup", "lang": "en", "question": "?",
            "expect": {"value": 0.0, "tolerance": 0.0}}
    assert score_item(item, R("There are no schools inside the zone."))["passed"]
    assert score_item(item, R("Walang paaralan sa loob ng flood zone."))["passed"]
    assert not score_item(item, R("There are 3 schools inside."))["passed"]
