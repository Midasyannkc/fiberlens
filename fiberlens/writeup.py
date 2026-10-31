"""Write docs/REPORT.md from the report dict. Every number comes from python -m fiberlens."""
import math
import os

from fiberlens.load import ROOT


def write_report_md(r):
    d, L, c, s = r["data"], r["lift"], r["competitive"], r["survey"]
    ch = [x for x in r["channels"] if x["channel"] != "organic"]
    org = next(x for x in r["channels"] if x["channel"] == "organic")
    rc = r["root_cause"][0]
    A = r["anomalies"][0]
    best, worst = min(ch, key=lambda x: x["cost_per_signup"]), max(ch, key=lambda x: x["cost_per_signup"])
    tiers = {t["tier"]: t for t in r["opportunity"]["tiers"]}
    wh = "\n".join(f"| {w['county_name']}, {w['st']} | {w['pop']:,} | {w['avail']:.1%} | {w['usage']:.1%} | {int(w['gap_pop']):,} | {w['score']:.3f} |"
                   for w in r["opportunity"]["white_space_top10"])
    chrows = "\n".join(f"| {x['channel']} | ${x['spend']:,.0f} | {int(x['signups']):,} | ${x['cost_per_signup']:,.0f} |" for x in sorted(ch, key=lambda y: y["cost_per_signup"]))
    text = f"""# FiberLens report

All numbers below come from `python -m fiberlens`. Campaign, order, competitor and survey data are **synthetic** (a fictional provider, Northwind Broadband); county availability, usage, population and unemployment are **real**.

## What the business should take away

1. **Mail worked, but modestly, and the first read said it did not.** Direct mail lifted sign-ups in treated markets by {L['lift']:+.1%} (95% interval {L['ci_low']:+.1%} to {L['ci_high']:+.1%}). The true simulated lift is {L['true']:+.1%}, inside that interval. A plain treated-versus-holdout comparison read {L['naive']:+.1%} because the business had put mail in different kinds of markets (INC-5). At ${L['mail_spend']:,.0f} spend that is about {L['incremental_orders']:,.0f} extra orders, or ${L['cost_per_incremental_order']:,.0f} per incremental order, versus ${next(x for x in ch if x['channel']=='direct_mail')['cost_per_signup']:,.0f} per last-touch order.
2. **Cheapest channel is {best['channel']} (${best['cost_per_signup']:,.0f} per sign-up); most expensive is {worst['channel']} (${worst['cost_per_signup']:,.0f}).** Last-touch credit favors channels that sit late in the journey, so treat it as a ranking of attributed cost, not of causal return.
3. **Week {A['week']} was an outage, not a demand problem.** Orders fell to {int(A['value']):,} (robust z {A['z']}). {rc['top_state']} explains {rc['top_state_share_of_change']:.0%} of the week-over-week change.
4. **Competitor coverage costs sign-ups.** A market fully covered by competitor A sells about {1 - math.exp(c['comp_a']):.0%} less than one it does not reach (log coefficient {c['comp_a']:+.2f}, 95% interval {c['comp_a_ci'][0]:+.2f} to {c['comp_a_ci'][1]:+.2f}); for competitor B the figure is about {1 - math.exp(c['comp_b']):.0%}.
5. **Survey intent is {s['intent_weighted']:.2f} of 5 once weighted, not {s['intent_unweighted']:.2f}.** The panel over-represents under-35s, who are keener. Net promoter score is {s['nps_weighted']} weighted versus {s['nps_unweighted']} raw.
6. **Where to look for new markets.** {int(tiers['A']['n'])} counties score Tier A; the ten largest not already in the footprint are listed below.

## Channel economics (last touch, synthetic spend)

| Channel | Spend | Sign-ups credited | Cost per sign-up |
| --- | --- | --- | --- |
{chrows}

Organic sign-ups (no marketing touch in the prior 28 days): {int(org['signups']):,} of {d['orders']:,} orders.

## White space: Tier A counties outside the footprint

Real data. Gap headcount is population times the share that can get broadband but does not use it.

| County | Population | Availability | Usage | Gap headcount | Score |
| --- | --- | --- | --- | --- | --- |
{wh}

## Data and limits

- Real: {d['counties']:,} counties, {d['population']:,} people. Availability is FCC Form 477 as published by Microsoft AI for Good in Oct 2020 and is old; usage is Microsoft's estimate; unemployment is BLS 2016. Vintages differ and are not aligned. Nine counties lack availability, eleven lack usage; they are excluded from scoring, not guessed.
- Synthetic: {d['markets']} markets, {d['orders']:,} orders, {d['touches']:,} touches, ${d['spend']:,.0f} spend, 3,000 survey respondents. The true effects are known from `data/synthetic/truth.json`, so the analysis can be graded, but that also means these results show the method works, not that any real campaign performs this way.
- Attribution is last touch over a 28-day window. It is a convention, not truth.
- The competitor effect is estimated across markets and could be confounded in real data; here it is clean by construction.
- No Tableau workbook is included. The extracts in `out/tableau/` and the build guide in `docs/tableau_build_guide.md` describe what to build; the PNGs in `docs/previews/` are matplotlib drawings of the intended layout.
"""
    open(os.path.join(ROOT, "docs", "REPORT.md"), "w").write(text)
