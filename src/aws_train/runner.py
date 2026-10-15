"""Shared entry point for Steps: settings, session, and readable failures."""

import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NoReturn

import boto3
from botocore.exceptions import LoginError, NoCredentialsError

from aws_train.config import ENV_FILE_NAME, ConfigError, Settings, load_settings, resolve_env
from aws_train.instances import InstanceNotAllowedError

StepMain = Callable[[Settings, boto3.Session], None]

_EXPIRED_CREDENTIALS = (LoginError, NoCredentialsError)


def make_session(settings: Settings) -> boto3.Session:
    return boto3.Session(profile_name=settings.profile, region_name=settings.region)


def account_id(session: boto3.Session) -> str:
    return str(session.client("sts").get_caller_identity()["Account"])


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
    except InstanceNotAllowedError as error:
        print(f"Refusing to continue: {error}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)
