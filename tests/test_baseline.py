import argparse

import pandas as pd

from rasoi.assignment.budget import eligible_mask
from rasoi.cli import cmd_submit
from rasoi.model.propensity import PropensityBaseline


def test_baseline_predicts_all_customers(bundle):
    model = PropensityBaseline().fit(bundle.trial, bundle.customers)
    probs = model.predict_proba(bundle.customers)
    assert set(probs) == {"CONTROL", "OFFER_10", "OFFER_20"}
    for values in probs.values():
        assert len(values) == len(bundle.customers)
        assert ((values >= 0) & (values <= 1)).all()


def test_baseline_plan_excludes_opt_outs(bundle, tmp_path):
    args = argparse.Namespace(data=str(bundle.customers.attrs.get("path", "data/public")), out=str(tmp_path), top_n=1000)
    # The CLI resolves the data directory itself; use the repo default.
    args.data = "data/public"
    assert cmd_submit(args) == 0
    plan = pd.read_csv(tmp_path / "plan.csv")
    offered = plan[plan["offer"] != "NONE"]
    assert len(offered) == 1000
    opted = set(bundle.customers.loc[bundle.customers["promo_opt_out"], "customer_id"])
    assert not (set(offered["customer_id"]) & opted)


def test_eligible_mask(bundle):
    mask = eligible_mask(bundle.customers)
    assert mask.sum() == (~bundle.customers["promo_opt_out"]).sum()
