from aws_train.naming import (
    BUDGET_NAME,
    MODEL_NAME,
    ROLE_NAME,
    SERVERLESS_ENDPOINT_NAME,
)
from aws_train.teardown import Deletion, plan_deletions

BUCKET = "aws-train-123456789012-us-east-1"
SM = "arn:aws:sagemaker:us-east-1:123456789012"


def _plan(arns: list[str], keep_guardrails: bool = False) -> list[Deletion]:
    return plan_deletions(arns, bucket=BUCKET, keep_guardrails=keep_guardrails)


def test_known_resources_are_planned_in_dependency_order() -> None:
    assert _plan([]) == [
        Deletion("endpoint", SERVERLESS_ENDPOINT_NAME),
        Deletion("endpoint-config", SERVERLESS_ENDPOINT_NAME),
        Deletion("model", MODEL_NAME),
        Deletion("bucket", BUCKET),
        Deletion("budget", BUDGET_NAME),
        Deletion("role", ROLE_NAME),
    ]


def test_extra_tagged_resources_join_their_group() -> None:
    plan = _plan([f"{SM}:model/aws-train-xgb-model-2", f"{SM}:endpoint/aws-train-old"])
    kinds = [deletion.kind for deletion in plan]

    assert Deletion("model", "aws-train-xgb-model-2") in plan
    assert Deletion("endpoint", "aws-train-old") in plan
    assert kinds == sorted(
        kinds, key=["endpoint", "endpoint-config", "model", "bucket", "budget", "role"].index
    )


def test_known_resources_reported_by_tags_are_not_duplicated() -> None:
    plan = _plan([f"{SM}:endpoint/{SERVERLESS_ENDPOINT_NAME}", f"arn:aws:s3:::{BUCKET}"])

    assert len(plan) == len(set(plan)) == 6


def test_training_jobs_are_ignored() -> None:
    plan = _plan([f"{SM}:training-job/aws-train-xgb-2026-10-15-14-05-09-123"])

    assert all(deletion.kind != "training-job" for deletion in plan)
    assert len(plan) == 6


def test_resources_outside_the_demo_prefix_are_ignored() -> None:
    plan = _plan([f"{SM}:endpoint/production-api", "arn:aws:s3:::someone-elses-bucket"])

    assert Deletion("endpoint", "production-api") not in plan
    assert Deletion("bucket", "someone-elses-bucket") not in plan


def test_unsupported_resource_types_are_ignored() -> None:
    plan = _plan(["arn:aws:logs:us-east-1:123456789012:log-group:/aws/sagemaker/aws-train-x"])

    assert len(plan) == 6


def test_keep_guardrails_keeps_budget_and_role() -> None:
    kinds = {deletion.kind for deletion in _plan([], keep_guardrails=True)}

    assert "budget" not in kinds
    assert "role" not in kinds
    assert {"endpoint", "endpoint-config", "model", "bucket"} <= kinds
