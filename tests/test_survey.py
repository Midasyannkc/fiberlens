import json

import numpy as np
import pytest

from fiberlens.survey import weighted_results


@pytest.fixture(scope="module")
def res(con):
    return weighted_results(con)


def test_weights_sum_to_the_sample_size(res):
    assert abs(sum(res["weights"]) - res["n"]) < 1e-6


def test_weighted_age_mix_matches_the_population(res):
    w = np.array(res["weights"]); ages = np.array(res["age_band"])
    shares = {a: w[ages == a].sum() / w.sum() for a in set(ages)}
    assert abs(shares["18-34"] - 0.30) < 1e-9 and abs(shares["55+"] - 0.35) < 1e-9


def test_weighting_recovers_the_true_population_intent_and_unweighted_does_not(res):
    truth = json.load(open("data/synthetic/truth.json"))["survey_population_intent_mean"]
    assert abs(res["intent_weighted"] - truth) < 0.05
    assert abs(res["intent_unweighted"] - truth) > 0.10


def test_recall_shares_sum_to_one(res):
    assert abs(sum(res["recall_weighted"].values()) - 1) < 0.01
