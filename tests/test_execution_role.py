import json
from typing import Any

from aws_train.execution_role import build_create_role_request, execution_policy, trust_policy
from aws_train.naming import ROLE_NAME
from aws_train.tags import PROJECT_TAG

BUCKET = "aws-train-123456789012-us-east-1"


def _statements(policy: dict[str, Any]) -> list[dict[str, Any]]:
    statements = policy["Statement"]
    assert isinstance(statements, list)
    return statements


def test_trust_policy_lets_only_sagemaker_assume_the_role() -> None:
    (statement,) = _statements(trust_policy())

    assert statement["Effect"] == "Allow"
    assert statement["Action"] == "sts:AssumeRole"
    assert statement["Principal"] == {"Service": "sagemaker.amazonaws.com"}


def test_s3_access_is_scoped_to_the_demo_bucket() -> None:
    s3_resources = [
        resource
        for statement in _statements(execution_policy(BUCKET))
        if any(str(action).startswith("s3:") for action in statement["Action"])
        for resource in statement["Resource"]
    ]

    assert s3_resources
    assert set(s3_resources) == {
        f"arn:aws:s3:::{BUCKET}",
        f"arn:aws:s3:::{BUCKET}/*",
    }


def test_execution_policy_never_grants_wildcard_actions() -> None:
    for statement in _statements(execution_policy(BUCKET)):
        for action in statement["Action"]:
            assert action != "*"
            assert not str(action).endswith(":*")


def test_execution_policy_allows_pulling_the_builtin_image() -> None:
    actions = {
        action
        for statement in _statements(execution_policy(BUCKET))
        for action in statement["Action"]
    }

    assert {"ecr:GetAuthorizationToken", "ecr:BatchGetImage"} <= actions


def test_create_role_request_is_tagged_and_serializes_the_trust_policy() -> None:
    request = build_create_role_request()

    assert request["RoleName"] == ROLE_NAME
    assert json.loads(str(request["AssumeRolePolicyDocument"])) == trust_policy()
    assert PROJECT_TAG in request["Tags"]
