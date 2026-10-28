"""Streamlit interface for browsing the CimaSeats movie catalogue."""

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


def movie_rows(movies) -> list[dict[str, object]]:
    """Convert movie models into rows ready for Streamlit's data table."""
    return [
        {
            "ID": movie.id,
            "Title": movie.title,
            "Genre": movie.genre,
            "Duration (min)": movie.duration_minutes,
            "Release year": str(movie.release_year or "N/A"),
            "Age rating": movie.age_rating or "N/A",
            "Description": movie.description,
        }
        for movie in movies
    ]


def get_session_catalog():
    """Load sessions through the existing cinema service."""
    cinema_service, _ = get_services()
    return cinema_service.get_sessions()


def get_reservation(reservation_id: str):
    """Load one reservation through the existing reservation service."""
    _, reservation_service = get_services()
    return reservation_service.get_reservation_by_id(reservation_id)


def main() -> None:
    """Render the movie catalogue page."""
    st.set_page_config(
        page_title="CiMaSeat - Movies",
        page_icon="🎬",
        layout="wide",
    )

    st.title("🎬 CiMaSeat")
    st.subheader("Available Movies")
    st.caption("Movie data loaded from data/movies.json")

    try:
        movies = get_movie_catalog()
    except JsonFileError as error:
        st.error(f"Unable to load movies: {error}")
        st.stop()

    if not movies:
        st.info("No movies are currently available.")
        return

    st.metric("Movies available", len(movies))
    st.dataframe(
        movie_rows(movies),
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Title": st.column_config.TextColumn("Title", width="medium"),
            "Genre": st.column_config.TextColumn("Genre", width="medium"),
            "Duration (min)": st.column_config.NumberColumn(
                "Duration (min)", format="%d"
            ),
            "Release year": st.column_config.TextColumn("Release year", width="small"),
            "Age rating": st.column_config.TextColumn("Age rating", width="small"),
            "Description": st.column_config.TextColumn(
                "Description", width="large"
            ),
        },
    )


if __name__ == "__main__":
    main()
