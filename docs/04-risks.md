# 04 — Risk Register

Scoring: **Likelihood (L)** and **Impact (I)** from 1 (low) to 3 (high).
**Score = L × I**: 6–9 high, 3–4 medium, 1–2 low. Reviewed at the end of each sprint.

| ID | Risk | L | I | Score | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|
| R-01 | **Time overrun.** 3 days is tight for docs + backend + frontend + agent + tests, with Vish new to coding (Day 3 is estimated at ~11.5h). | 3 | 3 | **9** | Strict cut list (05-project-plan); time-box each issue; build core flow first, agent last; skip polish. | Vish | Open |
| R-02 | **Scope creep.** New ideas mid-build ("let's add budgets…"). | 2 | 3 | **6** | Anything new goes into a "later" issue, not the sprint. Scope changes only through Vish's sign-off. | Vish | Open |
| R-03 | **Local LLM too slow on laptop CPU**, so first upload exceeds 120 s. | 2 | 2 | 4 | Rules-first means few LLM calls; batch several merchants per prompt; cache per merchant; pick a small 3–4B model. | Claude | Open |
| R-04 | **Small model accuracy below 90%.** | 2 | 3 | **6** | Strong seed rules for common merchants; few-shot examples in the prompt; enum-restricted structured output; corrections become rules; measure early with the eval (US-14). | Claude | Open |
| R-05 | **Small model is unreliable at tool calling**, so the agent breaks. | 3 | 2 | **6** | Only 3 simple tools with tiny input schemas; validate inputs; max 5 calls; test the agent first thing on Day 2. Fallback: a keyword router that picks the tool, with the LLM only phrasing the answer. | Claude | Open |
| R-06 | **Laptop can't run Ollama** (RAM/disk), or the model download is slow. | 2 | 3 | **6** | Check free RAM/disk before Sprint 1; pull the model once and keep it in a Docker volume; app works without the LLM (NFR-10). | Vish | Open |
| R-07 | **Money precision bug** (float sneaks in, totals off by cents). | 2 | 3 | **6** | `NUMERIC(12,2)` + `Decimal` everywhere; JSON as strings; a test that sums known values exactly; ruff/type hints. | Claude | Open |
| R-08 | **Sensitive data sent to the LLM** (amounts, account info). | 1 | 3 | 3 | Single function builds the prompt from `merchant_normalized` only; unit test asserts no digits beyond the merchant text are sent; synthetic data only. | Claude | Open |
| R-09 | **Prompt injection via merchant description** (e.g., "IGNORE INSTRUCTIONS…"). | 1 | 2 | 2 | Output must validate against the category enum; agent tools are read-only and fixed; no SQL generation. | Claude | Open |
| R-10 | **Secret committed to git.** | 1 | 3 | 3 | `.gitignore` for `.env`; `.env.example` with placeholders; review diffs before commit. (There are no paid keys at all, which lowers the impact.) | Vish | Open |
| R-11 | **Dev environment problems on Windows** (Docker Desktop, line endings, the home folder already being a git repo). | 2 | 2 | 4 | Create the project in its own folder with its own repo; add `.gitattributes`; test `docker compose up` in US-01. | Vish | Open |
| R-12 | **LLM cost / abuse.** | 1 | 1 | 1 | Eliminated: the LLM is local and free; no public endpoint. Could-have rate limit (US-17) if ever deployed. | — | Closed by design |
| R-13 | **Surprise AWS bill.** | 1 | 1 | 1 | Eliminated: no cloud deployment this release (ADR in Phase 2). | — | Closed by design |
| R-14 | **Anomaly checks too noisy** (e.g., duplicates firing on every coffee). | 3 | 1 | 3 | Accepted trade-off (Vish's decision); flags can be dismissed; thresholds are config values. | Vish | Accepted |
| R-15 | **Synthetic data too clean**, so the 90% accuracy doesn't reflect reality. | 2 | 2 | 4 | Generator adds messy variants (store numbers, prefixes like `SQ *`, `POS`); be honest in the README about it being synthetic data. | Claude | Open |
