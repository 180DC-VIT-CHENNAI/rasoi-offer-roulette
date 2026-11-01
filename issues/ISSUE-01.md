# ISSUE-01 · Build the uplift model

**Difficulty:** hard · **Area:** `src/rasoi/model/uplift.py` · **Tests:** `tests/test_uplift.py`

## Context

The shipped baseline predicts `P(order)` and uses it as if it were the
incremental effect of a coupon. The campaign's whole economics depend on the
difference between "would have ordered" and "ordered because of the offer".
The trial randomises 40,000 customers 1:1:1, so the effect is identifiable.

## What to change

Implement `UpliftModel.fit` and `UpliftModel.predict`:

- Fit the control outcome and the treatment-arm outcomes from the trial.
- Predict expected 30-day orders `λ0`, `λ10`, `λ20` for all 200,000 customers.
- Return `lift10 = λ10 − λ0` and `lift20 = λ20 − λ0`; negative lifts are valid.
- Use only pre-treatment features. Do not join trial outcomes onto the campaign
  snapshot.
- Persist the model for the API if you add one.

## Acceptance

- `pytest tests/test_uplift.py -q` passes.
- Predictions are finite, non-negative for order counts, and 200,000 rows.
- On a held-out slice of the trial, your model beats the propensity baseline on
  uplift MAE. Show the number.
- The model can predict negative 20% lifts for the deal-trained segment.
- `make lint typecheck` stay clean.

## Hints

The trial is small and noisy; a T-learner, an S-learner with treatment
interactions, a transformed-outcome model, or a causal forest all work. The
latent price sensitivity is not in the data; `historical_discount_rate`,
`avg_discount_pct`, recency and tenure are the observable proxies. Regularise.
A model that predicts a constant lift will lose the accuracy points.
