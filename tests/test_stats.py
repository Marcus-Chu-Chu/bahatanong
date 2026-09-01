import pytest

from evals.stats import mcnemar_exact


def test_known_exact_value():
    # 10 discordant pairs, 2 vs 8 -> two-sided exact p = 0.109375
    a = [True] * 2 + [False] * 8 + [True] * 20
    b = [False] * 2 + [True] * 8 + [True] * 20
    out = mcnemar_exact(a, b)
    assert (out["b"], out["c"]) == (2, 8)
    assert out["p_value"] == pytest.approx(0.109375, abs=1e-6)


def test_no_discordance_p_is_1():
    a = b = [True, False, True]
    assert mcnemar_exact(a, b)["p_value"] == 1.0


def test_delta_pp():
    a = [True] * 50 + [False] * 50
    b = [True] * 60 + [False] * 40
    assert mcnemar_exact(a, b)["delta_pp"] == pytest.approx(10.0)


def test_empty_vectors_raise():
    with pytest.raises(ValueError):
        mcnemar_exact([], [])
