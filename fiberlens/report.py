"""Run every analysis once and return one dict. python -m fiberlens writes it to out/report.json and docs/REPORT.md."""
import json

from fiberlens import anomaly, competitive, lift, survey
from fiberlens.load import ROOT
import os


def build_report(con):
    q = lambda sql: con.execute(sql).df()
    one = lambda sql: con.execute(sql).fetchone()[0]
    scorecard = q("select * from mart_weekly_scorecard order by week")
    anomalies = anomaly.find_anomalies(scorecard["orders"].tolist())
    chan = q("select * from mart_channel_performance order by spend desc")
    lf = lift.mail_lift(con)
    flight_orders = float(con.execute("""
        select sum(w.orders) from fct_market_week w join stg_experiment e on e.fips = w.fips
        where e.grp = 'treated' and w.week between 20 and 31""").fetchone()[0])
    incremental = flight_orders - flight_orders / (1 + lf["lift"])
    mail_spend = float(chan.loc[chan.channel == "direct_mail", "spend"].iloc[0])
    sv = survey.weighted_results(con)
    sv.pop("weights"); sv.pop("age_band")
    tiers = q("select tier, count(*) n, sum(pop) pop from mart_opportunity_score group by tier order by tier")
    white = q("""
        select s.fips, s.county_name, s.st, s.pop, round(s.avail, 3) avail, round(s.usage, 3) usage, round(s.gap_pop) gap_pop, s.score
        from mart_opportunity_score s
        where s.tier = 'A' and s.fips not in (select fips from stg_markets)
        order by s.gap_pop desc limit 10""")
    states = q("select st, pop, round(avail_fcc, 3) avail, round(usage_ms, 3) usage from mart_state_rollup order by pop desc limit 10")
    return {
        "data": {"counties": one("select count(*) from stg_county"), "population": int(one("select sum(pop) from stg_county")),
                 "unemployment_missing": one("select count(*) from stg_county where unemp_2016 is null"),
                 "avail_missing": 9, "usage_missing": 11, "markets": one("select count(*) from stg_markets"),
                 "orders": one("select count(*) from stg_orders"), "touches": one("select count(*) from stg_touches"),
                 "spend": float(one("select sum(spend) from stg_spend")), "mrr_added": float(one("select sum(monthly_price) from stg_orders"))},
        "scorecard": scorecard.assign(week_start=scorecard["week_start"].astype(str)).to_dict("records"),
        "anomalies": anomalies,
        "root_cause": [anomaly.explain_week(con, a["week"]) for a in anomalies],
        "channels": chan.round(2).to_dict("records"),
        "lift": {**lf, "true": lift.truth(), "flight_treated_orders": flight_orders, "incremental_orders": incremental,
                 "mail_spend": mail_spend, "cost_per_incremental_order": mail_spend / incremental if incremental > 0 else None},
        "competitive": competitive.competitive_effect(con),
        "survey": sv,
        "opportunity": {"tiers": tiers.to_dict("records"), "white_space_top10": white.to_dict("records"),
                        "states_top10_by_population": states.to_dict("records")},
    }


def save(report):
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    json.dump(report, open(os.path.join(ROOT, "out", "report.json"), "w"), indent=2, default=str)
