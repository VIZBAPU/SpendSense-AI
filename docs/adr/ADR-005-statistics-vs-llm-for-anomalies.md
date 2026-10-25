# ADR-005: Statistics decide anomalies; the LLM only explains

- **Status:** Accepted
- **Date:** 2026-10-25

## Context
We flag unusual spending (spikes, duplicates, large first charges, price increases). We
could ask the LLM "is this transaction unusual?", or compute it with rules and statistics.

## Options considered

| | **A. Statistical/rule checks (SQL)** | **B. LLM judges each transaction** |
|---|---|---|
| Explainable | Exact formula + numbers ("z = 3.0 vs 90-day Dining average") | "The model thought so" |
| Deterministic | Same data → same flags, every time | Can vary between runs and models |
| Testable | Unit tests at exact thresholds (2.5 vs 2.49) | Hard to test; needs an eval set |
| Privacy | Amounts stay in the DB | Would have to send amounts to the LLM (breaks a hard rule) |
| Cost/speed | Milliseconds in SQL, free | One LLM call per transaction; slow on CPU |
| Catches novel patterns | Only what we coded | Might notice odd things we didn't think of |

## Decision
**A.** The four checks are computed in SQL/Python with fixed, configurable thresholds
(11-anomaly-design). The LLM is used only to **phrase** an explanation, through a
placeholder template that never contains amounts.

## Consequences
- ✅ Every flag can be justified to a user, or a regulator ("model risk" teams in banks ask exactly this).
- ✅ 100% recall on planted anomalies is a testable requirement.
- ❌ We only catch the patterns we defined. Adding a new pattern means writing a new check.
- ❌ Thresholds need tuning; they're env-var config, not code changes.
