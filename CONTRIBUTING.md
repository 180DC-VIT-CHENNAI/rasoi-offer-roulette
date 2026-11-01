# Contributing

This is a DOOMFORGE 2026 engineering repository. The judges read the diff, not
the commit count.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make test
```

The public data is in `data/public`; do not edit it. Add fixtures under
`tests/fixtures/` for unit tests.

## Pick an issue

`issues/` is ordered by dependency:

- `ISSUE-01` uplift model (core)
- `ISSUE-02` budget accounting and offer selection
- `ISSUE-03` optimizer under the shared budget
- `ISSUE-04` first-order discount economics and portfolio claims
- `ISSUE-05` API and dashboard
- `ISSUE-06` randomisation checks, backtest and baseline comparison
- `ISSUE-07` reproducibility and edge-case hardening

## Branch and PR

```bash
git switch -c feat/issue-01-uplift
# code, tests, docs
make test lint typecheck
git push -u origin feat/issue-01-uplift
```

A useful PR links the issue and shows a before/after metric on a holdout:
uplift MAE, true extra profit, budget spend, or a failing test now passing. Do
not change a test expectation to hide a defect. Do not commit generated
submission files or hidden data. Do not hard-code customer IDs, hidden
responses, or the 200,000-row answers.

## Code style

- Python 3.11, `ruff` and `mypy` clean.
- Pure feature functions; no network calls.
- Keep the CLI contract: `rasoi submit --data ... --out ...`.
- Keep the submission schema and the 200,000-customer coverage.

## Security

Participant code runs with no network and a read-only filesystem. Hidden
response curves are not in the container. Attempts to read them disqualify the
submission.

## Licence

MIT. By contributing you agree to the licence in `LICENSE`.
