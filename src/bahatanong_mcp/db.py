"""Read-only DuckDB connection to the packaged atlas database."""
from functools import lru_cache

import duckdb

from .paths import DATA_DIR

DB_PATH = DATA_DIR / "bahatanong.duckdb"


@lru_cache(maxsize=1)
def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(DB_PATH), read_only=True)
