"""Interactive Streamlit booking interface for CimaSeats."""

from __future__ import annotations

from html import escape

import streamlit as st

from services import CinemaService, ReservationService
from utils.file_handler import JsonFileError


MENU_OPTIONS = (
    "View Movies",
    "View Sessions",
    "View Available Seats",
    "Book Tickets",
    "View Reservation",
    "Cancel Reservation",
    "Exit",
)


def apply_theme() -> None:
    """Apply the shared visual system used by every Streamlit page."""
    st.markdown(
        """
        <style>
        :root {
            --cima-ink: #182033;
            --cima-muted: #667085;
            --cima-primary: #0b6e99;
            --cima-primary-dark: #074c6b;
            --cima-surface: #ffffff;
            --cima-background: #f5f7fb;
            --cima-border: #e6eaf2;
            --cima-success: #11936f;
        }

        .stApp {
            background: var(--cima-background);
            color: var(--cima-ink);
        }

        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
            color: var(--cima-ink) !important;
        }
        .stApp [data-testid="stMarkdownContainer"] p,
        .stApp [data-testid="stMarkdownContainer"] li,
        .stApp [data-testid="stCaptionContainer"],
        .stApp label {
            color: #475467 !important;
        }
        .stApp [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--cima-surface);
            border-color: var(--cima-border);
        }
        .stApp [data-testid="stVerticalBlockBorderWrapper"] h1,
        .stApp [data-testid="stVerticalBlockBorderWrapper"] h2,
        .stApp [data-testid="stVerticalBlockBorderWrapper"] h3,
        .stApp [data-testid="stVerticalBlockBorderWrapper"] h4,
        .stApp [data-testid="stVerticalBlockBorderWrapper"] p,
        .stApp [data-testid="stVerticalBlockBorderWrapper"] label {
            color: var(--cima-ink) !important;
        }
        .stApp [data-testid="stVerticalBlockBorderWrapper"]
        [data-testid="stCaptionContainer"] {
            color: var(--cima-muted) !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #102a43 0%, #1f4e79 100%);
            border-right: 0;
        }

        [data-testid="stSidebar"] * { color: #f8faff !important; }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #b9c3df !important;
        }
        [data-testid="stSidebar"] [role="radiogroup"] {
            gap: 0.35rem;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            border-radius: 10px;
            padding: 0.55rem 0.7rem;
            transition: background 160ms ease;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(255,255,255,0.10);
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: #ffffff;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) * {
            color: var(--cima-primary-dark) !important;
            font-weight: 700;
        }

        .cima-brand {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            margin: 0.3rem 0 0.2rem;
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.03em;
        }
        .cima-brand-mark {
            display: grid;
            place-items: center;
            width: 2.1rem;
            height: 2.1rem;
            border-radius: 9px;
            background: linear-gradient(135deg, #2f80ed, #0b6e99);
            box-shadow: 0 8px 18px rgba(11,110,153,0.30);
        }
        .page-header { margin: 0.35rem 0 1.4rem; }
        .page-eyebrow {
            color: var(--cima-primary);
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        .page-header h1 {
            color: var(--cima-ink);
            font-size: clamp(2rem, 4vw, 3.15rem);
            letter-spacing: -0.055em;
            line-height: 1.05;
            margin: 0.25rem 0 0.45rem;
        }
        .page-header p { color: var(--cima-muted); margin: 0; font-size: 1rem; }
        .movie-meta, .session-meta { color: var(--cima-muted); font-size: 0.88rem; }
        .movie-description { color: #475467; line-height: 1.55; min-height: 4.5rem; }
        .movie-card {
            background: #ffffff;
            border: 1px solid #d7e1e8;
            border-radius: 18px;
            box-shadow: 0 8px 22px rgba(16,42,67,0.06);
            min-height: 245px;
            overflow: hidden;
            padding: 1.25rem;
            position: relative;
            transition: box-shadow 160ms ease, transform 160ms ease;
        }
        .movie-card:hover {
            box-shadow: 0 14px 30px rgba(16,42,67,0.12);
            transform: translateY(-3px);
        }
        .movie-card::before {
            background: linear-gradient(90deg, #0b6e99, #5aa9c5);
            content: "";
            height: 5px;
            left: 0;
            position: absolute;
            right: 0;
            top: 0;
        }
        .movie-card-top {
            align-items: center;
            display: flex;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        .movie-art {
            align-items: center;
            background: linear-gradient(135deg, #dff3f7, #b7dbe6);
            border-radius: 12px;
            color: #075985;
            display: flex;
            font-size: 1.35rem;
            font-weight: 800;
            height: 2.65rem;
            justify-content: center;
            width: 2.65rem;
        }
        .movie-card-id {
            color: #8293a1;
            font-family: monospace;
            font-size: 0.72rem;
            letter-spacing: 0.05em;
        }
        .movie-card h3 {
            color: var(--cima-ink);
            font-size: 1.12rem;
            letter-spacing: -0.02em;
            margin: 0 0 0.4rem;
        }
        .movie-card .movie-meta { margin-bottom: 0.85rem; }
        .movie-card-description {
            color: #475467;
            font-size: 0.9rem;
            line-height: 1.5;
            min-height: 4.1rem;
        }
        .movie-card-footer {
            align-items: center;
            border-top: 1px solid #edf1f4;
            display: flex;
            justify-content: space-between;
            margin-top: 1.05rem;
            padding-top: 0.85rem;
        }
        .badge {
            display: inline-block;
            border-radius: 999px;
            padding: 0.22rem 0.6rem;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.03em;
        }
        .badge-primary { color: #0b4f6c; background: #e5f3f8; }
        .badge-success { color: #087f5b; background: #e7f8f1; }
        .badge-danger { color: #b42318; background: #fff0ed; }
        .action-card {
            background: #ffffff;
            border: 1px solid #d7e1e8;
            border-radius: 18px;
            box-shadow: 0 10px 28px rgba(16,42,67,0.07);
            margin: 0.5rem 0 1rem;
            padding: 1.25rem;
        }
        .action-card h3 { margin: 0 0 0.25rem; }
        .action-card p { color: #667085; margin: 0; }
        .action-icon {
            align-items: center;
            border-radius: 12px;
            display: inline-flex;
            font-size: 1.35rem;
            height: 2.7rem;
            justify-content: center;
            margin-bottom: 0.65rem;
            width: 2.7rem;
        }
        .action-icon-search { background: #e5f3f8; }
        .action-icon-cancel { background: #fff0ed; }
        .warning-card {
            background: #fff8f5;
            border: 1px solid #f6c7bd;
            border-left: 4px solid #d6453d;
            border-radius: 12px;
            color: #7a271a;
            margin-bottom: 1rem;
            padding: 0.9rem 1rem;
        }
        .screen-bar {
            background: linear-gradient(90deg, #b7e4f0, #5aa9c5, #b7e4f0);
            border-radius: 999px;
            color: #0f3d4c;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.16em;
            padding: 0.65rem;
            text-align: center;
            text-transform: uppercase;
            margin: 0.8rem auto 1.25rem;
            max-width: 78%;
        }
        .seat-legend { color: var(--cima-muted); font-size: 0.82rem; margin-top: 0.75rem; }
        .ticket-header {
            background: linear-gradient(135deg, #123b5d, #0b6e99);
            border-radius: 16px 16px 0 0;
            color: white;
            padding: 1.35rem 1.5rem;
        }
        .ticket-header h2 { color: white; margin: 0.25rem 0 0; }
        .ticket-kicker { color: #b7e4f0; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; }
        .ticket-body { background: white; border: 1px solid var(--cima-border); border-top: 0; border-radius: 0 0 16px 16px; padding: 1.25rem 1.5rem; }
        .ticket-id { color: var(--cima-muted); font-family: monospace; font-size: 0.85rem; }
        div[data-testid="stButton"] > button {
            background: #ffffff;
            border-radius: 10px;
            border: 1px solid #b8c7d3;
            color: #123b5d !important;
            min-height: 2.55rem;
            font-weight: 650;
        }
        div[data-testid="stButton"] > button:hover {
            background: #eaf5f8;
            border-color: #5aa9c5;
            color: #075985 !important;
        }
        div[data-testid="stButton"] > button[kind="primary"],
        [data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, #168aad, #075985);
            border: 0 !important;
            color: #ffffff !important;
            box-shadow: 0 7px 16px rgba(7,88,133,0.22);
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover,
        [data-testid="stBaseButton-primary"]:hover {
            background: linear-gradient(135deg, #0b6e99, #064e70);
            color: #ffffff !important;
            transform: translateY(-1px);
        }
        div[data-testid="stButton"] > button:disabled,
        [data-testid="stBaseButton-secondary"]:disabled {
            background: #e5ebef;
            border-color: #c8d2d9;
            color: #5f6f7b !important;
        }
        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-testid="stTextInput"] input {
            background: #ffffff;
            border-color: #b8c7d3;
            color: #182033 !important;
        }
        [data-testid="stTextInput"] input::placeholder {
            color: #667085 !important;
        }
        [data-testid="stMetric"] {
            background: white;
            border: 1px solid var(--cima-border);
            border-radius: 12px;
            padding: 0.8rem 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(eyebrow: str, title: str, description: str) -> None:
    """Render a consistent modern header for a content page."""
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-eyebrow">{eyebrow}</div>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    """Render a polished ticket card after a successful booking."""
    st.markdown(
        f"""
        <div class="ticket-header">
            <div class="ticket-kicker">CiMaSeat · Booking confirmed</div>
            <h2>{ticket['movie_title']}</h2>
        </div>
        <div class="ticket-body">
            <div class="ticket-id">Reservation ID · {ticket['id']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    details_left, details_right = st.columns(2)
    with details_left:
        st.write(f"**Customer**  \n{ticket['customer_name']}")
        st.write(f"**Session**  \n{ticket['session_id']}")
        st.write(f"**Room**  \n{ticket['room']}")
    with details_right:
        st.write(f"**Date**  \n{ticket['date']}")
        st.write(f"**Seats**  \n{ticket['seats']}")
        st.markdown(f"**Total**  \n### {ticket['total_amount']} EUR")


@st.dialog("Booking confirmation")
def show_booking_confirmation(ticket: dict[str, str]) -> None:
    """Show a reservation summary before opening the ticket page."""
    st.success("Your booking has been confirmed.")
    st.markdown(f"## {ticket['movie_title']}")
    st.write(f"**Movie:** {ticket['movie_title']}")
    st.write(f"**Session:** {ticket['date']} · {ticket['room']}")
    st.write(f"**Seats:** {ticket['seats']}")
    st.write(f"**Total:** {ticket['total_amount']} EUR")
    st.caption("Open the next page to view and keep your complete ticket.")

    if st.button("View my ticket", type="primary", use_container_width=True):
        st.switch_page("pages/ticket.py")


def render_sidebar() -> str:
    """Render the fixed Streamlit sidebar with the CLI menu options."""
    st.sidebar.markdown(
        """
        <div class="cima-brand">
            <span class="cima-brand-mark">🎬</span>
            <span>CiMaSeat</span>
        </div>
        <p style="margin:0 0 1.6rem;">Your cinema, simplified.</p>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("<b>MENU</b>", unsafe_allow_html=True)
    return st.sidebar.radio(
        "Menu",
        MENU_OPTIONS,
        key="sidebar_menu",
        label_visibility="collapsed",
    )


def render_seat_map(
    cinema_service,
    reservation_service,
    session,
    *,
    interactive: bool = True,
) -> set[str]:
    """Render a seat map and return selected seats when booking is enabled."""
    room = cinema_service.get_room_for_session(session)
    booked_seats = reservation_service.get_booked_seats_for_session(session.id)

    if interactive and st.session_state.get("selected_session_id") != session.id:
        st.session_state.selected_session_id = session.id
        st.session_state.selected_seats = set()

    selected_seats: set[str] = (
        st.session_state.setdefault("selected_seats", set())
        if interactive
        else set()
    )

    st.markdown("### Select your seats" if interactive else "### Seat availability")
    st.markdown(
        "<div class='screen-bar'>Screen</div>",
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
                if interactive:
                    if st.button(
                        button_label,
                        key=f"seat-{session.id}-{seat_id}",
                        disabled=is_booked,
                        type="primary" if is_selected else "secondary",
                        use_container_width=True,
                    ):
                        if is_selected:
                            selected_seats.remove(seat_id)
                        else:
                            selected_seats.add(seat_id)
                        st.rerun()
                else:
                    color = "#777" if is_booked else "#20a77a"
                    st.markdown(
                        f"<div style='text-align:center;color:{color};padding:8px;'>"
                        f"{button_label}</div>",
                        unsafe_allow_html=True,
                    )

    st.markdown(
        "<div class='seat-legend'>Available · <b>Selected</b> ✓ · "
        "<b>Occupied</b> X</div>",
        unsafe_allow_html=True,
    )
    return selected_seats


def render_movie_cards(movies) -> None:
    """Display movies as presentation cards instead of a data table."""
    render_page_header(
        "Discover",
        "Find your next story",
        f"Explore {len(movies)} movies currently playing at CiMaSeat.",
    )
    for start in range(0, len(movies), 3):
        columns = st.columns(3)
        for column, movie in zip(columns, movies[start:start + 3]):
            with column:
                movie_title = escape(movie.title)
                movie_genre = escape(movie.genre)
                movie_description = escape(movie.description)
                movie_rating = escape(movie.age_rating or "All audiences")
                movie_id = escape(movie.id)
                movie_initial = escape(movie.title[:1].upper())
                st.markdown(
                    f"""
                    <article class="movie-card">
                        <div class="movie-card-top">
                            <div class="movie-art">{movie_initial}</div>
                            <div class="movie-card-id">{movie_id}</div>
                        </div>
                        <h3>{movie_title}</h3>
                        <div class="movie-meta">{movie_genre} · 
                            {movie.duration_minutes} min · {movie.release_year or 'N/A'}
                        </div>
                        <div class="movie-card-description">{movie_description}</div>
                        <div class="movie-card-footer">
                            <span class="badge badge-primary">{movie_rating}</span>
                            <span class="movie-card-id">CiMaSeat cinema</span>
                        </div>
                    </article>
                    """,
                    unsafe_allow_html=True,
                )


def render_sessions_page(movies, cinema_service) -> None:
    """Display sessions filtered by a selected movie."""
    render_page_header(
        "Plan your visit",
        "Choose a session",
        "Select a movie to see its available showtimes and ticket prices.",
    )
    movie_options = {f"{movie.title} · {movie.id}": movie for movie in movies}
    selected_label = st.selectbox("Choose a movie", list(movie_options))
    selected_movie = movie_options[selected_label]
    sessions = cinema_service.get_sessions_for_movie(selected_movie.id)

    for session in sessions:
        with st.container(border=True):
            left, right = st.columns([2, 1])
            with left:
                st.markdown(
                    f"<span class='badge badge-primary'>{session.id}</span>",
                    unsafe_allow_html=True,
                )
                st.subheader(session.start_time.strftime("%A %d %B · %H:%M"))
                st.markdown(
                    f"<div class='session-meta'>📍 {session.hall} · "
                    f"{session.rows} rows · {session.seats_per_row} seats per row</div>",
                    unsafe_allow_html=True,
                )
            with right:
                st.metric("Ticket price", f"{session.ticket_price:.2f} EUR")


def render_available_seats_page(movies, cinema_service, reservation_service) -> None:
    """Display the current seat availability for a selected session."""
    render_page_header(
        "Live availability",
        "Find your seat",
        "Choose a session to see which seats are available in real time.",
    )
    movie_options = {f"{movie.title} · {movie.id}": movie for movie in movies}
    selected_movie = movie_options[st.selectbox("Choose a movie", list(movie_options))]
    sessions = cinema_service.get_sessions_for_movie(selected_movie.id)
    session_options = {
        session.id: format_session_label(session) for session in sessions
    }
    selected_session_id = st.selectbox(
        "Choose a session",
        list(session_options),
        format_func=session_options.get,
    )
    selected_session = next(
        session for session in sessions if session.id == selected_session_id
    )
    room = cinema_service.get_room_for_session(selected_session)
    booked_count = len(reservation_service.get_booked_seats_for_session(selected_session.id))
    total_seats = room.rows * room.seats_per_row
    available_count = total_seats - booked_count
    metric_left, metric_center, metric_right = st.columns(3)
    metric_left.metric("Available", available_count)
    metric_center.metric("Occupied", booked_count)
    metric_right.metric("Capacity", total_seats)
    render_seat_map(
        cinema_service,
        reservation_service,
        selected_session,
        interactive=False,
    )


def render_reservation_details(
    reservation,
    cinema_service,
) -> None:
    """Display the movie, session, seats, amount, and status of a reservation."""
    session = cinema_service.get_session_by_id(reservation.session_id)
    movie = cinema_service.get_movie_by_id(session.movie_id) if session else None
    if session is None or movie is None:
        st.error("The movie or session linked to this reservation is unavailable.")
        return

    status_class = "badge-success" if reservation.is_active else "badge-danger"
    st.markdown(
        f"<span class='badge {status_class}'>{reservation.status.value.title()}</span>",
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.subheader(movie.title)
        st.caption(f"Reservation ID · {reservation.id}")
        detail_left, detail_center, detail_right = st.columns(3)
        with detail_left:
            st.markdown(f"**Customer**  \n{reservation.customer_name}")
            st.markdown(f"**Seats**  \n{', '.join(reservation.seats)}")
        with detail_center:
            st.markdown(f"**Session**  \n{format_session_label(session)}")
            st.markdown(f"**Room**  \n{session.hall}")
        with detail_right:
            st.markdown(f"**Amount paid**  \n### {reservation.total_amount:.2f} EUR")


def render_view_reservation_page(cinema_service, reservation_service) -> None:
    """Find and display one reservation by its identifier."""
    render_page_header(
        "Your bookings",
        "View a reservation",
        "Enter your reservation ID to review its details and current status.",
    )
    with st.container(border=True):
        st.markdown(
            """
            <div class="action-card">
                <div class="action-icon action-icon-search">🔎</div>
                <h3>Find your booking</h3>
                <p>Use the reservation ID from your confirmation ticket.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        reservation_id = st.text_input(
            "Reservation ID",
            placeholder="Example: RES-A1B2C3D4",
        )
        search_clicked = st.button(
            "🔎  Search reservation",
            type="secondary",
            use_container_width=True,
        )

    if search_clicked:
        if not reservation_id.strip():
            st.warning("Enter a reservation ID to continue.")
            return
        try:
            reservation = reservation_service.get_reservation_by_id(reservation_id.strip())
        except JsonFileError as error:
            st.error(f"Unable to load reservations: {error}")
            return
        if reservation is None:
            st.error("Reservation not found. Check the ID and try again.")
        else:
            render_reservation_details(reservation, cinema_service)


def render_cancel_reservation_page(cinema_service, reservation_service) -> None:
    """Cancel a confirmed reservation without deleting its history."""
    render_page_header(
        "Manage booking",
        "Cancel a reservation",
        "Cancellation keeps your reservation history and releases its seats.",
    )
    st.markdown(
        """
        <style>
        div[data-testid="stButton"] > button[kind="primary"],
        [data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, #d6453d, #a92f2b) !important;
            box-shadow: 0 7px 16px rgba(169,47,43,0.20) !important;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover,
        [data-testid="stBaseButton-primary"]:hover {
            background: linear-gradient(135deg, #c03935, #8f2724) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.markdown(
            """
            <div class="action-card">
                <div class="action-icon action-icon-cancel">⚠️</div>
                <h3>Cancel a confirmed booking</h3>
                <p>This keeps the reservation history and releases the seats.</p>
            </div>
            <div class="warning-card">
                Please make sure the reservation ID is correct. This action cannot
                be undone once the reservation is cancelled.
            </div>
            """,
            unsafe_allow_html=True,
        )
        reservation_id = st.text_input(
            "Reservation ID",
            placeholder="Example: RES-A1B2C3D4",
        )
        cancel_clicked = st.button(
            "⚠️  Cancel reservation",
            type="primary",
            use_container_width=True,
        )

    if cancel_clicked:
        if not reservation_id.strip():
            st.warning("Enter a reservation ID to continue.")
            return
        try:
            reservation = reservation_service.cancel_reservation(reservation_id.strip())
        except (JsonFileError, ValueError) as error:
            st.error(str(error))
        else:
            st.success("Reservation cancelled. Its seats are available again.")
            render_reservation_details(reservation, cinema_service)


def render_booking_page(movies, cinema_service, reservation_service) -> None:
    """Render the interactive movie booking workflow."""
    render_page_header(
        "Book in a few clicks",
        "Your cinema night starts here",
        "Choose a movie, pick a showtime, and reserve your favorite seats.",
    )

    if st.session_state.pop("show_confirmation", False):
        show_booking_confirmation(st.session_state.last_ticket)

    st.markdown("### Choose a movie")
    movie_options = {f"{movie.title} · {movie.id}": movie for movie in movies}
    selected_movie_label = st.selectbox(
        "Movie",
        list(movie_options),
        label_visibility="collapsed",
    )
    selected_movie = movie_options[selected_movie_label]

    with st.container(border=True):
        movie_left, movie_right = st.columns([2, 1])
        with movie_left:
            st.subheader(selected_movie.title)
            st.markdown(
                f"<div class='movie-meta'>{selected_movie.genre} · "
                f"{selected_movie.duration_minutes} min · "
                f"{selected_movie.release_year or 'N/A'}</div>",
                unsafe_allow_html=True,
            )
            st.write(selected_movie.description)
        with movie_right:
            st.markdown(
                f"<span class='badge badge-primary'>"
                f"{selected_movie.age_rating or 'All audiences'}</span>",
                unsafe_allow_html=True,
            )
            st.markdown("\n")
            st.caption("Selected movie")

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
        st.markdown(f"**Selected seats**  \n{selected_label}")
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


def main() -> None:
    """Render the booking page and dispatch the fixed sidebar menu."""
    st.set_page_config(
        page_title="CiMaSeat",
        page_icon="🎬",
        layout="wide",
    )
    apply_theme()

    selected_menu = render_sidebar()
    cinema_service, reservation_service = get_services()

    if selected_menu == "Exit":
        render_page_header(
            "CiMaSeat",
            "See you soon 👋",
            "Your next cinema experience is only a few clicks away.",
        )
        st.info("Thank you for visiting CiMaSeat.")
        return

    if selected_menu in {
        "View Movies",
        "View Sessions",
        "View Available Seats",
        "Book Tickets",
    }:
        try:
            movies = get_movie_catalog()
        except JsonFileError as error:
            st.error(f"Unable to load movies: {error}")
            return

        if not movies:
            st.info("No movies are currently available.")
            return
    else:
        movies = []

    if selected_menu == "View Movies":
        render_movie_cards(movies)
    elif selected_menu == "View Sessions":
        render_sessions_page(movies, cinema_service)
    elif selected_menu == "View Available Seats":
        render_available_seats_page(movies, cinema_service, reservation_service)
    elif selected_menu == "Book Tickets":
        render_booking_page(movies, cinema_service, reservation_service)
    elif selected_menu == "View Reservation":
        render_view_reservation_page(cinema_service, reservation_service)
    elif selected_menu == "Cancel Reservation":
        render_cancel_reservation_page(cinema_service, reservation_service)


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
