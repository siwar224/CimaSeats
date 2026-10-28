"""Services for browsing movies and cinema sessions."""

from __future__ import annotations

from collections.abc import Callable
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
            raise JsonFileError("File movies.json must contain a JSON list.")
        try:
            movies = [Movie.from_dict(item) for item in data]
        except (KeyError, TypeError, ValueError) as error:
            raise JsonFileError(
                f"File '{self.movies_path.name}' contains an invalid movie: {error}"
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
            raise JsonFileError("File sessions.json must contain a JSON list.")
        try:
            sessions = [Session.from_dict(item) for item in data]
        except (KeyError, TypeError, ValueError) as error:
            raise JsonFileError(
                f"File '{self.sessions_path.name}' contains an invalid session: {error}"
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
            raise JsonFileError("File rooms.json must contain a JSON list.")
        try:
            return [Room.from_dict(item) for item in data]
        except (KeyError, TypeError, ValueError) as error:
            raise JsonFileError(
                f"File '{self.rooms_path.name}' contains an invalid room: {error}"
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
            f"Room: {room.name} ({room.capacity} seats)",
            f"Session: {session.id} | {session.start_time.strftime('%d/%m/%Y at %H:%M')} | "
            f"Price: {session.ticket_price:.2f} EUR",
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
                "Legend: [ ] Available    [X] Occupied",
                f"Available seats: {available_count}/{room.capacity}",
            ]
        )
        return "\n".join(lines)

    def check_seat(self, session: Session, seat: str, booked_seats: set[str]) -> str:
        """Validate a seat number and report whether it is free or occupied."""
        room = self.get_room_for_session(session)
        normalised_seat = seat.strip().upper()
        if not room.is_valid_seat(normalised_seat):
            return f"Seat {normalised_seat or '(empty)'} does not exist in this room."
        if normalised_seat in {item.upper() for item in booked_seats}:
            return f"Seat {normalised_seat} is occupied for session {session.id}."
        return f"Seat {normalised_seat} is available for session {session.id}."

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
            return "Movies\nNo movies available."

        lines = ["Available movies", "-" * 78]
        for movie in movies:
            year = movie.release_year or "N/A"
            lines.append(
                f"{movie.id:<6} | {movie.title:<32} | {movie.genre:<15} | "
                f"{movie.duration_minutes:>3} min | {year} | {movie.age_rating or 'N/A'}"
            )
        return "\n".join(lines)

    def list_sessions(
        self,
        booked_seats_provider: Callable[[str], set[str]] | None = None,
    ) -> str:
        """Format all sessions for terminal display."""
        sessions = self.get_sessions()
        if not sessions:
            return "Sessions\nNo sessions available."
        return "Available sessions\n" + "\n".join(
            self._format_session(session, booked_seats_provider)
            for session in sessions
        )

    def list_sessions_for_movie(
        self,
        movie_id: str,
        booked_seats_provider: Callable[[str], set[str]] | None = None,
    ) -> str:
        """Format sessions belonging to a selected movie."""
        sessions = self.get_sessions_for_movie(movie_id)
        if not sessions:
            return "No sessions available for this movie."
        return "\n".join(
            self._format_session(session, booked_seats_provider)
            for session in sessions
        )

    @staticmethod
    def _format_session(
        session: Session,
        booked_seats_provider: Callable[[str], set[str]] | None = None,
    ) -> str:
        """Format one session with its relationship and viewing details."""
        date_time = session.start_time.strftime("%d/%m/%Y at %H:%M")
        booked_seats = (
            booked_seats_provider(session.id)
            if booked_seats_provider is not None
            else session.booked_seats
        )
        available_seats = len(session.all_seats.difference(booked_seats))
        return (
            f"{session.id:<6} | Movie: {session.movie_id:<6} | {date_time} | "
            f"{session.hall:<8} | {session.ticket_price:.2f} EUR | "
            f"{available_seats} seats available"
        )

    def list_available_seats(self) -> str:
        """Return the seat availability screen output."""
        return "Seats\nSeat availability is shown after selecting a session."
