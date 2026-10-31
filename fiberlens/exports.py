"""Tableau-ready extracts and dashboard previews.

No Tableau is available in the build environment, so this module writes the flat extracts a Tableau workbook
would connect to, plus PNG previews drawn with matplotlib to show the intended layout.  The previews are
labeled as such; they are not Tableau output."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from fiberlens.load import ROOT  # noqa: E402

OUT = os.path.join(ROOT, "out", "tableau")
PREV = os.path.join(ROOT, "docs", "previews")
NAVY, TEAL, ORANGE, GREY = "#14213D", "#0F766E", "#D9822B", "#8A94A6"


def write_extracts(con, report):
    os.makedirs(OUT, exist_ok=True)
    flagged = {a["week"] for a in report["anomalies"]}
    sc = con.execute("select * from mart_weekly_scorecard order by week").df()
    sc["anomaly_flag"] = sc["week"].isin(flagged)
    sc.to_csv(f"{OUT}/exec_scorecard_weekly.csv", index=False)
    ch = con.execute("select * from mart_channel_performance order by spend desc").df()
    ch["share_of_spend"] = ch["spend"] / ch["spend"].sum()
    ch["share_of_signups"] = ch["signups"] / ch["signups"].sum()
    ch.to_csv(f"{OUT}/channel_performance.csv", index=False)
    con.execute("""select s.fips, s.county_name, s.st, s.pop, s.avail, s.usage, s.unemp_2016, s.gap_pop, s.score, s.tier,
                   (s.fips in (select fips from stg_markets)) as in_footprint from mart_opportunity_score s""").df() \
        .to_csv(f"{OUT}/market_opportunity.csv", index=False)
    con.execute("select * from mart_state_rollup order by pop desc").df().to_csv(f"{OUT}/state_rollup.csv", index=False)
    con.execute("""select e.grp, w.week, sum(w.orders) as orders, sum(w.pop) as pop, sum(w.orders) * 10000.0 / sum(w.pop) as orders_per_10k
                   from fct_market_week w join stg_experiment e on e.fips = w.fips group by e.grp, w.week order by e.grp, w.week""").df() \
        .to_csv(f"{OUT}/lift_weekly.csv", index=False)
    con.execute("select * from mart_competitive").df().to_csv(f"{OUT}/competitive_markets.csv", index=False)
    return sorted(os.listdir(OUT))


def previews(con, report):
    os.makedirs(PREV, exist_ok=True)
    note = "Preview drawn with matplotlib to show intended layout. Not Tableau output. Campaign data is synthetic."
    sc = con.execute("select * from mart_weekly_scorecard order by week").df()
    fig, ax = plt.subplots(2, 1, figsize=(11, 6.2), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    ax[0].plot(sc["week"], sc["orders"], color=NAVY, lw=2)
    for a in report["anomalies"]:
        ax[0].scatter([a["week"]], [a["value"]], color=ORANGE, zorder=5, s=60)
        rc = next(r for r in report["root_cause"] if r["week"] == a["week"])
        ax[0].annotate(f"Week {a['week']}: {rc['top_state']} explains {rc['top_state_share_of_change']:.0%} of the drop",
                       (a["week"], a["value"]), xytext=(a["week"] - 27, a["value"] + 15), arrowprops={"arrowstyle": "->", "color": ORANGE}, fontsize=9)
    ax[0].set_title("Executive scorecard: weekly sign-ups", loc="left", fontweight="bold", color=NAVY)
    ax[0].spines[["top", "right"]].set_visible(False)
    ax[1].bar(sc["week"], sc["spend"] / 1000, color=GREY)
    ax[1].set_ylabel("Spend ($K)"); ax[1].set_xlabel("Week"); ax[1].spines[["top", "right"]].set_visible(False)
    fig.text(0.01, 0.01, note, fontsize=7, color=GREY); fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(f"{PREV}/01_exec_scorecard.png", dpi=110); plt.close(fig)

    ch = [c for c in report["channels"] if c["channel"] != "organic"]
    ch.sort(key=lambda c: c["cost_per_signup"])
    lw = con.execute("""select e.grp, w.week, sum(w.orders) * 10000.0 / sum(w.pop) as r from fct_market_week w
                        join stg_experiment e on e.fips = w.fips group by e.grp, w.week order by w.week""").df()
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))
    ax[0].barh([c["channel"] for c in ch], [c["cost_per_signup"] for c in ch], color=TEAL)
    for i, c in enumerate(ch):
        ax[0].text(c["cost_per_signup"] + 15, i, f"${c['cost_per_signup']:,.0f}", va="center", fontsize=9)
    ax[0].set_title("Cost per last-touch sign-up", loc="left", fontweight="bold", color=NAVY); ax[0].spines[["top", "right"]].set_visible(False)
    for g, color in (("treated", TEAL), ("holdout", GREY)):
        d = lw[lw.grp == g]; ax[1].plot(d["week"], d["r"], color=color, lw=2, label=g)
    ax[1].axvspan(20, 31, color=ORANGE, alpha=0.12)
    L = report["lift"]
    ax[1].set_title(f"Mail flight lift {L['lift']:+.1%} (95% CI {L['ci_low']:+.1%} to {L['ci_high']:+.1%})", loc="left", fontweight="bold", color=NAVY)
    ax[1].legend(frameon=False); ax[1].set_xlabel("Week"); ax[1].set_ylabel("Orders per 10k people"); ax[1].spines[["top", "right"]].set_visible(False)
    fig.text(0.01, 0.01, note, fontsize=7, color=GREY); fig.tight_layout(rect=(0, 0.04, 1, 1)); fig.savefig(f"{PREV}/02_campaign_effectiveness.png", dpi=110); plt.close(fig)

    st = con.execute("select st, pop, avail_fcc, usage_ms from mart_state_rollup order by pop desc limit 15").df()
    fig, ax = plt.subplots(figsize=(11, 4.8))
    x = range(len(st)); ax.bar([i - 0.2 for i in x], st["avail_fcc"], 0.4, color=NAVY, label="Can get broadband (FCC)")
    ax.bar([i + 0.2 for i in x], st["usage_ms"], 0.4, color=ORANGE, label="Use broadband (Microsoft)")
    ax.set_xticks(list(x)); ax.set_xticklabels(st["st"]); ax.set_ylim(0, 1.05); ax.legend(frameon=False, ncol=2)
    ax.set_title("Market opportunity: 15 largest states, population weighted", loc="left", fontweight="bold", color=NAVY)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, 0.01, "Preview drawn with matplotlib. Real data: Microsoft AI for Good (Oct 2020), JHU/Census population.", fontsize=7, color=GREY)
    fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(f"{PREV}/03_market_opportunity.png", dpi=110); plt.close(fig)
    return sorted(os.listdir(PREV))
