"""Step 03: train Built-in XGBoost in a SageMaker Training Job."""

import sys
from pathlib import Path
from typing import Any

import boto3
from sagemaker.core import image_uris
from sagemaker.core.helper.session_helper import Session
from sagemaker.train import ModelTrainer

from aws_train.config import Settings
from aws_train.instances import TRAINING_INSTANCE_TYPE
from aws_train.naming import TRAINING_JOB_PREFIX, bucket_name
from aws_train.runner import account_id, execution_role_arn, require_budget, run
from aws_train.state import STATE_FILE_NAME, update_state
from aws_train.training import XGB_VERSION, build_trainer_kwargs

RETRAIN_FLAG = "--retrain"


def latest_completed_job(sagemaker: Any) -> dict[str, Any] | None:
    summaries = sagemaker.list_training_jobs(
        NameContains=TRAINING_JOB_PREFIX,
        StatusEquals="Completed",
        SortBy="CreationTime",
        SortOrder="Descending",
        MaxResults=1,
    )["TrainingJobSummaries"]
    if not summaries:
        return None
    job: dict[str, Any] = sagemaker.describe_training_job(
        TrainingJobName=summaries[0]["TrainingJobName"]
    )
    return job


def save_artifact(job: dict[str, Any]) -> None:
    artifact = job["ModelArtifacts"]["S3ModelArtifacts"]
    update_state(
        Path.cwd() / STATE_FILE_NAME,
        training_job_name=job["TrainingJobName"],
        model_data_url=artifact,
    )
    print(f"Model Artifact: {artifact}")


def main(settings: Settings, session: boto3.Session) -> None:
    account = account_id(session)
    require_budget(session, account)
    sagemaker = session.client("sagemaker")

    previous = latest_completed_job(sagemaker)
    if previous is not None and RETRAIN_FLAG not in sys.argv:
        print(
            f"Reusing completed Training Job {previous['TrainingJobName']} "
            f"(pass {RETRAIN_FLAG} to train again)."
        )
        save_artifact(previous)
        return

    bucket = bucket_name(account, settings.region)
    image_uri = image_uris.retrieve("xgboost", settings.region, version=XGB_VERSION)
    trainer = ModelTrainer(
        sagemaker_session=Session(boto_session=session, default_bucket=bucket),
        **build_trainer_kwargs(
            bucket=bucket,
            role_arn=execution_role_arn(session),
            image_uri=image_uri,
            instance_type=TRAINING_INSTANCE_TYPE,
        ),
    )
    print(f"Starting Training Job on {TRAINING_INSTANCE_TYPE} with {image_uri} ...")
    trainer.train(wait=True, logs=True)

    job = latest_completed_job(sagemaker)
    if job is None:
        raise RuntimeError("The Training Job did not complete; check its logs in CloudWatch.")
    save_artifact(job)


if __name__ == "__main__":
    run(main)
