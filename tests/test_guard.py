import pytest

from bahatanong_mcp.db import get_connection
from bahatanong_mcp.guard import GuardError, run_guarded, safe_sql


def test_plain_select_gets_limit_appended():
    q = safe_sql("SELECT city FROM v_city_league ORDER BY city_rank")
    assert q.rstrip().upper().endswith("LIMIT 200")


def test_existing_limit_is_kept():
    q = safe_sql("SELECT barangay FROM v_exposure ORDER BY rank_ncr LIMIT 5")
    assert q.upper().count("LIMIT") == 1


@pytest.mark.parametrize("bad", [
    "DROP TABLE exposure",
    "INSERT INTO exposure VALUES (1)",
    "UPDATE exposure SET population = 0",
    "DELETE FROM exposure",
    "CREATE TABLE t (x INT)",
    "ATTACH 'other.duckdb' AS o",
    "PRAGMA database_list",
    "SELECT 1; SELECT 2",                       # multi-statement
    "SELECT * FROM information_schema.tables",  # off-allowlist relation
    "SELECT * FROM read_csv_auto('x.csv')",     # table function
    "COPY exposure TO 'out.csv'",
    "WITH x AS (DELETE FROM v_exposure RETURNING *) SELECT * FROM x",  # DML-bodied CTE
    "SELECT range(100000000)",                  # generator function (resource exhaustion)
    "SELECT * FROM UNNEST(generate_series(1, 100000000)) AS t(x)",  # UNNEST generator
    "not sql at all",
])
def test_rejected_statements(bad):
    with pytest.raises(GuardError):
        safe_sql(bad)


def test_union_cte_is_fine():
    # The DML rejection must not over-block legitimate set-operation CTEs.
    q = safe_sql("WITH x AS (SELECT 'a' AS c UNION ALL SELECT 'b') SELECT c FROM x")
    assert "UNION" in q.upper()


def test_top_level_set_operations_allowed():
    # Set operations over allowed views are read-only and explicitly permitted.
    q = safe_sql("SELECT barangay FROM v_exposure UNION SELECT city FROM v_city_league")
    assert "UNION" in q.upper() and q.rstrip().upper().endswith("LIMIT 200")


def test_cte_over_allowed_views_is_fine():
    q = safe_sql(
        "WITH top AS (SELECT * FROM v_exposure ORDER BY rank_ncr LIMIT 10) "
        "SELECT city, COUNT(*) FROM top GROUP BY city"
    )
    assert "WITH" in q.upper()


def test_run_guarded_returns_columns_and_rows():
    cols, rows = run_guarded(get_connection(), "SELECT barangay, city FROM v_exposure WHERE rank_ncr = 1")
    assert cols == ["barangay", "city"]
    assert len(rows) == 1


def test_run_guarded_row_cap():
    _, rows = run_guarded(get_connection(), "SELECT pcode FROM v_exposure")
    assert len(rows) == 200
