# 01 — Project Charter: SpendSense

| | |
|---|---|
| **Owner / developer** | Vish |
| **Mentor / reviewer** | Claude (senior engineer role) |
| **Audience** | Recruiters and interviewers for banking/fintech roles |
| **Timebox** | 3 working days (3 one-day sprints) |
| **Budget** | $0 |
| **Status** | Draft, awaiting sign-off |

## 1. Problem

Freelancers mix personal and business spending on the same account. Their bank
statement is a long, noisy list of cryptic merchant strings (`SQ *BLUE BOTTLE #1234
TORONTO ON`). It's hard to answer simple questions like "where did my money go this
month?", "what did I spend on business?" or "was I double-charged?".

## 2. Goals

1. **Understand spending:** turn a raw statement CSV into categorized transactions,
   with no manual tagging for common merchants.
2. **Catch problems:** flag unusual or suspicious charges using explainable statistics,
   not a black box.
3. **Learn from the user:** every manual correction becomes a rule, so the same mistake
   never happens twice.
4. **Answer questions:** let the user ask about their spending in plain English, safely.
5. **Portfolio goal:** show a full SDLC (requirements → design → build → test → release
   → retro) that Vish can explain line by line.

## 3. Success metrics

| # | Metric | Target | How we measure |
|---|---|---|---|
| SM-1 | Categorization accuracy (overall) | **≥ 90%** | Eval script vs ground-truth labels in the synthetic data |
| SM-2 | Rows that needed an LLM call | ≤ 30% on first upload | Counter in the eval script |
| SM-3 | Planted anomalies detected (recall) | 100% of planted z-score + duplicate cases | Eval script vs the generator's planted list |
| SM-4 | First upload time, 600 rows, laptop CPU | ≤ 120 s (incl. local LLM) | Timed in an integration test / manual run |
| SM-5 | Re-upload time, same file (cache warm) | ≤ 5 s | Same as SM-4 |
| SM-6 | Dashboard API response time, p95 | < 500 ms | API tests with timing |
| SM-7 | Backend test coverage | ≥ 80% | `pytest --cov` |
| SM-8 | CI | Green on every merged PR | GitHub Actions history |
| SM-9 | Money spent | $0 | No paid services used |

## 4. Scope

### In scope
- Upload one bank CSV format ("Format B": separate Debit/Credit columns), synthetic only
- Validation, merchant normalization, de-duplication across uploads
- Rules-first categorization with a local LLM fallback (Ollama), cached per merchant
- 13 fixed categories, including **Business Expense**
- Category corrections that create merchant rules
- Four anomaly checks: z-score (≥ 2.5), duplicates within 48h, large first charge at
  a new merchant, subscription price increase. The LLM writes short explanations.
- Dashboard: spending by category, monthly trends, income vs expenses
- Flags page, editable transactions table
- "Ask about my spending" agent with 3 fixed read-only tools
- Synthetic data generator with ground truth; accuracy eval
- Local run via Docker Compose; CI on GitHub Actions

### Out of scope
- Real bank data or real account numbers, ever
- Cloud deployment (AWS). Deferred, with the reasoning recorded in an ADR in Phase 2.
- Other CSV formats (the parser is designed so one can be added later)
- User accounts / login / multi-user
- Live bank connections (e.g., Open Banking APIs)
- Multi-currency (CAD only)
- Budgets, goals, forecasting, mobile app

## 5. Constraints

- **Time:** 3 days, including documentation and testing. Vish writes the code with guidance.
- **Cost:** $0. Only free/open-source tools; the public GitHub repo gets free Actions minutes.
- **Stack:** fixed in CLAUDE.md; changes only through an approved ADR.
- **Hardware:** the local LLM must run on Vish's laptop (CPU, limited RAM).
- **Privacy:** only the merchant description is sent to the LLM, never amounts or
  account info (even though the LLM is local).
- **Money:** `NUMERIC` in Postgres / `Decimal` in Python, never float.

## 6. Assumptions

- One user per running instance (no auth needed).
- Statements are ≤ 5,000 rows and ≤ 2 MB.
- Ollama with a small (3–8B) instruct model is good enough for categorization when
  rules handle most rows.

## 7. Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Owner | Vish | | |
