"""Read-only DuckDB connection to the packaged atlas database."""
from functools import lru_cache

import duckdb

from .paths import DATA_DIR

DB_PATH = DATA_DIR / "bahatanong.duckdb"


@lru_cache(maxsize=1)
def get_connection() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    # bounds generator/UNNEST-style blowups. MiB (binary), not MB (decimal): DuckDB
    # normalizes memory_limit internally and reports it back via current_setting()
    # in MiB, so a decimal '512MB' round-trips as '488.2 MiB' with no '512' in it.
    con.execute("SET memory_limit='512MiB'")
    return con
