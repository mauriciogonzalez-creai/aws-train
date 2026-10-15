import pytest

from aws_train.naming import bucket_name


def test_bucket_name_from_account_and_region() -> None:
    assert bucket_name("123456789012", "us-east-1") == "aws-train-123456789012-us-east-1"


@pytest.mark.parametrize("account_id", ["12345", "12345678901a", "", "1234567890123"])
def test_bucket_name_rejects_invalid_account_id(account_id: str) -> None:
    with pytest.raises(ValueError, match="account id"):
        bucket_name(account_id, "us-east-1")


def test_bucket_name_fits_s3_limit() -> None:
    assert len(bucket_name("123456789012", "ap-southeast-3")) <= 63
