from collections.abc import Sequence

from sqlalchemy.exc import SQLAlchemyError

from models import Movie, User, db


class DataManager:
    """Manage users and movies in the database."""

    def create_user(self, name: str) -> None:
        new_user = User(name=name)
        try:
            db.session.add(new_user)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def get_users(self) -> Sequence[User]:
        return (
            db.session.execute(db.select(User).order_by(User.name))
            .scalars()
            .all()
        )

    def get_user(self, user_id: int) -> User | None:
        return db.session.get(User, user_id)

    def add_movie(self, movie: Movie) -> None:
        try:
            db.session.add(movie)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def get_movies(self, user_id: int) -> Sequence[Movie]:
        return (
            db.session.execute(
                db.select(Movie)
                .where(Movie.user_id == user_id)
                .order_by(Movie.title)
            )
            .scalars()
            .all()
        )

    def update_movie(self, movie_id: int, new_title: str) -> Movie | None:
        try:
            movie = db.session.get(Movie, movie_id)

            if movie:
                movie.title = new_title
                db.session.commit()
                return movie
            return None
        except SQLAlchemyError:
            db.session.rollback()
            raise

    def delete_movie(self, movie_id: int) -> bool:
        try:
            movie = db.session.get(Movie, movie_id)

            if movie:
                db.session.delete(movie)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError:
            db.session.rollback()
            raise
