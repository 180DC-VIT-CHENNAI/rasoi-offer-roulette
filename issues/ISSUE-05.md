# ISSUE-05 · Serve an offer and show the targeting dashboard

**Difficulty:** medium · **Area:** `src/rasoi/serve/`, `ui/` · **Tests:** `tests/test_api.py`

## Context

`GET /predict/{customer_id}` is a 501 shell. The Streamlit page has empty
charts. The decision-maker needs a single-customer view and a team needs to see
the uplift deciles and the budget curve.

## What to change

- Load the persisted uplift model and campaign data at start-up.
- Return `{customer_id, offer, expected_discount_inr,
  expected_incremental_profit_inr, reason}` with 200.
- Respect opt-outs (return `NONE` with a reason).
- Wire the dashboard: uplift deciles, profit vs spend with the budget marked,
  and a waterfall from no-offer to blanket to targeted.

## Acceptance

- `pytest tests/test_api.py -q` passes.
- Unknown customer IDs return `NONE`, not a 500.
- `streamlit run ui/app.py` starts and renders without an exception.
- The API does not refit the model per request.
- Hidden contract tests pass.

## Hints

Persist the model with joblib or a small JSON of coefficients. The API is a
read-only decision surface, not a training job. Keep the reason codes short and
human.
