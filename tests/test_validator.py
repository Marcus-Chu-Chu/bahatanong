from agent.validator import extract_numbers, validate_answer


def test_extract_skips_small_years_and_rp_labels():
    nums = extract_numbers("In 2020, about 25% of the 5-year zone held 3 schools and 53,440 people")
    assert 53440.0 in nums and 25.0 not in nums and 2020.0 not in nums and 3.0 not in nums


def test_extract_handles_commas_and_decimals():
    assert extract_numbers("3,733,329 people (27.7%)") == [3733329.0, 27.7]


def test_grounded_answer_passes():
    evidence = ['{"columns": ["population"], "rows": [[52961]]}']
    assert validate_answer("Malanday has 52,961 residents.", evidence) == []


def test_hallucinated_number_is_caught():
    evidence = ['{"rows": [[93]]}']
    assert validate_answer("There are 90 exposed schools.", evidence) == [90.0]


def test_rounded_tagalog_paraphrase_is_caught():
    # BahaMap round-3 lesson: "mahigit 53,000" vs actual 53,440 must fail.
    evidence = ['{"rows": [[53440]]}']
    assert validate_answer("Mahigit 53,000 ang apektado.", evidence) == [53000.0]


def test_name_echo_numbers_are_allowed():
    # BahaMap validator lesson: "Barangay 176" in evidence legitimizes 176 in the answer.
    evidence = ['{"rows": [["Barangay 176", "Caloocan", 246515]]}']
    assert validate_answer("Barangay 176 in Caloocan has 246,515 residents.", evidence) == []


def test_tolerance_half_unit():
    evidence = ['{"rows": [[27.7]]}']
    assert validate_answer("about 27.7% of the population", evidence) == []
    assert validate_answer("about 28.4% of the population", evidence) == [28.4]
