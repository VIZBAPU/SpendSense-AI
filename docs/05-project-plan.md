# 05 — Project Plan

**Timebox:** 3 days = 3 one-day sprints = 3 GitHub milestones (`Sprint 1`, `Sprint 2`, `Sprint 3`).

**Working mode:** guided pair-programming. Claude gives the steps, the code and the
what/how/why; Vish writes the code, runs everything, commits, opens and merges PRs.
Estimates below are the original ones × ~1.5 to account for that, and include the
explain-and-quiz step after each issue.

> **Change log:** v1 had 2 sprints in 2 days with Claude writing the code. v2 (current)
> has 3 sprints in 3 days with Vish writing the code, approved at the Phase 1 sign-off.

## Sprint 1 — Day 1: "Foundations"

**Sprint goal:** the design is agreed, the stack runs with one command, CI guards `main`,
and we can generate synthetic data and upload it.

| Order | Work | Story | Est |
|---|---|---|---|
| 1 | Phase 2 design docs & ADRs | — | 3h |
| 2 | Repo skeleton, Docker Compose (db, api, web, ollama), health endpoint | US-01 (#1) | 2h |
| 3 | CI workflow | US-05 (#5) | 1h |
| 4 | Synthetic data generator + ground truth | US-02 (#2) | 1.5h |
| 5 | Upload endpoint: validate, normalize, dedupe | US-03 (#3) | 2h |
| | **Total** | | **~9.5h** |

## Sprint 2 — Day 2: "Intelligence"

**Sprint goal:** every uploaded row is categorized and checked for anomalies, the
accuracy is measured, and the analytics API is ready for the dashboard.

| Order | Work | Story | Est |
|---|---|---|---|
| 1 | Categorizer: rules → cache → Ollama | US-04 (#4) | 3h |
| 2 | Accuracy eval (early, so there's time to tune) | US-14 (#14) | 1h |
| 3 | Anomaly checks + explanations | US-06 (#6) | 3h |
| 4 | Analytics endpoints: by category, monthly trend (window functions), income vs expenses | US-07, US-08, US-09 (#7–#9, backend half) | 2h |
| 5 | Agent spike: prove the model can call tools (de-risks R-05) | US-13 (#13) | 0.5h |
| | **Total** | | **~9.5h** |

## Sprint 3 — Day 3: "Experience & ship"

**Sprint goal:** a working local web app with dashboard, corrections, flags and agent,
tested, documented and tagged `v1.0.0`.

| Order | Work | Story | Est |
|---|---|---|---|
| 1 | App shell, routing + upload page | US-11 (#11) | 1.5h |
| 2 | Dashboard views (charts for #7–#9) | US-07, US-08, US-09 (frontend half) | 1.5h |
| 3 | Transactions table + corrections | US-10 (#10) | 2h |
| 4 | Flags page | US-12 (#12) | 1h |
| 5 | Agent: tools + chat UI | US-13 (#13) | 2.5h |
| 6 | Phase 4 testing (test plan, integration tests, coverage, matrix) | — | 1.5h |
| 7 | Phases 5–6: CI polish, tag v1.0.0, README, runbook, retro, resume bullets | — | 1.5h |
| — | Could-haves, only if time is left: US-15, US-16, US-17 | #15–#17 | 2.5h |
| | **Total (without Could-haves)** | | **~11.5h** |

> ⚠️ **Day 3 is still over capacity** (~11.5h of work vs an 8–10h day). The Could-have
> stories will most likely be cut, and the cut list below is in play. A slip on Day 1 or 2
> pushes straight into Day 3.

## Cut list (cut from the top, one item at a time)

| # | Cut | Saves | What remains |
|---|---|---|---|
| 1 | US-17 rate limiting | 1.5h | Nothing; local-only app |
| 2 | US-16 flagged-items dashboard widget | 0.5h | Flags page still lists them |
| 3 | US-15 top-merchants dashboard view | 0.5h | The `top_merchants` query stays (the agent needs it) |
| 4 | FR-13 subscription price increase check | 0.5h | 3 other checks |
| 5 | FR-12 large first charge at new merchant | 0.5h | z-score + duplicates |
| 6 | FR-14 LLM-written flag explanations | 0.5h | Template explanations |
| 7 | Extra Vitest tests (keep 2) | 0.5h | Backend tests stay full |
| 8 | Agent chat UI → API-only demo via `/docs` (Swagger) | 1h | Agent still works |
| 9 | Agent tool-calling → keyword router picks the tool, LLM only phrases the answer | 1h | Agent still answers questions |

**Never cut:** upload, categorization + cache, corrections → rules, z-score + duplicate
checks, the 3 dashboard views, the accuracy eval, CI, money as Decimal, no secrets in git.

## Definition of Done

### Per issue
- [ ] All acceptance criteria in the issue are met
- [ ] Tests written for the new behaviour, all tests pass locally
- [ ] `ruff check` clean; `tsc --noEmit` clean (frontend)
- [ ] No secrets, no real data, no floats for money
- [ ] Conventional Commit messages on branch `feat/<num>-<name>`
- [ ] PR opened with `Closes #N` and the acceptance criteria checked off
- [ ] CI green
- [ ] Claude has reviewed the PR; Vish can explain it (quiz passed), then merges
- [ ] Docs updated if behaviour/API changed; traceability matrix updated
- [ ] Issue moved to **Done** on the board

### Per release (v1.0.0)
- [ ] All Must requirements met (or a cut is recorded with a reason)
- [ ] Accuracy eval run and results recorded in the README
- [ ] `docker compose up` works from a fresh clone, following the README
- [ ] Test plan, traceability matrix, runbook, CHANGELOG, retrospective written
- [ ] Tagged `v1.0.0` with release notes

## Phase gates (stop for Vish's sign-off)
1. End of Phase 1 (docs + GitHub setup) ✅ signed off
2. End of Phase 2 (design docs + ADRs)
3. End of Sprint 1
4. End of Sprint 2
5. End of Sprint 3 / Phase 4 testing
6. Release v1.0.0 / Phase 6 retro
