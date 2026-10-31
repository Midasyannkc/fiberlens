import hashlib
import json
import os
import subprocess
import sys

import pandas as pd

from tests.conftest import ROOT, SYN


def sha(name):
    return hashlib.sha256(open(os.path.join(SYN, name), "rb").read()).hexdigest()


def test_generator_is_deterministic():
    before = {n: sha(n) for n in ["orders.csv", "touches.csv", "survey.csv"]}
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "gen_synthetic.py")], check=True, capture_output=True)
    assert before == {n: sha(n) for n in before}


def test_truth_file_records_what_the_analysis_must_recover():
    t = json.load(open(os.path.join(SYN, "truth.json")))
    assert abs(t["mail_lift_true"] - 0.2 * (1 - 2.718281828 ** -1)) < 1e-4
    assert t["outage_week"] == 38 and t["markets"] == 420
    assert t["treated_mean_avail"] > t["holdout_mean_avail"] + 0.05  # selection bias is built in on purpose


def test_every_touch_belongs_to_an_order_and_precedes_it():
    o = pd.read_csv(os.path.join(SYN, "orders.csv"), parse_dates=["order_date"])
    t = pd.read_csv(os.path.join(SYN, "touches.csv"), parse_dates=["touch_date"])
    j = t.merge(o, on="order_id", how="left")
    assert j["order_date"].notna().all()
    assert (j["touch_date"] < j["order_date"]).all()


def test_markets_are_real_counties_with_competitor_shares_in_range():
    m = pd.read_csv(os.path.join(SYN, "markets.csv"), dtype={"fips": str})
    assert m["fips"].is_unique and len(m) == 420
    assert m[["comp_a", "comp_b"]].min().min() >= 0 and m[["comp_a", "comp_b"]].max().max() <= 1


def test_mail_spend_only_in_treated_markets_during_the_flight():
    s = pd.read_csv(os.path.join(SYN, "spend_weekly.csv"), dtype={"fips": str})
    e = pd.read_csv(os.path.join(SYN, "experiment_assignment.csv"), dtype={"fips": str})
    mail = s[s["channel"] == "direct_mail"]
    assert set(mail["fips"]) <= set(e.loc[e.grp == "treated", "fips"])
    assert mail["week"].between(20, 31).all()
