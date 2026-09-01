"""Exact McNemar test for paired pass/fail vectors (two prompt variants)."""
from scipy.stats import binomtest


def mcnemar_exact(pass_a: list[bool], pass_b: list[bool]) -> dict:
    if not pass_a:
        raise ValueError("empty pass vectors")
    assert len(pass_a) == len(pass_b)
    b = sum(1 for x, y in zip(pass_a, pass_b) if x and not y)   # A-only
    c = sum(1 for x, y in zip(pass_a, pass_b) if y and not x)   # B-only
    p = 1.0 if (b + c) == 0 else binomtest(min(b, c), b + c, 0.5).pvalue
    delta = 100.0 * (sum(pass_b) - sum(pass_a)) / len(pass_a)
    return {"b": b, "c": c, "p_value": float(p), "delta_pp": delta}
