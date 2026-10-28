"""Dedicated Streamlit page for the latest CimaSeats ticket."""

import streamlit as st

from app import render_booking_ticket, render_sidebar


st.set_page_config(
    page_title="CiMaSeat - Your Ticket",
    page_icon="🎟️",
    layout="wide",
)

selected_menu = render_sidebar()
if selected_menu != "Book Tickets":
    st.switch_page("pages/home.py")

st.title("🎟️ Your ticket")
st.caption("Keep this reservation ID for consultation or cancellation.")

ticket = st.session_state.get("last_ticket")
if ticket is None:
    st.warning("No ticket is available in this session.")
    if st.button("Return to booking", type="primary", use_container_width=True):
        st.switch_page("pages/home.py")
else:
    render_booking_ticket(ticket)
    if st.button("Book another movie", use_container_width=True):
        st.session_state.pop("last_ticket", None)
        st.session_state.selected_seats = set()
        st.switch_page("pages/home.py")
