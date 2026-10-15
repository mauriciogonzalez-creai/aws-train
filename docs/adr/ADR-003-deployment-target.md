# ADR-003: SageMaker Serverless Endpoint in us-east-1, Real-time Endpoint as Comparison

**Status:** Proposed
**Date:** 2026-10-15
**Deciders:** Mauricio González (tech lead)
**Tags:** infra, aws, deployment, cost

## Context

The guide must show a model served behind an endpoint, on the Learner's personal account and card. GRZR-11 originally suggested SageMaker or a FastAPI container on App Runner; App Runner closed to new customers on 2026-04-30, so a new account cannot use it. A Real-time Endpoint bills per hour while it exists, so a Learner who skips the Teardown keeps paying.

## Decision

We will deploy to Amazon SageMaker AI in `us-east-1`, using a Serverless Endpoint as the primary path and a Real-time Endpoint on an allowlisted instance as a guided comparison followed immediately by the Teardown. Cost guardrails (Budget Guardrail at Step 0, Project Tag on every resource, instance allowlist, mandatory Teardown) are part of this decision.

## Consequences

### Positive

- A forgotten Serverless Endpoint costs roughly nothing at rest.
- The comparison teaches when each endpoint type fits (cold start vs per-hour cost).
- `us-east-1` has the broadest SageMaker availability.

### Negative

- Serverless cold start makes the first call slow; the guide must explain it so it doesn't look like a failure.
- The Real-time section still carries real cost risk; the guardrails reduce but do not remove it.
- How SageMaker's free tier (2 months from first SageMaker resource) interacts with AWS's newer credit-based free plan is OPEN — I haven't verified it. The guide must not promise "free".

### Neutral

- Region is configurable, but the guide is only verified in `us-east-1`.

## Alternatives considered

- **FastAPI on App Runner:** closed to new customers since 2026-04-30. Rejected.
- **FastAPI on ECS Express Mode:** App Runner's AWS-recommended replacement; adds Docker, ECR and IAM. Rejected as primary path.
- **FastAPI on Lambda:** cheap, but package-size limits and not the typical ML path. Rejected.
- **Real-time Endpoint only:** typical production choice, but per-hour billing on a personal card. Rejected as primary.

## References

- GRZR-11 — Training de AWS
- https://docs.aws.amazon.com/apprunner/latest/dg/apprunner-availability-change.html
- https://aws.amazon.com/sagemaker-ai/pricing/
