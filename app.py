"""Main application file for the Movie App."""

import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from data_manager import DataManager
from models import Movie, User, db
from omdb import OMDbAPIError, fetch_movie_details
from validation import is_valid_text, normalize_text

app = Flask(__name__)

# Set up the database
basedir = Path(__file__).resolve().parent
data = basedir / "data"
data.mkdir(exist_ok=True)

# Configure the database URI and secret key
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{data}/movie_db.sqlite"
load_dotenv()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise ValueError("Secret key is not set. Please set it in the .env file.")

# Initialize the database and data manager
db.init_app(app)
data_manager = DataManager()


def get_user_or_redirect(user_id: int) -> User:
    """Return the user, or flash and redirect home
    if they don't exist."""
    user = data_manager.get_user(user_id)

    if user is None:
        flash("User not found.", "error")
        abort(redirect(url_for("index", _anchor="add-user")))
    return user


def get_movie_or_redirect(user_id: int, movie_id: int) -> Movie:
    """Return the move, or flash and redirect home
    if they don't exist."""
    movie = data_manager.get_movie(user_id, movie_id)

    if movie is None:
        flash("Movie not found.", "error")
        abort(redirect(url_for("get_movies", user_id=user_id)))
    return movie


@app.context_processor
def inject_now():
    """Inject the current UTC time into the template context."""
    return {"now": datetime.now(UTC)}


@app.route("/", methods=["GET"])
def index():
    """Render the index page."""
    users = data_manager.get_users()
    return render_template("index.html", users=users)


@app.route("/users/<int:user_id>/movies", methods=["GET"])
def get_movies(user_id: int):
    """Render the movies page."""
    user = get_user_or_redirect(user_id)

    movies = data_manager.get_movies(user_id)
    return render_template("movies.html", user=user, movies=movies)


@app.route("/users/<int:user_id>/movies", methods=["POST"])
def add_movie(user_id: int):
    """Handle a movie submission for a user."""
    user = get_user_or_redirect(user_id)

    query = normalize_text(request.form.get("title", ""))

    if not is_valid_text(query):
        flash("Title must contain at least one letter or number.", "error")
        return redirect(url_for("get_movies", user_id=user_id))

    try:
        movie_details = fetch_movie_details(query)
    except OMDbAPIError:
        flash(
            "The movie service is unavailable. Please try again later.",
            "error",
        )
        return redirect(url_for("get_movies", user_id=user_id))
    if not movie_details:
        flash(f"No movies found for: {query}.", "error")
        return redirect(url_for("get_movies", user_id=user_id))
    movies = data_manager.get_movies(user_id)
    for movie in movies:
        if movie.imdb_id == movie_details["imdb_id"]:
            flash(f"'{movie.title}' is already in your list.", "error")
            return redirect(url_for("get_movies", user_id=user_id))
    movie = Movie(**movie_details, user_id=user_id)
    data_manager.add_movie(movie)
    flash(f"'{movie.title}' added to {user.name}'s movie list.", "success")

    return redirect(url_for("get_movies", user_id=user_id))


@app.route(
    "/users/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"]
)
def update_movie(user_id: int, movie_id: int):
    """Rename one of the user's movies with the title from the form."""
    get_user_or_redirect(user_id)
    movie = get_movie_or_redirect(user_id, movie_id)
    title = normalize_text(request.form.get("title", ""))

    if not is_valid_text(title):
        flash("Title must contain at least one letter or number.", "error")
        return redirect(url_for("get_movies", user_id=user_id))

    old_title = movie.title

    data_manager.update_movie(movie.id, new_title=title)
    flash(f"'{old_title}' successfully updated to '{movie.title}'.", "success")

    return redirect(url_for("get_movies", user_id=user_id))


@app.route(
    "/users/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"]
)
def delete_movie(user_id: int, movie_id: int):
    user = get_user_or_redirect(user_id)
    movie = get_movie_or_redirect(user_id, movie_id)
    title = movie.title
    data_manager.delete_movie(movie.id)
    flash(f"Deleted '{title}' from {user.name}'s list.", "success")
    return redirect(url_for("get_movies", user_id=user_id))


@app.route("/users", methods=["POST"])
def create_user():
    """Create a new user."""
    name = normalize_text(request.form.get("name", ""))

    if not is_valid_text(name):
        flash("User name must contain at least one letter or number.", "error")
        return redirect(url_for("index"))
    data_manager.create_user(name)
    flash(f"User '{name}' added.", "success")
    return redirect(url_for("index"))


@app.errorhandler(500)
def handle_500(error):
    """Roll back the session and show the 500 error page."""
    db.session.rollback()
    return render_template("500.html"), 500


@app.errorhandler(404)
def handle_404(error):
    """Show the 404 page for unknown URLs and missing resources."""
    return render_template("404.html"), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
