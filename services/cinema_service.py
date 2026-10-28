"""Services for browsing cinema content.

The methods currently return informative placeholders. Keeping this behavior in
a service layer makes it possible to connect the JSON repositories later
without changing the command-line menu.
"""


class CinemaService:
    """Provide cinema-related actions for the command-line interface."""

    def list_movies(self) -> str:
        """Return the movies screen output."""
        return "Films\nLa fonctionnalité des films sera bientôt disponible."

    def list_sessions(self) -> str:
        """Return the sessions screen output."""
        return "Sessions\nLa fonctionnalité des séances sera bientôt disponible."

    def list_available_seats(self) -> str:
        """Return the seat availability screen output."""
        return "Seats\nLa fonctionnalité des sièges sera bientôt disponible."
