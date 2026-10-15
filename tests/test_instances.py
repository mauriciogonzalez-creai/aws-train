import pytest

from aws_train.instances import (
    ALLOWED_INSTANCE_TYPES,
    TRAINING_INSTANCE_TYPE,
    InstanceNotAllowedError,
    require_allowed,
)


def test_training_instance_type_is_allowed() -> None:
    assert TRAINING_INSTANCE_TYPE in ALLOWED_INSTANCE_TYPES


def test_require_allowed_returns_the_type() -> None:
    assert require_allowed("ml.m5.xlarge") == "ml.m5.xlarge"


@pytest.mark.parametrize("instance_type", ["ml.p3.2xlarge", "ml.g5.xlarge", "", "ML.M5.XLARGE"])
def test_require_allowed_rejects_other_types(instance_type: str) -> None:
    with pytest.raises(InstanceNotAllowedError, match="ml.m5.xlarge"):
        require_allowed(instance_type)
