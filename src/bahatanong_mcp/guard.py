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

    # Reject write/DDL nodes ANYWHERE in the tree (covers DML-bodied CTEs and
    # subqueries, e.g. WITH x AS (DELETE ... RETURNING *) SELECT * FROM x).
    for bad in tree.find_all(exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter):
        raise GuardError(f"Write/DDL operations are not allowed: {bad.key}")

    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    for table in tree.find_all(exp.Table):
        name = table.name.lower()
        if table.db or table.catalog:
            raise GuardError(f"Qualified relation not allowed: {table.sql()}")
        if name not in ALLOWED_RELATIONS and name not in cte_names:
            raise GuardError(
                f"Relation '{name}' is not allowed. Allowed: {sorted(ALLOWED_RELATIONS)}"
            )
    # Named generator/reader constructs are rejected explicitly: they parse as
    # dedicated node types (not Anonymous) and are resource-exhaustion vectors
    # with no legitimate use over this schema. Top-level set operations
    # (UNION/EXCEPT/INTERSECT) are ALLOWED by design - they are read-only Query
    # nodes and the relation/DML checks above walk every branch.
    for func in tree.find_all(exp.Anonymous, exp.GenerateSeries, exp.Unnest):
        raise GuardError(f"Function '{func.key}' is not allowed.")

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
