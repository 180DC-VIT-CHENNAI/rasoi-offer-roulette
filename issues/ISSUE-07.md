# ISSUE-07 · Harden submission reproducibility and edge cases

**Difficulty:** medium · **Area:** `submission.py`, `Makefile`, `tests/`

## Context

The engine reruns `make submit` in a clean container and compares the submitted
files. A submission that depends on a notebook state, a random seed, or a
generated artefact outside `data/public` loses the 10 reproducibility points.
The hidden suite also checks negative lifts, opt-outs, a budget violation and a
missing customer.

## What to change

- Make `make submit` deterministic: fixed seeds, sorted output, no timestamps
  in the scored files.
- Add `make clean-room`: copy the repo, run `submit`, compare values within
  ₹1 / 1e-6.
- Add tests for: negative lift allowed, negative expected order count rejected,
  opt-out rejected, budget violation rejected, missing customer rejected.
- Ensure the manifest hashes match the files after a rerun.

## Acceptance

- Two clean runs produce identical `predictions.csv` and `plan.csv` hashes.
- `make clean-room` exits non-zero on a mismatch and prints the differing rows.
- The new tests fail on the starter where appropriate and pass on a correct
  implementation.
- No hidden data or generated submission files are committed.

## Hints

Use `pandas.testing.assert_frame_equal` with a tolerance for float columns.
Sort by `customer_id` before writing. For the budget, use the true expected
cost, not the claimed one.
