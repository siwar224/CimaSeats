"""Helpers for reading and writing JSON data files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> Any:
    """Read and decode a UTF-8 JSON file."""
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)
