"""Load the four real files into DuckDB staging tables."""
import os

import duckdb
import pandas as pd

from fiberlens.keys import to_fips

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")


def read_ms_county():
    df = pd.read_csv(os.path.join(RAW, "ms_county.csv"))
    df.columns = ["st", "county_id", "county_name", "avail", "usage"]
    # The source uses "-" for missing values; keep them as NULL instead of dropping the county.
    df["avail"] = pd.to_numeric(df["avail"], errors="coerce")
    df["usage"] = pd.to_numeric(df["usage"], errors="coerce")
    df["fips"] = df["county_id"].map(to_fips)
    return df


def read_ms_zip():
    df = pd.read_csv(os.path.join(RAW, "ms_zip.csv"))
    df.columns = ["st", "county_name", "county_id", "zip", "usage", "mae", "ci95", "msd"]
    df["fips"] = df["county_id"].map(to_fips)
    df["zip"] = df["zip"].astype(str).str.zfill(5)
    return df


def read_population():
    df = pd.read_csv(os.path.join(RAW, "jhu_uid.csv"), dtype={"FIPS": float})
    df = df[(df["Country_Region"] == "US") & df["FIPS"].notna() & (df["Population"] > 0) & (df["FIPS"] < 80000)]
    out = pd.DataFrame({"fips": df["FIPS"].map(to_fips), "pop": df["Population"].astype(int),
                        "jhu_name": df["Admin2"], "jhu_state": df["Province_State"]})
    return out.drop_duplicates("fips")


def read_unemployment():
    df = pd.read_csv(os.path.join(RAW, "bls_unemp_2016.csv"), dtype={"fips": str})
    return df.rename(columns={"unemp": "unemp_2016"})


def connect():
    con = duckdb.connect(":memory:")
    for name, df in {"raw_ms_county": read_ms_county(), "raw_ms_zip": read_ms_zip(),
                     "raw_population": read_population(), "raw_unemployment": read_unemployment()}.items():
        con.register(f"_{name}", df)
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM _{name}")
    return con
