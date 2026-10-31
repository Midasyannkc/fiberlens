from fiberlens.lift import mail_lift


def test_lift_result_has_an_interval_that_brackets_the_estimate(con):
    r = mail_lift(con, n_boot=100)
    assert r["ci_low"] <= r["lift"] <= r["ci_high"]
    assert {"lift", "ci_low", "ci_high", "method"} <= set(r)


def test_lift_is_reproducible_for_a_fixed_seed(con):
    assert mail_lift(con, n_boot=50, seed=3) == mail_lift(con, n_boot=50, seed=3)


def test_market_arrays_are_ordered_by_market_so_the_bootstrap_cannot_depend_on_scan_order(con):
    from fiberlens.lift import _market_arrays
    a = _market_arrays(con)
    pops = {g: arr[:, 0] for g, arr in a.items()}
    keys = con.execute("select w.fips, e.grp from fct_market_week w join stg_experiment e on e.fips = w.fips group by all order by w.fips").df()
    for g, arr in a.items():
        assert len(arr) == (keys["grp"] == g).sum() == len(pops[g])


def test_lift_estimate_recovers_the_true_effect_despite_biased_market_selection(con):
    from fiberlens.lift import truth
    r = mail_lift(con)
    assert abs(r["lift"] - truth()) < 0.04
    assert r["ci_low"] <= truth() <= r["ci_high"]
    assert r["ci_low"] > 0  # the campaign did work, and the interval should say so


def test_the_naive_comparison_is_far_from_the_truth_which_is_why_it_is_not_used(con):
    from fiberlens.lift import naive_lift, truth
    assert abs(naive_lift(con) - truth()) > 0.10
