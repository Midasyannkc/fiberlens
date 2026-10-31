import pandas as pd


def one(con, sql):
    return con.execute(sql).fetchone()[0]


def test_weekly_scorecard_covers_all_orders(con):
    assert one(con, "select sum(orders) from mart_weekly_scorecard") == one(con, "select count(*) from stg_orders")
    assert one(con, "select count(*) from mart_weekly_scorecard") == 52


def test_spend_in_the_channel_mart_equals_raw_spend(con):
    raw = one(con, "select sum(spend) from stg_spend")
    assert abs(one(con, "select sum(spend) from mart_channel_performance") - raw) < 1


def test_every_channel_has_a_row(con):
    chans = {r[0] for r in con.execute("select channel from mart_channel_performance").fetchall()}
    assert {"search", "social", "email", "direct_mail", "tv", "door_to_door", "organic"} <= chans


def test_competitive_mart_is_one_row_per_market(con):
    assert one(con, "select count(*) from mart_competitive") == one(con, "select count(distinct fips) from mart_competitive") == 420


def test_market_week_grid_is_complete(con):
    assert one(con, "select count(*) from fct_market_week") == 420 * 52
    assert one(con, "select sum(orders) from fct_market_week") == one(con, "select count(*) from stg_orders")


def test_experiment_groups_are_disjoint(con):
    assert one(con, "select count(*) from stg_experiment") == one(con, "select count(distinct fips) from stg_experiment") == 180


def test_attribution_credits_each_order_to_exactly_one_channel(con):
    orders = one(con, "select count(*) from stg_orders")
    assert one(con, "select count(*) from attributed_orders") == orders
    assert one(con, "select count(distinct order_id) from attributed_orders") == orders
    assert one(con, "select sum(signups) from mart_channel_performance") == orders


def test_state_availability_and_usage_are_population_weighted(con):
    expected = con.execute("""
        SELECT st, sum(avail * pop) / sum(CASE WHEN avail IS NOT NULL THEN pop END) AS avail_w,
                   sum(usage * pop) / sum(CASE WHEN usage IS NOT NULL THEN pop END) AS usage_w
        FROM stg_county GROUP BY st""").df().set_index("st")
    got = con.execute("select st, avail_fcc, usage_ms from mart_state_rollup").df().set_index("st")
    for st in expected.index:
        assert abs(got.loc[st, "avail_fcc"] - expected.loc[st, "avail_w"]) < 1e-9, st
        assert abs(got.loc[st, "usage_ms"] - expected.loc[st, "usage_w"]) < 1e-9, st


def test_cost_per_signup_is_total_spend_over_total_signups(con):
    rows = con.execute("select channel, spend, signups, cost_per_signup from mart_channel_performance where spend > 0").fetchall()
    assert len(rows) == 6
    for channel, spend, signups, cps in rows:
        assert abs(cps - spend / signups) < 1e-6, channel


def test_organic_has_no_cost_per_signup(con):
    assert con.execute("select cost_per_signup from mart_channel_performance where channel = 'organic'").fetchone()[0] is None
