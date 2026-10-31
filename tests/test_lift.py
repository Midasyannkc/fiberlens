from fiberlens.lift import mail_lift


def test_lift_result_has_an_interval_that_brackets_the_estimate(con):
    r = mail_lift(con, n_boot=100)
    assert r["ci_low"] <= r["lift"] <= r["ci_high"]
    assert {"lift", "ci_low", "ci_high", "method"} <= set(r)


def test_lift_is_reproducible_for_a_fixed_seed(con):
    assert mail_lift(con, n_boot=50, seed=3) == mail_lift(con, n_boot=50, seed=3)
