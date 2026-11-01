# ISSUE-06 · Check the randomisation and build a holdout comparison

**Difficulty:** easy-medium · **Area:** `tests/`, `benchmarks/` · **Tests:** visible and hidden

## Context

The trial is the only fair comparison in the case. Before using it, check that
the arms are balanced on pre-treatment features and that the raw means move in
the expected direction. The shipped benchmark does not compare models, so a
reviewer cannot see whether a change helped.

## What to change

- Add a randomisation check: arm sizes, feature means, and a standardised
  difference for the key features.
- Add a `benchmarks/bench_uplift.py` that reports uplift MAE and true expected
  profit on a held-out slice for the baseline and the team model.
- Make the benchmark deterministic and under 60 seconds.
- Document the command in the README.

## Acceptance

- Arm sizes are within a few customers of each other.
- The benchmark prints UMAE, true profit, spend and customers offered for both
  policies.
- No hidden data is read.
- The CI green job runs the check in under a minute.

## Hints

Split the trial by customer, not by row. Use the control arm as the
counterfactual for the holdout evaluation. Do not tune on the holdout.
