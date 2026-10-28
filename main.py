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


def handle_choice(
    choice: str,
    cinema_service: CinemaService,
    reservation_service: ReservationService,
) -> bool:
    """Handle one menu choice and return whether the application should exit."""
    actions = {
        "1": cinema_service.list_movies,
        "2": cinema_service.list_sessions,
        "3": cinema_service.list_available_seats,
        "4": reservation_service.create_reservation,
        "5": reservation_service.consult_reservations,
        "6": reservation_service.cancel_reservation,
    }

    if choice == "7":
        print("\nMerci d'avoir utilisé CiMaSeat. À bientôt !")
        return True

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
