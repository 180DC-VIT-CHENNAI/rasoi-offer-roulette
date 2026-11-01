from __future__ import annotations

import pandas as pd

from rasoi.model.uplift import UpliftModel


def train_uplift(trial: pd.DataFrame, customers: pd.DataFrame) -> UpliftModel:
    """Fit and return the team's uplift model.

    ISSUE-01: this is a thin wrapper so the CLI and the hidden tests share one
    entry point.  Persist any artefacts under artifacts/ and load them in the
    API rather than refitting per request.
    """
    return UpliftModel().fit(trial, customers)
