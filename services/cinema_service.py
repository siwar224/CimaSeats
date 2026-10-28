"""Services for browsing movies and cinema sessions."""

from __future__ import annotations

from pathlib import Path

from models import Movie, Session
from utils.file_handler import read_json


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"


class CinemaService:
    """Provide movie and session data to the command-line interface."""

    def __init__(
        self,
        movies_path: str | Path = DATA_DIRECTORY / "movies.json",
        sessions_path: str | Path = DATA_DIRECTORY / "sessions.json",
    ) -> None:
        self.movies_path = Path(movies_path)
        self.sessions_path = Path(sessions_path)

    def get_movies(self) -> list[Movie]:
        """Load all active movies from the JSON data file."""
        movies = [Movie.from_dict(item) for item in read_json(self.movies_path)]
        return [movie for movie in movies if movie.is_active]

    def get_movie_by_id(self, movie_id: str) -> Movie | None:
        """Return a movie by ID, ignoring surrounding spaces and case."""
        searched_id = movie_id.strip().upper()
        return next(
            (movie for movie in self.get_movies() if movie.id.upper() == searched_id),
            None,
        )

    def get_sessions(self) -> list[Session]:
        """Load all sessions from the JSON data file in chronological order."""
        sessions = [Session.from_dict(item) for item in read_json(self.sessions_path)]
        return sorted(sessions, key=lambda session: session.start_time)

    def get_sessions_for_movie(self, movie_id: str) -> list[Session]:
        """Return all sessions associated with one movie ID."""
        searched_id = movie_id.strip().upper()
        return [
            session
            for session in self.get_sessions()
            if session.movie_id.upper() == searched_id
        ]

    def get_session_by_id(self, session_id: str) -> Session | None:
        """Return a session by ID, ignoring surrounding spaces and case."""
        searched_id = session_id.strip().upper()
        return next(
            (session for session in self.get_sessions() if session.id.upper() == searched_id),
            None,
        )

    def list_movies(self) -> str:
        """Format the complete movie catalogue for terminal display."""
        movies = self.get_movies()
        if not movies:
            return "Films\nAucun film disponible."

        lines = ["Films disponibles", "-" * 78]
        for movie in movies:
            year = movie.release_year or "N/A"
            lines.append(
                f"{movie.id:<6} | {movie.title:<32} | {movie.genre:<15} | "
                f"{movie.duration_minutes:>3} min | {year} | {movie.age_rating or 'N/A'}"
            )
        return "\n".join(lines)

    def list_sessions(self) -> str:
        """Format all sessions for terminal display."""
        sessions = self.get_sessions()
        if not sessions:
            return "Sessions\nAucune séance disponible."
        return "Sessions disponibles\n" + "\n".join(
            self._format_session(session) for session in sessions
        )

    def list_sessions_for_movie(self, movie_id: str) -> str:
        """Format sessions belonging to a selected movie."""
        sessions = self.get_sessions_for_movie(movie_id)
        if not sessions:
            return "Aucune séance disponible pour ce film."
        return "\n".join(self._format_session(session) for session in sessions)

    @staticmethod
    def _format_session(session: Session) -> str:
        """Format one session with its relationship and viewing details."""
        date_time = session.start_time.strftime("%d/%m/%Y à %H:%M")
        available_seats = len(session.available_seats)
        return (
            f"{session.id:<6} | Film: {session.movie_id:<6} | {date_time} | "
            f"{session.hall:<8} | {session.ticket_price:.2f} EUR | "
            f"{available_seats} places disponibles"
        )

    def list_available_seats(self) -> str:
        """Return the seat availability screen output."""
        return "Seats\nLa fonctionnalité des sièges sera bientôt disponible."
