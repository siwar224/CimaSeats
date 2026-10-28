"""Services for reading and managing reservations."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from models import Reservation, ReservationStatus, Session
from utils.file_handler import read_json, write_json


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
        return [
            Reservation.from_dict(item) for item in read_json(self.reservations_path)
        ]

    def get_reservations_for_session(self, session_id: str) -> list[Reservation]:
        """Return only active reservations belonging to one session."""
        searched_id = session_id.strip().upper()
        return [
            reservation
            for reservation in self.get_reservations()
            if reservation.session_id.upper() == searched_id and reservation.is_active
        ]

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
            raise ValueError("Vous devez sélectionner au moins un siège.")
        if len(set(requested_seats)) != len(requested_seats):
            raise ValueError("Un même siège ne peut pas être sélectionné deux fois.")

        invalid_seats = set(requested_seats).difference(session.all_seats)
        if invalid_seats:
            raise ValueError(
                f"Siège(s) inexistant(s) : {', '.join(sorted(invalid_seats))}."
            )

        booked_seats = self.get_booked_seats_for_session(session.id)
        occupied_seats = set(requested_seats).intersection(booked_seats)
        if occupied_seats:
            raise ValueError(
                f"Siège(s) déjà occupé(s) pour cette séance : "
                f"{', '.join(sorted(occupied_seats))}. Réservation refusée."
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

    def consult_reservations(self) -> str:
        """Return the reservation consultation screen output."""
        return "Consultation\nLa consultation des réservations sera bientôt disponible."

    def cancel_reservation(self) -> str:
        """Return the reservation cancellation screen output."""
        return "Cancelation\nL'annulation des réservations sera bientôt disponible."
