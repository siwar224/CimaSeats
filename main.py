"""Command-line entry point for the CimaSeats application."""

from services import CinemaService, ReservationService
from models import Reservation
from utils.file_handler import JsonFileError


MENU_OPTIONS = {
    "1": "View Movies",
    "2": "View Sessions",
    "3": "View Available Seats",
    "4": "Book Tickets",
    "5": "View Reservation",
    "6": "Cancel Reservation",
    "7": "Exit",
}


def display_title() -> None:
    """Display the application title."""
    print("\n" + "=" * 36)
    print("              CiMaSeat")
    print("=" * 36)


def display_menu() -> None:
    """Display all available menu options."""
    print("\nMenu")
    for number, label in MENU_OPTIONS.items():
        print(f"{number}. {label}")


def book_tickets(
    cinema_service: CinemaService,
    reservation_service: ReservationService,
) -> None:
    """Display movies, select a movie and session, then create a booking."""
    print(f"\n{cinema_service.format_movie_catalog()}")
    movie_id = input("\nMovie ID (or press Enter to return): ").strip()
    if not movie_id:
        return

    movie = cinema_service.get_movie_by_id(movie_id)
    if movie is None:
        print("Movie not found. Please check the ID.")
        return

    sessions = cinema_service.get_sessions_for_movie(movie.id)
    print(f"\nSessions for {movie.title} ({movie.id})")
    print(
        cinema_service.format_movie_sessions(
            movie.id,
            reservation_service.get_booked_seats_for_session,
        )
    )
    if not sessions:
        return

    session_id = input(
        "\nSession ID (or press Enter to return): "
    ).strip()
    if not session_id:
        return

    selected_session = cinema_service.get_session_by_id(session_id)
    if selected_session is None or selected_session.movie_id.upper() != movie.id.upper():
        print("Session not found for the selected movie.")
        return

    booked_seats = reservation_service.get_booked_seats_for_session(selected_session.id)
    create_booking(
        cinema_service,
        reservation_service,
        movie,
        selected_session,
        booked_seats,
    )


def view_movies(cinema_service: CinemaService) -> None:
    """Display the movie catalogue."""
    print(f"\n{cinema_service.format_movie_catalog()}")


def view_sessions(
    cinema_service: CinemaService,
    reservation_service: ReservationService,
) -> None:
    """Display every session with current available-seat counts."""
    sessions_output = cinema_service.format_session_catalog(
        reservation_service.get_booked_seats_for_session
    )
    print(f"\n{sessions_output}")


def view_available_seats(
    cinema_service: CinemaService,
    reservation_service: ReservationService,
) -> None:
    """Display the seat map for a selected session."""
    session_id = input("\nSession ID (or press Enter to return): ").strip()
    if not session_id:
        return

    session = cinema_service.get_session_by_id(session_id)
    if session is None:
        print("Session not found.")
        return

    booked_seats = reservation_service.get_booked_seats_for_session(session.id)
    print(f"\n{cinema_service.format_seat_map(session, booked_seats)}")
    seat = input("\nSeat to check (or press Enter to return): ").strip()
    if seat:
        print(cinema_service.check_seat(session, seat, booked_seats))


def create_booking(
    cinema_service: CinemaService,
    reservation_service: ReservationService,
    movie,
    session,
    booked_seats: set[str],
) -> None:
    """Collect customer details and create a reservation for a selected session."""
    print(f"\n{cinema_service.format_seat_map(session, booked_seats)}")

    customer_name = input("\nCustomer full name (or press Enter to cancel): ").strip()
    if not customer_name:
        print("Booking cancelled.")
        return

    customer_email = input("Customer email (or press Enter to cancel): ").strip()
    if not customer_email:
        print("Booking cancelled.")
        return

    seat_input = input(
        "Seats, separated by commas (example: A1,A2): "
    )
    seats = [seat.strip() for seat in seat_input.split(",")]

    try:
        reservation = reservation_service.create_reservation(
            session=session,
            customer_name=customer_name,
            customer_email=customer_email,
            seats=seats,
        )
    except ValueError as error:
        print(f"\nBooking rejected: {error}")
        return

    print_booking_ticket(reservation, movie, session)
    updated_booked_seats = reservation_service.get_booked_seats_for_session(session.id)
    print("\nUpdated seat map")
    print(cinema_service.format_seat_map(session, updated_booked_seats))


def print_booking_ticket(reservation: Reservation, movie, session) -> None:
    """Print a clear terminal ticket for a confirmed reservation."""
    border = "+" + "=" * 62 + "+"
    print("\n" + border)
    print("|" + "CIMASEATS - BOOKING TICKET".center(62) + "|")
    print("|" + "BOOKING CONFIRMED".center(62) + "|")
    print("+" + "-" * 62 + "+")
    print(f"| Reservation : {reservation.id:<46}|")
    print(f"| Customer    : {reservation.customer_name:<46}|")
    print(f"| Email       : {reservation.customer_email:<46}|")
    print(f"| Movie       : {movie.title:<46}|")
    print(f"| Session     : {session.id:<46}|")
    print(f"| Date        : {session.start_time.strftime('%d/%m/%Y at %H:%M'):<46}|")
    print(f"| Room        : {session.hall:<46}|")
    print(f"| Seats       : {', '.join(reservation.seats):<46}|")
    print(f"| Unit price  : {str(session.ticket_price) + ' EUR':<46}|")
    print(f"| TOTAL       : {str(reservation.total_amount) + ' EUR':<46}|")
    print("+" + "-" * 62 + "+")
    print("| Thank you for your booking. Enjoy the movie!".ljust(63) + "|")
    print(border)


def view_reservation_details(
    cinema_service: CinemaService,
    reservation_service: ReservationService,
) -> None:
    """Display the complete details of one reservation by ID."""
    reservation_id = input(
        "\nReservation ID (or press Enter to return): "
    ).strip()
    if not reservation_id:
        return

    reservation = reservation_service.get_reservation_by_id(reservation_id)
    if reservation is None:
        print("\nReservation not found.")
        return

    session = cinema_service.get_session_by_id(reservation.session_id)
    movie = cinema_service.get_movie_by_id(session.movie_id) if session else None
    print("\n" + "=" * 58)
    print("RESERVATION DETAILS")
    print("=" * 58)
    print(f"Reservation ID : {reservation.id}")
    print(f"Customer       : {reservation.customer_name}")
    print(f"Email          : {reservation.customer_email}")
    print(f"Movie          : {movie.title if movie else 'Unknown'}")
    print(f"Session        : {reservation.session_id}")
    if session:
        print(f"Date           : {session.start_time.strftime('%d/%m/%Y at %H:%M')}")
        print(f"Room           : {session.hall}")
    print(f"Seats          : {', '.join(reservation.seats)}")
    print(f"Amount paid    : {reservation.total_amount:.2f} EUR")
    print(f"Status         : {reservation.status.value}")
    print("=" * 58)


def cancel_reservation_flow(
    cinema_service: CinemaService,
    reservation_service: ReservationService,
) -> None:
    """Cancel one reservation by ID and display the released seats."""
    reservation_id = input("\nReservation ID (or press Enter to return): ").strip()
    if not reservation_id:
        return

    try:
        reservation = reservation_service.cancel_reservation(reservation_id)
    except ValueError as error:
        print(f"\nCancellation failed: {error}")
        return

    print(f"\nReservation {reservation.id} cancelled successfully.")
    print(f"Released seats: {', '.join(reservation.seats)}")
    session = cinema_service.get_session_by_id(reservation.session_id)
    if session:
        booked_seats = reservation_service.get_booked_seats_for_session(session.id)
        print("\nUpdated seat map")
        print(cinema_service.format_seat_map(session, booked_seats))


def handle_choice(
    choice: str,
    cinema_service: CinemaService,
    reservation_service: ReservationService,
) -> bool:
    """Handle one menu choice and return whether the application should exit."""
    try:
        if choice == "7":
            print("\nThank you for using CiMaSeat. Goodbye!")
            return True

        if choice == "1":
            view_movies(cinema_service)
            return False

        if choice == "2":
            view_sessions(cinema_service, reservation_service)
            return False

        if choice == "3":
            view_available_seats(cinema_service, reservation_service)
            return False

        if choice == "4":
            book_tickets(cinema_service, reservation_service)
            return False

        if choice == "5":
            view_reservation_details(cinema_service, reservation_service)
            return False

        if choice == "6":
            cancel_reservation_flow(cinema_service, reservation_service)
            return False

        print("\nInvalid choice. Please select an option from 1 to 7.")
        return False
    except JsonFileError as error:
        print(f"\nData error: {error}")
        print("Check the relevant JSON file and try again.")
        return False
    except ValueError as error:
        print(f"\nOperation failed: {error}")
        return False


def main() -> None:
    """Start the interactive CimaSeats command-line application."""
    cinema_service = CinemaService()
    reservation_service = ReservationService()

    display_title()
    while True:
        display_menu()
        choice = input("\nYour choice: ").strip()
        if handle_choice(choice, cinema_service, reservation_service):
            break


if __name__ == "__main__":
    main()
