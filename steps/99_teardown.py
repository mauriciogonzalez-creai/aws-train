"""Step 99: delete everything the demo created (pass --keep-guardrails to keep Budget and Role)."""

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError

from aws_train.budget import BUDGETS_REGION
from aws_train.config import Settings
from aws_train.naming import ROLE_POLICY_NAME, bucket_name
from aws_train.runner import account_id, run
from aws_train.state import STATE_FILE_NAME
from aws_train.tags import PROJECT_TAG_KEY, PROJECT_TAG_VALUE
from aws_train.teardown import Deletion, plan_deletions

KEEP_GUARDRAILS_FLAG = "--keep-guardrails"
NOT_FOUND_CODES = frozenset({"NoSuchBucket", "NoSuchEntity", "NotFoundException", "404"})
SAGEMAKER_NOT_FOUND = "Could not find"
TRAINING_JOB_MARKER = ":training-job/"


def tagged_arns(session: boto3.Session) -> list[str]:
    paginator = session.client("resourcegroupstaggingapi").get_paginator("get_resources")
    pages = paginator.paginate(TagFilters=[{"Key": PROJECT_TAG_KEY, "Values": [PROJECT_TAG_VALUE]}])
    return [item["ResourceARN"] for page in pages for item in page["ResourceTagMappingList"]]


def empty_and_delete_bucket(s3: Any, bucket: str) -> None:
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket):
        objects = [{"Key": item["Key"]} for item in page.get("Contents", [])]
        if objects:
            s3.delete_objects(Bucket=bucket, Delete={"Objects": objects})
    s3.delete_bucket(Bucket=bucket)


def delete_role(iam: Any, role: str) -> None:
    try:
        iam.delete_role_policy(RoleName=role, PolicyName=ROLE_POLICY_NAME)
    except iam.exceptions.NoSuchEntityException:
        pass
    iam.delete_role(RoleName=role)


def deleters(session: boto3.Session, account: str) -> dict[str, Callable[[str], object]]:
    sagemaker = session.client("sagemaker")
    budgets = session.client("budgets", region_name=BUDGETS_REGION)
    return {
        "endpoint": lambda name: sagemaker.delete_endpoint(EndpointName=name),
        "endpoint-config": lambda name: sagemaker.delete_endpoint_config(EndpointConfigName=name),
        "model": lambda name: sagemaker.delete_model(ModelName=name),
        "bucket": lambda name: empty_and_delete_bucket(session.client("s3"), name),
        "budget": lambda name: budgets.delete_budget(AccountId=account, BudgetName=name),
        "role": lambda name: delete_role(session.client("iam"), name),
    }


def is_not_found(error: ClientError) -> bool:
    code = error.response["Error"]["Code"]
    message = error.response["Error"].get("Message", "")
    return code in NOT_FOUND_CODES or (
        code == "ValidationException" and SAGEMAKER_NOT_FOUND in message
    )


def delete(deletion: Deletion, deleter: Callable[[str], object]) -> None:
    try:
        deleter(deletion.name)
        print(f"Deleted {deletion.kind} {deletion.name}.")
    except ClientError as error:
        if not is_not_found(error):
            raise
        print(f"Skipped {deletion.kind} {deletion.name} (not found).")


def main(settings: Settings, session: boto3.Session) -> None:
    account = account_id(session)
    keep_guardrails = KEEP_GUARDRAILS_FLAG in sys.argv
    plan = plan_deletions(
        tagged_arns(session),
        bucket=bucket_name(account, settings.region),
        keep_guardrails=keep_guardrails,
    )
    by_kind = deleters(session, account)
    for deletion in plan:
        delete(deletion, by_kind[deletion.kind])

    (Path.cwd() / STATE_FILE_NAME).unlink(missing_ok=True)

    leftovers = [arn for arn in tagged_arns(session) if TRAINING_JOB_MARKER not in arn]
    if leftovers:
        print("Still tagged project=aws-train (deletions can take a few minutes to show):")
        for arn in leftovers:
            print(f"  {arn}")
    else:
        print("No resources tagged project=aws-train remain (Training Jobs excluded).")
    if keep_guardrails:
        print("Kept the Budget and the Execution Role (--keep-guardrails).")


if __name__ == "__main__":
    run(main)
