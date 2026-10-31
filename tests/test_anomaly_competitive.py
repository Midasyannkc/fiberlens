from fiberlens.anomaly import explain_week, find_anomalies
from fiberlens.competitive import competitive_effect


def test_flat_series_with_one_dip_flags_only_the_dip():
    x = [100, 101, 99, 100, 102, 98, 100, 60, 101, 100, 99, 100]
    assert [a["week"] for a in find_anomalies(x)] == [8]


def test_smooth_seasonal_series_flags_nothing():
    import math
    assert find_anomalies([100 + 10 * math.sin(i / 6) for i in range(52)]) == []


def test_the_planted_outage_week_is_found_and_only_that_week(con):
    sc = con.execute("select orders from mart_weekly_scorecard order by week").df()["orders"].tolist()
    assert [a["week"] for a in find_anomalies(sc)] == [38]


def test_root_cause_names_the_outage_state(con):
    import json
    truth = json.load(open("data/synthetic/truth.json"))
    r = explain_week(con, truth["outage_week"])
    assert r["top_state"] == truth["outage_state"]
    assert r["top_state_share_of_change"] > 0.5


def test_competitor_coverage_depresses_signups_with_an_interval_excluding_zero(con):
    r = competitive_effect(con, n_boot=200)
    assert r["comp_a"] < 0 and r["comp_a_ci"][1] < 0
    assert -0.8 < r["comp_a"] < -0.1
