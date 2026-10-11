"""Main application file for the Movie App."""

import os
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template

from models import db

app = Flask(__name__)

basedir = Path(__file__).resolve().parent
data = basedir / "data"
data.mkdir(exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{data}/movie_db.sqlite"
load_dotenv()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise ValueError("Secret key is not set. Please set it in the .env file.")

db.init_app(app)


@app.context_processor
def inject_now():
    return {"now": datetime.now(UTC)}


@app.route("/", methods=["GET"])
def index():
    return render_template("base.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
