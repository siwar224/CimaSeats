"""Command-line entry point for the CimaSeats application."""

from services import CinemaService, ReservationService


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


def browse_movies_and_select_session(cinema_service: CinemaService) -> None:
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

    print(
        f"Séance sélectionnée : {selected_session.id} - "
        f"{selected_session.start_time.strftime('%d/%m/%Y à %H:%M')} - "
        f"{selected_session.hall} - {selected_session.ticket_price:.2f} EUR"
    )
    print("La réservation sera disponible dans une prochaine étape.")


def handle_choice(
    choice: str,
    cinema_service: CinemaService,
    reservation_service: ReservationService,
) -> bool:
    """Handle one menu choice and return whether the application should exit."""
    actions = {
        "2": cinema_service.list_sessions,
        "3": cinema_service.list_available_seats,
        "4": reservation_service.create_reservation,
        "5": reservation_service.consult_reservations,
        "6": reservation_service.cancel_reservation,
    }

    if choice == "7":
        print("\nMerci d'avoir utilisé CiMaSeat. À bientôt !")
        return True

    if choice == "1":
        browse_movies_and_select_session(cinema_service)
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
