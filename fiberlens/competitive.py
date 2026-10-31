"""Does competitor coverage depress our sign-ups once market quality and marketing exposure are held constant?"""
import numpy as np


def competitive_effect(con, n_boot=400, seed=11):
    df = con.execute("""
        SELECT c.fips, c.orders_per_10k, c.comp_a, c.comp_b, c.avail, c.usage,
               coalesce(s.spend, 0) * 10000.0 / c.pop AS spend_per_10k
        FROM mart_competitive c
        LEFT JOIN (SELECT fips, sum(spend) AS spend FROM stg_spend WHERE channel <> 'direct_mail' GROUP BY fips) s ON s.fips = c.fips
        WHERE c.orders_per_10k > 0""").df()
    y = np.log(df["orders_per_10k"].to_numpy())
    X = np.column_stack([np.ones(len(df)), df["comp_a"], df["comp_b"], np.log(0.4 + df["avail"]), np.log(1.6 - df["usage"]),
                         np.log1p(df["spend_per_10k"])])
    fit = lambda idx: np.linalg.lstsq(X[idx], y[idx], rcond=None)[0]
    beta = fit(np.arange(len(df)))
    rng = np.random.default_rng(seed)
    boots = np.array([fit(rng.integers(0, len(df), len(df))) for _ in range(n_boot)])
    ci = np.percentile(boots, [2.5, 97.5], axis=0)
    return {"comp_a": float(beta[1]), "comp_a_ci": [float(ci[0][1]), float(ci[1][1])],
            "comp_b": float(beta[2]), "comp_b_ci": [float(ci[0][2]), float(ci[1][2])], "n": int(len(df))}
