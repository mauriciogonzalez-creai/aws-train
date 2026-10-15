from typing import Any

from aws_train.hosting import (
    MAX_CONCURRENCY,
    MEMORY_SIZE_MB,
    build_endpoint_config_kwargs,
    build_endpoint_kwargs,
    build_model_kwargs,
)
from aws_train.naming import MODEL_NAME, SERVERLESS_ENDPOINT_NAME
from aws_train.tags import PROJECT_TAG

ARTIFACT = "s3://aws-train-123456789012-us-east-1/models/job/output/model.tar.gz"
ROLE = "arn:aws:iam::123456789012:role/aws-train-sagemaker-execution"
IMAGE = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-xgboost:1.7-1"
PROJECT = (PROJECT_TAG["Key"], PROJECT_TAG["Value"])


def _tag_pairs(kwargs: dict[str, Any]) -> set[tuple[str, str]]:
    return {(tag.key, tag.value) for tag in kwargs["tags"]}


def test_model_wraps_the_artifact_image_and_role() -> None:
    kwargs = build_model_kwargs(model_data_url=ARTIFACT, image_uri=IMAGE, role_arn=ROLE)

    assert kwargs["model_name"] == MODEL_NAME
    assert kwargs["execution_role_arn"] == ROLE
    assert kwargs["primary_container"].image == IMAGE
    assert kwargs["primary_container"].model_data_url == ARTIFACT
    assert PROJECT in _tag_pairs(kwargs)


def test_endpoint_config_is_serverless_only() -> None:
    kwargs = build_endpoint_config_kwargs()
    (variant,) = kwargs["production_variants"]

    assert kwargs["endpoint_config_name"] == SERVERLESS_ENDPOINT_NAME
    assert variant.model_name == MODEL_NAME
    assert variant.serverless_config.memory_size_in_mb == MEMORY_SIZE_MB
    assert variant.serverless_config.max_concurrency == MAX_CONCURRENCY
    assert PROJECT in _tag_pairs(kwargs)


def test_endpoint_config_never_requests_an_instance() -> None:
    (variant,) = build_endpoint_config_kwargs()["production_variants"]

    assert not variant.instance_type
    assert not variant.initial_instance_count


def test_endpoint_uses_the_serverless_config_and_is_tagged() -> None:
    kwargs = build_endpoint_kwargs()

    assert kwargs["endpoint_name"] == SERVERLESS_ENDPOINT_NAME
    assert kwargs["endpoint_config_name"] == SERVERLESS_ENDPOINT_NAME
    assert PROJECT in _tag_pairs(kwargs)
