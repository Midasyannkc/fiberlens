"""Generate the SYNTHETIC half of FiberLens: a fictional provider called Northwind Broadband.

Everything here is invented and labeled as such: marketing spend, orders, touches, competitor footprint,
the survey panel and the experiment assignment.  It is layered on REAL county availability, usage and
population, so market sizes and baseline demand are realistic while the campaign data is a controlled
simulation whose true effects are written to data/synthetic/truth.json.  Tests recover those effects."""
import json
import os
import sys
from datetime import date, timedelta

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fiberlens.load import read_ms_county, read_population  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "synthetic")
SEED = 20261031
WEEKS = 52
START = date(2025, 1, 6)
CHANNELS = ["search", "social", "email", "direct_mail", "tv", "door_to_door"]
EFFECT = {"search": 0.25, "social": 0.10, "email": 0.05, "direct_mail": 0.20, "tv": 0.12, "door_to_door": 0.30}
HALF = {"search": 40, "social": 35, "email": 8, "direct_mail": 60, "tv": 50, "door_to_door": 70}  # saturation scale, $ per 10k pop
TARGET = {"search": 45, "social": 30, "email": 6, "tv": 35, "door_to_door": 80}
MAIL_SPEND = 60.0
FLIGHT = (20, 31)
OUTAGE_WEEK = 38
PLANS = {"300M": 55, "1G": 75, "2G": 110}
AGES = ["18-34", "35-54", "55+"]
POP_AGE = np.array([0.30, 0.35, 0.35])
SAMPLE_AGE = np.array([0.45, 0.35, 0.20])
INTENT_MEAN = np.array([3.9, 3.3, 2.6])


def sat(spend_per10k, ch):
    return 1 - np.exp(-spend_per10k / HALF[ch])


def make_markets(rng):
    c = read_ms_county().merge(read_population(), on="fips")
    c = c.dropna(subset=["avail", "usage"])
    c = c[(c["pop"] >= 20000) & (c["pop"] <= 1_500_000) & (c["avail"] >= 0.40)].reset_index(drop=True)
    m = c.sample(420, random_state=int(rng.integers(1_000_000))).reset_index(drop=True)
    m = m[["fips", "st", "county_name", "pop", "avail", "usage"]].copy()
    m["comp_a"] = rng.beta(2, 5, len(m)).round(3)
    m["comp_b"] = rng.beta(1.5, 6, len(m)).round(3)
    m["base_rate"] = (0.30 * (0.4 + m["avail"]) * (0.6 + (1 - m["usage"])) * (1 - 0.30 * m["comp_a"] - 0.15 * m["comp_b"])
                      * np.exp(rng.normal(0, 0.15, len(m))))
    m["tv_on"] = rng.random(len(m)) < 0.5
    m["door_on"] = rng.random(len(m)) < 0.3
    return m


def assign_experiment(m, rng):
    """Selection is deliberately biased: treated markets come from the better-served half."""
    order = m.sort_values("avail", ascending=False)["fips"].tolist()
    top, bottom = order[: int(len(order) * 0.6)], order[int(len(order) * 0.4):]
    treated = list(rng.choice(top, 90, replace=False))
    rest = [f for f in bottom if f not in set(treated)]
    holdout = list(rng.choice(rest, 90, replace=False))
    g = pd.DataFrame({"fips": treated + holdout, "grp": ["treated"] * 90 + ["holdout"] * 90})
    return g


def main():
    rng = np.random.default_rng(SEED)
    os.makedirs(OUT, exist_ok=True)
    m = make_markets(rng)
    exp = assign_experiment(m, rng)
    treated = set(exp.loc[exp.grp == "treated", "fips"])
    season = lambda w: 1 + 0.12 * np.sin(2 * np.pi * (w - 8) / 52)
    top_state = m["st"].value_counts().idxmax()

    spend_rows, orders, touches = [], [], []
    oid = 0
    for _, r in m.iterrows():
        scale = r["pop"] / 1e4
        for w in range(1, WEEKS + 1):
            wk_start = START + timedelta(weeks=w - 1)
            eff = {}
            for ch in CHANNELS:
                if ch == "direct_mail":
                    s = MAIL_SPEND * scale if (r["fips"] in treated and FLIGHT[0] <= w <= FLIGHT[1]) else 0.0
                elif ch == "tv" and not r["tv_on"]:
                    s = 0.0
                elif ch == "door_to_door" and not r["door_on"]:
                    s = 0.0
                else:
                    s = TARGET[ch] * scale * float(np.exp(rng.normal(0, 0.2))) if ch != "email" else TARGET[ch] * scale
                if s > 0:
                    spend_rows.append((r["fips"], w, wk_start.isoformat(), ch, round(s, 2)))
                eff[ch] = EFFECT[ch] * sat(s / scale, ch) if s > 0 else 0.0
            lam = scale * r["base_rate"] * season(w) * np.prod([1 + e for e in eff.values()])
            if w == OUTAGE_WEEK and r["st"] == top_state:
                lam *= 0.55
            n = int(rng.poisson(lam))
            weights = np.array([eff[c] for c in CHANNELS])
            p_marketing = weights.sum() / (1 + weights.sum())
            for _ in range(n):
                oid += 1
                day = int(rng.integers(0, 7))
                odate = wk_start + timedelta(days=day)
                plan = str(rng.choice(list(PLANS), p=[0.5, 0.35, 0.15]))
                orders.append((f"O{oid:07d}", r["fips"], w, odate.isoformat(), plan, PLANS[plan]))
                if weights.sum() > 0 and rng.random() < p_marketing:
                    k = min(1 + int(rng.binomial(2, 0.5)), int((weights > 0).sum()))
                    chosen = rng.choice(len(CHANNELS), size=k, replace=False, p=weights / weights.sum())
                    days = sorted(rng.choice(28, size=k, replace=False).tolist())  # ascending: smallest = last touch
                    for ci, d in zip(chosen, days):
                        touches.append((f"O{oid:07d}", CHANNELS[ci], (odate - timedelta(days=int(d) + 1)).isoformat()))

    pd.DataFrame(spend_rows, columns=["fips", "week", "week_start", "channel", "spend"]).to_csv(f"{OUT}/spend_weekly.csv", index=False)
    pd.DataFrame(orders, columns=["order_id", "fips", "week", "order_date", "plan", "monthly_price"]).to_csv(f"{OUT}/orders.csv", index=False)
    pd.DataFrame(touches, columns=["order_id", "channel", "touch_date"]).to_csv(f"{OUT}/touches.csv", index=False)
    m.drop(columns=["base_rate"]).to_csv(f"{OUT}/markets.csv", index=False)
    exp.to_csv(f"{OUT}/experiment_assignment.csv", index=False)

    # survey panel: respondents skew young relative to the population, and intent falls with age
    n = 3000
    w = np.sqrt(m["pop"].values); w = w / w.sum()
    age = rng.choice(3, n, p=SAMPLE_AGE)
    intent_latent = rng.normal(INTENT_MEAN[age], 1.0)
    intent = np.clip(np.rint(intent_latent), 1, 5).astype(int)
    nps = np.clip(np.rint(rng.normal(INTENT_MEAN[age] * 2.0, 2.2)), 0, 10).astype(int)
    recall = rng.choice(CHANNELS + ["none"], n, p=[0.20, 0.15, 0.08, 0.12, 0.15, 0.05, 0.25])
    sv = pd.DataFrame({"resp_id": [f"R{i:05d}" for i in range(n)], "fips": rng.choice(m["fips"].values, n, p=w),
                       "age_band": [AGES[a] for a in age], "intent": intent, "nps": nps, "recalled_channel": recall})
    sv.to_csv(f"{OUT}/survey.csv", index=False)
    big = rng.choice(3, 400_000, p=POP_AGE)
    truth_intent = float(np.clip(np.rint(rng.normal(INTENT_MEAN[big], 1.0)), 1, 5).mean())

    tr = m[m.fips.isin(treated)]
    mail_pop = float(np.mean([1 + EFFECT["direct_mail"] * sat(MAIL_SPEND, "direct_mail")]))
    truth = {"seed": SEED, "provider": "Northwind Broadband (fictional)", "markets": int(len(m)),
             "mail_lift_true": mail_pop - 1, "flight_weeks": list(FLIGHT), "outage_week": OUTAGE_WEEK, "outage_state": top_state,
             "outage_factor": 0.55, "survey_population_intent_mean": truth_intent,
             "population_age_shares": dict(zip(AGES, POP_AGE.tolist())), "comp_a_effect": -0.30, "comp_b_effect": -0.15,
             "treated_mean_avail": float(tr["avail"].mean()),
             "holdout_mean_avail": float(m[m.fips.isin(set(exp.loc[exp.grp == "holdout", "fips"]))]["avail"].mean())}
    json.dump(truth, open(f"{OUT}/truth.json", "w"), indent=2)
    print(len(m), "markets", len(orders), "orders", len(touches), "touches", len(spend_rows), "spend rows")


if __name__ == "__main__":
    main()
