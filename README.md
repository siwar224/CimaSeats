# CimaSeats

CimaSeats is a Python command-line application for browsing movies, selecting
showtimes, checking seat availability, booking tickets, and cancelling
reservations.

The project uses JSON files for data storage and is designed for practicing
Python fundamentals, object-oriented programming, and clean code practices.

The catalogue currently contains 20 films and 60 sessions. Sessions reference
their movie through `movie_id` in `data/sessions.json`. Rooms are defined in
`data/rooms.json`, and sample confirmed reservations are stored in
`data/reservations.json`.

## Run

### Requirements

- Python 3.11 or newer
- No external packages are required; the project uses the Python standard library

### Start the CLI

```bash
python main.py
```

The menu is fully available in English:

1. `View Movies`
2. `View Sessions`
3. `View Available Seats`
4. `Book Tickets`
5. `View Reservation`
6. `Cancel Reservation`
7. `Exit`

Choose `Book Tickets`, enter a movie ID such as `MOV001`, then select one of
the displayed session IDs. The terminal displays the room layout with `[ ]`
for a free seat and `[X]` for an occupied seat. `View Reservation` searches
by reservation ID and displays the movie, session, seats, amount paid, and
status. `Cancel Reservation` also uses the reservation ID; a confirmed
reservation becomes `cancelled` without being removed from the JSON history,
and its seats become available again.

All movies are read from `data/movies.json`. Reservations are read from and
saved to `data/reservations.json`, so they remain available after restarting
the application. Missing JSON files are initialized automatically; malformed
files are reported as data errors without crashing the menu.

## Run the tests

From the project root:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

The test suite covers movie and session loading, seat-map rendering, JSON
persistence, invalid seat rejection, reservation cancellation, and malformed
or missing data files.

## Project structure

```text
CimaSeats/
├── main.py
├── models/
├── services/
├── utils/
├── data/
├── tests/
├── requirements.txt
└── README.md
```
