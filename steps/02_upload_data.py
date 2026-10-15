"""Step 02: create the demo bucket and upload the training data."""

from typing import Any

import boto3
from botocore.exceptions import ClientError

from aws_train.config import Settings
from aws_train.dataset import load_dataset, split, to_xgboost_csv
from aws_train.naming import bucket_name
from aws_train.runner import account_id, require_budget, run
from aws_train.tags import with_project_tag
from aws_train.training import DATA_PREFIX

US_EAST_1 = "us-east-1"


def ensure_bucket(s3: Any, bucket: str, region: str) -> None:
    try:
        s3.head_bucket(Bucket=bucket)
        print(f"Bucket {bucket} already exists.")
        return
    except ClientError as error:
        if error.response["Error"]["Code"] not in ("404", "NoSuchBucket"):
            raise
    if region == US_EAST_1:
        s3.create_bucket(Bucket=bucket)
    else:
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": region})
    print(f"Created bucket {bucket}.")


def main(settings: Settings, session: boto3.Session) -> None:
    account = account_id(session)
    require_budget(session, account)
    bucket = bucket_name(account, settings.region)
    s3 = session.client("s3")
    ensure_bucket(s3, bucket, settings.region)
    s3.put_bucket_tagging(Bucket=bucket, Tagging={"TagSet": with_project_tag()})

    train, validation = split(load_dataset())
    for channel, frame in (("train", train), ("validation", validation)):
        key = f"{DATA_PREFIX}/{channel}.csv"
        s3.put_object(Bucket=bucket, Key=key, Body=to_xgboost_csv(frame).encode("utf-8"))
        print(f"Uploaded s3://{bucket}/{key} ({len(frame)} rows).")


if __name__ == "__main__":
    run(main)
