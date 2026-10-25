# Architecture Decision Records

An **ADR** records one important decision: the context, the options we considered, what we
chose, and what it costs us. ADRs are never edited after they're accepted. If a decision
changes, a new ADR **supersedes** the old one, so the history of *why* is never lost.

| # | Decision | Status |
|---|---|---|
| [ADR-001](ADR-001-fastapi-vs-spring-boot.md) | FastAPI (Python) instead of Spring Boot (Java) for the backend | Accepted |
| [ADR-002](ADR-002-defer-cloud-deployment.md) | Run locally with Docker Compose; defer AWS deployment | Accepted |
| [ADR-003](ADR-003-neon-vs-rds.md) | Neon vs Amazon RDS for cloud Postgres | Deferred (by ADR-002) |
| [ADR-004](ADR-004-sam-vs-console.md) | AWS SAM vs console setup | Deferred (by ADR-002) |
| [ADR-005](ADR-005-statistics-vs-llm-for-anomalies.md) | Statistics decide anomalies; the LLM only explains | Accepted |
| [ADR-006](ADR-006-local-llm-ollama.md) | Local LLM via Ollama instead of a hosted API | Accepted |
| [ADR-007](ADR-007-background-upload-processing.md) | Background task for LLM work after upload | Accepted |

**Template:** Status · Date · Context · Options considered · Decision · Consequences
