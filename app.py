from pathlib import Path

from flask import Flask

from models import db

app = Flask(__name__)

basedir = Path(__file__).resolve().parent
data = basedir / "data"
data.mkdir(exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{data}/movie_db.sqlite"

db.init_app(app)


@app.route("/", methods=["GET"])
def hello_world():
    return "Welcome to the Movie App"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)
