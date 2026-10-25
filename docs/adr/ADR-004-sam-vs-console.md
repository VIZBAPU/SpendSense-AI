# ADR-004: AWS SAM vs manual console setup

- **Status:** Deferred. Not needed while ADR-002 is in force.
- **Date:** 2026-10-25

## Context
A future cloud version needs Lambda, API Gateway, S3, CloudFront, Secrets Manager and
CloudWatch alarms. They can be created by clicking in the AWS console or defined as code.

## Options considered

| | **AWS SAM (infrastructure as code)** | **Console (click-ops)** |
|---|---|---|
| Repeatable | Same template → same stack, any account/region | Depends on someone remembering every click |
| Reviewable | Changes go through PRs like code | Invisible changes; no history |
| Rollback | CloudFormation rolls back failed deploys; redeploy an older template | Manual, error-prone |
| CI/CD | `sam deploy` from GitHub Actions with OIDC | Not automatable |
| Learning curve | YAML + CloudFormation concepts | Easy to start, hard to keep consistent |

## Proposed decision (if/when deployed)
**SAM.** Infrastructure as code is the standard in regulated environments: auditors can
see *what* changed, *who* approved it, and *when*. The console is only for exploring and for the
one-off steps that must be done by a human (e.g. the OIDC role and the budget alert).

## Consequences
- Adds a `template.yaml` to the repo when cloud work starts.
- Every resource is explained before the first deploy (CLAUDE.md, Phase 5).
