# CiMaSeat

CiMaSeat is a cinema booking application built with Python. It allows users to
browse movies, view showtimes, check live seat availability, book one or more
seats, consult reservations, and cancel confirmed bookings.

The project was designed as a practical exercise in Python fundamentals,
object-oriented programming, clean architecture, testing, and Streamlit UI
development.

## Live demo

Try the deployed Streamlit application:

**[Open CiMaSeat on Streamlit](https://cimaseats-pro.streamlit.app/)**

## Features

### Booking workflow

- Browse a catalogue of 20 movies and 60 showtimes.
- Select a movie and one of its sessions.
- View the room layout with available, selected, and occupied seats.
- Select one or multiple seats in an interactive seat map.
- Reject a booking if at least one requested seat is unavailable.
- Calculate the total price automatically.
- Generate a unique reservation ID and a confirmation ticket.

### Reservation management

- Search for a reservation by its ID.
- Display the movie, session, room, seats, customer, amount, and status.
- Cancel confirmed reservations without deleting their history.
- Release cancelled seats so they become available again.
- Reject unknown or already cancelled reservations.

### User interfaces

- English command-line interface.
- Modern Streamlit web interface with:
  - fixed navigation sidebar;
  - movie cards;
  - session and seat availability views;
  - interactive booking flow;
  - confirmation popup;
  - dedicated ticket page;
  - consultation and cancellation screens.

## Technology stack

- Python 3.11+
- Streamlit
- JSON file storage
- `unittest` for automated tests
- Dataclasses and service-oriented application logic

## Installation

Clone the repository and move into the project directory:

```bash
git clone <repository-url>
cd CimaSeats
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run the application

### Streamlit interface

```bash
streamlit run app.py
```

The application opens in the browser. The main sidebar provides the following
workflows:

1. View Movies
2. View Sessions
3. View Available Seats
4. Book Tickets
5. View Reservation
6. Cancel Reservation
7. Exit

### Command-line interface

```bash
python main.py
```

The CLI uses the same services, business rules, and JSON data files as the
Streamlit interface.

## Run the tests

From the project root, run:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

The test suite covers:

- movie and session loading;
- movie/session relationships;
- seat-map rendering;
- reservation creation and JSON persistence;
- atomic rejection of invalid or occupied seats;
- reservation cancellation and seat release;
- missing and malformed JSON files.

## Data storage

The application uses JSON files to keep the project simple and transparent:

| File | Purpose |
| --- | --- |
| `data/movies.json` | Movie catalogue |
| `data/sessions.json` | Movie showtimes and session configuration |
| `data/rooms.json` | Room layouts and seat capacity |
| `data/reservations.json` | Confirmed and cancelled reservations |

Missing JSON files are initialized automatically. Malformed files are reported
through controlled application errors instead of crashing the menu.

For local execution, reservations persist between runs. The deployed demo uses
the project JSON files and is intended for demonstration purposes; hosted
filesystem changes may be reset when the application is restarted or rebuilt.

## Architecture

```text
CimaSeats/
├── main.py                         # CLI entry point
├── app.py                          # Streamlit navigation and UI logic
├── pages/
│   ├── home.py                     # Main Streamlit page
│   └── ticket.py                   # Dedicated ticket page
├── models/
│   ├── movie.py                    # Movie domain model
│   ├── session.py                  # Cinema session domain model
│   ├── reservation.py              # Reservation lifecycle model
│   └── room.py                     # Room and seat layout model
├── services/
│   ├── cinema_service.py           # Catalogue, sessions, rooms, seats
│   └── reservation_service.py      # Booking, lookup, cancellation
├── utils/
│   ├── file_handler.py             # Safe JSON reading and writing
│   └── validators.py               # Input validation helpers
├── data/
│   ├── movies.json
│   ├── sessions.json
│   ├── rooms.json
│   └── reservations.json
├── tests/
│   ├── test_cinema.py
│   └── test_reservation.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Design principles

- Domain models are separated from application services.
- Business rules are shared by the CLI and Streamlit interfaces.
- Reservation updates are persisted through a dedicated JSON handler.
- Seat validation is performed before any reservation is saved.
- Cancelled reservations remain available for historical consultation.
- User-facing errors are handled without terminating the application.

## Project status

CiMaSeat is a functional MVP suitable for learning, demonstration, and further
development. A future production version could replace JSON storage with a
database and add authentication, payments, and administration features.
