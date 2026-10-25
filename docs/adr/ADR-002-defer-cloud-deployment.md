# ADR-002: Run locally with Docker Compose; defer AWS deployment

- **Status:** Accepted
- **Date:** 2026-10-25
- **Deciders:** Vish
- **Changes:** removes Lambda, API Gateway, S3, CloudFront, Secrets Manager, CloudWatch,
  SAM and the OIDC deploy from the release scope. Defers ADR-003 and ADR-004.

## Context
The original plan deployed to AWS (Lambda + API Gateway, S3/CloudFront, Neon) with SAM and
GitHub OIDC. During Phase 1, three constraints changed:
1. **Budget: $0.** Vish doesn't want to spend anything.
2. **LLM: Ollama, running locally** (ADR-006). A multi-GB model can't run on Lambda, and
   a GPU/always-on server would cost money.
3. **Timebox:** 3 days with Vish new to coding. Cloud setup (IAM, OIDC, SAM, networking)
   would take most of a day.

## Options considered

| | **A. Deploy to AWS as planned** | **B. Local Docker Compose only** |
|---|---|---|
| Cost | Small but not $0 (Secrets Manager ~$0.40/secret/month; LLM hosting not free) | $0 |
| Live demo link | ✅ yes | ❌ no; demo via README, screenshots, a short video |
| LLM | Needs a hosted API (paid) | Ollama works as-is |
| Time | ~1 day of cloud work | Hours saved for features and tests |
| Skills shown | IaC, IAM, OIDC, serverless | Containers, CI, local dev setup |

## Decision
**Option B.** Ship a solid local release first, with CI on GitHub Actions. Keep the design
cloud-ready so deploying later is an add-on, not a rewrite.

## Consequences
- ✅ $0, no surprise bills (closes risks R-12 and R-13).
- ✅ More time for the core features, tests and the accuracy eval.
- ❌ No live URL for recruiters → the README will have screenshots and a GIF, and setup must be
  one command.
- **Cloud-ready choices we keep:** config only via env vars, stateless API, migrations
  with Alembic, Postgres (works on Neon/RDS), LLM behind a `llm/client.py` factory so a
  hosted provider can be swapped in.
- Phase 5 shrinks to `ci.yml` + tagging `v1.0.0`. A future "v2: deploy to AWS" can pick up
  ADR-003 and ADR-004.
