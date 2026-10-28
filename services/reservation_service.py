"""Services for reading and managing reservations."""

from __future__ import annotations

from pathlib import Path

from models import Reservation
from utils.file_handler import read_json


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

    def create_reservation(self) -> str:
        """Return the reservation screen output."""
        return "Reservation\nLa fonctionnalité de réservation sera bientôt disponible."

    def consult_reservations(self) -> str:
        """Return the reservation consultation screen output."""
        return "Consultation\nLa consultation des réservations sera bientôt disponible."

    def cancel_reservation(self) -> str:
        """Return the reservation cancellation screen output."""
        return "Cancelation\nL'annulation des réservations sera bientôt disponible."
