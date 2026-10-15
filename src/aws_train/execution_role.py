"""Execution Role that SageMaker assumes for training and hosting (Step 01)."""

import json
from typing import Any

from aws_train.naming import ROLE_NAME
from aws_train.tags import with_project_tag

POLICY_VERSION = "2012-10-17"
SAGEMAKER_LOG_GROUPS = "arn:aws:logs:*:*:log-group:/aws/sagemaker/*"


def trust_policy() -> dict[str, Any]:
    """Allow only the SageMaker service to assume the role."""
    return {
        "Version": POLICY_VERSION,
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "sagemaker.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }


def execution_policy(bucket: str) -> dict[str, Any]:
    """Least-privilege inline policy: the demo bucket, the Built-in image, logs and metrics.

    ECR actions use ``*`` resources because the Built-in XGBoost image lives in an
    AWS-owned account that differs per region.
    """
    bucket_arn = f"arn:aws:s3:::{bucket}"
    return {
        "Version": POLICY_VERSION,
        "Statement": [
            {
                "Sid": "DemoBucketObjects",
                "Effect": "Allow",
                "Action": ["s3:GetObject", "s3:PutObject"],
                "Resource": [f"{bucket_arn}/*"],
            },
            {
                "Sid": "DemoBucketListing",
                "Effect": "Allow",
                "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
                "Resource": [bucket_arn],
            },
            {
                "Sid": "PullBuiltinImage",
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:BatchGetImage",
                    "ecr:GetDownloadUrlForLayer",
                ],
                "Resource": ["*"],
            },
            {
                "Sid": "SageMakerLogs",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:DescribeLogStreams",
                    "logs:PutLogEvents",
                ],
                "Resource": [SAGEMAKER_LOG_GROUPS],
            },
            {
                "Sid": "SageMakerMetrics",
                "Effect": "Allow",
                "Action": ["cloudwatch:PutMetricData"],
                "Resource": ["*"],
            },
        ],
    }


def build_create_role_request() -> dict[str, Any]:
    """Keyword arguments for ``iam.create_role``."""
    return {
        "RoleName": ROLE_NAME,
        "AssumeRolePolicyDocument": json.dumps(trust_policy()),
        "Description": "Assumed by SageMaker for the aws-train demo (training and hosting).",
        "Tags": with_project_tag(),
    }
