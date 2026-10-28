"""Services for browsing movies and cinema sessions."""

from __future__ import annotations

from pathlib import Path

from models import Movie, Room, Session
from utils.file_handler import JsonFileError, read_json


DATA_DIRECTORY = Path(__file__).resolve().parents[1] / "data"


class CinemaService:
    """Provide movie and session data to the command-line interface."""

    def __init__(
        self,
        movies_path: str | Path = DATA_DIRECTORY / "movies.json",
        sessions_path: str | Path = DATA_DIRECTORY / "sessions.json",
        rooms_path: str | Path = DATA_DIRECTORY / "rooms.json",
    ) -> None:
        self.movies_path = Path(movies_path)
        self.sessions_path = Path(sessions_path)
        self.rooms_path = Path(rooms_path)

    def get_movies(self) -> list[Movie]:
        """Load all active movies from the JSON data file."""
        data = read_json(self.movies_path, default=[])
        if not isinstance(data, list):
            raise JsonFileError("Le fichier movies.json doit contenir une liste JSON.")
        try:
            movies = [Movie.from_dict(item) for item in data]
        except (KeyError, TypeError, ValueError) as error:
            raise JsonFileError(
                f"Le fichier '{self.movies_path.name}' contient un film invalide : {error}"
            ) from error
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
        data = read_json(self.sessions_path, default=[])
        if not isinstance(data, list):
            raise JsonFileError("Le fichier sessions.json doit contenir une liste JSON.")
        try:
            sessions = [Session.from_dict(item) for item in data]
        except (KeyError, TypeError, ValueError) as error:
            raise JsonFileError(
                f"Le fichier '{self.sessions_path.name}' contient une séance invalide : {error}"
            ) from error
        return sorted(sessions, key=lambda session: session.start_time)

    def get_sessions_for_movie(self, movie_id: str) -> list[Session]:
        """Return all sessions associated with one movie ID."""
        searched_id = movie_id.strip().upper()
        return [
            session
            for session in self.get_sessions()
            if session.movie_id.upper() == searched_id
        ]

    def get_rooms(self) -> list[Room]:
        """Load all cinema rooms from the JSON data file."""
        data = read_json(self.rooms_path, default=[])
        if not isinstance(data, list):
            raise JsonFileError("Le fichier rooms.json doit contenir une liste JSON.")
        try:
            return [Room.from_dict(item) for item in data]
        except (KeyError, TypeError, ValueError) as error:
            raise JsonFileError(
                f"Le fichier '{self.rooms_path.name}' contient une salle invalide : {error}"
            ) from error

    def get_room_for_session(self, session: Session) -> Room:
        """Return the room linked to a session through its hall identifier."""
        room = next(
            (room for room in self.get_rooms() if room.id == session.hall),
            None,
        )
        if room is None:
            raise ValueError(f"Room not found for session hall: {session.hall}")
        if room.rows != session.rows or room.seats_per_row != session.seats_per_row:
            raise ValueError(f"Room layout does not match session {session.id}")
        return room

    def format_seat_map(self, session: Session, booked_seats: set[str]) -> str:
        """Render a clear terminal seat map for a session."""
        room = self.get_room_for_session(session)
        normalised_booked_seats = {seat.upper().strip() for seat in booked_seats}
        invalid_seats = normalised_booked_seats.difference(room.all_seats)
        if invalid_seats:
            raise ValueError(f"Invalid booked seats for {session.id}: {sorted(invalid_seats)}")

        seat_numbers = " ".join(f"{number:>3}" for number in range(1, room.seats_per_row + 1))
        lines = [
            f"Salle : {room.name} ({room.capacity} places)",
            f"Séance : {session.id} | {session.start_time.strftime('%d/%m/%Y à %H:%M')} | "
            f"Prix : {session.ticket_price:.2f} EUR",
            "",
            f"      {seat_numbers}",
        ]
        for row_number in range(1, room.rows + 1):
            row_name = room.row_label(row_number)
            seats = []
            for seat_number in range(1, room.seats_per_row + 1):
                seat_id = f"{row_name}{seat_number}"
                marker = "[X]" if seat_id in normalised_booked_seats else "[ ]"
                seats.append(f"{marker:>3}")
            lines.append(f"  {row_name}   " + " ".join(seats))

        available_count = room.capacity - len(normalised_booked_seats)
        lines.extend(
            [
                "",
                "Légende : [ ] Libre    [X] Occupée",
                f"Places libres : {available_count}/{room.capacity}",
            ]
        )
        return "\n".join(lines)

    def check_seat(self, session: Session, seat: str, booked_seats: set[str]) -> str:
        """Validate a seat number and report whether it is free or occupied."""
        room = self.get_room_for_session(session)
        normalised_seat = seat.strip().upper()
        if not room.is_valid_seat(normalised_seat):
            return f"Le siège {normalised_seat or '(vide)'} n'existe pas dans cette salle."
        if normalised_seat in {item.upper() for item in booked_seats}:
            return f"Le siège {normalised_seat} est occupé pour la séance {session.id}."
        return f"Le siège {normalised_seat} est libre pour la séance {session.id}."

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
