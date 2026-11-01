import json

import pandas as pd

from rasoi.submission import (
    SubmissionError,
    validate_plan,
    validate_predictions,
    write_submission,
)


def _tiny_frames():
    predictions = pd.DataFrame(
        {
            "customer_id": ["CU-000001", "CU-000002", "CU-000003"],
            "pred_orders_no_offer": [1.0, 2.0, 0.5],
            "pred_orders_10": [1.2, 2.1, 0.9],
            "pred_orders_20": [1.3, 2.2, 1.0],
            "pred_lift_10": [0.2, 0.1, 0.4],
            "pred_lift_20": [0.3, 0.2, 0.5],
        }
    )
    plan = pd.DataFrame(
        {
            "customer_id": ["CU-000001", "CU-000002", "CU-000003"],
            "offer": ["OFFER_10", "NONE", "OFFER_20"],
            "expected_discount_inr": [42.0, 0.0, 84.0],
            "expected_incremental_profit_inr": [10.0, 0.0, 12.0],
        }
    )
    portfolio = {
        "expected_discount_inr": 126.0,
        "expected_incremental_profit_inr": 22.0,
        "customers_offered": 2,
        "opt_out_respected": True,
    }
    return predictions, plan, portfolio


def test_small_submission_round_trip(tmp_path):
    predictions, plan, portfolio = _tiny_frames()
    manifest = write_submission(
        tmp_path, predictions, plan, portfolio, expected_customers=3
    )
    assert (tmp_path / "predictions.csv").exists()
    assert (tmp_path / "plan.csv").exists()
    assert (tmp_path / "portfolio.json").exists()
    assert json.loads((tmp_path / "manifest.json").read_text())["case_id"] == "m3-rasoi"
    assert manifest["files"]


def test_opt_out_is_rejected():
    _, plan, _ = _tiny_frames()
    try:
        validate_plan(plan, eligible_ids={"CU-000001", "CU-000002"}, expected_customers=3)
    except SubmissionError:
        return
    raise AssertionError("an opted-out customer should have been rejected")


def test_negative_order_count_is_rejected():
    predictions, _, _ = _tiny_frames()
    predictions.loc[0, "pred_orders_10"] = -0.1
    try:
        validate_predictions(predictions, expected_customers=3)
    except SubmissionError:
        return
    raise AssertionError("negative order counts should have been rejected")


def test_negative_lift_is_allowed():
    predictions, _, _ = _tiny_frames()
    predictions.loc[0, "pred_lift_10"] = -0.1
    validate_predictions(predictions, expected_customers=3)
