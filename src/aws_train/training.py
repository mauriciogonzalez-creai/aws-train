"""Training Job configuration for Built-in XGBoost (Step 03)."""

from typing import Any

from sagemaker.core.training.configs import Compute, InputData, OutputDataConfig

from aws_train.instances import require_allowed
from aws_train.naming import TRAINING_JOB_PREFIX
from aws_train.tags import as_sdk_tags

XGB_VERSION = "1.7-1"
CSV_CONTENT_TYPE = "text/csv"
DATA_PREFIX = "data"
MODELS_PREFIX = "models"
HYPERPARAMETERS: dict[str, str] = {
    "objective": "binary:logistic",
    "eval_metric": "auc",
    "num_round": "100",
    "max_depth": "4",
    "eta": "0.2",
}


def data_uris(bucket: str) -> dict[str, str]:
    """S3 URIs of the train and validation CSVs, keyed by channel name."""
    return {
        channel: f"s3://{bucket}/{DATA_PREFIX}/{channel}.csv" for channel in ("train", "validation")
    }


def build_trainer_kwargs(
    *, bucket: str, role_arn: str, image_uri: str, instance_type: str
) -> dict[str, Any]:
    """Keyword arguments for ``sagemaker.train.ModelTrainer``.

    Raises InstanceNotAllowedError before anything is sent to AWS.
    """
    return {
        "training_image": image_uri,
        "role": role_arn,
        "base_job_name": TRAINING_JOB_PREFIX,
        "compute": Compute(instance_type=require_allowed(instance_type), instance_count=1),
        "hyperparameters": HYPERPARAMETERS,
        "input_data_config": [
            InputData(channel_name=channel, data_source=uri, content_type=CSV_CONTENT_TYPE)
            for channel, uri in data_uris(bucket).items()
        ],
        "output_data_config": OutputDataConfig(s3_output_path=f"s3://{bucket}/{MODELS_PREFIX}"),
        "tags": as_sdk_tags(),
    }
