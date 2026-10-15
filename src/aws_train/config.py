"""Settings the Steps read from the environment and an optional `.env` file."""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

DEFAULT_REGION = "us-east-1"
DEFAULT_BUDGET_LIMIT_USD = Decimal("10")
ENV_FILE_NAME = ".env"
_ENV_KEY = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class ConfigError(ValueError):
    """Raised when a required variable is missing or a value is invalid."""


@dataclass(frozen=True)
class Settings:
    profile: str
    region: str
    budget_email: str
    budget_limit_usd: Decimal


def _required(env: Mapping[str, str], name: str) -> str:
    value = env.get(name, "").strip()
    if not value:
        raise ConfigError(f"{name} is required; see docs/guide/00-prerequisites.md")
    return value


def _budget_limit(env: Mapping[str, str]) -> Decimal:
    raw = env.get("BUDGET_LIMIT_USD", "").strip()
    if not raw:
        return DEFAULT_BUDGET_LIMIT_USD
    try:
        limit = Decimal(raw)
    except InvalidOperation as error:
        raise ConfigError(f"BUDGET_LIMIT_USD must be a number, got {raw!r}") from error
    if not limit.is_finite() or limit <= 0:
        raise ConfigError(f"BUDGET_LIMIT_USD must be greater than 0, got {raw!r}")
    return limit


def load_settings(env: Mapping[str, str]) -> Settings:
    """Build Settings from an environment mapping such as ``os.environ``.

    Raises ConfigError naming the offending variable.
    """
    return Settings(
        profile=_required(env, "AWS_PROFILE"),
        region=env.get("AWS_REGION", "").strip() or DEFAULT_REGION,
        budget_email=_required(env, "BUDGET_EMAIL"),
        budget_limit_usd=_budget_limit(env),
    )


def _parse_env_line(line: str, number: int) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("export "):
        stripped = stripped.removeprefix("export ").lstrip()
    key, separator, value = stripped.partition("=")
    key = key.strip()
    if not separator or not _ENV_KEY.fullmatch(key):
        raise ConfigError(f".env line {number}: expected KEY=VALUE, got {line.strip()!r}")
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return key, value


def read_env_file(path: Path) -> dict[str, str]:
    """Read KEY=VALUE pairs from a ``.env`` file; a missing file yields no values.

    Blank lines, ``#`` comments and an ``export`` prefix are accepted; matching
    surrounding quotes are stripped. Raises ConfigError naming the malformed line.
    """
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        pair = _parse_env_line(line, number)
        if pair is not None:
            values[pair[0]] = pair[1]
    return values


def resolve_env(path: Path, environ: Mapping[str, str]) -> dict[str, str]:
    """Merge ``.env`` values with ``environ``; exported variables take precedence."""
    return {**read_env_file(path), **environ}
