# 11 — Anomaly Detection Design

The **numbers decide** whether something is unusual; the LLM only phrases the explanation.
See [ADR-005](adr/ADR-005-statistics-vs-llm-for-anomalies.md) for why.

## 1. When the checks run

At the end of each upload's background task, **all 4 checks re-run over all
transactions** (only ~600 rows, so it takes well under a second in SQL). Results are
**upserted** on `(transaction_id, type)`:
- a new anomaly → insert
- an existing one → update `score`/`details`, but **keep `dismissed`** as it was
- one that no longer qualifies (e.g. new data changed the average) → delete it, unless it was dismissed

**Scope:** only `direction = 'debit'` and categories other than `Transfers` and `Income`.

## 2. z-score vs rolling category average (FR-10)

For a debit *t* in category *c* on date *d*:

```
window(t) = debits in category c with date in [d − 90 days, d − 1 day]   (prior only, t excluded)
n         = count(window)
mean      = average(window amounts)
std       = sample standard deviation(window amounts)       (divides by n − 1)
z         = (t.amount − mean) / std
```

**Flag when:** `n ≥ 5` **and** `std > 0` **and** `z ≥ 2.5`.

| Guard | Why |
|---|---|
| `n ≥ 5` | With 1–4 data points the average is meaningless, and every early charge would be flagged |
| `std > 0` | Identical amounts (e.g. a fixed rent) would cause division by zero |
| prior window only | The charge being tested must not influence its own baseline |
| only high side (`z ≥ 2.5`, not `|z|`) | Spending *less* than usual isn't a problem to flag |

SQL sketch (Postgres window functions with a date `RANGE`):
```sql
SELECT id, amount,
       COUNT(*)            OVER w AS n,
       AVG(amount)         OVER w AS mean,
       STDDEV_SAMP(amount) OVER w AS std
FROM transactions
WHERE direction = 'debit' AND category NOT IN ('Transfers', 'Income')
WINDOW w AS (PARTITION BY category ORDER BY txn_date
             RANGE BETWEEN INTERVAL '90 days' PRECEDING AND INTERVAL '1 day' PRECEDING);
```
Postgres computes `AVG`/`STDDEV_SAMP` on `NUMERIC` exactly, so no floats are involved.
`score = z` (rounded to 3 places); `details = {mean, std, n}` (money as strings).

**Worked example:** Dining window: n = 12, mean = 25.00, std = 10.00. A $55.00 dinner →
z = (55 − 25) / 10 = **3.0 ≥ 2.5 → flagged**. A $45.00 dinner → z = 2.0 → not flagged.

## 3. Duplicate charge within 48h (FR-11)

Bank exports have **dates, not times**, so "within 48 hours" is approximated as **≤ 2
calendar days apart**. That's slightly generous (Mon 00:01 and Wed 23:59 is almost 72h),
but it never misses a true 48h duplicate.

```
Flag charge t if there is an earlier debit p (p.id < t.id) with
  p.merchant_normalized = t.merchant_normalized
  AND p.amount = t.amount
  AND t.txn_date − p.txn_date ≤ 2 days
```
SQL: `LAG(txn_date) OVER (PARTITION BY merchant_normalized, amount ORDER BY txn_date, id)`.
Only the **second** (and any later) charge is flagged. `details = {first_transaction_id, first_date, days_apart}`.
Small amounts are included, as Vish decided, so two coffees on one day get flagged; the user can dismiss them.

## 4. Large first charge at a new merchant (FR-12)

```
first(t)  = t is the earliest debit for its merchant_normalized (lowest date, then lowest id)
prior     = all debits dated before t.txn_date
median    = PERCENTILE_CONT(0.5) of prior amounts
Flag when: first(t) AND count(prior) ≥ 20 AND t.amount > 3 × median AND t.amount > 100.00
```
Guards: `count(prior) ≥ 20` plus a **30-day warm-up** (no flags in the first 30 days of
data), because at the start of a statement *every* merchant is "new".
`score = t.amount / median`; `details = {median, prior_n}`.

## 5. Subscription price increase (FR-13)

```
For debits in category Subscriptions, per merchant_normalized, ordered by date:
  prev = previous charge from the same merchant (LAG)
Flag t when: prev exists AND t.txn_date − prev.txn_date ≤ 45 days AND t.amount > prev.amount
```
The 45-day limit means it's a recurring charge (monthly, with some slack), not two unrelated one-off charges.
`score = % increase`; `details = {previous_amount, previous_date}`.

## 6. Explanations (FR-14) and the "no amounts to the LLM" rule

The hard rule says **amounts never go to the LLM**. So the LLM writes a **template with
placeholders**, and the code fills in the real numbers afterwards:

```text
LLM input:  type=zscore, category=Dining, merchant="BLUE BOTTLE", z_bucket="very high"
LLM output: "This {amount} charge at BLUE BOTTLE is much higher than your usual Dining spend of about {mean}."
Code fills: "This $55.00 charge at BLUE BOTTLE is much higher than your usual Dining spend of about $25.00."
```

- The LLM gets: flag type, category, merchant name, and a word bucket instead of the number
  (`z ≥ 4` → "extremely high", `≥ 3` → "very high", else "high").
- The output must contain only the allowed placeholders for that type and be ≤ 200 chars.
  Otherwise → template.
- **Fallback templates** (always available, also used in tests and CI):

| Type | Template |
|---|---|
| zscore | `{amount} at {merchant} is unusually high for {category} (usual ≈ {mean}).` |
| duplicate | `{merchant} charged {amount} twice within {days_apart} day(s). Possible duplicate.` |
| new_merchant_large | `First charge at {merchant} is {amount}, about {ratio}× your typical purchase.` |
| subscription_increase | `{merchant} went from {previous_amount} to {amount} (+{pct}%).` |

## 7. Thresholds are config, not magic numbers

| Setting | Default | Env var |
|---|---|---|
| z threshold | 2.5 | `ANOMALY_Z_THRESHOLD` |
| z window | 90 days | `ANOMALY_Z_WINDOW_DAYS` |
| z min samples | 5 | `ANOMALY_Z_MIN_N` |
| duplicate window | 2 days | `ANOMALY_DUP_DAYS` |
| new-merchant multiplier / floor | 3 / 100.00 | `ANOMALY_NEW_MULT`, `ANOMALY_NEW_MIN` |
| subscription max gap | 45 days | `ANOMALY_SUB_GAP_DAYS` |

## 8. Testing

- The generator plants **≥ 3 of each type**, with known transaction IDs → **recall must be
  100%** for zscore + duplicate (SM-3).
- Unit tests at the edges: z exactly 2.5 (flagged), 2.49 (not), n = 4 (skipped), std = 0
  (skipped), duplicates 2 days apart (flagged) vs 3 (not), a subscription decrease (not flagged).
- Re-running the checks twice gives the same rows (idempotency), and dismissed flags stay dismissed.
