from __future__ import annotations

import numpy as np
import pandas as pd


def expected_discount_cost(discount_pct: float, aov_inr: float, p_order: float) -> float:
    """Expected rupee discount for one customer.

    The offer applies to the customer's first redeemed order in the 30-day
    window, so the expected cost is `discount_pct × AOV × P(at least one
    order)`, not `discount_pct × AOV`.

    ISSUE-02: the shipped implementation ignores `p_order`.  That understates
    the budget, especially for low-propensity customers.
    """
    return float(discount_pct) / 100.0 * float(aov_inr)


def eligible_mask(customers: pd.DataFrame) -> np.ndarray:
    """Customers who did not opt out of promotions."""
    return ~customers["promo_opt_out"].astype(bool).to_numpy()


def select_offers(
    customers: pd.DataFrame,
    p0: np.ndarray,
    p10: np.ndarray,
    p20: np.ndarray,
    budget_inr: float,
) -> pd.Series:
    """Choose an offer for every customer under the budget and opt-out rules.

    ISSUE-02: implement.  Return a Series aligned to `customers.index` with
    values `NONE`, `OFFER_10` or `OFFER_20`.  Opt-outs must be `NONE`; the
    expected discount must not exceed the budget.
    """
    raise NotImplementedError("ISSUE-02: implement select_offers()")
