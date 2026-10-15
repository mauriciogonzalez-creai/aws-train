"""Request and response handling for the Serverless Endpoint (Steps 04–05)."""

import statistics
from collections.abc import Sequence
from dataclasses import dataclass

CSV_CONTENT_TYPE = "text/csv"


class PredictionError(ValueError):
    """Raised when the endpoint response is not a probability."""


@dataclass(frozen=True)
class LatencySummary:
    first_ms: float
    warm_p50_ms: float | None
    warm_calls: int


def features_to_csv(row: Sequence[float]) -> str:
    """One feature row as the CSV body Built-in XGBoost expects: no label, no newline."""
    if not row:
        raise ValueError("A feature row needs at least one value")
    return ",".join(repr(float(value)) for value in row)


def parse_prediction(body: object) -> float:
    """Probability from an endpoint response body (bytes, text or an already-parsed number)."""
    if isinstance(body, bytes):
        body = body.decode("utf-8")
    text = str(body).strip().split("\n")[0].split(",")[0].strip()
    try:
        probability = float(text)
    except ValueError as error:
        raise PredictionError(f"Expected a probability, got {body!r}") from error
    if not 0.0 <= probability <= 1.0:
        raise PredictionError(f"Expected a probability in [0, 1], got {probability}")
    return probability


def summarize_latencies(latencies_ms: Sequence[float]) -> LatencySummary:
    """Separate the first call (may include a cold start) from the warm calls."""
    if not latencies_ms:
        raise ValueError("Need at least one latency")
    first, *warm = latencies_ms
    return LatencySummary(
        first_ms=first,
        warm_p50_ms=statistics.median(warm) if warm else None,
        warm_calls=len(warm),
    )
