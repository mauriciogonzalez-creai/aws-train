# ADR-001: Python 3.12, uv and the SageMaker SDK with Built-in XGBoost

**Status:** Proposed
**Date:** 2026-10-15
**Deciders:** Mauricio González (tech lead)
**Tags:** stack, python, ml

## Context

The repo is a training guide plus a runnable demo for Learners who know Python and ML but not AWS. The demo must be reproducible on a personal account, cheap, and readable by a beginner. Every extra tool (Docker, IaC, a web framework) is one more subject competing with AWS itself for the Learner's attention.

## Decision

We will write the demo as numbered Python 3.12 scripts (Steps) managed with uv (venv + lockfile), calling AWS through the SageMaker Python SDK and boto3, training with SageMaker's Built-in XGBoost on a public non-PII dataset, and testing local logic with pytest.

## Consequences

### Positive

- No Docker, no IaC tool, no web server: the Learner only meets Python and AWS.
- Built-in XGBoost removes the need to write or maintain a training/inference container.
- uv gives one command to reproduce the exact environment from the lockfile.

### Negative

- Training runs remotely as a Training Job: every run costs money (cents on the allowlisted instance) and needs network access.
- Built-in XGBoost dictates the data format (CSV, label first, no header); the guide must teach it.
- The SageMaker SDK has had breaking major versions; the pinned major must be stated in the guide. Whether to pin v2 (what most tutorials, including those linked in GRZR-11, use) or v3 is OPEN — I haven't verified v3's API differences; resolve before the first Step is written.

### Neutral

- Scripts instead of notebooks: diffs stay readable; a notebook can be added later as an appendix.

## Alternatives considered

- **FastAPI container on ECS Express Mode / Lambda:** teaches generic containers but adds Docker, ECR and more IAM. Rejected as primary path for a beginner; may become an appendix.
- **AWS Console click-through:** easiest start but not reproducible and goes stale when the UI changes. Rejected.
- **CDK/Terraform:** reproducible but a whole extra subject. Rejected for this audience.
- **scikit-learn or PyTorch model:** sklearn would train locally; chosen XGBoost to teach a remote Training Job. PyTorch rejected as too heavy for a quick training.
- **pip + venv / Python 3.11:** familiar but no lockfile by default. Rejected in favour of uv.

## References

- GRZR-11 — Training de AWS
- https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html
