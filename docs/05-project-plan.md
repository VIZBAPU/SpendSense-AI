# 05 — Project Plan

**Timebox:** 2 days = 2 one-day sprints = 2 GitHub milestones (`Sprint 1`, `Sprint 2`).
Estimates include the explain-and-quiz step after each issue.

## Sprint 1 — Day 1: "Data in, categorized"

**Sprint goal:** upload a synthetic statement and see every row stored and categorized,
with CI guarding the main branch.

| Order | Work | Story | Est |
|---|---|---|---|
| 1 | Phase 1 wrap-up (GitHub setup) + Phase 2 design docs & ADRs | — | 3h |
| 2 | Repo skeleton, Docker Compose (db, api, web, ollama), health endpoint | US-01 | 1.5h |
| 3 | CI workflow | US-05 | 0.5h |
| 4 | Synthetic data generator + ground truth | US-02 | 1h |
| 5 | Upload endpoint: validate, normalize, dedupe | US-03 | 1.5h |
| 6 | Categorizer: rules → cache → Ollama | US-04 | 2h |
| | **Total** | | **~9.5h** |

## Sprint 2 — Day 2: "Insights, flags, agent, ship"

**Sprint goal:** a working local app with dashboard, flags and agent, tested, documented and tagged `v1.0.0`.

| Order | Work | Story | Est |
|---|---|---|---|
| 1 | Accuracy eval (run early so there's time to tune) | US-14 | 0.5h |
| 2 | Agent spike: prove the model can call tools (de-risks R-05) | US-13 | 0.5h |
| 3 | Anomaly checks + explanations | US-06 | 2h |
| 4 | Analytics endpoints + dashboard views | US-07, US-08, US-09 | 2.5h |
| 5 | Upload page (+ app shell / routing) | US-11 | 1h |
| 6 | Transactions table + corrections | US-10 | 1.5h |
| 7 | Flags page | US-12 | 0.5h |
| 8 | Agent: finish tools + chat UI | US-13 | 1.5h |
| 9 | Phase 4 testing (test plan, integration tests, coverage, matrix) | — | 1h |
| 10 | Phases 5–6: CI polish, tag v1.0.0, README, runbook, retro, resume bullets | — | 1h |
| | **Total** | | **~12h** |

> ⚠️ **Day 2 is over capacity** (~12h of work vs an 8–10h day). Expect to use the cut
> list below. Day 1 is full too, so slips there push straight into Day 2.

## Cut list (cut from the top, one item at a time)

| # | Cut | Saves | What remains |
|---|---|---|---|
| 1 | US-17 rate limiting | 1h | Nothing; local-only app |
| 2 | US-16 flagged-items dashboard widget | 0.5h | Flags page still lists them |
| 3 | US-15 top-merchants dashboard view | 0.5h | The `top_merchants` query stays (the agent needs it) |
| 4 | FR-13 subscription price increase check | 0.5h | 3 other checks |
| 5 | FR-12 large first charge at new merchant | 0.5h | z-score + duplicates |
| 6 | FR-14 LLM-written flag explanations | 0.5h | Template explanations |
| 7 | Extra Vitest tests (keep 2) | 0.5h | Backend tests stay full |
| 8 | Agent chat UI → API-only demo via `/docs` (Swagger) | 0.5h | Agent still works |
| 9 | Agent tool-calling → keyword router picks the tool, LLM only phrases the answer | 0.5h | Agent still answers questions |

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
- [ ] Vish has reviewed, understood (quiz passed) and merged
- [ ] Docs updated if behaviour/API changed; traceability matrix updated
- [ ] Issue moved to **Done** on the board

### Per release (v1.0.0)
- [ ] All Must requirements met (or a cut is recorded with a reason)
- [ ] Accuracy eval run and results recorded in the README
- [ ] `docker compose up` works from a fresh clone, following the README
- [ ] Test plan, traceability matrix, runbook, CHANGELOG, retrospective written
- [ ] Tagged `v1.0.0` with release notes

## Phase gates (stop for Vish's sign-off)
1. End of Phase 1 (these docs + GitHub setup)
2. End of Phase 2 (design docs + ADRs)
3. End of Sprint 1
4. End of Sprint 2 / Phase 4 testing
5. Release v1.0.0 / Phase 6 retro
