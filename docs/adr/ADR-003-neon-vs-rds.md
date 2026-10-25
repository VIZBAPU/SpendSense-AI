# ADR-003: Neon vs Amazon RDS for cloud Postgres

- **Status:** Deferred. Not needed while ADR-002 is in force; recorded so a future cloud
  version starts from an agreed position.
- **Date:** 2026-10-25

## Context
If SpendSense is deployed to AWS later, the Lambda-based API needs a managed Postgres.

## Options considered

| | **Neon (serverless Postgres)** | **Amazon RDS for PostgreSQL** |
|---|---|---|
| Cost at demo traffic | Free tier; scales to zero when idle | Pay per hour even when idle (free tier is limited and time-bound) |
| Lambda fit | HTTP/serverless driver + connection pooling, which suits many short Lambda invocations | Needs RDS Proxy (extra cost) to avoid exhausting connections from Lambda |
| Networking | Public endpoint + TLS; no VPC needed | Usually in a VPC, so Lambda needs VPC config (cold starts, NAT costs) |
| Enterprise/bank fit | Newer vendor, external to AWS | AWS-native, IAM auth, familiar to bank auditors |
| Data residency / compliance | Depends on Neon's regions and terms | Full control within your AWS account |

## Proposed decision (if/when deployed)
**Neon** for a portfolio demo (free, scales to zero, no VPC). For a real bank workload,
**RDS** (or Aurora) inside a private VPC would be the right call, for control, compliance and IAM integration.

## Consequences
- Our schema uses plain Postgres features only (window functions, `NUMERIC`, `JSONB`), so it works on both.
