# ADR-007: Background task for LLM work after upload

- **Status:** Accepted
- **Date:** 2026-10-25
- **Deciders:** Vish (decision D1)

## Context
A first upload can need ~100 LLM categorizations plus explanation calls. On a laptop
CPU that can take up to ~2 minutes (NFR-08). An HTTP request that hangs that long makes for a bad
experience and risks timeouts.

## Options considered

| | **A. Synchronous** | **B. Background job + status polling** |
|---|---|---|
| UX | Page waits up to ~2 min with a spinner | Rows appear right away; categories fill in; a progress status shows |
| Timeouts | Risky for long uploads | Request finishes in ~1 s |
| Code | Simplest | + status column, + polling endpoint, + restart recovery |
| Real-world pattern | Fine for fast work only | Standard for slow work (statement imports, report generation) |

Within B, the queue could be a real job queue (Celery/RQ + Redis) or FastAPI's built-in
`BackgroundTasks`.

## Decision
**B, using FastAPI `BackgroundTasks`** (no new infrastructure):
1. The request validates, saves rows, applies rules → returns **201** with
   `status = "categorizing"`.
2. A background task does cache lookup → LLM batches → anomaly checks → explanations →
   `status = "done"` (or `"failed"` with an error).
3. The UI polls `GET /uploads/{id}` every 2 s (TanStack Query `refetchInterval`) until it's done.
4. On API startup, uploads stuck in `categorizing` are re-queued. Every step is idempotent,
   so re-running is safe.

## Consequences
- ✅ Fast, responsive upload; a good interview story about sync vs async work.
- ✅ No Redis/Celery to run or explain.
- ❌ `BackgroundTasks` run inside the API process. If it crashes, the job stops, which is why
  we have the startup re-queue. With many users or multiple API instances, we'd move to a real
  queue (Celery/RQ, or SQS on AWS). This is noted as the scaling path.
- ❌ Tests must wait for the background task. In tests we call the service function
  directly, and integration tests poll the status.
