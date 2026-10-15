# Proposal — SageMaker training demo and guide [GRZR-11]

**Jira:** GRZR-11 (epic GRZR-9) · subtask GRZR-113
**Branch:** `feature/GRZR-11-sagemaker-training-demo`

## Problem

Creai devs and data people who know Python and ML have no hands-on path to put a model behind an AWS endpoint. GRZR-11 collected links, but links are not a runnable exercise, and GRZR-113's App Runner path is no longer open to new AWS customers (closed 2026-04-30, see ADR-003).

## Goals

- A Learner with a personal AWS account and no AWS experience goes from zero to a working prediction from a SageMaker endpoint by running the Steps in order and reading the Spanish guide.
- The run ends with every created resource deleted, and cost exposure is bounded from Step 0.

## Non-goals

- FastAPI, Docker, ECR, ECS, App Runner or Lambda paths (ADR-003). GRZR-113 must be rewritten to match.
- CI/CD, GitHub Actions or OIDC deployment pipelines.
- Real or client data, hyperparameter tuning, model monitoring, SageMaker Studio or notebooks.
- Any coupling to Origo (ADR-004).
- Multi-region support beyond making the region configurable (verified in `us-east-1` only).
- Deploying a Real-time Endpoint; the guide explains when one fits but never creates it (ADR-003).

## Success criteria

1. `uv sync && uv run pytest` passes on a clean clone; local-logic coverage ≥ 70% (POLICIES backend floor).
2. Running `steps/00` through `steps/99` against a fresh personal account (`aws login` profile configured) produces: a Budget with email alert, a Training Job that completes, a Serverless Endpoint that returns a prediction with cold and warm latencies printed, and finally zero resources tagged `project=aws-train` left (verified with the Resource Groups Tagging API).
3. Re-running any Step without the Teardown does not create duplicates or fail (idempotency).
4. A Step asked to use an instance type outside the allowlist exits with an error before calling AWS.
5. `docs/guide/` (Spanish) covers account, IAM user and `aws login` setup, one section per Step, the cost warnings and the Teardown, and states the SDK v3 pin.

## Open questions

- SageMaker's free tier vs AWS's credit-based free plan for new accounts — I haven't verified it; the guide will not promise "free" (ADR-003).
- Built-in XGBoost on a Serverless Endpoint — I haven't verified it in a live account; task 7's real run confirms it. If it fails, the fallback is a Real-time Endpoint, which needs a superseding ADR-003.
