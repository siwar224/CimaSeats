"""Movie domain model."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class Movie:
    """Represent a movie available in the cinema.

    The model deliberately contains only movie information. Showtimes and
    bookings belong to :class:`models.session.Session` and
    :class:`models.reservation.Reservation` respectively.
    """

    id: str
    title: str
    genre: str
    duration_minutes: int
    description: str = ""
    release_year: int | None = None
    age_rating: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        self.id = self._required_text(self.id, "Movie id")
        self.title = self._required_text(self.title, "Movie title")
        self.genre = self._required_text(self.genre, "Movie genre")
        self.description = self.description.strip()

        if self.duration_minutes <= 0:
            raise ValueError("Movie duration must be greater than zero")
        if self.release_year is not None and not 1888 <= self.release_year <= 2100:
            raise ValueError("Release year must be between 1888 and 2100")

    @staticmethod
    def _required_text(value: str, field_name: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError(f"{field_name} cannot be empty")
        return cleaned_value

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the movie."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Movie:
        """Build a movie from a dictionary loaded from JSON."""
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            genre=str(data["genre"]),
            duration_minutes=int(data["duration_minutes"]),
            description=str(data.get("description", "")),
            release_year=(
                int(data["release_year"])
                if data.get("release_year") is not None
                else None
            ),
            age_rating=(
                str(data["age_rating"]) if data.get("age_rating") is not None else None
            ),
            is_active=bool(data.get("is_active", True)),
        )
