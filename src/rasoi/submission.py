from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

PREDICTION_COLUMNS = [
    "customer_id",
    "pred_orders_no_offer",
    "pred_orders_10",
    "pred_orders_20",
    "pred_lift_10",
    "pred_lift_20",
]
PLAN_COLUMNS = [
    "customer_id",
    "offer",
    "expected_discount_inr",
    "expected_incremental_profit_inr",
]
OFFERS = {"NONE", "OFFER_10", "OFFER_20"}


class SubmissionError(ValueError):
    pass


def validate_predictions(
    predictions: pd.DataFrame, expected_customers: int = 200_000
) -> None:
    missing = [c for c in PREDICTION_COLUMNS if c not in predictions.columns]
    if missing:
        raise SubmissionError(f"predictions missing columns: {missing}")
    if len(predictions) != expected_customers:
        raise SubmissionError(
            f"predictions must have {expected_customers} rows, got {len(predictions)}"
        )
    if predictions["customer_id"].duplicated().any():
        raise SubmissionError("predictions have duplicate customer_id values")
    if predictions[PREDICTION_COLUMNS].isna().any().any():
        raise SubmissionError("predictions contain NaN")
    for column in ("pred_orders_no_offer", "pred_orders_10", "pred_orders_20"):
        if (predictions[column] < 0).any():
            raise SubmissionError(f"{column} must be non-negative")
    # Incremental lifts may be negative: some customers order less after a discount.


def validate_plan(
    plan: pd.DataFrame,
    eligible_ids: set[str] | None = None,
    expected_customers: int = 200_000,
) -> None:
    missing = [c for c in PLAN_COLUMNS if c not in plan.columns]
    if missing:
        raise SubmissionError(f"plan missing columns: {missing}")
    if len(plan) != expected_customers:
        raise SubmissionError(f"plan must have {expected_customers} rows, got {len(plan)}")
    if plan["customer_id"].duplicated().any():
        raise SubmissionError("plan has duplicate customer_id values")
    if not set(plan["offer"].unique()) <= OFFERS:
        raise SubmissionError(f"plan has invalid offers: {set(plan['offer'].unique()) - OFFERS}")
    if plan[PLAN_COLUMNS].isna().any().any():
        raise SubmissionError("plan contains NaN")
    if (plan["expected_discount_inr"] < 0).any():
        raise SubmissionError("expected_discount_inr must be non-negative")
    if eligible_ids is not None:
        contacted = plan.loc[plan["offer"] != "NONE", "customer_id"]
        bad = set(contacted) - eligible_ids
        if bad:
            raise SubmissionError(f"{len(bad)} opted-out customers were contacted")


def validate_portfolio(portfolio: dict, budget_inr: float) -> None:
    required = {
        "expected_discount_inr",
        "expected_incremental_profit_inr",
        "customers_offered",
        "opt_out_respected",
    }
    missing = required - set(portfolio)
    if missing:
        raise SubmissionError(f"portfolio missing keys: {sorted(missing)}")
    if float(portfolio["expected_discount_inr"]) > float(budget_inr) + 1e-6:
        raise SubmissionError("portfolio expected discount exceeds the budget")
    if not bool(portfolio["opt_out_respected"]):
        raise SubmissionError("portfolio reports opt-out violations")


def write_predictions(predictions: pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    predictions[PREDICTION_COLUMNS].to_csv(path, index=False, float_format="%.6f")


def write_plan(plan: pd.DataFrame, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plan[PLAN_COLUMNS].to_csv(path, index=False, float_format="%.2f")


def write_portfolio(portfolio: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(portfolio, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def build_manifest(out_dir: str | Path) -> dict:
    root = Path(out_dir)
    files = {}
    for name in ("predictions.csv", "plan.csv", "portfolio.json"):
        path = root / name
        if path.exists():
            files[name] = sha256_file(path)
    memo = root / "memo.md"
    slides = root / "slides.pdf"
    return {
        "schema_version": "1.0",
        "case_id": "m3-rasoi",
        "team_id": os.environ.get("RASOI_TEAM_ID", "local"),
        "commit": _git_commit(),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "entrypoints": {"submit": "make submit", "api": "uvicorn rasoi.serve.api:app"},
        "files": files,
        "memo": str(memo) if memo.exists() else None,
        "slides": str(slides) if slides.exists() else None,
        "bonus": [],
    }


def write_submission(
    out_dir: str | Path,
    predictions: pd.DataFrame,
    plan: pd.DataFrame,
    portfolio: dict,
    eligible_ids: set[str] | None = None,
    expected_customers: int = 200_000,
) -> dict:
    validate_predictions(predictions, expected_customers)
    validate_plan(plan, eligible_ids, expected_customers)
    validate_portfolio(portfolio, 8_000_000.0)
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    write_predictions(predictions, root / "predictions.csv")
    write_plan(plan, root / "plan.csv")
    write_portfolio(portfolio, root / "portfolio.json")
    manifest = build_manifest(root)
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest
