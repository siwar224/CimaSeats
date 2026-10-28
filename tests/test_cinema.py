"""Unit tests for movie, session, room, and seat-map services."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from services import CinemaService
from utils.file_handler import JsonFileError


class CinemaServiceTests(unittest.TestCase):
    """Test catalogue and seat-map behavior using the bundled data."""

    def setUp(self) -> None:
        self.service = CinemaService()

    def test_catalogue_contains_movies_and_sessions(self) -> None:
        self.assertEqual(len(self.service.get_movies()), 20)
        self.assertEqual(len(self.service.get_sessions()), 60)

    def test_movie_sessions_are_filtered_by_movie_id(self) -> None:
        sessions = self.service.get_sessions_for_movie("mov001")

        self.assertEqual(len(sessions), 3)
        self.assertTrue(all(session.movie_id == "MOV001" for session in sessions))

    def test_seat_map_marks_occupied_and_available_seats(self) -> None:
        session = self.service.get_session_by_id("SES002")
        self.assertIsNotNone(session)

        seat_map = self.service.format_seat_map(session, {"B4", "E8"})

        self.assertIn("[X]", seat_map)
        self.assertIn("[ ]", seat_map)
        self.assertIn("Available seats: 94/96", seat_map)

    def test_malformed_movie_file_is_reported(self) -> None:
        with TemporaryDirectory() as directory:
            movies_path = Path(directory) / "movies.json"
            movies_path.write_text("{not valid json", encoding="utf-8")
            service = CinemaService(movies_path=movies_path)

            with self.assertRaises(JsonFileError):
                service.get_movies()


if __name__ == "__main__":
    unittest.main()
