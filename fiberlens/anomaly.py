"""Spot an unusual week in sign-ups and say which state explains it."""
import numpy as np


def find_anomalies(values, window=9, z=4.0, min_rel=0.05):
    """Robust z-score of each point against the rolling median of its neighbours (centered window).
    A point must also be at least `min_rel` away from that median, so a very smooth series cannot flag tiny wiggles."""
    x = np.asarray(values, float)
    half = window // 2
    out = []
    resid = np.zeros(len(x))
    ref = np.zeros(len(x))
    for i in range(len(x)):
        lo, hi = max(0, i - half), min(len(x), i + half + 1)
        neigh = np.delete(x[lo:hi], i - lo)
        ref[i] = np.median(neigh)
        resid[i] = x[i] - ref[i]
    mad = np.median(np.abs(resid - np.median(resid))) * 1.4826
    for i, r in enumerate(resid):
        if mad > 0 and abs(r / mad) > z and abs(r) >= min_rel * abs(ref[i]):
            out.append({"index": i, "week": i + 1, "value": float(x[i]), "z": round(float(r / mad), 1)})
    return out


def explain_week(con, week, lookback=4):
    """Compare each state's orders in `week` with its mean over the previous `lookback` weeks."""
    df = con.execute(f"""
        SELECT st, sum(CASE WHEN week = {week} THEN orders END) AS now,
               sum(CASE WHEN week BETWEEN {week - lookback} AND {week - 1} THEN orders END) / {lookback}.0 AS base
        FROM fct_market_week GROUP BY st""").df()
    df["delta"] = df["now"] - df["base"]
    total = df["delta"].sum()
    df = df.sort_values("delta")
    top = df.iloc[0]
    return {"week": week, "total_delta": float(total), "top_state": top["st"], "top_state_delta": float(top["delta"]),
            "top_state_share_of_change": float(top["delta"] / total) if total else None,
            "by_state": df[["st", "now", "base", "delta"]].head(5).round(1).to_dict("records")}
