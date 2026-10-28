# CimaSeats

CimaSeats is a Python command-line application for browsing movies, selecting
showtimes, checking seat availability, booking tickets, and cancelling
reservations.

The project uses JSON files for data storage and is designed for practicing
Python fundamentals, object-oriented programming, and clean code practices.

The catalogue currently contains 20 films and 60 sessions. Sessions reference
their movie through `movie_id` in `data/sessions.json`.

## Run

```bash
python main.py
```

Choose `Films`, enter a movie ID such as `MOV001`, then select one of the
displayed session IDs. Reservation is not enabled yet.
