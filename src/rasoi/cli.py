from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

from rasoi.assignment.budget import eligible_mask, expected_discount_cost
from rasoi.assignment.optimizer import optimise_offers
from rasoi.io.loaders import load_bundle
from rasoi.model.propensity import PropensityBaseline
from rasoi.model.uplift import UpliftModel
from rasoi.simulate.revenue import incremental_profit
from rasoi.submission import SubmissionError, write_submission


def _baseline(bundle):
    model = PropensityBaseline().fit(bundle.trial, bundle.customers)
    return model, model.predict_proba(bundle.customers)


def cmd_inspect(args: argparse.Namespace) -> int:
    bundle = load_bundle(args.data)
    trial = bundle.trial
    summary = {
        "customers": len(bundle.customers),
        "orders_rows": len(bundle.orders),
        "trial_rows": len(trial),
        "trial_arms": trial["offer_bucket"].value_counts().to_dict(),
        "trial_mean_orders": {
            arm: round(float(group["orders_30d_after"].mean()), 3)
            for arm, group in trial.groupby("offer_bucket")
        },
        "opt_out_share": round(float(bundle.customers["promo_opt_out"].mean()), 4),
        "budget_inr": bundle.campaign.discount_budget_inr,
        "campaign_date": str(bundle.campaign.campaign_date),
    }
    print(json.dumps(summary, indent=2))
    return 0


def cmd_train(args: argparse.Namespace) -> int:
    bundle = load_bundle(args.data)
    model, probs = _baseline(bundle)
    print("Fitted propensity baseline on", len(bundle.trial), "trial customers")
    for arm, key in (("CONTROL", "CONTROL"), ("OFFER_10", "OFFER_10"), ("OFFER_20", "OFFER_20")):
        observed = float(bundle.trial.loc[bundle.trial.offer_bucket == arm, "orders_30d_after"].mean())
        print(f"{arm:9s} observed mean orders={observed:.3f} predicted P(order)={probs[key].mean():.3f}")
    print("Remember: P(order) is not incremental orders. See ISSUE-01.")
    return 0


def cmd_submit(args: argparse.Namespace) -> int:
    bundle = load_bundle(args.data)
    customers = bundle.customers
    aov = customers["avg_order_value_inr"].to_numpy()
    eligible = eligible_mask(customers)
    model_name = getattr(args, "model", "propensity")

    if model_name == "uplift":
        uplift = UpliftModel().fit(bundle.trial, customers)
        pred = uplift.predict(customers)
        lambda0, lambda10, lambda20 = pred.lambda0, pred.lambda10, pred.lambda20
        cost10 = 0.10 * aov * (1.0 - np.exp(-lambda10))
        cost20 = 0.20 * aov * (1.0 - np.exp(-lambda20))
        inc10 = np.asarray(incremental_profit(lambda0, lambda10, aov, 10.0), dtype=float)
        inc20 = np.asarray(incremental_profit(lambda0, lambda20, aov, 20.0), dtype=float)
        offer_series = optimise_offers(
            customers, lambda0, lambda10, lambda20, cost10, cost20, inc10, inc20,
            bundle.campaign.discount_budget_inr,
        )
        offer = offer_series.to_numpy()
        discount = np.where(offer == "OFFER_10", cost10, np.where(offer == "OFFER_20", cost20, 0.0))
        profit = np.where(offer == "OFFER_10", inc10, np.where(offer == "OFFER_20", inc20, 0.0))
        predictions = pd.DataFrame(
            {
                "customer_id": customers["customer_id"],
                "pred_orders_no_offer": lambda0,
                "pred_orders_10": lambda10,
                "pred_orders_20": lambda20,
                "pred_lift_10": lambda10 - lambda0,
                "pred_lift_20": lambda20 - lambda0,
            }
        )
    else:
        _, probs = _baseline(bundle)
        p0 = np.asarray(probs["CONTROL"])
        p10 = np.asarray(probs["OFFER_10"])
        p20 = np.asarray(probs["OFFER_20"])
        top = np.zeros(len(customers), dtype=bool)
        eligible_idx = np.flatnonzero(eligible)
        n_offers = min(args.top_n, len(eligible_idx))
        if n_offers:
            top[eligible_idx[np.argsort(-p20[eligible_idx])[:n_offers]]] = True
        offer = np.where(top, "OFFER_20", "NONE")
        discount = np.where(
            top,
            [expected_discount_cost(20.0, av, p) for av, p in zip(aov, p20, strict=True)],
            0.0,
        )
        profit = np.where(top, incremental_profit(p0, p20, aov, 20.0), 0.0)
        predictions = pd.DataFrame(
            {
                "customer_id": customers["customer_id"],
                "pred_orders_no_offer": p0,
                "pred_orders_10": p10,
                "pred_orders_20": p20,
                "pred_lift_10": p10,
                "pred_lift_20": p20,
            }
        )

    plan = pd.DataFrame(
        {
            "customer_id": customers["customer_id"],
            "offer": offer,
            "expected_discount_inr": discount,
            "expected_incremental_profit_inr": profit,
        }
    )
    portfolio = {
        "expected_discount_inr": round(float(np.nansum(discount)), 2),
        "expected_incremental_profit_inr": round(float(np.nansum(profit)), 2),
        "customers_offered": int((offer != "NONE").sum()),
        "opt_out_respected": bool(not ((offer != "NONE") & ~eligible).any()),
    }
    try:
        manifest = write_submission(
            args.out,
            predictions,
            plan,
            portfolio,
            eligible_ids=set(customers.loc[eligible, "customer_id"]),
            expected_customers=len(customers),
        )
    except SubmissionError as exc:
        print(f"submission invalid: {exc}")
        return 2
    print(f"wrote {args.out} ({len(plan):,} customers, {portfolio['customers_offered']:,} offered)")
    print(json.dumps({"portfolio": portfolio, "files": manifest["files"]}, indent=2))
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rasoi", description="Rasoi offer-targeting CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="print a data summary")
    inspect.add_argument("--data", default="data/public")
    inspect.set_defaults(func=cmd_inspect)

    train = sub.add_parser("train", help="fit the shipped baseline and report")
    train.add_argument("--data", default="data/public")
    train.set_defaults(func=cmd_train)

    submit = sub.add_parser("submit", help="write the submission directory")
    submit.add_argument("--data", default="data/public")
    submit.add_argument("--out", default="submission/")
    submit.add_argument("--top-n", type=int, default=50_000)
    submit.add_argument("--model", choices=["propensity", "uplift"], default="propensity")
    submit.set_defaults(func=cmd_submit)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
