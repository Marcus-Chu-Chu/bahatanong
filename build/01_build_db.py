"""Build src/bahatanong_mcp/data/bahatanong.duckdb from BahaMap processed outputs.

Run once (re-runnable; overwrites): ./.venv/Scripts/python build/01_build_db.py
"""
import sys
from pathlib import Path

import duckdb
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bahatanong_mcp.paths import BAHAMAP_PROCESSED, DATA_DIR

OUT = DATA_DIR / "bahatanong.duckdb"

DICTIONARY = [
    ("v_exposure", "pcode", "PSGC barangay code (join key; also keys briefs)"),
    ("v_exposure", "barangay", "Barangay name"),
    ("v_exposure", "city", "City/municipality in Metro Manila (NCR), natural short name (leading 'City of' removed, e.g. 'Marikina')"),
    ("v_exposure", "population", "2020 census population (PSA, reconciled to NCR total 13,484,462)"),
    ("v_exposure", "pct_area_5yr", "Percent (0-100) of land inside the Medium/High flood zone, 5-year scenario (Project NOAH). A scenario probability, NOT flood history"),
    ("v_exposure", "pct_area_25yr", "Percent (0-100) of land inside the Medium/High flood zone, 25-year scenario"),
    ("v_exposure", "pct_area_100yr", "Percent (0-100) of land inside the Medium/High flood zone, 100-year scenario"),
    ("v_exposure", "est_pop_exposed_25yr", "Estimated residents inside the 25-year Medium/High zone"),
    ("v_exposure", "schools_total", "Mapped schools in the barangay (OpenStreetMap)"),
    ("v_exposure", "schools_exposed", "Mapped schools inside the 25-year zone"),
    ("v_exposure", "health_total", "Mapped health facilities in the barangay (OpenStreetMap)"),
    ("v_exposure", "health_exposed", "Mapped health facilities inside the 25-year zone"),
    ("v_exposure", "infra_exposed", "Exposed schools + health facilities combined"),
    ("v_exposure", "exposure_score", "Composite exposure score 0-1: 0.5*population + 0.3*area + 0.2*infrastructure, on the 25-year layer"),
    ("v_exposure", "rank_ncr", "Rank by exposure_score, 1 = most exposed of 1,710 NCR barangays"),
    ("v_city_league", "city", "City/municipality"),
    ("v_city_league", "n_barangays", "Barangays in the city"),
    ("v_city_league", "population", "City 2020 population (sum of barangays)"),
    ("v_city_league", "est_pop_exposed_25yr", "City residents inside the 25-year zone (sum)"),
    ("v_city_league", "exposure_share_pct", "Percent (0-100) of city population inside the 25-year zone"),
    ("v_city_league", "city_rank", "Rank by exposure_share_pct, 1 = highest"),
    ("v_rainfall", "year", "Calendar year (Open-Meteo ERA5 reanalysis, Metro Manila)"),
    ("v_rainfall", "max_daily_mm", "Highest single-day rainfall that year, millimetres"),
    ("v_rainfall", "days_ge_50", "Days with at least 50 mm of rain"),
    ("v_rainfall", "days_ge_100", "Days with at least 100 mm of rain (only metric with a significant trend: +0.07 days/decade, p=.047)"),
    ("v_rainfall", "total_mm", "Total rainfall that year, millimetres"),
]


def main() -> None:
    master = pd.read_parquet(BAHAMAP_PROCESSED / "barangay_master.parquet")
    rain = pd.read_parquet(BAHAMAP_PROCESSED / "rainfall_annual.parquet")
    rain.index.name = rain.index.name or "year"
    rain = rain.reset_index()

    OUT.unlink(missing_ok=True)
    con = duckdb.connect(str(OUT))
    con.register("master_df", master)
    con.register("rain_df", rain)

    con.execute("""
        CREATE TABLE exposure AS
        SELECT pcode, name AS barangay, REGEXP_REPLACE(city, '^City of ', '') AS city, CAST(population AS BIGINT) AS population,
               ROUND(100 * pct_area_mh_5, 1)   AS pct_area_5yr,
               ROUND(100 * pct_area_mh_25, 1)  AS pct_area_25yr,
               ROUND(100 * pct_area_mh_100, 1) AS pct_area_100yr,
               CAST(est_pop_exposed_25 AS BIGINT) AS est_pop_exposed_25yr,
               CAST(schools_total   AS BIGINT) AS schools_total,
               CAST(schools_exposed AS BIGINT) AS schools_exposed,
               CAST(health_total    AS BIGINT) AS health_total,
               CAST(health_exposed  AS BIGINT) AS health_exposed,
               CAST(infra_exposed   AS BIGINT) AS infra_exposed,
               ROUND(score, 4) AS exposure_score,
               CAST(rank_ncr AS BIGINT) AS rank_ncr
        FROM master_df
    """)
    con.execute("CREATE VIEW v_exposure AS SELECT * FROM exposure")
    con.execute("""
        CREATE VIEW v_city_league AS
        WITH agg AS (
            SELECT city, COUNT(*) AS n_barangays, SUM(population) AS population,
                   SUM(est_pop_exposed_25yr) AS est_pop_exposed_25yr,
                   ROUND(100.0 * SUM(est_pop_exposed_25yr) / SUM(population), 1) AS exposure_share_pct
            FROM exposure GROUP BY city
        )
        SELECT *, CAST(RANK() OVER (ORDER BY exposure_share_pct DESC) AS BIGINT) AS city_rank
        FROM agg
    """)
    con.execute("""
        CREATE TABLE rainfall AS
        SELECT CAST(year AS BIGINT) AS year, max_daily_mm,
               CAST(days_ge_50 AS BIGINT) AS days_ge_50,
               CAST(days_ge_100 AS BIGINT) AS days_ge_100, total_mm
        FROM rain_df
    """)
    con.execute("CREATE VIEW v_rainfall AS SELECT * FROM rainfall")

    con.execute("CREATE TABLE data_dictionary (view_name TEXT, column_name TEXT, description TEXT)")
    con.executemany("INSERT INTO data_dictionary VALUES (?, ?, ?)", DICTIONARY)
    con.close()
    print(f"Wrote {OUT} ({OUT.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
