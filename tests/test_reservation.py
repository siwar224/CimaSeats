"""Unit tests for reservation creation, persistence, and cancellation."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from services import CinemaService, ReservationService
from utils.file_handler import JsonFileError, read_json, write_json


class ReservationServiceTests(unittest.TestCase):
    """Test the complete reservation lifecycle in temporary JSON files."""

    def setUp(self) -> None:
        self.temp_directory = TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.reservations_path = Path(self.temp_directory.name) / "reservations.json"
        write_json(self.reservations_path, [])
        self.service = ReservationService(self.reservations_path)
        self.session = CinemaService().get_session_by_id("SES003")
        self.assertIsNotNone(self.session)

    def test_create_reservation_persists_between_service_instances(self) -> None:
        reservation = self.service.create_reservation(
            self.session,
            "Ada Lovelace",
            "ada@example.com",
            ["A1", "A2"],
        )

        reloaded_service = ReservationService(self.reservations_path)
        loaded = reloaded_service.get_reservation_by_id(reservation.id)

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.customer_name, "Ada Lovelace")
        self.assertEqual(set(loaded.seats), {"A1", "A2"})
        self.assertEqual(reloaded_service.get_booked_seats_for_session("SES003"), {"A1", "A2"})

    def test_booking_is_rejected_if_one_requested_seat_is_occupied(self) -> None:
        self.service.create_reservation(
            self.session,
            "First Customer",
            "first@example.com",
            ["A1"],
        )

        with self.assertRaisesRegex(ValueError, "already occupied"):
            self.service.create_reservation(
                self.session,
                "Second Customer",
                "second@example.com",
                ["A2", "A1"],
            )

        self.assertEqual(len(self.service.get_reservations()), 1)
        self.assertEqual(read_json(self.reservations_path)[0]["seats"], ["A1"])

    def test_cancel_marks_reservation_and_releases_seats(self) -> None:
        reservation = self.service.create_reservation(
            self.session,
            "Cancel Customer",
            "cancel@example.com",
            ["C1", "C2"],
        )

        cancelled = self.service.cancel_reservation(reservation.id)
        reloaded = ReservationService(self.reservations_path)

        self.assertEqual(cancelled.status.value, "cancelled")
        self.assertEqual(reloaded.get_reservation_by_id(reservation.id).status.value, "cancelled")
        self.assertEqual(reloaded.get_booked_seats_for_session("SES003"), set())

    def test_cancel_rejects_unknown_or_already_cancelled_reservation(self) -> None:
        with self.assertRaisesRegex(ValueError, "not found"):
            self.service.cancel_reservation("RES-UNKNOWN")

        reservation = self.service.create_reservation(
            self.session,
            "Repeat Customer",
            "repeat@example.com",
            ["D1"],
        )
        self.service.cancel_reservation(reservation.id)

        with self.assertRaisesRegex(ValueError, "already cancelled"):
            self.service.cancel_reservation(reservation.id)

    def test_missing_or_malformed_reservation_file_is_handled(self) -> None:
        missing_path = Path(self.temp_directory.name) / "missing.json"
        missing_service = ReservationService(missing_path)
        self.assertEqual(missing_service.get_reservations(), [])
        self.assertTrue(missing_path.exists())

        malformed_path = Path(self.temp_directory.name) / "malformed.json"
        malformed_path.write_text("{not valid json", encoding="utf-8")
        malformed_service = ReservationService(malformed_path)

        with self.assertRaises(JsonFileError):
            malformed_service.get_reservations()


if __name__ == "__main__":
    unittest.main()
