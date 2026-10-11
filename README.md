# MoviWeb App

A small Flask web app for keeping lists of favourite movies. Users add a
movie by title, and the app fetches the director, year and poster from
the [OMDb API](https://www.omdbapi.com/).

Built as a school project combining OOP, Flask and SQLAlchemy.

## Features

- Create users and pick one from the home page
- Add movies by title; details are fetched from OMDb
- Rename or delete movies in a user's list
- Each movie can only be in a user's list once (matched by IMDb ID)
- Input validation and flash messages for feedback
- Custom 404 and 500 error pages

## Tech stack

- Python 3.13
- Flask
- Flask-SQLAlchemy with SQLAlchemy 2.0-style models
- SQLite
- requests and python-dotenv
- [uv](https://docs.astral.sh/uv/) for dependency management,
  [Ruff](https://docs.astral.sh/ruff/) and [djLint](https://djlint.com/) for linting
  and formatting

## Setup

### 1. Clone the repository

```bash
git clone git@github.com:thatAxelGuy/MovieWebApp.git
cd MovieWebApp
```

### 2. Install dependencies

With uv (recommended):

```bash
uv sync
```

Or with pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and fill in both values:

```bash
cp .env.example .env
```

| Variable       | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| `OMDB_API_KEY` | Free key from [omdbapi.com](https://www.omdbapi.com/apikey.aspx)            |
| `SECRET_KEY`   | Random string for signing sessions. Generate one with the command below     |

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

The app refuses to start if either value is missing.

### 4. Run the app

```bash
uv run app.py
```

Then open <http://127.0.0.1:5000>. The SQLite database is created
automatically in `data/` on the first run.

## Project structure

```
MovieWebApp/
├── app.py            # Flask app, routes and error handlers
├── data_manager.py   # DataManager class: all database access (CRUD)
├── models.py         # SQLAlchemy models: User and Movie
├── omdb.py           # OMDb API client
├── validation.py     # Helpers for cleaning and validating form input
├── data/             # SQLite database (not committed)
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── index.html    # User list and add-user form
    ├── movies.html   # A user's movies: add, rename, delete
    ├── 404.html
    └── 500.html
```

## Routes

| Method | URL                                         | Description               |
|--------|---------------------------------------------|---------------------------|
| GET    | `/`                                         | List users, add-user form |
| POST   | `/users`                                    | Create a user             |
| GET    | `/users/<user_id>/movies`                   | Show a user's movies      |
| POST   | `/users/<user_id>/movies`                   | Add a movie via OMDb      |
| POST   | `/users/<user_id>/movies/<movie_id>/update` | Rename a movie            |
| POST   | `/users/<user_id>/movies/<movie_id>/delete` | Delete a movie            |

## Development

```bash
uv run ruff check .            # lint Python
uv run ruff format .           # format Python
uv run djlint templates --reformat   # format templates
```

## License

[MIT](LICENSE)
