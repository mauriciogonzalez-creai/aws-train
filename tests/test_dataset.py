import io

import pandas as pd

from aws_train.dataset import LABEL_COLUMN, load_dataset, split, to_xgboost_csv


def test_dataset_has_the_label_first_and_binary_targets() -> None:
    frame = load_dataset()

    assert frame.columns[0] == LABEL_COLUMN
    assert set(frame[LABEL_COLUMN].unique()) == {0, 1}


def test_dataset_has_no_missing_values() -> None:
    assert not load_dataset().isna().any().any()


def test_split_is_deterministic_for_a_seed() -> None:
    frame = load_dataset()

    first_train, first_validation = split(frame, seed=7)
    second_train, second_validation = split(frame, seed=7)

    pd.testing.assert_frame_equal(first_train, second_train)
    pd.testing.assert_frame_equal(first_validation, second_validation)


def test_split_keeps_every_row_exactly_once() -> None:
    frame = load_dataset()

    train, validation = split(frame)

    assert len(train) + len(validation) == len(frame)
    assert set(train.index).isdisjoint(validation.index)


def test_split_holds_out_a_fifth_for_validation() -> None:
    frame = load_dataset()

    _, validation = split(frame)

    assert abs(len(validation) / len(frame) - 0.2) < 0.01


def test_csv_has_no_header_and_label_in_column_zero() -> None:
    frame = load_dataset().head(3)

    csv = to_xgboost_csv(frame)
    parsed = pd.read_csv(io.StringIO(csv), header=None)

    assert not csv.startswith(LABEL_COLUMN)
    assert parsed.shape == frame.shape
    assert list(parsed[0]) == list(frame[LABEL_COLUMN])
