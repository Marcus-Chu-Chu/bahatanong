import pytest

from bahatanong_mcp.db import get_connection

pytestmark = pytest.mark.skipif(
    False, reason=""
)  # DB is committed; tests always run once Task 2 lands.


def test_v_exposure_shape_and_columns():
    con = get_connection()
    cols = [r[0] for r in con.execute("DESCRIBE v_exposure").fetchall()]
    assert cols == [
        "pcode", "barangay", "city", "population",
        "pct_area_5yr", "pct_area_25yr", "pct_area_100yr",
        "est_pop_exposed_25yr", "schools_total", "schools_exposed",
        "health_total", "health_exposed", "infra_exposed",
        "exposure_score", "rank_ncr",
    ]
    assert con.execute("SELECT COUNT(*) FROM v_exposure").fetchone()[0] == 1710


def test_census_total_reconciles():
    con = get_connection()
    total = con.execute("SELECT SUM(population) FROM v_exposure").fetchone()[0]
    assert total == 13_484_462


def test_city_league_top_is_marikina():
    con = get_connection()
    row = con.execute(
        "SELECT city, exposure_share_pct FROM v_city_league ORDER BY city_rank LIMIT 1"
    ).fetchone()
    assert row[0] == "Marikina"
    assert row[1] == pytest.approx(61.8, abs=0.2)


def test_rainfall_years_and_dictionary():
    con = get_connection()
    n_years = con.execute("SELECT COUNT(*) FROM v_rainfall").fetchone()[0]
    assert n_years == 86
    n_dict = con.execute(
        "SELECT COUNT(*) FROM data_dictionary WHERE description = ''"
    ).fetchone()[0]
    assert n_dict == 0  # every column documented


def test_connection_is_read_only():
    con = get_connection()
    with pytest.raises(Exception):
        con.execute("CREATE TABLE nope (x INT)")
