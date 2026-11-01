from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from rasoi.features.customer import build_features

ARMS = ("CONTROL", "OFFER_10", "OFFER_20")


class PropensityBaseline:
    """The shipped baseline: predict who will order, not who responds to an offer.

    It trains a logistic regression on the randomised trial with the offer
    bucket as a feature.  The resulting p10/p20 are order probabilities, not
    incremental orders.  Using them as uplift is the central trap of the case
    (ISSUE-01).
    """

    def __init__(self) -> None:
        self.model = None
        self.columns: list[str] = []

    def fit(self, trial: pd.DataFrame, customers: pd.DataFrame) -> PropensityBaseline:
        frame = trial.merge(customers, on="customer_id", how="left")
        matrix, _ = build_features(frame)
        arm = pd.get_dummies(frame["offer_bucket"], prefix="arm", drop_first=True).astype(float)
        matrix = pd.concat([matrix, arm], axis=1)
        self.columns = list(matrix.columns)
        self.model = make_pipeline(
            StandardScaler(), LogisticRegression(max_iter=1000, random_state=7)
        ).fit(matrix[self.columns], frame["responded"])
        return self

    def predict_proba(self, customers: pd.DataFrame) -> dict[str, np.ndarray]:
        if self.model is None:
            raise RuntimeError("fit the baseline before predicting")
        matrix, _ = build_features(customers)
        matrix = matrix.reindex(columns=self.columns, fill_value=0.0)
        out: dict[str, np.ndarray] = {}
        for arm in ARMS:
            z = matrix.copy()
            z["arm_OFFER_10"] = 1.0 if arm == "OFFER_10" else 0.0
            z["arm_OFFER_20"] = 1.0 if arm == "OFFER_20" else 0.0
            out[arm] = self.model.predict_proba(z[self.columns])[:, 1]
        return out
