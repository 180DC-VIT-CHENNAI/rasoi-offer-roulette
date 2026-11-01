# Data dictionary

Synthetic data, fixed seed. Money is in rupees. Dates are ISO-8601. The
snapshot is **31 August 2026**. The trial ran **1–30 September 2026**. The
campaign decision is for **1–31 October 2026**.

## `customers.parquet` (200,000 rows)

| Column | Type | Notes |
|---|---|---|
| `customer_id` | string | `CU-000001` … |
| `city` | string | Eight Indian cities |
| `signup_date`, `tenure_days` | date, int | Tenure at the snapshot |
| `loyalty_tier` | enum | `BRONZE`, `SILVER`, `GOLD` from historical frequency |
| `cuisine_pref` | enum | Six cuisines |
| `device_type` | enum | `Android`, `iOS` |
| `promo_opt_out` | bool | ~6% of customers; **never contact** |
| `orders_30d`, `orders_90d`, `orders_180d` | int | Counts from the order log |
| `avg_order_value_inr` | float | Mean historical order value |
| `days_since_last_order` | int | 999 if no order in 180 days |
| `app_sessions_30d` | int | App engagement |
| `historical_discount_rate` | float | Share of historical orders with a discount; the best observed proxy for price sensitivity |
| `avg_discount_pct` | float | Mean discount on discounted orders |
| `weekend_share`, `late_night_share` | float | Order timing |

**No post-offer columns are in this file.** `orders_30d_after`,
`gmv_30d_after`, `discount_inr_used` and `responded` exist only in the trial.
Joining them onto the campaign snapshot is leakage.

## `orders_180d.parquet` (2,082,718 rows)

`order_id, customer_id, order_ts, order_value_inr, discount_pct (0/10/20),
cuisine, delivery_zone, restaurant_id, channel`. Use it for frequency,
recency, concentration and discount-sensitivity features. Do not use orders
after 31 August 2026 (there are none in this file).

## `trial.parquet` (40,000 rows)

`customer_id, offer_date, offer_bucket (CONTROL/OFFER_10/OFFER_20),
orders_30d_after, gmv_30d_after, discount_inr_used, responded`.

The trial is a random 20% of customers, assigned 1:1:1. The control third is a
deliberate holdout inside the trial; the case needs a fair counterfactual.
Check the randomisation before trusting it: arm sizes, pre-treatment feature
balance, and the raw order means. The treatment effect is real but noisy at the
individual level.

## `campaign.json`

Dates, the 200,000-customer base, the ₹80 lakh budget, the ₹55 profit per order
before discounts, and the constraint that the offer applies to the customer's
first redeemed order in the window.

## Economics

For customer `i` and offer `d ∈ {10, 20}`:

```
λ_i(d)      = expected orders in 30 days under offer d
P_i(d)      = 1 − exp(−λ_i(d))              # Poisson approximation
cost_i(d)   = (d/100) × AOV_i × P_i(d)      # one discounted first order
profit_i(d) = 55 × λ_i(d) − cost_i(d)
incremental = profit_i(d) − 55 × λ_i(0)
```

The budget is the sum of `cost_i(d)` over offered customers, not the number of
coupons × AOV. The true response curves are hidden; the trial is your estimate.

Some customers have **negative** uplift at 20%: they stock up, wait for
discounts, or shift orders. A model that cannot predict a negative lift is
structurally wrong.

## Defect classes in the starter

- The propensity baseline uses `P(order)` as if it were incremental orders.
- `expected_discount_cost` omits `P(order)`.
- `incremental_profit` charges the discount on every order, not the first.
- The offer optimizer and uplift model are stubs.
- The API and dashboard are shells.

The public data dictionary deliberately does not list the hidden response
parameters. The hidden set uses the same generator; every hidden feature has a
visible precursor.
