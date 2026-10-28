"""Reservation domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any


class ReservationStatus(StrEnum):
    """Possible lifecycle states for a reservation."""

    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Reservation:
    """Represent a customer's booking for one or more cinema seats."""

    id: str
    session_id: str
    customer_name: str
    customer_email: str
    seats: tuple[str, ...]
    total_amount: Decimal
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: ReservationStatus = ReservationStatus.CONFIRMED

    def __post_init__(self) -> None:
        self.id = self._required_text(self.id, "Reservation id")
        self.session_id = self._required_text(self.session_id, "Session id")
        self.customer_name = self._required_text(self.customer_name, "Customer name")
        self.customer_email = self._validate_email(self.customer_email)
        self.seats = self._normalise_seats(self.seats)
        self.total_amount = self._as_amount(self.total_amount)
        if isinstance(self.status, str):
            try:
                self.status = ReservationStatus(self.status.lower())
            except ValueError:
                raise ValueError(f"Unknown reservation status: {self.status}") from None

    @property
    def is_active(self) -> bool:
        """Return whether the reservation still holds its seats."""
        return self.status is ReservationStatus.CONFIRMED

    def cancel(self) -> None:
        """Cancel the reservation."""
        if not self.is_active:
            raise ValueError("Reservation is already cancelled")
        self.status = ReservationStatus.CANCELLED

    @staticmethod
    def _required_text(value: str, field_name: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name} cannot be empty")
        return cleaned_value

    @classmethod
    def _validate_email(cls, value: str) -> str:
        email = cls._required_text(value, "Customer email")
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Customer email must be valid")
        return email

    @staticmethod
    def _normalise_seats(seats: tuple[str, ...] | list[str]) -> tuple[str, ...]:
        normalised_seats = tuple(sorted(seat.upper().strip() for seat in seats))
        if not normalised_seats or any(not seat for seat in normalised_seats):
            raise ValueError("At least one seat is required")
        if len(set(normalised_seats)) != len(normalised_seats):
            raise ValueError("A seat cannot be selected more than once")
        return normalised_seats

    @staticmethod
    def _as_amount(value: Decimal | int | float | str) -> Decimal:
        try:
            amount = Decimal(str(value)).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            raise ValueError("Total amount must be a valid amount") from None
        if amount < 0:
            raise ValueError("Total amount cannot be negative")
        return amount

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the reservation."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "seats": list(self.seats),
            "total_amount": str(self.total_amount),
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Reservation:
        """Build a reservation from a dictionary loaded from JSON."""
        return cls(
            id=str(data["id"]),
            session_id=str(data["session_id"]),
            customer_name=str(data["customer_name"]),
            customer_email=str(data["customer_email"]),
            seats=tuple(data["seats"]),
            total_amount=data["total_amount"],
            created_at=datetime.fromisoformat(data["created_at"]),
            status=data.get("status", ReservationStatus.CONFIRMED.value),
        )
