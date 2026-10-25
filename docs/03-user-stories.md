# 03 — User Stories

**Personas**
- **Freelancer** (end user): mixes personal and business spending on one account and
  wants to know where the money goes.
- **Developer** (Vish): builds, tests and runs the project.

Each story becomes one GitHub issue. Est = rough effort in hours, including the
explain-and-quiz step.

---

### US-01 — Run everything with one command
*Developer · Sprint 1 · infra · Est 1.5h · FRs: FR-25, NFR-01, NFR-14*

**As a** developer **I want** to start the database, API, web app and LLM with one
command **so that** anyone can run the project in minutes.

- **Given** a fresh clone and Docker installed, **when** I copy `.env.example` to `.env`
  and run `docker compose up`, **then** `db`, `api`, `web` and `ollama` start, with no errors.
- **Given** the stack is running, **when** I call `GET /health`, **then** I get 200 with
  the status of `db` and `ollama`.
- **Given** the repo, **when** I search it for secrets, **then** only `.env.example`
  (placeholder values) is committed and `.env` is gitignored.

### US-02 — Generate realistic synthetic statements
*Developer · Sprint 1 · feature · Est 1h · FRs: FR-04, NFR-06*

**As a** developer **I want** a generator that makes a fake freelancer statement
**so that** I can test and measure the app without real bank data.

- **Given** a fixed random seed, **when** I run the generator, **then** it writes ~600
  rows over 6 months in Format B, and the same seed produces the same file.
- **Given** the output, **then** a ground-truth file maps every row to one of the 13
  categories, and an anomalies file lists every planted anomaly (at least 3 per check type).
- **Given** the output, **then** no row contains a real-looking account or card number.

### US-03 — Upload a statement (API)
*Freelancer · Sprint 1 · feature · Est 1.5h · FRs: FR-01, FR-02, FR-03, NFR-03, NFR-07*

**As a** freelancer **I want** to upload my statement CSV **so that** my transactions
are loaded without typing anything.

- **Given** a valid Format B file, **when** I `POST /uploads`, **then** I get 201 with
  counts of rows inserted, skipped as duplicates, and rejected.
- **Given** a file with a bad date on row 7, **when** I upload it, **then** I get 422
  listing `row 7: invalid date`, and nothing is saved.
- **Given** a file over 2 MB, a non-CSV file, or one with wrong headers, **then** I get a 4xx error with a clear message.
- **Given** I upload the same file twice, **then** the second upload inserts 0 rows.
- **Given** a file with two identical rows (a real double charge), **then** both are saved.
- **Given** any saved row, **then** amounts are stored as `NUMERIC(12,2)` and
  `merchant_normalized` is filled.

### US-04 — Categorize transactions automatically
*Freelancer · Sprint 1 · feature · Est 2h · FRs: FR-05, FR-06, FR-07, FR-09, NFR-04, NFR-06, NFR-10*

**As a** freelancer **I want** each transaction categorized automatically **so that**
I don't have to tag hundreds of rows.

- **Given** a merchant matching a rule, **when** it's uploaded, **then** it gets the
  rule's category with source `rule`, and no LLM call is made.
- **Given** an unknown merchant, **then** the LLM is called with **only** the normalized
  merchant text, and the result is one of the 13 categories with source `llm`.
- **Given** the same unknown merchant appears again, **then** the cached result is used
  (source `cache`) and the LLM is not called again.
- **Given** the LLM returns something outside the 13 categories, **then** the row falls back to `Other`.
- **Given** Ollama is down, **then** the upload still succeeds and unmatched rows get
  `Other` + `needs_review = true`.

### US-05 — CI on every pull request
*Developer · Sprint 1 · infra · Est 0.5h · FRs: NFR-13, NFR-16*

**As a** developer **I want** lint, type-checks, tests and builds to run on every PR
**so that** broken code can't be merged.

- **Given** a PR, **when** it's opened or updated, **then** GitHub Actions runs `ruff`,
  `pytest`, `tsc --noEmit`, `vitest` and `vite build`.
- **Given** any step fails, **then** the PR shows a red check.
- **Given** CI runs, **then** it doesn't need any secrets and never calls a real LLM.

### US-06 — Detect unusual spending
*Freelancer · Sprint 2 · feature · Est 2h · FRs: FR-10, FR-11, FR-12, FR-13, FR-14*

**As a** freelancer **I want** unusual charges flagged with a reason **so that** I can
catch mistakes, fraud, or creeping costs.

- **Given** a Dining charge with z ≥ 2.5 vs the last 90 days of Dining (≥ 5 prior rows),
  **then** a `zscore` flag is created showing the z value.
- **Given** the same merchant + amount twice within 48h, **then** a `duplicate` flag is created on the second charge.
- **Given** a first-ever charge at a merchant that is > 3× the median debit and > $100,
  **then** a `new_merchant_large` flag is created.
- **Given** a subscription charging more than last time, **then** a
  `subscription_increase` flag is created showing the old and new price.
- **Given** a flag, **then** it has a 1–2 sentence explanation (from the LLM, or a template if the LLM fails).
- **Given** the synthetic dataset, **then** 100% of planted z-score and duplicate anomalies are flagged.

### US-07 — See spending by category
*Freelancer · Sprint 2 · feature · Est 1h · FRs: FR-16, NFR-09, NFR-12*

**As a** freelancer **I want** to see how much I spent per category in a month **so
that** I know where my money goes.

- **Given** uploaded data, **when** I pick a month, **then** I see a chart and a table
  of debit totals per category, and the totals add up to that month's total spending.
- **Given** I use only the keyboard, **then** I can change the month and read the
  table without a mouse.

### US-08 — See monthly trends
*Freelancer · Sprint 2 · feature · Est 1h · FRs: FR-17, NFR-09*

**As a** freelancer **I want** to see spending month by month **so that** I can spot when it's growing.

- **Given** 6 months of data, **then** I see a line/bar chart of total spending per
  month, with the month-over-month change in $ and %.
- **Given** the first month, **then** its change shows "—" (no previous month), not an error.

### US-09 — See income vs expenses
*Freelancer · Sprint 2 · feature · Est 0.5h · FRs: FR-18*

**As a** freelancer **I want** income and expenses side by side per month **so that**
I know whether I'm saving or burning money.

- **Given** data, **then** I see income (credits, excluding Transfers) and expenses
  (debits, excluding Transfers) per month, plus the net amount.

### US-10 — Review and correct transactions
*Freelancer · Sprint 2 · feature · Est 1.5h · FRs: FR-08, FR-19*

**As a** freelancer **I want** to fix a wrong category **so that** the app learns and
gets it right next time.

- **Given** the transactions table, **then** I can filter by month and category.
- **Given** a row categorized as Shopping, **when** I change it to Business Expense,
  **then** it saves with source `user`, a merchant rule is created, and other
  transactions from the same merchant are updated.
- **Given** I upload a new file with that merchant, **then** it's categorized by the
  new rule, with no LLM call.

### US-11 — Upload from the browser
*Freelancer · Sprint 2 · feature · Est 1h · FRs: FR-01, NFR-12*

**As a** freelancer **I want** an upload page **so that** I don't need to use an API tool.

- **Given** the upload page, **when** I pick a CSV and submit, **then** I see progress
  and then the inserted/duplicate/rejected counts.
- **Given** a rejected file, **then** I see the row-level errors in a readable list.

### US-12 — Review flags
*Freelancer · Sprint 2 · feature · Est 0.5h · FRs: FR-15*

**As a** freelancer **I want** a page listing all flagged charges **so that** I can
review them in one place.

- **Given** flags exist, **then** I see type, date, merchant, amount and explanation, newest first.
- **When** I dismiss a flag, **then** it disappears from the list and stays dismissed after a refresh.

### US-13 — Ask about my spending
*Freelancer · Sprint 2 · feature · Est 2h · FRs: FR-22, NFR-05, NFR-10*

**As a** freelancer **I want** to ask questions in plain English **so that** I get
answers without building reports.

- **Given** "How much did I spend on dining in March?", **then** the agent calls
  `spend_by_category` and answers with the correct amount.
- **Given** "What are my biggest merchants?", **then** it calls `top_merchants`.
- **Given** "Anything suspicious?", **then** it calls `get_anomalies`.
- **Given** "Delete all my transactions" or "run this SQL…", **then** it refuses and makes no tool call outside the 3 tools.
- **Given** Ollama is down, **then** I get "assistant unavailable", not a 500 error.

### US-14 — Measure categorization accuracy
*Developer · Sprint 2 · test · Est 0.5h · FRs: FR-23*

**As a** developer **I want** an eval script **so that** I can prove the accuracy
number on my resume.

- **Given** the synthetic data + ground truth, **when** I run the eval, **then** it
  prints overall accuracy, per-category precision, % of rows that needed an LLM call,
  and anomaly recall.
- **Given** the eval is run twice with a warm cache, **then** the results are identical.

---

### Could-have stories (cut first if behind)

### US-15 — Top merchants *(Could · FR-20 · Est 0.5h)*
**As a** freelancer **I want** my top 10 merchants by spend **so that** I see who gets my money.
- **Given** data, **then** I see 10 merchants sorted by total debit, with totals.

### US-16 — Flagged-items widget *(Could · FR-21 · Est 0.5h)*
**As a** freelancer **I want** the latest flags on the dashboard **so that** I notice them right away.
- **Given** flags exist, **then** the dashboard shows the 5 newest, linking to the Flags page.

### US-17 — Rate limiting *(Could · FR-24 · Est 1h)*
**As a** developer **I want** per-IP limits **so that** the LLM can't be overloaded.
- **Given** more than 5 uploads per hour from one IP, **then** the next one gets 429.
- **Given** the daily LLM-call cap is reached, **then** unmatched rows fall back to `Other` + `needs_review`.
