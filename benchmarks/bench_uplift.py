"""Small trial-only benchmark.

It reports the raw arm means and the propensity baseline's average predicted
order probability.  Extend it with an uplift model and a holdout split in
ISSUE-06.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rasoi.io.loaders import load_bundle  # noqa: E402
from rasoi.model.propensity import PropensityBaseline  # noqa: E402


def main() -> None:
    bundle = load_bundle(Path(__file__).resolve().parents[1] / "data" / "public")
    print("Raw trial means (orders in 30 days):")
    print(bundle.trial.groupby("offer_bucket")["orders_30d_after"].agg(["mean", "count"]).round(3))
    model = PropensityBaseline().fit(bundle.trial, bundle.customers)
    probs = model.predict_proba(bundle.customers)
    print("\nPropensity baseline mean P(order):")
    for arm, values in probs.items():
        print(f"  {arm:9s} {values.mean():.3f}")
    print("\nRemember: P(order) is not incremental orders. See ISSUE-01.")


if __name__ == "__main__":
    main()
