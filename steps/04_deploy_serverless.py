"""Step 04: serve the trained model from a SageMaker Serverless Endpoint."""

from pathlib import Path

import boto3
from sagemaker.core import image_uris
from sagemaker.core.resources import Endpoint, EndpointConfig, Model

from aws_train.config import Settings
from aws_train.hosting import (
    build_endpoint_config_kwargs,
    build_endpoint_kwargs,
    build_model_kwargs,
)
from aws_train.naming import MODEL_NAME, SERVERLESS_ENDPOINT_NAME
from aws_train.runner import (
    PreviousStepMissingError,
    account_id,
    execution_role_arn,
    require_budget,
    resource_exists,
    run,
)
from aws_train.state import STATE_FILE_NAME, load_state, update_state
from aws_train.training import XGB_VERSION

POLL_SECONDS = 15
TIMEOUT_SECONDS = 20 * 60


def main(settings: Settings, session: boto3.Session) -> None:
    require_budget(session, account_id(session))
    state_path = Path.cwd() / STATE_FILE_NAME
    model_data_url = load_state(state_path).get("model_data_url")
    if not model_data_url:
        raise PreviousStepMissingError("No trained model found. Run steps/03_train.py first.")
    sagemaker = session.client("sagemaker")
    region = settings.region

    if resource_exists(lambda: sagemaker.describe_model(ModelName=MODEL_NAME)):
        print(f"Model {MODEL_NAME} already exists.")
    else:
        Model.create(
            session=session,
            region=region,
            **build_model_kwargs(
                model_data_url=model_data_url,
                image_uri=image_uris.retrieve("xgboost", region, version=XGB_VERSION),
                role_arn=execution_role_arn(session),
            ),
        )
        print(f"Created Model {MODEL_NAME} from {model_data_url}.")

    if resource_exists(
        lambda: sagemaker.describe_endpoint_config(EndpointConfigName=SERVERLESS_ENDPOINT_NAME)
    ):
        print(f"Endpoint Configuration {SERVERLESS_ENDPOINT_NAME} already exists.")
    else:
        EndpointConfig.create(session=session, region=region, **build_endpoint_config_kwargs())
        print(f"Created serverless Endpoint Configuration {SERVERLESS_ENDPOINT_NAME}.")

    if resource_exists(lambda: sagemaker.describe_endpoint(EndpointName=SERVERLESS_ENDPOINT_NAME)):
        endpoint = Endpoint.get(
            endpoint_name=SERVERLESS_ENDPOINT_NAME, session=session, region=region
        )
        print(f"Endpoint {SERVERLESS_ENDPOINT_NAME} already exists.")
    else:
        endpoint = Endpoint.create(session=session, region=region, **build_endpoint_kwargs())
        print(f"Creating Endpoint {SERVERLESS_ENDPOINT_NAME} (usually a few minutes) ...")

    endpoint.wait_for_status("InService", poll=POLL_SECONDS, timeout=TIMEOUT_SECONDS)
    update_state(state_path, endpoint_name=SERVERLESS_ENDPOINT_NAME)
    print(f"Endpoint {SERVERLESS_ENDPOINT_NAME} is InService.")


if __name__ == "__main__":
    run(main)
