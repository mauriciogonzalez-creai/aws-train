# CONTEXT.md — aws-train

> Domain vocabulary, business rules and key concepts of this project. The agent reads this to avoid hallucinating domain terms. Keep entries short and precise.

**What this repo is:** a Spanish-language training guide plus a runnable demo that teaches a Creai dev or data person with no AWS experience how to train an XGBoost model and deploy it as a SageMaker endpoint in their own AWS account. Independent of the Origo platform (ADR-004). Jira: GRZR-11 (epic GRZR-9).

## Domain Vocabulary

- **Learner** — the person following the guide: a Creai dev/data person who knows Python and ML but not AWS. Every design choice is judged by "can a Learner run this unaided on a personal account?".
- **Step** — one numbered script under `steps/` (e.g. `00_budget.py`, `03_train.py`) plus its section in the guide. Steps run in order; each one is idempotent.
- **Training Job** — a SageMaker job that trains the model on a remote, per-second-billed instance using the built-in XGBoost algorithm.
- **Built-in XGBoost** — the AWS-managed XGBoost container, addressed by an **Image URI** resolved per region; we write no training container of our own.
- **Model Artifact** — the `model.tar.gz` a Training Job writes to S3; the only thing that travels from training to deployment.
- **SageMaker Model** — the resource that binds a Model Artifact, an Image URI and the Execution Role. Not the same as the trained model file.
- **Endpoint Configuration** — the resource that says HOW a SageMaker Model is served (instance type and count, or serverless memory and concurrency).
- **Endpoint** — the live HTTPS inference resource created from an Endpoint Configuration.
- **Serverless Endpoint** — an Endpoint that scales to zero and bills per request; the guide's primary path.
- **Real-time Endpoint** — an Endpoint on a dedicated instance that bills per hour while it exists; taught as a comparison only.
- **Cold start** — the extra latency on the first call to a Serverless Endpoint after it scaled to zero.
- **Execution Role** — the IAM role SageMaker assumes to read and write S3 and pull the Image URI. Distinct from the Learner's own SSO credentials.
- **Budget Guardrail** — the AWS Budget with email alert created by Step 0 before any billable resource.
- **Project Tag** — the tag `project=aws-train` carried by every resource the demo creates; the Teardown finds resources by it.
- **Teardown** — the final Step that deletes every tagged resource (Endpoint, Endpoint Configuration, SageMaker Model, S3 bucket).

## Business Rules

- Step 0 creates the Budget Guardrail; no Step may create a billable resource before it exists (ref: GRZR-11 kickoff, 2026-10-15).
- Every resource the demo creates carries the Project Tag; a resource created without it is a bug, because the Teardown cannot find it.
- The guide always ends with the Teardown Step; any new Step that creates a resource must extend the Teardown in the same change.
- Instance types come from a single allowlist constant; Steps reject any other type. The allowlist holds the smallest free-tier-eligible types (ml.m5.xlarge for training and real-time per AWS's published free tier — I haven't verified the current free-tier list; re-check before the first release).
- The Serverless Endpoint is the primary path; the Real-time Endpoint section must warn about per-hour billing and send the Learner to the Teardown immediately after the comparison.
- Only public, non-PII datasets are used. Real or client data is out of scope for this repo.
- Default region is `us-east-1`; the region is configurable but the guide is only verified there.
- AWS App Runner is not used: it closed to new customers on 2026-04-30, so a Learner's new account cannot follow that path.

## External Integrations

- **AWS IAM Identity Center** — auth: SSO via `aws configure sso` (temporary credentials). Used for: the Learner's access to their own account (ADR-002).
- **AWS IAM** — auth: Learner's SSO session. Used for: creating the Execution Role.
- **Amazon S3** — auth: SSO session (scripts) / Execution Role (SageMaker). Used for: training data and the Model Artifact.
- **Amazon SageMaker AI** — auth: SSO session + Execution Role. Used for: Training Job, SageMaker Model, Endpoint Configuration, Endpoints, inference calls.
- **AWS Budgets** — auth: SSO session. Used for: the Budget Guardrail in Step 0.

## Key Concepts

- **Training → S3 → Endpoint** — the whole guide in one line: a Training Job writes a Model Artifact to S3; a SageMaker Model wraps it; an Endpoint serves it.
- **Steps are the demo** — there is no application server; the deliverable is the ordered Steps plus the guide that explains each one.
- **Pure-logic tests** — pytest covers local logic only (data prep, CSV payload format, config and tag validation). AWS calls are not mocked; the end-to-end flow is verified by running the guide against a real account.
- **Two languages** — the guide (README/docs for the Learner) is in Spanish; code, comments, commits and agent-facing docs are in English.

## Estimation Scale

**Estimation unit:** hours

**Parent roll-up target:** none (Jira aggregates)

**Write size labels to Jira:** yes
**Size label prefix:** `talla-`

| Size | Range | Typical work |
|------|-------|--------------|
| S | ≤ 3 h | One Step or one guide section adjustment |
| M | 4–8 h | A new Step with its tests and guide section |
| L | 9–24 h | A multi-Step path (e.g. the Real-time comparison end to end) |
| XL | > 24 h | Over the vara — split the subtask |
