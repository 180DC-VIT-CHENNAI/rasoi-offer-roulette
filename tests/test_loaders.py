import pandas as pd


def test_public_files_load(bundle):
    assert len(bundle.customers) == 200_000
    assert len(bundle.trial) == 40_000
    assert len(bundle.orders) > 1_000_000
    assert bundle.campaign.discount_budget_inr == 8_000_000


def test_trial_is_randomised_and_complete(bundle):
    arms = bundle.trial["offer_bucket"].value_counts().to_dict()
    assert set(arms) == {"CONTROL", "OFFER_10", "OFFER_20"}
    assert max(arms.values()) - min(arms.values()) < 10
    assert bundle.trial["responded"].isin([0, 1]).all()


def test_no_post_offer_leak_in_customer_columns(bundle):
    forbidden = {"orders_30d_after", "gmv_30d_after", "discount_inr_used", "responded"}
    assert not (forbidden & set(bundle.customers.columns))


def test_order_log_shape(bundle):
    assert pd.api.types.is_datetime64_any_dtype(bundle.orders["order_ts"])
    assert bundle.orders["order_value_inr"].min() > 0
    assert bundle.orders["discount_pct"].isin([0, 10, 20]).all()
