from __future__ import annotations

import numpy as np
import pandas as pd

PROFIT_PER_ORDER_INR = 55.0


def incremental_profit(
    lambda0: np.ndarray | float,
    lambda_offer: np.ndarray | float,
    aov_inr: np.ndarray | float,
    discount_pct: float,
) -> np.ndarray | float:
    """Expected incremental profit from offering a discount.

    The discount applies once, to the first redeemed order:
      profit = 55 × (λ_offer − λ0) − (d/100) × AOV × P(order | offer)

    ISSUE-04: the shipped version charges the discount on *every* order
    (`× λ_offer`) and ignores the redemption probability.  That overstates the
    cost for frequent customers and understates it for sporadic ones.
    """
    lam0 = np.asarray(lambda0, dtype=float)
    lam = np.asarray(lambda_offer, dtype=float)
    aov = np.asarray(aov_inr, dtype=float)
    return PROFIT_PER_ORDER_INR * (lam - lam0) - (float(discount_pct) / 100.0) * aov * lam


def portfolio_expected_profit(
    plan: pd.DataFrame,
    lambda0: np.ndarray,
    lambda10: np.ndarray,
    lambda20: np.ndarray,
    aov: np.ndarray,
) -> float:
    """Sum the expected incremental profit of the chosen offers."""
    offer = plan["offer"].to_numpy()
    values = np.zeros(len(plan))
    mask10 = offer == "OFFER_10"
    mask20 = offer == "OFFER_20"
    values[mask10] = incremental_profit(lambda0[mask10], lambda10[mask10], aov[mask10], 10.0)
    values[mask20] = incremental_profit(lambda0[mask20], lambda20[mask20], aov[mask20], 20.0)
    return float(np.nansum(values))
