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

```bash
python main.py
```

Choose `Films`, enter a movie ID such as `MOV001`, then select one of the
displayed session IDs. The terminal displays the room layout with `[ ]` for a
free seat and `[X]` for an occupied seat. You can enter a seat ID to check its
availability. Choose `Reservation` to create a reservation and receive a
confirmation ticket in the terminal. The `Reservation` menu option displays
the reservations associated with a customer's email; a new reservation starts
from the `Films` option.

All movies are read from `data/movies.json`. Reservations are read from and
saved to `data/reservations.json`, so they remain available after restarting
the application. Missing JSON files are initialized automatically; malformed
files are reported as data errors without crashing the menu.
