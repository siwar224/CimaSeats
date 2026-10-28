"""Services for creating and managing reservations."""


class ReservationService:
    """Provide reservation-related actions for the command-line interface."""

    def create_reservation(self) -> str:
        """Return the reservation screen output."""
        return "Reservation\nLa fonctionnalité de réservation sera bientôt disponible."

    def consult_reservations(self) -> str:
        """Return the reservation consultation screen output."""
        return "Consultation\nLa consultation des réservations sera bientôt disponible."

    def cancel_reservation(self) -> str:
        """Return the reservation cancellation screen output."""
        return "Cancelation\nL'annulation des réservations sera bientôt disponible."
