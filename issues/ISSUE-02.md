# ISSUE-02 · Fix the discount cost and select offers under the budget

**Difficulty:** medium-hard · **Area:** `src/rasoi/assignment/budget.py` · **Tests:** `tests/test_budget.py`

## Context

`expected_discount_cost` charges `d × AOV` for every offer, ignoring whether
the customer actually orders. The true expected cost is `d × AOV × P(order)`.
This understates spend for low-propensity customers and makes the budget
constraint look looser than it is.

## What to change

- Fix `expected_discount_cost(discount_pct, aov_inr, p_order)`.
- Implement `select_offers(customers, p0, p10, p20, budget_inr)`:
  - opt-outs are `NONE`;
  - one offer per customer;
  - expected discount at most the budget;
  - choose offers with positive incremental profit, not the highest propensity.

## Acceptance

- `pytest tests/test_budget.py -q` passes.
- Opt-outs are never contacted.
- The sum of expected discounts is at most the budget.
- On the trial holdout, your selection beats the top-propensity baseline on
  true expected profit at the same spend. Show the before/after.
- No hard-coded customer IDs or 200,000-row literals.

## Hints

The incremental profit for arm `d` is `55 × (λd − λ0) − cost_d`. Sort by
incremental profit per rupee of expected discount when the budget binds. A
customer with a high `P(order)` can have zero uplift; do not target them.
