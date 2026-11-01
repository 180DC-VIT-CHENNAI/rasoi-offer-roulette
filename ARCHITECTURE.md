# Architecture

```
data/public ──► io.loaders ──► features/customer ──► model/propensity
                                      │                    │
                                      ▼                    ▼
                               model/uplift (team)   assignment/budget
                                      │                    │
                                      └────► assignment/optimizer
                                                     │
                                                     ▼
                                          simulate/revenue
                                                     │
                                                     ▼
                                        submission/{predictions,plan,portfolio}
```

The CLI contract is the judge's entry point:

```
rasoi submit --data data/public --out submission/
```

## Module responsibilities

| Module | Responsibility | Debt |
|---|---|---|
| `config.py` | Campaign dates, budget, economics | none |
| `io/loaders.py` | Parquet loaders with dates | no schema versioning |
| `features/customer.py` | Snapshot feature matrix | deliberately simple; ISSUE-01 |
| `features/history.py` | Order-log aggregates | partial |
| `model/propensity.py` | Baseline `P(order)` | uses propensity as uplift |
| `model/uplift.py` | Incremental model | stub; ISSUE-01 |
| `model/train.py` | Shared training entry point | stub wrapper |
| `assignment/budget.py` | Expected discount and selection | cost bug; ISSUE-02 |
| `assignment/optimizer.py` | Budget-constrained assignment | stub; ISSUE-03 |
| `simulate/revenue.py` | Incremental profit | first-order bug; ISSUE-04 |
| `serve/api.py` | Read-only offer API | 501; ISSUE-05 |
| `submission.py` | Schema, hashes, writer | no clean-room target |
| `cli.py` | inspect / train / submit | baseline is the only default |

## Design decisions

**The trial is the identification strategy.** 40,000 customers, 1:1:1. The
control third is a real holdout, not a discarded arm. Any model that ignores
the randomisation and fits `P(order)` will target the wrong customers.

**The 30-day window is common across arms.** The trial outcomes are one 30-day
realisation; the campaign is another 30 days. Do not mix the trial window into
the campaign features.

**The discount is a first-order cost.** A coupon applies once. The budget is the
sum of expected discounts, not `coupons × AOV`.

**Negative uplift is real.** A 20% coupon can reduce a customer's subsequent
orders. The schema allows negative predicted lifts; the plan should simply not
buy those offers.

**The baseline is valid by construction.** `make submit` uses the propensity
baseline and a top-50k heuristic; it writes 200,000 rows and passes the schema.
It is wrong about the decision, not broken.

## Performance envelope

- 200,000 customers; 2.08 million order rows; 46 MB Parquet.
- Load + baseline fit + submit: under 10 seconds on 4 cores / 8 GB.
- Uplift training should stay under a minute; no GPU.
- The API must return in well under 100 ms; persist the model.

## Judging boundary

The hidden response curves are never mounted in the participant container. The
scorer recomputes the true cost and profit. Do not attempt to read hidden paths
or open sockets; attempts are logged and disqualify the submission.
