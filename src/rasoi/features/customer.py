from __future__ import annotations

import pandas as pd

NUMERIC_FEATURES = [
    "tenure_days",
    "orders_30d",
    "orders_90d",
    "orders_180d",
    "avg_order_value_inr",
    "days_since_last_order",
    "app_sessions_30d",
    "historical_discount_rate",
    "avg_discount_pct",
    "weekend_share",
    "late_night_share",
]

CATEGORICAL_FEATURES = ["city", "loyalty_tier", "cuisine_pref", "device_type"]


def build_features(customers: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Turn the customer snapshot into a numeric matrix.

    The shipped version is deliberately simple.  ISSUE-01 asks for features
    that actually separate deal-seekers from loyal full-price customers:
    recency/frequency interactions, discount sensitivity and concentration in
    the order log.  Keep the function pure: same input, same output.
    """
    frame = customers[NUMERIC_FEATURES].copy()
    for column in CATEGORICAL_FEATURES:
        dummies = pd.get_dummies(
            customers[column].astype(str), prefix=column, drop_first=True
        )
        frame = pd.concat([frame, dummies], axis=1)
    frame = frame.astype(float)
    return frame, list(frame.columns)
