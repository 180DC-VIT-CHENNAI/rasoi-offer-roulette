# Scoring and the hidden simulator

Marketing track rubric. The Finance track's 76-automated-point structure does
**not** apply here.

## The 100 points

| Part | Points | What it measures | Mode |
|---|---:|---|---|
| Hidden extra profit | 40 | True incremental profit of your plan under the organisers' response curves, net of discounts | automated |
| Hidden uplift accuracy | 20 | Mean absolute error of `pred_lift_10` and `pred_lift_20` against the true incremental orders | automated |
| Memo | 20 | Two-page decision memo, four-item rubric | semi-automated + human |
| Reproducibility | 10 | Clean-room `make submit` reproduces the submitted files | automated |
| Demo | 10 | Five-minute defence | human |

The hidden 60 is normalised against three anchors: a trivial floor (blanket 20%
to every eligible customer), the shipped baseline, and the reference solution.
Matching the baseline earns 40% of the hidden category; matching the reference
earns 100%.

## Gates

- Every one of the 200,000 customers appears exactly once.
- `offer` is one of `NONE`, `OFFER_10`, `OFFER_20`.
- No opted-out customer is contacted.
- The **true** expected discount spend (evaluated on hidden response) is at
  most ₹80 lakh. The engine does not trust the claimed cost.
- `predictions.csv` has no NaN and non-negative expected order counts; lifts
  may be negative.

A budget or opt-out violation sets the 40 profit points to zero and adds a flag
for the judges. The 20 accuracy points are still awarded.

## How the hidden simulator works

For each customer the organisers hold the true `λ0`, `λ10`, `λ20`, AOV and the
resulting expected cost and profit. Given your plan:

```
true_extra_profit = Σ_i [ profit_i(offer_i) − 55·λ0_i ]
true_discount     = Σ_i cost_i(offer_i)
```

There is no random draw in the final score; the expected values are used so a
lucky trial draw does not decide the ranking. The public trial is one noisy
realisation, which is why a model must use features, not just the raw arm means.

## Memo rubric (20)

Four items, each 0–3, scaled to 12, plus 8 for the defence:

1. **Uplift evidence.** Show that the model predicts incremental orders, not
   order propensity. Compare with the blanket-coupon and no-offer policies.
2. **Money.** State the expected discount spend, the incremental profit, and
   the profit per rupee of discount. Every number must trace to a submission
   file.
3. **Who is left out.** Explain opt-outs, low-uplift customers and the
   customers who order less after a 20% offer. Say whether that is acceptable.
4. **Budget and risk.** What happens if the uplift model is wrong by 20%? What
   would you test next month, and what would you stop?

The defence is five minutes plus questions. Judges reward a recommendation
that is consistent with the team's own predicted numbers.

## Anti-gaming

- The hidden response curves are never shipped. A submission that scores
  suspiciously well (uplift MAE below 0.05) is flagged for review.
- `make submit` is rerun in a clean container. If the files do not reproduce,
  the reproducibility points are lost and the rebuilt files are scored.
- Hidden IDs are disjoint from the public range where the case permits.
- Do not read hidden paths, open sockets, or write outside the submission
  directory. The sandbox blocks and logs attempts.
- Tie-breaks: higher true extra profit, then lower uplift MAE, then earlier
  tag.

## Local checks

```bash
make test          # three visible failures encode the starter defects
make submit
python -c "import pandas as pd; p=pd.read_csv('submission/plan.csv'); print(p.offer.value_counts()); print(p.expected_discount_inr.sum())"
```

The hidden suite is a superset of the visible tests. Passing the visible tests
is necessary, not sufficient.
