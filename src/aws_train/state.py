"""Local state file shared between Steps (git-ignored, safe to delete)."""

import json
from pathlib import Path

STATE_FILE_NAME = ".aws-train-state.json"


def load_state(path: Path) -> dict[str, str]:
    """Return saved values, or an empty dict when the file doesn't exist."""
    if not path.is_file():
        return {}
    values: dict[str, str] = json.loads(path.read_text(encoding="utf-8"))
    return values


def update_state(path: Path, **values: str) -> None:
    """Merge ``values`` into the state file, overwriting keys that already exist."""
    merged = {**load_state(path), **values}
    path.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n", encoding="utf-8")
