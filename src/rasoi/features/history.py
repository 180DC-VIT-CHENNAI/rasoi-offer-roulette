from __future__ import annotations

import pandas as pd


def customer_order_summary(orders: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the 180-day order log to one row per customer.

    Given as a starting point: count, mean value, discount share, weekend
    share.  Extend it with concentration and recency features in ISSUE-01.
    """
    grouped = orders.groupby("customer_id")
    out = grouped.agg(
        n_orders=("order_id", "count"),
        mean_order_value_inr=("order_value_inr", "mean"),
        discount_share=("discount_pct", lambda s: float((s > 0).mean())),
        weekend_share=("order_ts", lambda s: float((pd.to_datetime(s).dt.weekday >= 5).mean())),
    ).reset_index()
    return out
