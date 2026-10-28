"""Cinema session domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any


@dataclass(slots=True)
class Session:
    """Represent one scheduled showing of a movie.

    Seats are generated from the configured row and seat counts. Booked seats
    are kept on the session so availability can be checked atomically before a
    reservation is created.
    """

    id: str
    movie_id: str
    start_time: datetime
    hall: str
    rows: int = 10
    seats_per_row: int = 10
    ticket_price: Decimal = Decimal("0.00")
    booked_seats: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        self.id = self._required_text(self.id, "Session id")
        self.movie_id = self._required_text(self.movie_id, "Movie id")
        self.hall = self._required_text(self.hall, "Hall")

        if self.rows <= 0 or self.seats_per_row <= 0:
            raise ValueError("Rows and seats per row must be greater than zero")
        self.ticket_price = self._as_price(self.ticket_price)
        self.booked_seats = {seat.upper().strip() for seat in self.booked_seats}
        invalid_seats = self.booked_seats.difference(self.all_seats)
        if invalid_seats:
            raise ValueError(f"Invalid booked seats: {sorted(invalid_seats)}")

    @property
    def all_seats(self) -> frozenset[str]:
        """Return every valid seat identifier for the hall."""
        return frozenset(
            f"{self._row_label(row)}{number}"
            for row in range(1, self.rows + 1)
            for number in range(1, self.seats_per_row + 1)
        )

    @property
    def available_seats(self) -> frozenset[str]:
        """Return seats that have not been booked yet."""
        return self.all_seats.difference(self.booked_seats)

    def has_seats_available(self, seats: list[str] | tuple[str, ...]) -> bool:
        """Return whether all requested seats are valid and available."""
        requested_seats = self._normalise_seats(seats)
        return requested_seats.issubset(self.available_seats)

    def reserve_seats(self, seats: list[str] | tuple[str, ...]) -> None:
        """Book a group of seats, failing without partial changes."""
        requested_seats = self._normalise_seats(seats)
        invalid_seats = requested_seats.difference(self.all_seats)
        if invalid_seats:
            raise ValueError(f"Invalid seats: {sorted(invalid_seats)}")
        unavailable_seats = requested_seats.intersection(self.booked_seats)
        if unavailable_seats:
            raise ValueError(f"Seats already booked: {sorted(unavailable_seats)}")
        self.booked_seats.update(requested_seats)

    def release_seats(self, seats: list[str] | tuple[str, ...]) -> None:
        """Release seats when a reservation is cancelled."""
        requested_seats = self._normalise_seats(seats)
        self.booked_seats.difference_update(requested_seats)

    @staticmethod
    def _required_text(value: str, field_name: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name} cannot be empty")
        return cleaned_value

    @staticmethod
    def _as_price(value: Decimal | int | float | str) -> Decimal:
        try:
            price = Decimal(str(value)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            raise ValueError("Ticket price must be a valid amount") from None
        if price < 0:
            raise ValueError("Ticket price cannot be negative")
        return price

    @staticmethod
    def _normalise_seats(seats: list[str] | tuple[str, ...]) -> set[str]:
        normalised_seats = {seat.upper().strip() for seat in seats}
        if not normalised_seats or "" in normalised_seats:
            raise ValueError("At least one valid seat is required")
        if len(normalised_seats) != len(seats):
            raise ValueError("A seat cannot be selected more than once")
        return normalised_seats

    @staticmethod
    def _row_label(row_number: int) -> str:
        label = ""
        while row_number:
            row_number, remainder = divmod(row_number - 1, 26)
            label = chr(65 + remainder) + label
        return label

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the session."""
        return {
            "id": self.id,
            "movie_id": self.movie_id,
            "start_time": self.start_time.isoformat(),
            "hall": self.hall,
            "rows": self.rows,
            "seats_per_row": self.seats_per_row,
            "ticket_price": str(self.ticket_price),
            "booked_seats": sorted(self.booked_seats),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Session:
        """Build a session from a dictionary loaded from JSON."""
        return cls(
            id=str(data["id"]),
            movie_id=str(data["movie_id"]),
            start_time=datetime.fromisoformat(data["start_time"]),
            hall=str(data["hall"]),
            rows=int(data.get("rows", 10)),
            seats_per_row=int(data.get("seats_per_row", 10)),
            ticket_price=data.get("ticket_price", "0.00"),
            booked_seats=set(data.get("booked_seats", [])),
        )
