"""Command-line entry point for the CimaSeats application."""

from services import CinemaService, ReservationService
from models import Reservation


MENU_OPTIONS = {
    "1": "Films",
    "2": "Sessions",
    "3": "Seats",
    "4": "Reservation",
    "5": "Consultation",
    "6": "Cancelation",
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


def browse_movies_and_select_session(
    cinema_service: CinemaService,
    reservation_service: ReservationService,
) -> None:
    """Display movies, select a movie, then display and select its sessions."""
    print(f"\n{cinema_service.list_movies()}")
    movie_id = input("\nEntrez l'ID du film (ou Entrée pour revenir au menu) : ").strip()
    if not movie_id:
        return

    movie = cinema_service.get_movie_by_id(movie_id)
    if movie is None:
        print("Film introuvable. Vérifiez l'ID saisi.")
        return

    sessions = cinema_service.get_sessions_for_movie(movie.id)
    print(f"\nSéances de {movie.title} ({movie.id})")
    print(cinema_service.list_sessions_for_movie(movie.id))
    if not sessions:
        return

    session_id = input(
        "\nEntrez l'ID de la séance (ou Entrée pour revenir au menu) : "
    ).strip()
    if not session_id:
        return

    selected_session = cinema_service.get_session_by_id(session_id)
    if selected_session is None or selected_session.movie_id.upper() != movie.id.upper():
        print("Séance introuvable pour le film sélectionné.")
        return

    booked_seats = reservation_service.get_booked_seats_for_session(selected_session.id)
    print(f"\n{cinema_service.format_seat_map(selected_session, booked_seats)}")

    seat_to_check = input(
        "\nEntrez un numéro de siège à vérifier (ou Entrée pour revenir au menu) : "
    ).strip()
    if seat_to_check:
        print(cinema_service.check_seat(selected_session, seat_to_check, booked_seats))

    print(
        f"Séance sélectionnée : {selected_session.id} - "
        f"{selected_session.start_time.strftime('%d/%m/%Y à %H:%M')} - "
        f"{selected_session.hall} - {selected_session.ticket_price:.2f} EUR"
    )
    print("La réservation sera disponible dans une prochaine étape.")


def print_confirmation_ticket(reservation: Reservation, movie, session) -> None:
    """Print a clear terminal ticket for a confirmed reservation."""
    border = "+" + "=" * 62 + "+"
    print("\n" + border)
    print("|" + "CIMASEATS - TICKET DE CONFIRMATION".center(62) + "|")
    print("|" + "RESERVATION CONFIRMEE".center(62) + "|")
    print("+" + "-" * 62 + "+")
    print(f"| Reservation : {reservation.id:<46}|")
    print(f"| Client      : {reservation.customer_name:<46}|")
    print(f"| Email       : {reservation.customer_email:<46}|")
    print(f"| Film        : {movie.title:<46}|")
    print(f"| Séance      : {session.id:<46}|")
    print(f"| Date        : {session.start_time.strftime('%d/%m/%Y à %H:%M'):<46}|")
    print(f"| Salle       : {session.hall:<46}|")
    print(f"| Sièges      : {', '.join(reservation.seats):<46}|")
    print(f"| Prix unitaire : {str(session.ticket_price) + ' EUR':<44}|")
    print(f"| TOTAL       : {str(reservation.total_amount) + ' EUR':<46}|")
    print("+" + "-" * 62 + "+")
    print("| Merci pour votre réservation. Bon film !".ljust(63) + "|")
    print(border)


def create_reservation_flow(
    cinema_service: CinemaService,
    reservation_service: ReservationService,
) -> None:
    """Guide the user through a complete reservation."""
    print(f"\n{cinema_service.list_movies()}")
    movie_id = input("\nID du film (ou Entrée pour annuler) : ").strip()
    if not movie_id:
        return

    movie = cinema_service.get_movie_by_id(movie_id)
    if movie is None:
        print("Film introuvable. La réservation est annulée.")
        return

    print(f"\nSéances de {movie.title} ({movie.id})")
    print(cinema_service.list_sessions_for_movie(movie.id))
    session_id = input("\nID de la séance (ou Entrée pour annuler) : ").strip()
    if not session_id:
        return

    session = cinema_service.get_session_by_id(session_id)
    if session is None or session.movie_id.upper() != movie.id.upper():
        print("Séance introuvable pour ce film. La réservation est annulée.")
        return

    booked_seats = reservation_service.get_booked_seats_for_session(session.id)
    print(f"\n{cinema_service.format_seat_map(session, booked_seats)}")

    customer_name = input("\nNom complet du client : ").strip()
    customer_email = input("Email du client : ").strip()
    seat_input = input(
        "Sièges souhaités, séparés par des virgules (ex: A1,A2) : "
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
        print(f"\nRéservation refusée : {error}")
        return

    print_confirmation_ticket(reservation, movie, session)
    updated_booked_seats = reservation_service.get_booked_seats_for_session(session.id)
    print("\nPlan de salle mis à jour")
    print(cinema_service.format_seat_map(session, updated_booked_seats))


def handle_choice(
    choice: str,
    cinema_service: CinemaService,
    reservation_service: ReservationService,
) -> bool:
    """Handle one menu choice and return whether the application should exit."""
    actions = {
        "2": cinema_service.list_sessions,
        "3": cinema_service.list_available_seats,
        "5": reservation_service.consult_reservations,
        "6": reservation_service.cancel_reservation,
    }

    if choice == "7":
        print("\nMerci d'avoir utilisé CiMaSeat. À bientôt !")
        return True

    if choice == "1":
        browse_movies_and_select_session(cinema_service, reservation_service)
        return False

    if choice == "4":
        create_reservation_flow(cinema_service, reservation_service)
        return False

    action = actions.get(choice)
    if action is None:
        print("\nChoix invalide. Veuillez sélectionner une option entre 1 et 7.")
        return False

    print(f"\n{action()}")
    return False


def main() -> None:
    """Start the interactive CimaSeats command-line application."""
    cinema_service = CinemaService()
    reservation_service = ReservationService()

    display_title()
    while True:
        display_menu()
        choice = input("\nVotre choix : ").strip()
        if handle_choice(choice, cinema_service, reservation_service):
            break


if __name__ == "__main__":
    main()
