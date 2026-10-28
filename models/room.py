"""Cinema room and seat-layout domain model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Room:
    """Represent a cinema room with a rectangular seat layout."""

    id: str
    name: str
    rows: int
    seats_per_row: int

    def __post_init__(self) -> None:
        self.id = self._required_text(self.id, "Room id")
        self.name = self._required_text(self.name, "Room name")
        if self.rows <= 0 or self.seats_per_row <= 0:
            raise ValueError("Rows and seats per row must be greater than zero")

    @property
    def capacity(self) -> int:
        """Return the total number of seats in the room."""
        return self.rows * self.seats_per_row

    @property
    def all_seats(self) -> frozenset[str]:
        """Return every valid seat identifier in the room."""
        return frozenset(
            f"{self.row_label(row)}{number}"
            for row in range(1, self.rows + 1)
            for number in range(1, self.seats_per_row + 1)
        )

    @staticmethod
    def row_label(row_number: int) -> str:
        """Convert a row number to a spreadsheet-style label: A, B ... AA."""
        label = ""
        while row_number:
            row_number, remainder = divmod(row_number - 1, 26)
            label = chr(65 + remainder) + label
        return label

    def is_valid_seat(self, seat: str) -> bool:
        """Return whether a seat identifier exists in this room."""
        return seat.strip().upper() in self.all_seats

    @staticmethod
    def _required_text(value: str, field_name: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name} cannot be empty")
        return cleaned_value

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the room."""
        return {
            "id": self.id,
            "name": self.name,
            "rows": self.rows,
            "seats_per_row": self.seats_per_row,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Room:
        """Build a room from a dictionary loaded from JSON."""
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            rows=int(data["rows"]),
            seats_per_row=int(data["seats_per_row"]),
        )
