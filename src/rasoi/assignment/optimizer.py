from __future__ import annotations

import numpy as np
import pandas as pd


def optimise_offers(
    customers: pd.DataFrame,
    lambda0: np.ndarray,
    lambda10: np.ndarray,
    lambda20: np.ndarray,
    cost10: np.ndarray,
    cost20: np.ndarray,
    inc10: np.ndarray,
    inc20: np.ndarray,
    budget_inr: float,
) -> pd.Series:
    """Choose offers to maximise expected incremental profit under the budget.

    ISSUE-03: implement.  A greedy selection by incremental profit per rupee of
    expected discount is a good baseline; a Lagrangian (maximise profit − θ·cost,
    binary-search θ to meet the budget) handles the shared budget better.

    Return a Series aligned to `customers.index` with values `NONE`,
    `OFFER_10` or `OFFER_20`.  Opt-outs must be `NONE`.
    """
    raise NotImplementedError("ISSUE-03: implement optimise_offers()")
