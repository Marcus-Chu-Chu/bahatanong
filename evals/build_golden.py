"""Generate evals/golden.jsonl: 85 computed items + 35 hand-authored items.

Ground truth is computed with hand-written SQL against the same DuckDB the agent
queries - independent of whatever SQL the agent chooses to write.

Run: ./.venv/Scripts/python evals/build_golden.py
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bahatanong_mcp import tools

OUT = Path(__file__).parent / "golden.jsonl"
MANUAL = Path(__file__).parent / "golden_manual.jsonl"
random.seed(20260901)

Q = lambda sql: tools.run_sql(sql)["rows"]  # noqa: E731

# Sample pool: top-60 barangays by exposure keeps questions meaningful and names unambiguous.
POOL = Q("""SELECT barangay, city, pcode, population, est_pop_exposed_25yr,
            pct_area_25yr, schools_exposed, rank_ncr
            FROM v_exposure ORDER BY rank_ncr LIMIT 60""")
CITIES = [r[0] for r in Q("SELECT city FROM v_city_league ORDER BY city_rank")]

LOOKUP_TEMPLATES = [  # (metric_idx in POOL row, en, tl, tolerance)
    (3, "How many residents does {b} in {c} have?",
        "Ilan ang residente ng {b} sa {c}?", 0),
    (4, "How many residents of {b}, {c} are estimated to live inside the 25-year flood zone?",
        "Ilan ang tinatayang residente ng {b}, {c} na nakatira sa loob ng 25-year flood zone?", 0),
    (5, "What percent of {b}, {c}'s land is inside the 25-year Medium/High flood zone?",
        "Ilang porsyento ng lupain ng {b}, {c} ang nasa 25-year Medium/High flood zone?", 1.0),
    (6, "How many schools in {b}, {c} are inside the 25-year flood zone?",
        "Ilang paaralan sa {b}, {c} ang nasa loob ng 25-year flood zone?", 0),
    (7, "What is {b}, {c}'s flood-exposure rank among all NCR barangays?",
        "Pang-ilan ang {b}, {c} sa flood-exposure ranking ng lahat ng barangay sa NCR?", 0),
]


def make_lookup(n=30):
    items, rows = [], random.sample(POOL, n // 5 * 2)
    i = 0
    for metric, en, tl, tol in LOOKUP_TEMPLATES:
        # 6 slots (3 EN + 3 TL) x 5 templates = 30 = n. A 4-slot cycle here would
        # cap out at 20 and never reach n (the len(items)>=n break never fires).
        for lang, tpl in (("en", en), ("tl", tl), ("en", en), ("tl", tl), ("en", en), ("tl", tl)):
            if len(items) >= n:
                break
            r = rows[i % len(rows)]
            i += 1
            items.append({"id": f"look-{len(items)+1:03d}", "type": "lookup", "lang": lang,
                          "question": tpl.format(b=r[0], c=r[1]),
                          "expect": {"value": float(r[metric]), "tolerance": float(tol)}})
    return items[:n]


def make_ranking(n=20):
    items = []
    cities = random.sample(CITIES[:10], 5)
    for city in cities:
        for k, lang, tpl in [
            (3, "en", "What are the top {k} most flood-exposed barangays in {city} by exposure score?"),
            (3, "tl", "Ano ang top {k} barangay sa {city} na pinakamataas ang exposure score?"),
        ]:
            names = [r[0] for r in Q(
                f"SELECT barangay FROM v_exposure WHERE city = '{city}' "
                f"ORDER BY rank_ncr LIMIT {k}")]
            items.append({"id": f"rank-{len(items)+1:03d}", "type": "ranking", "lang": lang,
                          "question": tpl.format(k=k, city=city),
                          "expect": {"ordered_names": names}})
    ncr = [r[0] for r in Q("SELECT barangay FROM v_exposure ORDER BY rank_ncr LIMIT 5")]
    for lang, q in [("en", "Which 5 barangays are the most flood-exposed in all of Metro Manila?"),
                    ("tl", "Aling limang barangay ang pinaka-exposed sa baha sa buong Metro Manila?")]:
        items.append({"id": f"rank-{len(items)+1:03d}", "type": "ranking", "lang": lang,
                      "question": q, "expect": {"ordered_names": ncr}})
    for lang, q in [("en", "Which city ranks highest for share of population in the 25-year flood zone?"),
                    ("tl", "Aling lungsod ang pinakamataas sa bahagi ng populasyon na nasa 25-year flood zone?")]:
        top = Q("SELECT city FROM v_city_league ORDER BY city_rank LIMIT 3")
        items.append({"id": f"rank-{len(items)+1:03d}", "type": "ranking", "lang": lang,
                      "question": q, "expect": {"ordered_names": [top[0][0]]}})
    # pad to n with top-3-per-metric variants - shuffle-and-dedupe instead of
    # random.choice-with-replacement, which let the same city (and therefore the
    # same question text) get drawn more than once.
    pad_cities = list(CITIES[:8])
    random.shuffle(pad_cities)
    for city in pad_cities:
        if len(items) >= n:
            break
        q = f"Top 3 barangays in {city} by estimated exposed residents?"
        if any(i["question"] == q for i in items):
            continue
        names = [r[0] for r in Q(
            f"SELECT barangay FROM v_exposure WHERE city = '{city}' "
            f"ORDER BY est_pop_exposed_25yr DESC LIMIT 3")]
        items.append({"id": f"rank-{len(items)+1:03d}", "type": "ranking", "lang": "en",
                      "question": q, "expect": {"ordered_names": names}})
    return items[:n]


def make_aggregation(n=20):
    items = []
    # 9 cities x 2 langs = 18 = n - 2, leaving exactly room for the 2 singleton
    # items below. 8 cities (16) undershoots: the n-2 break never fires and the
    # loop below only ever appends 2 more, landing on 18 instead of 20.
    for city in random.sample(CITIES, 9):
        v = Q(f"SELECT est_pop_exposed_25yr FROM v_city_league WHERE city = '{city}'")[0][0]
        for lang, tpl in [
            ("en", "How many residents of {city} in total are estimated inside the 25-year flood zone?"),
            ("tl", "Ilan lahat ang tinatayang residente ng {city} na nasa loob ng 25-year flood zone?"),
        ]:
            if len(items) >= n - 2:
                break
            items.append({"id": f"agg-{len(items)+1:03d}", "type": "aggregation", "lang": lang,
                          "question": tpl.format(city=city),
                          "expect": {"value": float(v), "tolerance": 0}})
    total = Q("SELECT SUM(est_pop_exposed_25yr) FROM v_exposure")[0][0]
    items.append({"id": f"agg-{len(items)+1:03d}", "type": "aggregation", "lang": "en",
                  "question": "How many NCR residents in total are estimated to live inside the 25-year flood zone?",
                  "expect": {"value": float(total), "tolerance": 0}})
    nbig = Q("SELECT COUNT(*) FROM v_exposure WHERE pct_area_25yr > 50")[0][0]
    items.append({"id": f"agg-{len(items)+1:03d}", "type": "aggregation", "lang": "en",
                  "question": "How many barangays have more than half their land inside the 25-year flood zone?",
                  "expect": {"value": float(nbig), "tolerance": 0}})
    return items[:n]


def make_comparison(n=15):
    items, pairs = [], []
    metrics = [(4, "estimated exposed residents", "tinatayang residenteng apektado"),
               (6, "schools inside the 25-year flood zone", "paaralang nasa 25-year flood zone"),
               (3, "residents", "residente")]
    while len(pairs) < n:
        a, b = random.sample(POOL, 2)
        if a[1] == b[1] and a[0] == b[0]:
            continue
        m = metrics[len(pairs) % 3][0]  # the metric THIS pair will be scored on
        if a[m] == b[m]:
            continue  # would be an unresolvable tie - resample instead
        pairs.append((a, b))
    for i, (a, b) in enumerate(pairs):
        m, en_name, tl_name = metrics[i % 3]
        winner = a if a[m] >= b[m] else b
        lang = "tl" if i % 3 == 2 else "en"
        q = (f"Which has more {en_name}: {a[0]} ({a[1]}) or {b[0]} ({b[1]})?"
             if lang == "en" else
             f"Alin ang mas maraming {tl_name}: {a[0]} ({a[1]}) o {b[0]} ({b[1]})?")
        items.append({"id": f"comp-{i+1:03d}", "type": "comparison", "lang": lang,
                      "question": q,
                      "expect": {"winner": winner[0], "values": [float(a[m]), float(b[m])]}})
    return items


def main() -> None:
    manual = [json.loads(ln) for ln in MANUAL.read_text(encoding="utf-8").splitlines() if ln.strip()]
    for it in manual:  # resolve PCODE:<Name>,<City> placeholders
        pc = it["expect"].get("pcode", "")
        if pc.startswith("PCODE:"):
            name, city = pc[6:].split(",")
            rows = Q(f"SELECT pcode FROM v_exposure WHERE barangay = '{name}' AND city = '{city}'")
            assert len(rows) == 1, f"{name}, {city}: expected exactly 1 match, got {len(rows)}"
            it["expect"]["pcode"] = rows[0][0]

    items = make_lookup() + make_ranking() + make_aggregation() + make_comparison() + manual

    rank_qs = [i["question"] for i in items if i["type"] == "ranking"]
    assert len(set(rank_qs)) == len(rank_qs), "duplicate ranking questions"
    for i in items:
        if i["type"] == "comparison":
            v = i["expect"]["values"]
            assert v[0] != v[1], f"tie comparison in {i['id']}"

    assert len(items) == 120, f"got {len(items)}"
    OUT.write_text("\n".join(json.dumps(i, ensure_ascii=False) for i in items) + "\n",
                   encoding="utf-8")
    print(f"Wrote {OUT}: {len(items)} items")


if __name__ == "__main__":
    main()
