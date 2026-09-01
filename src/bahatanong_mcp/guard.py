"""SQL guard: exactly one SELECT over allowlisted relations, capped and timed.

Belt: this parser-level guard. Suspenders: the connection itself is read_only.
"""
import threading

import sqlglot
from sqlglot import exp

ALLOWED_RELATIONS = {"v_exposure", "v_city_league", "v_rainfall", "data_dictionary"}
ROW_CAP = 200


class GuardError(Exception):
    pass


def safe_sql(query: str) -> str:
    try:
        statements = sqlglot.parse(query, read="duckdb")
    except sqlglot.errors.ParseError as e:
        raise GuardError(f"Could not parse SQL: {e}") from e
    if len(statements) != 1 or statements[0] is None:
        raise GuardError("Exactly one SQL statement is allowed.")
    tree = statements[0]
    if not isinstance(tree, exp.Select) and not (
        isinstance(tree, exp.Query) and isinstance(tree.this, exp.Select)
    ):
        raise GuardError("Only SELECT statements are allowed.")

    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    for table in tree.find_all(exp.Table):
        name = table.name.lower()
        if table.db or table.catalog:
            raise GuardError(f"Qualified relation not allowed: {table.sql()}")
        if name not in ALLOWED_RELATIONS and name not in cte_names:
            raise GuardError(
                f"Relation '{name}' is not allowed. Allowed: {sorted(ALLOWED_RELATIONS)}"
            )
    for func in tree.find_all(exp.Anonymous):
        raise GuardError(f"Function '{func.name}' is not allowed.")
    if list(tree.find_all(exp.ReadCSV)):
        raise GuardError("File-reading functions are not allowed.")

    if tree.args.get("limit") is None:
        tree = tree.limit(ROW_CAP)
    return tree.sql(dialect="duckdb")


def run_guarded(con, query: str, timeout_s: float = 5.0):
    q = safe_sql(query)
    timer = threading.Timer(timeout_s, con.interrupt)
    timer.start()
    try:
        cur = con.execute(q)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    finally:
        timer.cancel()
    return cols, rows
