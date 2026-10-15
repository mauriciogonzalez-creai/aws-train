from typing import Any

import pytest

from aws_train.instances import InstanceNotAllowedError
from aws_train.naming import TRAINING_JOB_PREFIX
from aws_train.tags import PROJECT_TAG
from aws_train.training import (
    HYPERPARAMETERS,
    build_trainer_kwargs,
    data_uris,
)

BUCKET = "aws-train-123456789012-us-east-1"
ROLE = "arn:aws:iam::123456789012:role/aws-train-sagemaker-execution"
IMAGE = "683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-xgboost:1.7-1"


def _kwargs(instance_type: str = "ml.m5.xlarge") -> dict[str, Any]:
    return build_trainer_kwargs(
        bucket=BUCKET, role_arn=ROLE, image_uri=IMAGE, instance_type=instance_type
    )


def test_data_uris_point_into_the_demo_bucket() -> None:
    assert data_uris(BUCKET) == {
        "train": f"s3://{BUCKET}/data/train.csv",
        "validation": f"s3://{BUCKET}/data/validation.csv",
    }


def test_hyperparameters_are_binary_classification() -> None:
    assert HYPERPARAMETERS["objective"] == "binary:logistic"


def test_trainer_uses_the_builtin_image_role_and_job_prefix() -> None:
    kwargs = _kwargs()

    assert kwargs["training_image"] == IMAGE
    assert kwargs["role"] == ROLE
    assert kwargs["base_job_name"] == TRAINING_JOB_PREFIX
    assert kwargs["hyperparameters"] == HYPERPARAMETERS


def test_trainer_runs_one_allowlisted_instance() -> None:
    compute = _kwargs()["compute"]

    assert compute.instance_type == "ml.m5.xlarge"
    assert compute.instance_count == 1


def test_trainer_rejects_an_instance_outside_the_allowlist() -> None:
    with pytest.raises(InstanceNotAllowedError):
        _kwargs("ml.p3.2xlarge")


def test_trainer_reads_csv_channels_and_writes_into_the_bucket() -> None:
    kwargs = _kwargs()
    channels = {c.channel_name: c for c in kwargs["input_data_config"]}

    assert set(channels) == {"train", "validation"}
    assert all(c.content_type == "text/csv" for c in channels.values())
    assert channels["train"].data_source == f"s3://{BUCKET}/data/train.csv"
    assert kwargs["output_data_config"].s3_output_path == f"s3://{BUCKET}/models"


def test_trainer_is_tagged() -> None:
    tags = {(tag.key, tag.value) for tag in _kwargs()["tags"]}

    assert (PROJECT_TAG["Key"], PROJECT_TAG["Value"]) in tags
