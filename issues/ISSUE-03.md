# ISSUE-03 · Optimise the offer portfolio under the shared budget

**Difficulty:** medium-hard · **Area:** `src/rasoi/assignment/optimizer.py` · **Tests:** hidden superset

## Context

`optimise_offers` is a stub. The budget is shared across all customers, so the
choice is not independent: spending ₹80 on one customer prevents spending it on
another. Greedy by incremental profit per rupee is a good baseline; a
Lagrangian (`maximise profit − θ·cost`, binary-search θ) handles the shared cap
better.

## What to change

- Implement `optimise_offers` with the given λ, cost and incremental-profit
  arrays.
- Exclude opt-outs.
- Respect the budget with a small safety margin.
- Return a Series aligned to the customer index.
- Keep it fast: 200,000 customers, under a few seconds.

## Acceptance

- Hidden tests for budget and opt-outs pass.
- The selected portfolio's expected spend is at or below ₹80 lakh.
- On the public trial holdout, the optimiser beats a single-threshold policy
  with the same spend. Show the numbers.
- The code is deterministic for a fixed input.

## Hints

Start with the unconstrained best arm per customer. If the spend is under the
budget, stop. Otherwise sort by `profit / cost` and remove the weakest offers
until the cap is met. A binary search on θ is the cleaner version.
