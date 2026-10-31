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
    """Difference-in-differences on log sign-up rates.  Each group is compared with ITS OWN pre-flight rate, so
    the permanent gap between the groups (they were not randomized) drops out, and so does any season effect
    that hits both groups.  exp(DiD) - 1 is the relative lift."""
    t, h = arrs["treated"], arrs["holdout"]
    rate = lambda a, col, weeks: a[:, col].sum() / (a[:, 0].sum() * weeks) * 1e4
    did = (np.log(rate(t, 2, len(FLIGHT)) / rate(t, 1, len(PRE)))
           - np.log(rate(h, 2, len(FLIGHT)) / rate(h, 1, len(PRE))))
    return np.exp(did) - 1


def naive_lift(con):
    """The comparison the business first made: treated vs holdout rate during the flight, ignoring their pre-flight gap.
    Kept only to show how far off it is; do not use it for decisions."""
    arrs = _market_arrays(con)
    rate = lambda a: a[:, 2].sum() / (a[:, 0].sum() * len(FLIGHT)) * 1e4
    return float(rate(arrs["treated"]) / rate(arrs["holdout"]) - 1)


def mail_lift(con, n_boot=400, seed=7):
    arrs = _market_arrays(con)
    est = _estimate(arrs)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        s = {g: a[rng.integers(0, len(a), len(a))] for g, a in arrs.items()}
        boots.append(_estimate(s))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"lift": float(est), "ci_low": float(lo), "ci_high": float(hi), "method": "difference-in-differences on log rates, bootstrap over markets"}


def truth():
    return json.load(open(os.path.join(ROOT, "data", "synthetic", "truth.json")))["mail_lift_true"]
