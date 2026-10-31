def one(con, sql):
    return con.execute(sql).fetchone()[0]


def test_county_grain_is_one_row_per_county(con):
    assert one(con, "select count(*) from stg_county") == one(con, "select count(distinct fips) from stg_county") == 3142


def test_total_population_is_us_scale(con):
    assert 3.2e8 < one(con, "select sum(pop) from stg_county") < 3.4e8


def test_opportunity_score_is_bounded_and_tiered(con):
    lo, hi = con.execute("select min(score), max(score) from mart_opportunity_score").fetchone()
    assert 0 <= lo and hi <= 1
    assert {r[0] for r in con.execute("select distinct tier from mart_opportunity_score").fetchall()} <= {"A", "B", "C"}


def test_score_rises_with_the_unrealized_demand_gap(con):
    df = con.execute("select score, gap_pop from mart_opportunity_score").df()
    assert df["score"].corr(df["gap_pop"], method="spearman") > 0.6


def test_counties_missing_availability_are_excluded_not_scored(con):
    assert one(con, "select count(*) from mart_opportunity_score where avail is null or usage is null") == 0


def test_market_opportunity_mart_has_one_row_per_county_and_keeps_population(con):
    assert one(con, "select count(*) from mart_market_opportunity") == one(con, "select count(*) from stg_county")
    assert one(con, "select count(distinct fips) from mart_market_opportunity") == one(con, "select count(*) from mart_market_opportunity")
    assert one(con, "select sum(pop) from mart_market_opportunity") == one(con, "select sum(pop) from stg_county")
