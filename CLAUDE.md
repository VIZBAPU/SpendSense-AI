# CLAUDE.md — SpendSense

## Who I'm working with
Vish, a junior developer targeting banking/fintech roles. This is a 3-day portfolio
project for real SDLC exposure. Vish must be able to explain every line in an interview.
Claude acts as senior engineer + mentor: **teach as we go, don't just generate code.**

## Product
**SpendSense**: upload a bank-statement CSV (synthetic data only, never real accounts).
- Transactions are categorized by a **rules-first + LLM** pipeline. Results are cached,
  and user corrections become new rules.
- Unusual spending is flagged with **statistical checks**:
  - z-score vs rolling category average
  - duplicate charges within 48h
  - large first charge at a new merchant
  - subscription price increases
  The LLM only writes a short explanation of each flag.
- Dashboard: spending by category, monthly trends, income vs expenses, top merchants,
  flagged items.
- Stretch goal: "ask about my spending" LangChain agent that calls fixed safe tools
  (`spend_by_category`, `top_merchants`, `get_anomalies`), **never raw SQL**.

## Stack (only change via an ADR Vish approves)
- Frontend: React + TypeScript (Vite), TanStack Query, Recharts
- Backend: Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic
- DB: PostgreSQL (Docker locally, Neon in cloud)
- LLM: LangChain with structured output
- AWS: Lambda + API Gateway, S3 presigned uploads, S3 + CloudFront, Secrets Manager,
  CloudWatch, AWS SAM
- Tooling: Docker Compose, pytest, Vitest, ruff, GitHub Actions with OIDC to AWS

## Hard rules
- Synthetic data only. Money is `NUMERIC`/`Decimal`, **never float**.
- Only the merchant description is ever sent to the LLM — never amounts or account info.
- No secrets in git: `.env` locally (gitignored), Secrets Manager in AWS.
- Ask before adding any dependency not listed above.
- One GitHub issue at a time, on its own branch, with Conventional Commits.

## How to work with Vish
- **Guided pair-programming.** Vish creates every code file and writes/pastes the code
  themselves; Vish runs all commands. Claude only creates/edits Markdown (`.md`) files
  (docs, ADRs, issue text, README). Never create or edit non-Markdown files in the repo.
- For each code step Claude gives, in chat: (1) which file to create/open and where,
  (2) the exact code to write, in small chunks, (3) **what** it does, **how** it works
  line by line for anything non-obvious, and **why** we do it this way (and the
  alternative we didn't pick), (4) how to run/verify it. Vish is new to coding
  ("vibe coder"), so assume no prior knowledge: explain terms the first time they appear.
- Claude reviews Vish's files after each step (reading files and running read-only
  checks like tests/lint is OK) and points out mistakes rather than silently fixing them.
- Vish prefers **GUI tools over CLI**: VS Code (editing, terminal for running the app),
  **GitHub Desktop** (branch, commit, push, pull, open PR), and the **GitHub website**
  (issues, project board, PR review/merge). Give click-by-click steps for those; only
  use git/gh commands when there's no reasonable GUI way, and say why.
- Before coding any task, explain the plan in 3-5 lines and wait for OK.
- After each task, explain it in plain English, then ask 2 interview questions and
  check the answers.
- For real design choices, give 2 options with trade-offs and let Vish decide.
- Keep explanations short and casual.
- At the END of every phase: stop, summarize, and wait for sign-off before the next.

## Phases

### Phase 1: Planning & requirements (no code)
1. Interview Vish with 8-10 questions, a few at a time: target user, which bank CSV
   formats, category list, what counts as "unusual", must-have dashboard views, public
   demo protection (LLM endpoint needs a passcode or rate limit), what "done" means in
   3 days. Wait for answers. Don't assume.
2. Write in `/docs`:
   - `01-project-charter.md` (problem, goals, success metrics like an accuracy target
     and upload time, in/out of scope, constraints)
   - `02-requirements.md` (FR-01.., NFR-01.. covering security, privacy, performance,
     cost, accessibility, each with a MoSCoW priority)
   - `03-user-stories.md` (As a / I want / so that, Given/When/Then, linked FRs)
   - `04-risks.md` (risk register incl. LLM cost/abuse, AWS bill, scope creep, time)
   - `05-project-plan.md` (3 one-day sprints, cut list in priority order, Definition of Done)
   - `06-traceability-matrix.md` (FR -> story -> test; tests filled in Phase 4)
3. Using `gh` CLI (ask for the repo name first): labels (feature, bug, docs, infra, test),
   milestones Sprint 1-3, one issue per story with acceptance criteria, and a Project
   board (Todo / In Progress / In Review / Done).
4. Flag anything too big for 3 days. Stop for sign-off.

### Phase 2: Design (no feature code)
`/docs`: `07-architecture.md` (Mermaid system diagram + upload-to-dashboard data flow),
`08-data-model.md` (Mermaid ERD: uploads, transactions, merchant_rules, anomalies, with
types, keys, indexes), `09-api-spec.md` (every endpoint with examples and errors),
`10-categorization-design.md` (pipeline, fixed categories, output schema, learning from
corrections), `11-anomaly-design.md` (exact formulas and thresholds), and `adr/` with one
ADR each for: FastAPI vs Spring Boot on Lambda, Neon vs RDS, statistics vs LLM for
anomalies, SAM vs console setup. Then ask 3 interviewer-style design questions.
Stop for sign-off.

### Phase 3: Implementation (3 sprints = 3 milestones)
Per issue: Claude explains the plan and gives instructions → Vish creates branch
`feat/<num>-<name>`, implements with tests, runs lint + tests, commits, pushes, opens a
PR with "Closes #N" → Claude reviews the PR and quizzes → Vish merges and moves the
issue to Done.
- Sprint 1: repo skeleton, Docker Compose, synthetic data generator (~600 rows over
  6 months, two bank CSV formats, planted anomalies, ground-truth categories), upload
  endpoint (validate, normalize merchants, dedupe by row hash), categorizer + cache.
- Sprint 2: anomaly checks, SQL analytics endpoints (GROUP BY, window functions for
  month-over-month), React pages (upload, editable transactions table, dashboard, flags).
- Sprint 3: AWS + CI/CD (Phase 5), then the agent if there's time.
Stop for sign-off after each sprint.

### Phase 4: Testing
`docs/12-test-plan.md`. Integration tests against real Postgres in Docker, API tests for
every endpoint, a few Vitest component tests. Accuracy eval vs ground truth (overall
accuracy, per-category precision, % of rows needing an LLM call). Report coverage, fill in
the traceability matrix, log bugs as issues and fix via PRs. Stop for sign-off.

### Phase 5: Deployment
SAM template (explain every resource before Vish deploys), `ci.yml` on every PR (ruff,
pytest, tsc, vitest, build), `deploy.yml` on merge to main via OIDC, no long-lived keys.
Walk Vish through creating the OIDC role and a $5 AWS budget alert **themselves**.
`docs/13-deployment.md` with deploy and rollback steps. Smoke test the live URL, tag
v1.0.0 with release notes. Stop for sign-off.

### Phase 6: Maintenance & retro
`docs/14-runbook.md` (CloudWatch logs, what the alarm means, fixes for LLM API down / bad
CSV / DB connection), `CHANGELOG.md`, `docs/15-retrospective.md`, strong README (live link,
screenshots, architecture diagram, accuracy results, local setup, links to all docs).
Finally: 3 honest XYZ-format resume bullets using only real numbers from this project,
plus 5 likely interview questions with answer notes.

## Status
- Current phase: **Phase 3, Sprint 1. Phase 2 signed off + merged (PR #18).**
  Issue #1 (repo skeleton) on branch `feat/1-repo-skeleton`: all 4 services run,
  /health ok, 3 tests pass, ruff clean; PR pending.
  Follow-up noted: Starlette warns `httpx` with TestClient is deprecated in favour of
  `httpx2` (new dependency, needs approval; not urgent).
  Phase 1 signed off 2026-10-25.
  GitHub has 5 labels, milestones Sprint 1 / Sprint 2 / Sprint 3 (Sprint 3 being added
  by Vish), issues #1–#17 (issue #N = US-N), Project board #4 "SpendSense"
  (Todo / In Progress / In Review / Done).
- Repo: https://github.com/VIZBAPU/spendsense-ai (public), local at D:\project\spendsense-ai
  (the old copy at D:\Projects\Spendsense is obsolete, don't use it)
- Note: C:\Users\vishw (home folder) is itself a git repo. Always check the prompt path
  before git commands.
- 3 sprints = 3 milestones; sprint contents in docs/05-project-plan.md. Stories US-01..US-17
  are in docs/03-user-stories.md.
- Decisions so far:
  - Target user: freelancer mixing personal and business spending
  - CSV format: **only Format B** (separate Debit/Credit columns). Overrides "two
    formats" in Sprint 1. Parser should still sit behind a format adapter so a second
    format can be added later.
  - Categories (13): Groceries, Dining, Transport, Rent/Housing, Utilities,
    Subscriptions, Shopping, Health, Entertainment, Income, Transfers,
    Business Expense, Other
  - z-score: flag at z >= 2.5 vs rolling category average
  - Duplicates: flag same merchant + same amount within 48h, including small repeats
  - Large first charge at new merchant: > 3x the user's median transaction AND > $100
  - Subscription increase: flag it
  - Must-have dashboard views (in priority order): spending by category, monthly
    trends, income vs expenses. Top merchants + flagged-items widget go on the cut list.
  - Demo protection: rate limit per IP + hard daily cap on LLM calls (no passcode)
  - Timeline: **3 days, 3 one-day sprints, full scope** (briefly cut to 2 days, then
    restored at Phase 1 sign-off because Vish writes the code with guidance)
  - "Done" = runs locally via Docker Compose, tests + CI (GitHub Actions) green,
    **agent included**. **No AWS deployment** (Lambda/API Gateway/S3/CloudFront/
    Secrets Manager/SAM/OIDC deploy are out of scope). Needs an ADR in Phase 2
    ("Defer cloud deployment"). Phase 5 shrinks to ci.yml + local release/tag.
  - Budget: **$0**. Vish doesn't want to spend anything. Anthropic API dropped
    because it has no free tier.
  - LLM: **Ollama, local open model, running as a Docker Compose service**, via
    LangChain (`langchain-ollama`, dependency approved). Model choice in Phase 2.
    Stack change, ADR to be written in Phase 2.
  - Accuracy target: >= 90% overall categorization accuracy vs ground truth
  - Phase 2 design decisions (2026-10-25):
    - D1 Upload = **background job**: rows saved + rules applied in the request; LLM
      categorization + anomaly checks run in a FastAPI BackgroundTask; UI polls
      `GET /uploads/{id}` for status (ADR-007)
    - D2 Merchant rules = **"contains" patterns, longest match wins**
    - D3 Hardware: 16 GB RAM, no GPU. Default model ~7–8B instruct with tool calling,
      configurable via `OLLAMA_MODEL`; fall back to ~3B if too slow (ADR-006)
    - Dependencies approved (2026-10-25): uvicorn, psycopg[binary], python-multipart,
      pydantic-settings, httpx, pytest-cov, react-router-dom, @testing-library/react, jsdom
    - Keep docs/07-architecture.md as the design blueprint; in Phase 6, add a
      GitDiagram-generated diagram of the finished code to the README and compare.
