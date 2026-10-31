"""Load the synthetic Northwind tables into DuckDB. Everything loaded here is invented (see scripts/gen_synthetic.py)."""
import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYN = os.path.join(ROOT, "data", "synthetic")
TABLES = {
    "stg_markets": ("markets.csv", {"fips": str}),
    "stg_spend": ("spend_weekly.csv", {"fips": str}),
    "stg_orders": ("orders.csv", {"fips": str}),
    "stg_touches": ("touches.csv", {}),
    "stg_survey": ("survey.csv", {"fips": str}),
    "stg_experiment": ("experiment_assignment.csv", {"fips": str}),
}


def load_synthetic(con):
    for table, (fname, dtypes) in TABLES.items():
        df = pd.read_csv(os.path.join(SYN, fname), dtype=dtypes)
        con.register(f"_{table}", df)
        con.execute(f"CREATE TABLE {table} AS SELECT * FROM _{table}")
    return con
