# Design — SageMaker training demo and guide [GRZR-11]

Aligned with ADR-001 (stack, SDK v3), ADR-002 (`aws login` + Execution Role), ADR-003 (Serverless only, guardrails), ADR-004 (no Origo), ADR-005 (`main` only). Vocabulary per `docs/CONTEXT.md`.

## ADR gate

| Trigger | Applies? | Note |
|---|---|---|
| Datastore / broker / cache | No | S3 for data and Model Artifact is already in ADR-003 / CONTEXT |
| Auth or payments provider | No | Covered by ADR-002 |
| Public contract / breaking change | No | No API is exposed beyond the Learner's own endpoint |
| New repo boundary / cross-repo coupling | No | Single repo, ADR-004 |
| Language / runtime / framework | No | Covered by ADR-001 (SDK v3 recorded 2026-10-15) |
| Contradicts an existing ADR | No | GRZR-113's App Runner text contradicts ADR-003; the ticket changes, not the ADR |

## Layout

```
pyproject.toml, uv.lock          sagemaker>=3,<4, boto3[crt] (required by `aws login` profiles), scikit-learn (dataset only), pandas; dev: pytest, pytest-cov, ruff, black, mypy
src/aws_train/
  config.py      Settings from env: AWS_PROFILE (required), AWS_REGION (default us-east-1), BUDGET_EMAIL (required), BUDGET_LIMIT_USD (default 10)
  tags.py        PROJECT_TAG = {"Key": "project", "Value": "aws-train"}; with_project_tag(extra) → list
  instances.py   ALLOWED_INSTANCE_TYPES = {"ml.m5.xlarge"}; require_allowed(instance_type) raises before any AWS call
  naming.py      deterministic names: bucket aws-train-<account_id>-<region>, role, job prefix, endpoint names
  dataset.py     load public dataset, train/validation split, to Built-in XGBoost CSV (label first, no header)
  payload.py     feature row → CSV body; parse endpoint response → float probability
  state.py       read/write .aws-train-state.json (gitignored): training job name, model data URI, endpoint names
  teardown.py    plan_deletions(tagged_arns) → ordered list (endpoints → endpoint configs → models → bucket); pure
  session.py     boto3 / sagemaker.Session factory from config (thin, not unit-tested)
steps/
  00_budget.py             Budget Guardrail (AWS Budgets, email subscriber, forecast + actual alerts)
  01_execution_role.py     Execution Role: trust sagemaker.amazonaws.com, inline policy scoped to the demo bucket + ECR pull + CloudWatch Logs
  02_upload_data.py        create tagged bucket, upload train/validation CSV
  03_train.py              ModelTrainer(training_image=image_uris.retrieve("xgboost", region, version=XGB_VERSION), compute=Compute(instance_type=allowlisted), input_data_config=[InputData(...)], tags=...).train()
  04_deploy_serverless.py  sagemaker.core.resources: Model.create → EndpointConfig.create(production_variants=[ProductionVariant(serverless_config=ProductionVariantServerlessConfig(memory_size_in_mb=2048, max_concurrency=1))]) → Endpoint.create, all tagged
  05_invoke_serverless.py  N calls; print first-call (cold start) and warm latencies
  99_teardown.py           find resources by Project Tag (Resource Groups Tagging API) + state file, delete per plan, empty and delete bucket, keep Budget and Role only if --keep-guardrails
tests/                     one module per src module
docs/guide/                Spanish: 00-prerequisites (account, IAM user, `aws login`, uv), one page per Step, 99-teardown, costs
```

## Key decisions inside the ADRs (reversible)

- **Dataset:** scikit-learn's breast cancer dataset (public, anonymized, no PII, binary target). It fits `binary:logistic` and loads offline from the installed package. Swapping it later only touches `dataset.py`.
- **XGBoost container version:** one constant `XGB_VERSION`. SDK v3.25 bundles 1.3-1, 1.5-1, 1.7-1, 3.0-5 and 3.2-0 (verified offline with `sagemaker.core.image_uris.retrieve`). Which of them Serverless Inference accepts is not verified; task 4 picks one and task 7's real run confirms it.
- **State between Steps:** a local JSON file, not SSM or tags, so that a Learner can read it and delete it. Steps re-derive what they can from deterministic names and use the file only for generated names (training job).
- **Idempotency:** every create is preceded by a describe/exists check; "already exists" → reuse and print it.
- **Teardown by tag, not only by state:** if the state file is lost, the tag still finds leftovers. Training Jobs cannot be deleted and cost nothing at rest, so they are ignored.
- **Budget and Role survive Teardown?** Default: Teardown deletes everything the demo created, Budget and Role included, because "zero leftovers" is the success criterion. Flag `--keep-guardrails` keeps them for a second run.
- **Execution Role permissions:** scoped inline policy instead of `AmazonSageMakerFullAccess`. I haven't verified the exact minimal action set Built-in XGBoost needs; the real run in task 7 validates it, and any missing action is added there.

## Failure modes the guide must handle

| Failure | Trigger | Handling |
|---|---|---|
| Expired `aws login` session | Session older than its 12 h refresh window | Steps catch `LoginError` / `NoCredentialsError` and print the exact `aws login --profile` command |
| Service quota 0 for an instance type | New accounts sometimes have 0 quota for `ml.m5.xlarge` training/endpoint usage | Step prints the quota name and the Service Quotas console link; guide section on requesting it (I haven't verified default quotas on new accounts) |
| Serverless cold start looks like a hang | First invocation after idle | Step 05 prints "first call includes cold start" and the measured latency |
| Learner stops halfway | Closes terminal after Step 04 | Budget alert + Teardown works from tags without the state file |

## Out of scope for design

Everything in proposal Non-goals. GRZR-113's text gets rewritten separately (Jira edit, shown to the dev first).
