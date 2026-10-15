"""Step 05: send validation rows to the Serverless Endpoint and time each call."""

import time

import boto3
from sagemaker.core.resources import Endpoint

from aws_train.config import Settings
from aws_train.dataset import LABEL_COLUMN, load_dataset, split
from aws_train.naming import SERVERLESS_ENDPOINT_NAME
from aws_train.payload import (
    CSV_CONTENT_TYPE,
    features_to_csv,
    parse_prediction,
    summarize_latencies,
)
from aws_train.runner import PreviousStepMissingError, resource_exists, run

CALLS = 5
DECISION_THRESHOLD = 0.5


def main(settings: Settings, session: boto3.Session) -> None:
    sagemaker = session.client("sagemaker")
    if not resource_exists(
        lambda: sagemaker.describe_endpoint(EndpointName=SERVERLESS_ENDPOINT_NAME)
    ):
        raise PreviousStepMissingError(
            f"Endpoint {SERVERLESS_ENDPOINT_NAME} not found. "
            "Run steps/04_deploy_serverless.py first."
        )
    endpoint = Endpoint.get(
        endpoint_name=SERVERLESS_ENDPOINT_NAME, session=session, region=settings.region
    )
    _, validation = split(load_dataset())

    latencies_ms: list[float] = []
    for _, row in validation.head(CALLS).iterrows():
        body = features_to_csv(row.drop(LABEL_COLUMN).tolist())
        started = time.perf_counter()
        response = endpoint.invoke(
            body=body,
            content_type=CSV_CONTENT_TYPE,
            accept=CSV_CONTENT_TYPE,
            session=session,
            region=settings.region,
        )
        latencies_ms.append((time.perf_counter() - started) * 1000)
        probability = parse_prediction(response.body if response else None)
        predicted = int(probability >= DECISION_THRESHOLD)
        print(
            f"label={int(row[LABEL_COLUMN])} predicted={predicted} "
            f"probability={probability:.3f} latency={latencies_ms[-1]:.0f} ms"
        )

    summary = summarize_latencies(latencies_ms)
    print(f"First call (may include cold start): {summary.first_ms:.0f} ms")
    if summary.warm_p50_ms is not None:
        print(f"Warm calls median over {summary.warm_calls}: {summary.warm_p50_ms:.0f} ms")


if __name__ == "__main__":
    run(main)
