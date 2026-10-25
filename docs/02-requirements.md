# 02 — Requirements

Priorities use **MoSCoW**: **M**ust (release fails without it), **S**hould (important,
cut only if behind), **C**ould (nice to have), **W**on't (explicitly not this release).

## Functional requirements

### Data in
| ID | Requirement | Priority |
|---|---|---|
| FR-01 | The user can upload a Format B CSV (`Date, Description, Debit, Credit`) through the web UI. The system validates headers, dates, and amounts, and rejects bad files with row-level error messages (row number + reason). | M |
| FR-02 | The system normalizes merchant descriptions (uppercase, strip store numbers, card/reference suffixes, city/province, extra spaces) into a `merchant_normalized` value. | M |
| FR-03 | The system de-duplicates rows **across uploads** using a row hash. Identical rows **within the same file** are kept (the hash includes the row's occurrence index), so a real double charge isn't silently dropped. | M |
| FR-04 | A synthetic data generator produces ~600 rows over 6 months in Format B, with ground-truth categories and a list of planted anomalies. | M |

### Categorization
| ID | Requirement | Priority |
|---|---|---|
| FR-05 | Each transaction is categorized **rules-first**: a match on `merchant_rules` (exact or pattern) wins. | M |
| FR-06 | Unmatched merchants go to the local LLM. Output is structured and restricted to the 13 fixed categories, plus a confidence value. Only `merchant_normalized` is sent. | M |
| FR-07 | LLM results are cached per normalized merchant, so the same merchant is never sent twice. | M |
| FR-08 | The user can change a transaction's category. The correction creates or updates a merchant rule and re-categorizes other transactions from that merchant. | M |
| FR-09 | Each transaction records its category source: `rule`, `llm`, `cache`, or `user`. | S |

### Anomaly detection
| ID | Requirement | Priority |
|---|---|---|
| FR-10 | **z-score:** flag a debit when z ≥ 2.5 vs the rolling 90-day mean/std of the same category (requires ≥ 5 prior transactions in the window). | M |
| FR-11 | **Duplicate:** flag a debit when the same merchant + same amount appears again within 48 hours (small amounts included). | M |
| FR-12 | **Large first charge:** flag the first-ever charge at a merchant when it is > 3× the user's median debit **and** > $100. | S |
| FR-13 | **Subscription increase:** flag when a recurring Subscriptions merchant charges more than its previous charge. | S |
| FR-14 | Each flag gets a 1–2 sentence explanation written by the LLM from the flag type and numbers computed by the code (no account info). If the LLM fails, a template explanation is used. | S |
| FR-15 | A Flags page lists all flags with type, transaction, explanation, and lets the user dismiss a flag. | S |

### Insights
| ID | Requirement | Priority |
|---|---|---|
| FR-16 | Dashboard: spending by category for a selected month (chart + totals). | M |
| FR-17 | Dashboard: monthly spending trend with month-over-month change (SQL window functions). | M |
| FR-18 | Dashboard: income vs expenses per month. | M |
| FR-19 | Transactions table with filter by month and category, and inline category editing (uses FR-08). | M |
| FR-20 | Dashboard: top 10 merchants by spend. | C |
| FR-21 | Dashboard: flagged-items widget (latest 5 flags). | C |
| FR-22 | "Ask about my spending" agent: answers questions using **only** 3 read-only tools: `spend_by_category`, `top_merchants`, `get_anomalies`. Never writes or runs SQL. | M |

### Quality & ops
| ID | Requirement | Priority |
|---|---|---|
| FR-23 | An eval script reports overall accuracy, per-category precision, % of rows that needed an LLM call, and anomaly recall vs ground truth. | M |
| FR-24 | Per-IP rate limit on upload and agent endpoints, plus a daily cap on LLM calls. (Downgraded from Should: no public demo now that AWS is out of scope.) | C |
| FR-25 | Health endpoint reports API, database and Ollama status. | S |
| FR-26 | Export transactions to CSV. | W |
| FR-27 | User accounts / authentication. | W |

## Non-functional requirements

| ID | Category | Requirement | Priority |
|---|---|---|---|
| NFR-01 | Security | No secrets in git. Config comes from environment variables; `.env` is gitignored and `.env.example` is committed. | M |
| NFR-02 | Security | All SQL goes through the SQLAlchemy ORM/Core with bound parameters; no string-built SQL. | M |
| NFR-03 | Security | Upload limits: `.csv` only, ≤ 2 MB, ≤ 5,000 rows. Oversized or invalid files are rejected with HTTP 4xx, not 500. | M |
| NFR-04 | Security | Merchant text is treated as untrusted input: LLM output must validate against the category enum (Pydantic), otherwise it falls back to `Other`. This defends against prompt injection in descriptions. | M |
| NFR-05 | Security | The agent can only call its 3 tools; tool inputs are validated with Pydantic; there's a max of 5 tool calls per question. | M |
| NFR-06 | Privacy | Synthetic data only. Only the normalized merchant description is sent to the LLM. The LLM runs locally, so no data leaves the machine. | M |
| NFR-07 | Data integrity | Money is `NUMERIC(12,2)` in Postgres and `Decimal` in Python, and is serialized as strings in JSON. Floats are never used for money. | M |
| NFR-08 | Performance | First upload of 600 rows ≤ 120 s on a laptop CPU; re-upload with a warm cache ≤ 5 s. | S |
| NFR-09 | Performance | Dashboard/analytics endpoints p95 < 500 ms on the 600-row dataset. | S |
| NFR-10 | Reliability | If Ollama is down, upload still succeeds: unmatched rows get `Other` + `needs_review`, flag explanations use templates, and the agent returns a clear "assistant unavailable" message. | M |
| NFR-11 | Cost | $0: no paid APIs or cloud services. | M |
| NFR-12 | Accessibility | WCAG 2.1 AA basics: keyboard navigable, labelled form controls, chart colours not the only signal (labels/legend/table fallback), text contrast ≥ 4.5:1. | S |
| NFR-13 | Maintainability | `ruff` clean, type hints on the backend, `tsc --noEmit` clean on the frontend, backend coverage ≥ 80%. | S |
| NFR-14 | Portability | `docker compose up` starts everything (db, api, web, ollama) on Windows/macOS/Linux; setup documented in the README. | M |
| NFR-15 | Observability | Structured logs with a request ID; LLM call count and latency are logged. | C |
| NFR-16 | Process | Every change goes through an issue → branch → PR with green CI. | M |
