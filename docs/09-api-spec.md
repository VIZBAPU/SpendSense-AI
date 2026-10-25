# 09 — API Specification

Base URL (local): `http://localhost:8000`. FastAPI also serves interactive docs at `/docs`.

## 1. Conventions

- **JSON** everywhere, except the file upload (`multipart/form-data`).
- **Money** is a **string** with 2 decimals: `"42.50"`. Never a JSON number, which a
  browser would parse as a float.
- **Dates** are ISO `YYYY-MM-DD`; **months** are `YYYY-MM`.
- **Categories** are exactly one of: `Groceries`, `Dining`, `Transport`, `Rent/Housing`,
  `Utilities`, `Subscriptions`, `Shopping`, `Health`, `Entertainment`, `Income`,
  `Transfers`, `Business Expense`, `Other`.
- **Lists** are paginated with `?page=1&page_size=50` (max 200) and return
  `{"items": [...], "page": 1, "page_size": 50, "total": 612}`.
- **Errors** always have this shape:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "2 rows failed validation",
    "details": [ { "row": 7, "field": "Date", "message": "invalid date '13/45/2026'" } ]
  }
}
```

| HTTP | `code` | When |
|---|---|---|
| 400 | `BAD_REQUEST` | Missing file / malformed request |
| 404 | `NOT_FOUND` | Unknown id |
| 413 | `FILE_TOO_LARGE` | Upload > 2 MB or > 5,000 rows |
| 415 | `UNSUPPORTED_TYPE` | Not a `.csv` |
| 422 | `VALIDATION_FAILED` | Bad headers, bad rows, invalid category, bad query params |
| 429 | `RATE_LIMITED` | Could-have (US-17) |
| 503 | `LLM_UNAVAILABLE` | Agent called while Ollama is down |
| 500 | `INTERNAL_ERROR` | Bug; message is generic, details are only in the logs |

## 2. Endpoints

### `GET /health` (US-01)
```json
200 { "status": "ok", "db": "up", "ollama": "up", "model": "qwen2.5:7b" }
```
`status` is `"degraded"` if Ollama is down (still 200, since the app works without it), and
returns 503 only if the DB is down.

---

### `POST /uploads` (US-03)
Body: `multipart/form-data` with a field `file`, a Format B CSV:
```csv
Date,Description,Debit,Credit
03/02/2026,SQ *BLUE BOTTLE #1234 TORONTO ON,6.75,
03/02/2026,CLIENT PAYMENT - ACME DESIGN,,2500.00
```
Rules: `Date` is `MM/DD/YYYY`; exactly one of `Debit`/`Credit` is filled in per row, and it's > 0
with ≤ 2 decimals; `Description` is not empty.

**201 Created**
```json
{
  "id": 12,
  "filename": "statement_2026H1.csv",
  "status": "categorizing",
  "row_count": 612,
  "inserted_count": 604,
  "duplicate_count": 8,
  "rule_categorized_count": 455,
  "pending_llm_count": 149
}
```
**Errors:** 400 (no `file`), 413, 415, 422 (wrong headers, or any invalid row; **nothing is saved**).

### `GET /uploads/{id}`
```json
200 {
  "id": 12, "status": "done", "row_count": 612, "inserted_count": 604,
  "duplicate_count": 8, "llm_calls": 8, "anomaly_count": 23,
  "created_at": "2026-10-26T14:02:11Z", "finished_at": "2026-10-26T14:03:40Z", "error": null
}
```
**Errors:** 404.

---

### `GET /transactions` (US-10)
Query: `month` (`YYYY-MM`, optional), `category` (optional), `needs_review` (bool, optional), `page`, `page_size`.
```json
200 {
  "items": [
    {
      "id": 381, "txn_date": "2026-03-02",
      "description_raw": "SQ *BLUE BOTTLE #1234 TORONTO ON",
      "merchant_normalized": "BLUE BOTTLE",
      "direction": "debit", "amount": "6.75",
      "category": "Dining", "category_source": "rule", "needs_review": false
    }
  ],
  "page": 1, "page_size": 50, "total": 604
}
```
**Errors:** 422 (bad `month` format or unknown category).

### `PATCH /transactions/{id}` (US-10)
```json
{ "category": "Business Expense" }
```
```json
200 {
  "transaction": { "id": 381, "category": "Business Expense", "category_source": "user", "...": "..." },
  "rule": { "pattern": "BLUE BOTTLE", "category": "Business Expense", "created": true },
  "recategorized_count": 14
}
```
Effects: saves the transaction with source `user`, creates or updates a rule
`pattern = merchant_normalized`, and re-categorizes every other transaction whose
merchant matches, except ones the user already set by hand.
**Errors:** 404, 422 (category not in the list).

---

### `GET /categories`
```json
200 ["Groceries", "Dining", "Transport", "Rent/Housing", "Utilities", "Subscriptions", "Shopping", "Health", "Entertainment", "Income", "Transfers", "Business Expense", "Other"]
```

---

### `GET /analytics/spend-by-category?month=2026-03` (US-07)
Debits only, `Transfers` excluded.
```json
200 {
  "month": "2026-03",
  "total": "3184.40",
  "items": [
    { "category": "Rent/Housing", "total": "1650.00", "count": 1 },
    { "category": "Groceries", "total": "512.37", "count": 11 }
  ]
}
```
**Errors:** 422 (missing/bad `month`).

### `GET /analytics/monthly-trend` (US-08)
```json
200 { "items": [
  { "month": "2026-01", "total": "2950.10", "change_amount": null, "change_pct": null },
  { "month": "2026-02", "total": "3102.55", "change_amount": "152.45", "change_pct": "5.17" }
] }
```
Built with `LAG(total) OVER (ORDER BY month)`. The first month has `null` change.

### `GET /analytics/income-vs-expenses` (US-09)
`Transfers` are excluded from both sides.
```json
200 { "items": [
  { "month": "2026-01", "income": "5200.00", "expenses": "2950.10", "net": "2249.90" }
] }
```

### `GET /analytics/top-merchants?limit=10&month=2026-03` (US-15, also an agent tool)
`month` is optional; `limit` is 1–50, default 10.
```json
200 { "items": [ { "merchant": "LOBLAWS", "total": "402.18", "count": 7 } ] }
```

---

### `GET /anomalies?include_dismissed=false` (US-12)
```json
200 { "items": [
  {
    "id": 57, "type": "duplicate", "score": null,
    "transaction": { "id": 412, "txn_date": "2026-03-14", "merchant_normalized": "ADOBE", "amount": "29.99" },
    "details": { "first_transaction_id": 409, "first_date": "2026-03-13", "days_apart": 1 },
    "explanation": "You were charged $29.99 by ADOBE twice within 1 day. Check whether this is a duplicate.",
    "explanation_source": "llm", "dismissed": false
  }
] }
```

### `PATCH /anomalies/{id}`
```json
{ "dismissed": true }
```
`200` returns the updated anomaly. **Errors:** 404, 422.

---

### `POST /agent/ask` (US-13)
```json
{ "question": "How much did I spend on dining in March?" }
```
```json
200 {
  "answer": "You spent $284.60 on Dining in March 2026 across 19 transactions.",
  "tools_used": [ { "name": "spend_by_category", "args": { "month": "2026-03" } } ]
}
```
Question length is 1–500 chars. The agent can only call `spend_by_category(month)`,
`top_merchants(limit, month?)` and `get_anomalies(include_dismissed?)`, with a max of 5 calls.
Requests to change data or run SQL get a polite refusal (still 200, `tools_used: []`).
**Errors:** 422 (empty/too long), 503 `LLM_UNAVAILABLE`, 429 (Could-have).

## 3. Endpoint → story map

| Endpoint | Story |
|---|---|
| `GET /health` | US-01 |
| `POST /uploads`, `GET /uploads/{id}` | US-03, US-11 |
| `GET /transactions`, `PATCH /transactions/{id}`, `GET /categories` | US-10 |
| `GET /analytics/spend-by-category` | US-07 |
| `GET /analytics/monthly-trend` | US-08 |
| `GET /analytics/income-vs-expenses` | US-09 |
| `GET /analytics/top-merchants` | US-15, US-13 |
| `GET /anomalies`, `PATCH /anomalies/{id}` | US-12, US-16 |
| `POST /agent/ask` | US-13 |
