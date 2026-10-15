# ADR-003: SageMaker Serverless Endpoint in us-east-1

**Status:** Proposed
**Date:** 2026-10-15
**Deciders:** Mauricio González (tech lead)
**Tags:** infra, aws, deployment, cost

## Context

The guide must show a model served behind an endpoint, on the Learner's personal account and card. GRZR-11 originally suggested SageMaker or a FastAPI container on App Runner; App Runner closed to new customers on 2026-04-30, so a new account cannot use it. A Real-time Endpoint bills per hour while it exists, so a Learner who skips the Teardown keeps paying.

## Decision

We will deploy to Amazon SageMaker AI in `us-east-1` using a Serverless Endpoint only. The guide explains in prose when a Real-time Endpoint would fit, but the demo never creates one. Cost guardrails (Budget Guardrail at Step 0, Project Tag on every resource, instance allowlist for the Training Job, mandatory Teardown) are part of this decision.

## Consequences

### Positive

- A forgotten Serverless Endpoint costs roughly nothing at rest; no Step creates a per-hour-billed endpoint.
- `us-east-1` has the broadest SageMaker availability.
- Smaller scope: one deployment path to write, run and maintain.

### Negative

- Serverless cold start makes the first call slow; the guide must explain it so it doesn't look like a failure.
- The Learner never deploys the typical production endpoint type; the Serverless vs Real-time trade-off is explained, not measured.
- How SageMaker's free tier (2 months from first SageMaker resource) interacts with AWS's newer credit-based free plan is OPEN — I haven't verified it. The guide must not promise "free".

### Neutral

- Region is configurable, but the guide is only verified in `us-east-1`.

## Alternatives considered

- **FastAPI on App Runner:** closed to new customers since 2026-04-30. Rejected.
- **FastAPI on ECS Express Mode:** App Runner's AWS-recommended replacement; adds Docker, ECR and IAM. Rejected as primary path.
- **FastAPI on Lambda:** cheap, but package-size limits and not the typical ML path. Rejected.
- **Real-time Endpoint only:** typical production choice, but per-hour billing on a personal card. Rejected as primary.
- **Serverless plus a measured Real-time comparison:** taught the trade-off hands-on, but added a per-hour-billed resource and ~1 h of scope. Dropped by the tech lead on 2026-10-15 to keep the training within one L.

## References

- GRZR-11 — Training de AWS
- https://docs.aws.amazon.com/apprunner/latest/dg/apprunner-availability-change.html
- https://aws.amazon.com/sagemaker-ai/pricing/
