from decimal import Decimal

import pytest

from aws_train.config import ConfigError, load_settings

REQUIRED = {"AWS_PROFILE": "aws-train", "BUDGET_EMAIL": "learner@example.com"}


def test_load_settings_reads_required_values() -> None:
    settings = load_settings(REQUIRED)

    assert settings.profile == "aws-train"
    assert settings.budget_email == "learner@example.com"


def test_region_defaults_to_us_east_1() -> None:
    assert load_settings(REQUIRED).region == "us-east-1"


def test_region_can_be_overridden() -> None:
    assert load_settings({**REQUIRED, "AWS_REGION": "us-east-2"}).region == "us-east-2"


def test_budget_limit_defaults_to_ten_dollars() -> None:
    assert load_settings(REQUIRED).budget_limit_usd == Decimal("10")


def test_budget_limit_can_be_overridden() -> None:
    settings = load_settings({**REQUIRED, "BUDGET_LIMIT_USD": "5.50"})

    assert settings.budget_limit_usd == Decimal("5.50")


@pytest.mark.parametrize("missing", ["AWS_PROFILE", "BUDGET_EMAIL"])
def test_missing_required_variable_raises(missing: str) -> None:
    env = {key: value for key, value in REQUIRED.items() if key != missing}

    with pytest.raises(ConfigError, match=missing):
        load_settings(env)


@pytest.mark.parametrize("missing", ["AWS_PROFILE", "BUDGET_EMAIL"])
def test_blank_required_variable_raises(missing: str) -> None:
    with pytest.raises(ConfigError, match=missing):
        load_settings({**REQUIRED, missing: "  "})


@pytest.mark.parametrize("limit", ["0", "-1", "ten"])
def test_invalid_budget_limit_raises(limit: str) -> None:
    with pytest.raises(ConfigError, match="BUDGET_LIMIT_USD"):
        load_settings({**REQUIRED, "BUDGET_LIMIT_USD": limit})
