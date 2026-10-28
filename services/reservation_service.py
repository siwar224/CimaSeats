"""Services for reading and managing reservations."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from models import Reservation, ReservationStatus, Session
from utils.file_handler import JsonFileError, read_json, write_json


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"


class ReservationService:
    """Provide reservation data to the cinema and command-line services."""

    def __init__(
        self,
        reservations_path: str | Path = DATA_DIRECTORY / "reservations.json",
    ) -> None:
        self.reservations_path = Path(reservations_path)

    def get_reservations(self) -> list[Reservation]:
        """Load reservations from the JSON data file."""
        data = read_json(self.reservations_path, default=[])
        if not isinstance(data, list):
            raise JsonFileError(
                "File reservations.json must contain a JSON list."
            )
        try:
            return [Reservation.from_dict(item) for item in data]
        except (KeyError, TypeError, ValueError) as error:
            raise JsonFileError(
                f"File '{self.reservations_path.name}' contains an invalid reservation: "
                f"{error}"
            ) from error

    def get_reservations_for_session(self, session_id: str) -> list[Reservation]:
        """Return only active reservations belonging to one session."""
        searched_id = session_id.strip().upper()
        return [
            reservation
            for reservation in self.get_reservations()
            if reservation.session_id.upper() == searched_id and reservation.is_active
        ]

    def get_reservations_for_customer(self, customer_email: str) -> list[Reservation]:
        """Return confirmed and cancelled reservations for one customer email."""
        searched_email = customer_email.strip().lower()
        return [
            reservation
            for reservation in self.get_reservations()
            if reservation.customer_email.lower() == searched_email
        ]

    def format_customer_reservations(self, customer_email: str) -> str:
        """Format a customer's reservations for terminal display."""
        reservations = self.get_reservations_for_customer(customer_email)
        if not reservations:
            return "No reservations found for this email."

        lines = ["Your reservations", "-" * 72]
        for reservation in reservations:
            lines.extend(
                [
                    f"ID         : {reservation.id}",
                    f"Session    : {reservation.session_id}",
                    f"Seats      : {', '.join(reservation.seats)}",
                    f"Amount     : {reservation.total_amount:.2f} EUR",
                    f"Status     : {reservation.status.value}",
                    "-" * 72,
                ]
            )
        return "\n".join(lines)

    def get_booked_seats_for_session(self, session_id: str) -> set[str]:
        """Return occupied seats for one session only.

        Reservations are filtered by session ID, so a seat occupied in one
        showing remains independent from the same seat in another showing.
        """
        booked_seats: set[str] = set()
        for reservation in self.get_reservations_for_session(session_id):
            booked_seats.update(reservation.seats)
        return booked_seats

    def create_reservation(
        self,
        session: Session,
        customer_name: str,
        customer_email: str,
        seats: list[str] | tuple[str, ...],
    ) -> Reservation:
        """Validate, create, and persist one reservation atomically.

        Seat validation happens before the JSON file is changed. Therefore a
        request containing one invalid or occupied seat is rejected completely.
        """
        requested_seats = tuple(seat.strip().upper() for seat in seats)
        if not requested_seats or any(not seat for seat in requested_seats):
            raise ValueError("You must select at least one seat.")
        if len(set(requested_seats)) != len(requested_seats):
            raise ValueError("The same seat cannot be selected more than once.")

        invalid_seats = set(requested_seats).difference(session.all_seats)
        if invalid_seats:
            raise ValueError(
                f"Seat(s) do not exist: {', '.join(sorted(invalid_seats))}."
            )

        booked_seats = self.get_booked_seats_for_session(session.id)
        occupied_seats = set(requested_seats).intersection(booked_seats)
        if occupied_seats:
            raise ValueError(
                f"Seat(s) already occupied for this session: "
                f"{', '.join(sorted(occupied_seats))}. Booking rejected."
            )

        reservation = Reservation(
            id=self._next_reservation_id(),
            session_id=session.id,
            customer_name=customer_name,
            customer_email=customer_email,
            seats=requested_seats,
            total_amount=session.ticket_price * len(requested_seats),
            status=ReservationStatus.CONFIRMED,
        )

        reservations = self.get_reservations()
        reservations.append(reservation)
        write_json(self.reservations_path, [item.to_dict() for item in reservations])
        return reservation

    def _next_reservation_id(self) -> str:
        """Generate a reservation ID that is not already stored."""
        existing_ids = {reservation.id for reservation in self.get_reservations()}
        reservation_id = f"RES-{uuid4().hex[:8].upper()}"
        while reservation_id in existing_ids:
            reservation_id = f"RES-{uuid4().hex[:8].upper()}"
        return reservation_id

    def cancel_reservation(
        self,
        reservation_id: str,
        customer_email: str,
    ) -> Reservation:
        """Cancel and persist a reservation belonging to the given customer."""
        searched_id = reservation_id.strip().upper()
        searched_email = customer_email.strip().lower()
        reservations = self.get_reservations()
        reservation = next(
            (
                item
                for item in reservations
                if item.id.upper() == searched_id
                and item.customer_email.lower() == searched_email
            ),
            None,
        )
        if reservation is None:
            raise ValueError("Reservation not found for this ID and email.")

        reservation.cancel()
        write_json(self.reservations_path, [item.to_dict() for item in reservations])
        return reservation
