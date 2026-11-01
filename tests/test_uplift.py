"""ISSUE-01: the uplift model is a stub and these tests fail initially."""

import numpy as np

from rasoi.model.uplift import UpliftModel


def test_uplift_model_returns_incremental_orders(bundle):
    model = UpliftModel().fit(bundle.trial, bundle.customers)
    predictions = model.predict(bundle.customers)
    assert len(predictions.lift10) == len(bundle.customers)
    assert len(predictions.lift20) == len(bundle.customers)
    assert np.isfinite(predictions.lift10).all()
    assert np.isfinite(predictions.lift20).all()
    assert (predictions.lambda0 >= 0).all()
