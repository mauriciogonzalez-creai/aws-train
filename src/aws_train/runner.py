"""Shared entry point for Steps: settings, session, and readable failures."""

import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NoReturn

import boto3
from botocore.exceptions import ClientError, LoginError, NoCredentialsError

from aws_train.budget import BUDGETS_REGION
from aws_train.config import ENV_FILE_NAME, ConfigError, Settings, load_settings, resolve_env
from aws_train.instances import InstanceNotAllowedError
from aws_train.naming import BUDGET_NAME, ROLE_NAME

StepMain = Callable[[Settings, boto3.Session], None]

_EXPIRED_CREDENTIALS = (LoginError, NoCredentialsError)


def make_session(settings: Settings) -> boto3.Session:
    return boto3.Session(profile_name=settings.profile, region_name=settings.region)


def account_id(session: boto3.Session) -> str:
    return str(session.client("sts").get_caller_identity()["Account"])


class PreviousStepMissingError(RuntimeError):
    """Raised when a Step needs something an earlier Step creates."""


def require_budget(session: boto3.Session, account: str) -> None:
    """Refuse to continue until Step 00 has created the Budget Guardrail."""
    budgets = session.client("budgets", region_name=BUDGETS_REGION)
    try:
        budgets.describe_budget(AccountId=account, BudgetName=BUDGET_NAME)
    except budgets.exceptions.NotFoundException as error:
        raise PreviousStepMissingError(
            f"Budget {BUDGET_NAME} not found. Run steps/00_budget.py first."
        ) from error


def execution_role_arn(session: boto3.Session) -> str:
    """ARN of the Execution Role created by Step 01."""
    iam = session.client("iam")
    try:
        return str(iam.get_role(RoleName=ROLE_NAME)["Role"]["Arn"])
    except iam.exceptions.NoSuchEntityException as error:
        raise PreviousStepMissingError(
            f"Role {ROLE_NAME} not found. Run steps/01_execution_role.py first."
        ) from error


def resource_exists(describe: Callable[[], object]) -> bool:
    """True if a SageMaker ``describe_*`` call succeeds, False if the resource doesn't exist."""
    try:
        describe()
    except ClientError as error:
        if error.response["Error"]["Code"] == "ValidationException":
            return False
        raise
    return True


def run(main: StepMain) -> NoReturn:
    """Run a Step's ``main`` and exit 0, or print the cause and exit 1."""
    try:
        settings = load_settings(resolve_env(Path.cwd() / ENV_FILE_NAME, os.environ))
    except ConfigError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        sys.exit(1)
    try:
        main(settings, make_session(settings))
    except _EXPIRED_CREDENTIALS:
        print(
            f"AWS credentials are missing or expired. Run:\n"
            f"  aws login --profile {settings.profile}",
            file=sys.stderr,
        )
        sys.exit(1)
    except (InstanceNotAllowedError, PreviousStepMissingError) as error:
        print(f"Refusing to continue: {error}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)
