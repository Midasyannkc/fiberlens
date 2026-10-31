"""Did the direct-mail flight raise sign-ups, and by how much?

Markets were assigned to the treated and holdout groups by the business, not at random, so the two groups
differ before the flight starts.  The estimator has to cope with that."""
import json
import os

import numpy as np

from fiberlens.load import ROOT

PRE = range(1, 20)       # weeks before the flight
FLIGHT = range(20, 32)   # flight weeks 20 to 31


def _market_arrays(con):
    df = con.execute("""
        SELECT w.fips, e.grp, any_value(w.pop) AS pop,
               sum(CASE WHEN w.week BETWEEN 1 AND 19 THEN w.orders END) AS pre,
               sum(CASE WHEN w.week BETWEEN 20 AND 31 THEN w.orders END) AS flight
        FROM fct_market_week w JOIN stg_experiment e ON e.fips = w.fips
        GROUP BY w.fips, e.grp
        ORDER BY w.fips""").df()
    return {g: d[["pop", "pre", "flight"]].to_numpy(float) for g, d in df.groupby("grp")}


def _estimate(arrs):
    t, h = arrs["treated"], arrs["holdout"]
    rate = lambda a, col, weeks: a[:, col].sum() / (a[:, 0].sum() * weeks) * 1e4
    return rate(t, 2, len(FLIGHT)) / rate(h, 2, len(FLIGHT)) - 1


def mail_lift(con, n_boot=400, seed=7):
    arrs = _market_arrays(con)
    est = _estimate(arrs)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        s = {g: a[rng.integers(0, len(a), len(a))] for g, a in arrs.items()}
        boots.append(_estimate(s))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"lift": float(est), "ci_low": float(lo), "ci_high": float(hi), "method": "treated vs holdout during flight"}


def truth():
    return json.load(open(os.path.join(ROOT, "data", "synthetic", "truth.json")))["mail_lift_true"]
