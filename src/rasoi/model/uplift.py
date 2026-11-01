from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class UpliftPredictions:
    lambda0: np.ndarray
    lambda10: np.ndarray
    lambda20: np.ndarray
    lift10: np.ndarray
    lift20: np.ndarray


class UpliftModel:
    """The model the case is really about.

    Fit P(orders) for the control and each offer arm, then predict the
    *expected incremental orders* for every customer.  A good model separates
    deal-seekers from loyal full-price customers; a propensity model does not.

    ISSUE-01: implement `fit` and `predict`.  You may use a T-learner, an
    S-learner with treatment interactions, a transformed-outcome model, or a
    causal forest if it is already in the environment.  The hidden tests check
    the interface and the absence of post-offer features; the judge scores the
    hidden uplift error and the profit of the resulting plan.
    """

    def fit(self, trial: pd.DataFrame, customers: pd.DataFrame) -> UpliftModel:
        raise NotImplementedError("ISSUE-01: implement UpliftModel.fit()")

    def predict(self, customers: pd.DataFrame) -> UpliftPredictions:
        raise NotImplementedError("ISSUE-01: implement UpliftModel.predict()")
