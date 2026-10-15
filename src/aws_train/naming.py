"""Deterministic resource names, so Steps can find what earlier Steps created."""

import re

PREFIX = "aws-train"
ROLE_NAME = f"{PREFIX}-sagemaker-execution"
ROLE_POLICY_NAME = f"{PREFIX}-sagemaker-execution-policy"
BUDGET_NAME = f"{PREFIX}-budget"
TRAINING_JOB_PREFIX = f"{PREFIX}-xgb"
MODEL_NAME = f"{PREFIX}-xgb-model"
SERVERLESS_ENDPOINT_NAME = f"{PREFIX}-serverless"

_ACCOUNT_ID = re.compile(r"\d{12}")


def bucket_name(account_id: str, region: str) -> str:
    """Globally unique demo bucket name for one account and region."""
    if not _ACCOUNT_ID.fullmatch(account_id):
        raise ValueError(f"Expected a 12-digit AWS account id, got {account_id!r}")
    return f"{PREFIX}-{account_id}-{region}"
