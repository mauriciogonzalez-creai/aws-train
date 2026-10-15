from pathlib import Path

from aws_train.state import load_state, update_state


def test_missing_state_file_is_empty(tmp_path: Path) -> None:
    assert load_state(tmp_path / "state.json") == {}


def test_update_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "state.json"

    update_state(path, training_job_name="aws-train-xgb-1")

    assert load_state(path) == {"training_job_name": "aws-train-xgb-1"}


def test_update_merges_with_existing_values(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    update_state(path, training_job_name="aws-train-xgb-1")

    update_state(path, model_data_url="s3://bucket/model.tar.gz")

    assert load_state(path) == {
        "training_job_name": "aws-train-xgb-1",
        "model_data_url": "s3://bucket/model.tar.gz",
    }


def test_update_overwrites_a_key(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    update_state(path, training_job_name="old")

    update_state(path, training_job_name="new")

    assert load_state(path)["training_job_name"] == "new"
