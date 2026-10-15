import pytest

from aws_train.payload import (
    PredictionError,
    features_to_csv,
    parse_prediction,
    summarize_latencies,
)


def test_features_to_csv_joins_values_without_label_or_newline() -> None:
    assert features_to_csv([17.99, 10.38, 122.8]) == "17.99,10.38,122.8"


def test_features_to_csv_rejects_an_empty_row() -> None:
    with pytest.raises(ValueError):
        features_to_csv([])


@pytest.mark.parametrize("body", [b"0.93", "0.93", "0.93\n", b"0.93,", 0.93])
def test_parse_prediction_accepts_bytes_text_and_numbers(body: object) -> None:
    assert parse_prediction(body) == pytest.approx(0.93)


@pytest.mark.parametrize("body", [b"1.5", "-0.1", b"", "not-a-number"])
def test_parse_prediction_rejects_values_outside_a_probability(body: object) -> None:
    with pytest.raises(PredictionError):
        parse_prediction(body)


def test_latency_summary_separates_the_first_call() -> None:
    summary = summarize_latencies([2500.0, 40.0, 60.0, 50.0])

    assert summary.first_ms == 2500.0
    assert summary.warm_p50_ms == 50.0
    assert summary.warm_calls == 3


def test_latency_summary_with_a_single_call_has_no_warm_median() -> None:
    summary = summarize_latencies([2500.0])

    assert summary.first_ms == 2500.0
    assert summary.warm_p50_ms is None
    assert summary.warm_calls == 0


def test_latency_summary_needs_at_least_one_call() -> None:
    with pytest.raises(ValueError):
        summarize_latencies([])
