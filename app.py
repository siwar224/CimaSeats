"""Interactive Streamlit booking interface for CimaSeats."""

from __future__ import annotations

import streamlit as st

from services import CinemaService, ReservationService
from utils.file_handler import JsonFileError


@st.cache_resource
def get_services() -> tuple[CinemaService, ReservationService]:
    """Return the shared application services used by the Streamlit UI."""
    return CinemaService(), ReservationService()


def get_movie_catalog():
    """Load movies through the existing cinema service."""
    cinema_service, _ = get_services()
    return cinema_service.get_movies()


def get_session_catalog():
    """Load sessions through the existing cinema service."""
    cinema_service, _ = get_services()
    return cinema_service.get_sessions()


def get_reservation(reservation_id: str):
    """Load one reservation through the existing reservation service."""
    _, reservation_service = get_services()
    return reservation_service.get_reservation_by_id(reservation_id)


def format_session_label(session) -> str:
    """Create a readable showtime label for the session selector."""
    start_time = session.start_time.strftime("%A %d %B · %H:%M")
    return f"{start_time} · {session.hall} · {session.ticket_price:.2f} EUR"


def render_booking_ticket(ticket: dict[str, str]) -> None:
    """Render a compact confirmation ticket after a successful booking."""
    with st.container(border=True):
        st.markdown(f"### {ticket['movie_title']}")
        st.caption(f"Reservation ID: `{ticket['id']}`")
        details_left, details_right = st.columns(2)
        with details_left:
            st.write(f"**Customer:** {ticket['customer_name']}")
            st.write(f"**Session:** {ticket['session_id']}")
            st.write(f"**Room:** {ticket['room']}")
        with details_right:
            st.write(f"**Date:** {ticket['date']}")
            st.write(f"**Seats:** {ticket['seats']}")
            st.write(f"**Total:** {ticket['total_amount']} EUR")


@st.dialog("Booking confirmation")
def show_booking_confirmation(ticket: dict[str, str]) -> None:
    """Show a reservation summary before opening the ticket page."""
    st.success("Your booking has been confirmed.")
    st.write(f"**Movie:** {ticket['movie_title']}")
    st.write(f"**Session:** {ticket['date']} · {ticket['room']}")
    st.write(f"**Seats:** {ticket['seats']}")
    st.write(f"**Total:** {ticket['total_amount']} EUR")
    st.caption("Open the next page to view and keep your complete ticket.")

    if st.button("View my ticket", type="primary", use_container_width=True):
        st.switch_page("pages/ticket.py")


def render_seat_map(cinema_service, reservation_service, session) -> set[str]:
    """Render an interactive seat map and return the selected seat IDs."""
    room = cinema_service.get_room_for_session(session)
    booked_seats = reservation_service.get_booked_seats_for_session(session.id)

    if st.session_state.get("selected_session_id") != session.id:
        st.session_state.selected_session_id = session.id
        st.session_state.selected_seats = set()

    selected_seats: set[str] = st.session_state.setdefault("selected_seats", set())

    st.markdown("### Select your seats")
    st.markdown(
        "<div style='background:#222;border-radius:8px;padding:10px;"
        "text-align:center;margin:12px 0 22px;'>SCREEN</div>",
        unsafe_allow_html=True,
    )

    header_columns = st.columns([0.7] + [1] * room.seats_per_row)
    with header_columns[0]:
        st.write("")
    for number, column in enumerate(header_columns[1:], start=1):
        with column:
            st.caption(str(number))

    for row_number in range(1, room.rows + 1):
        row_label = room.row_label(row_number)
        row_columns = st.columns([0.7] + [1] * room.seats_per_row)
        with row_columns[0]:
            st.markdown(f"**{row_label}**")

        for seat_number, column in enumerate(row_columns[1:], start=1):
            seat_id = f"{row_label}{seat_number}"
            is_booked = seat_id in booked_seats
            is_selected = seat_id in selected_seats
            button_label = "X" if is_booked else ("✓" if is_selected else str(seat_number))
            with column:
                if st.button(
                    button_label,
                    key=f"seat-{session.id}-{seat_id}",
                    disabled=is_booked,
                    use_container_width=True,
                ):
                    if is_selected:
                        selected_seats.remove(seat_id)
                    else:
                        selected_seats.add(seat_id)
                    st.rerun()

    st.caption("Available: [ ] · Selected: ✓ · Occupied: X")
    return selected_seats


def main() -> None:
    """Render the interactive movie booking page."""
    st.set_page_config(
        page_title="CiMaSeat - Book Tickets",
        page_icon="🎬",
        layout="wide",
    )

    st.title("🎬 CiMaSeat")
    st.caption("Book your favorite movie in a few clicks.")

    try:
        movies = get_movie_catalog()
    except JsonFileError as error:
        st.error(f"Unable to load movies: {error}")
        st.stop()

    if not movies:
        st.info("No movies are currently available.")
        return

    if st.session_state.pop("show_confirmation", False):
        show_booking_confirmation(st.session_state.last_ticket)

    st.markdown("### Choose a movie")
    movie_options = {f"{movie.title} · {movie.id}": movie for movie in movies}
    selected_movie_label = st.selectbox("Movie", list(movie_options), label_visibility="collapsed")
    selected_movie = movie_options[selected_movie_label]

    st.caption(
        f"{selected_movie.genre} · {selected_movie.duration_minutes} min · "
        f"{selected_movie.release_year or 'N/A'} · "
        f"{selected_movie.age_rating or 'N/A'}"
    )
    st.write(selected_movie.description)

    cinema_service, reservation_service = get_services()
    sessions = cinema_service.get_sessions_for_movie(selected_movie.id)
    if not sessions:
        st.info("No sessions are available for this movie.")
        return

    st.markdown("### Showtime")
    session_options = {session.id: format_session_label(session) for session in sessions}
    selected_session_id = st.radio(
        "Showtime",
        list(session_options),
        format_func=session_options.get,
        horizontal=True,
        label_visibility="collapsed",
    )
    selected_session = next(
        session for session in sessions if session.id == selected_session_id
    )

    st.divider()
    selected_seats = render_seat_map(
        cinema_service,
        reservation_service,
        selected_session,
    )

    st.divider()
    summary_left, summary_right = st.columns([2, 1])
    with summary_left:
        selected_label = ", ".join(sorted(selected_seats)) or "None"
        st.write(f"**Selected seats:** {selected_label}")
    with summary_right:
        total_amount = selected_session.ticket_price * len(selected_seats)
        st.metric("Total", f"{total_amount:.2f} EUR")

    customer_left, customer_right = st.columns(2)
    with customer_left:
        customer_name = st.text_input("Full name", key="booking_customer_name")
    with customer_right:
        customer_email = st.text_input("Email", key="booking_customer_email")

    if st.button(
        "Confirm booking",
        type="primary",
        use_container_width=True,
        disabled=not selected_seats,
    ):
        if not customer_name.strip() or not customer_email.strip():
            st.error("Please enter your full name and email.")
        else:
            try:
                reservation = reservation_service.create_reservation(
                    session=selected_session,
                    customer_name=customer_name,
                    customer_email=customer_email,
                    seats=sorted(selected_seats),
                )
            except (JsonFileError, ValueError) as error:
                st.error(f"Booking failed: {error}")
            else:
                st.session_state.last_ticket = {
                    "id": reservation.id,
                    "movie_title": selected_movie.title,
                    "customer_name": reservation.customer_name,
                    "session_id": selected_session.id,
                    "room": selected_session.hall,
                    "date": selected_session.start_time.strftime("%d/%m/%Y at %H:%M"),
                    "seats": ", ".join(reservation.seats),
                    "total_amount": str(reservation.total_amount),
                }
                st.session_state.selected_seats = set()
                st.session_state.show_confirmation = True
                st.rerun()


def run_streamlit_app() -> None:
    """Register the application pages and start Streamlit navigation."""
    booking_page = st.Page(
        "pages/home.py",
        title="Book tickets",
        icon="🎬",
        url_path="",
        default=True,
    )
    ticket_page = st.Page(
        "pages/ticket.py",
        title="Your ticket",
        icon="🎟️",
        url_path="ticket",
    )
    navigation = st.navigation(
        [booking_page, ticket_page],
        position="hidden",
    )
    navigation.run()


if __name__ == "__main__":
    run_streamlit_app()
