"""Helpers for reading and writing JSON data files."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar


Record = TypeVar("Record")


class JsonFileError(Exception):
    """Raised when a JSON data file is missing, invalid, or unusable."""


def read_json(path: str | Path, default: Any | None = None) -> Any:
    """Read a UTF-8 JSON file and create a missing file with a default value."""
    file_path = Path(path)
    if not file_path.exists():
        initial_value = [] if default is None else default
        write_json(file_path, initial_value)
        return initial_value

    try:
        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as error:
        raise JsonFileError(
            f"File '{file_path.name}' contains malformed JSON "
            f"(line {error.lineno}, column {error.colno})."
        ) from error
    except OSError as error:
        raise JsonFileError(
            f"Unable to read file '{file_path.name}'."
        ) from error


def write_json(path: str | Path, data: Any) -> None:
    """Write data as formatted UTF-8 JSON."""
    file_path = Path(path)
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
            file.write("\n")
    except (OSError, TypeError, ValueError) as error:
        raise JsonFileError(
            f"Unable to save data to '{file_path.name}'."
        ) from error


def read_json_records(
    path: str | Path,
    record_factory: Callable[[dict[str, Any]], Record],
    record_name: str,
) -> list[Record]:
    """Read a JSON list and convert each item into a domain object."""
    file_path = Path(path)
    data = read_json(file_path, default=[])
    if not isinstance(data, list):
        raise JsonFileError(f"File {file_path.name} must contain a JSON list.")

    try:
        return [record_factory(item) for item in data]
    except (KeyError, TypeError, ValueError) as error:
        raise JsonFileError(
            f"File '{file_path.name}' contains an invalid {record_name}: {error}"
        ) from error
