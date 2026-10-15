"""SageMaker Model, Endpoint Configuration and Serverless Endpoint requests (Step 04)."""

from typing import Any

from sagemaker.core.shapes import (
    ContainerDefinition,
    ProductionVariant,
    ProductionVariantServerlessConfig,
)

from aws_train.naming import MODEL_NAME, SERVERLESS_ENDPOINT_NAME
from aws_train.tags import as_sdk_tags

MEMORY_SIZE_MB = 2048
MAX_CONCURRENCY = 1
VARIANT_NAME = "AllTraffic"


def build_model_kwargs(*, model_data_url: str, image_uri: str, role_arn: str) -> dict[str, Any]:
    """Keyword arguments for ``sagemaker.core.resources.Model.create``."""
    return {
        "model_name": MODEL_NAME,
        "primary_container": ContainerDefinition(image=image_uri, model_data_url=model_data_url),
        "execution_role_arn": role_arn,
        "tags": as_sdk_tags(),
    }


def build_endpoint_config_kwargs() -> dict[str, Any]:
    """Keyword arguments for ``EndpointConfig.create``: one serverless variant, no instances."""
    return {
        "endpoint_config_name": SERVERLESS_ENDPOINT_NAME,
        "production_variants": [
            ProductionVariant(
                variant_name=VARIANT_NAME,
                model_name=MODEL_NAME,
                serverless_config=ProductionVariantServerlessConfig(
                    memory_size_in_mb=MEMORY_SIZE_MB, max_concurrency=MAX_CONCURRENCY
                ),
            )
        ],
        "tags": as_sdk_tags(),
    }


def build_endpoint_kwargs() -> dict[str, Any]:
    """Keyword arguments for ``Endpoint.create``."""
    return {
        "endpoint_name": SERVERLESS_ENDPOINT_NAME,
        "endpoint_config_name": SERVERLESS_ENDPOINT_NAME,
        "tags": as_sdk_tags(),
    }
