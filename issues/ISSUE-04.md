# ISSUE-04 · Apply the discount to the first order, not every order

**Difficulty:** medium · **Area:** `src/rasoi/simulate/revenue.py` · **Tests:** hidden superset

## Context

A coupon applies once, to the customer's first redeemed order in the 30-day
window. `incremental_profit` currently multiplies the discount by the expected
number of orders (`λ`), which overstates the cost for frequent customers and
understates it for sporadic ones. The portfolio's claimed profit inherits the
error, and the memo's numbers will not reconcile with the submission files.

## What to change

- Use `cost = (d/100) × AOV × (1 − exp(−λ_offer))`.
- Compute `incremental = 55 × (λ_offer − λ0) − cost`.
- Update `portfolio_expected_profit` to use the same rule.
- Make the claimed portfolio numbers traceable to `plan.csv`.

## Acceptance

- The hidden first-order-discount tests pass.
- `incremental_profit(1, 2, 400, 10)` equals
  `55 − 0.10 × 400 × (1 − e^−2)`.
- A zero-uplift customer has negative incremental profit, not zero.
- The memo's claimed expected profit agrees with `portfolio.json` within 1%.

## Hints

The Poisson probability of at least one order is `1 − exp(−λ)`. Do not confuse
expected orders with the redemption probability.
