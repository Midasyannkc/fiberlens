"""Weight the survey panel back to the population. The panel skews young, and intent falls with age."""
import json
import os

from fiberlens.load import ROOT


def population_shares():
    return json.load(open(os.path.join(ROOT, "data", "synthetic", "truth.json")))["population_age_shares"]


def weighted_results(con):
    df = con.execute("select age_band, intent, nps, recalled_channel from stg_survey").df()
    pop = population_shares()
    sample = df["age_band"].value_counts(normalize=True)
    df["w"] = df["age_band"].map(lambda a: pop[a] / sample[a])
    wmean = lambda col: float((df[col] * df["w"]).sum() / df["w"].sum())
    promoters = lambda m: float(((m >= 9) * df["w"]).sum() / df["w"].sum())
    detractors = lambda m: float(((m <= 6) * df["w"]).sum() / df["w"].sum())
    recall = (df.groupby("recalled_channel")["w"].sum() / df["w"].sum()).sort_values(ascending=False)
    return {
        "n": int(len(df)),
        "intent_unweighted": float(df["intent"].mean()),
        "intent_weighted": wmean("intent"),
        "nps_weighted": round(100 * (promoters(df["nps"]) - detractors(df["nps"])), 1),
        "nps_unweighted": round(100 * (float((df["nps"] >= 9).mean()) - float((df["nps"] <= 6).mean())), 1),
        "recall_weighted": {k: round(float(v), 4) for k, v in recall.items()},
        "weights": df["w"].tolist(),
        "age_band": df["age_band"].tolist(),
    }
