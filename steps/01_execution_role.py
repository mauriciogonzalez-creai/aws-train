"""Step 01: create the Execution Role that SageMaker assumes."""

import json

import boto3

from aws_train.config import Settings
from aws_train.execution_role import build_create_role_request, execution_policy
from aws_train.naming import ROLE_NAME, ROLE_POLICY_NAME, bucket_name
from aws_train.runner import account_id, run


def main(settings: Settings, session: boto3.Session) -> None:
    iam = session.client("iam")
    try:
        role = iam.get_role(RoleName=ROLE_NAME)["Role"]
        print(f"Role {ROLE_NAME} already exists.")
    except iam.exceptions.NoSuchEntityException:
        role = iam.create_role(**build_create_role_request())["Role"]
        print(f"Created role {ROLE_NAME}.")
    bucket = bucket_name(account_id(session), settings.region)
    iam.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName=ROLE_POLICY_NAME,
        PolicyDocument=json.dumps(execution_policy(bucket)),
    )
    print(f"Policy {ROLE_POLICY_NAME} scoped to bucket {bucket}.")
    print(f"Role ARN: {role['Arn']}")


if __name__ == "__main__":
    run(main)
