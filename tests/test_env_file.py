from pathlib import Path

import pytest

from aws_train.config import ConfigError, read_env_file, resolve_env


def _write(tmp_path: Path, content: str) -> Path:
    path = tmp_path / ".env"
    path.write_text(content, encoding="utf-8")
    return path


def test_missing_file_yields_no_values(tmp_path: Path) -> None:
    assert read_env_file(tmp_path / ".env") == {}


def test_reads_key_value_pairs(tmp_path: Path) -> None:
    path = _write(tmp_path, "AWS_PROFILE=aws-train\nBUDGET_EMAIL=learner@example.com\n")

    assert read_env_file(path) == {
        "AWS_PROFILE": "aws-train",
        "BUDGET_EMAIL": "learner@example.com",
    }


def test_ignores_blank_lines_and_comments(tmp_path: Path) -> None:
    path = _write(tmp_path, "# settings\n\n   \nAWS_PROFILE=aws-train\n  # indented comment\n")

    assert read_env_file(path) == {"AWS_PROFILE": "aws-train"}


def test_accepts_export_prefix_and_surrounding_spaces(tmp_path: Path) -> None:
    path = _write(tmp_path, "export AWS_PROFILE = aws-train  \n")

    assert read_env_file(path) == {"AWS_PROFILE": "aws-train"}


@pytest.mark.parametrize("quoted", ['"aws-train"', "'aws-train'"])
def test_strips_matching_quotes(tmp_path: Path, quoted: str) -> None:
    path = _write(tmp_path, f"AWS_PROFILE={quoted}\n")

    assert read_env_file(path) == {"AWS_PROFILE": "aws-train"}


def test_keeps_equals_signs_inside_the_value(tmp_path: Path) -> None:
    path = _write(tmp_path, "TOKEN=a=b=c\n")

    assert read_env_file(path) == {"TOKEN": "a=b=c"}


@pytest.mark.parametrize("line", ["AWS_PROFILE", "=value", "BAD KEY=value"])
def test_malformed_line_raises_with_its_line_number(tmp_path: Path, line: str) -> None:
    path = _write(tmp_path, f"# first\n{line}\n")

    with pytest.raises(ConfigError, match=r"\.env line 2"):
        read_env_file(path)


def test_exported_variables_win_over_the_file(tmp_path: Path) -> None:
    path = _write(tmp_path, "AWS_PROFILE=from-file\nBUDGET_EMAIL=file@example.com\n")

    env = resolve_env(path, {"AWS_PROFILE": "from-shell"})

    assert env["AWS_PROFILE"] == "from-shell"
    assert env["BUDGET_EMAIL"] == "file@example.com"
