"""Database models for the app."""

from typing import TYPE_CHECKING

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base shared by all models of the app."""


db = SQLAlchemy(model_class=Base)

if TYPE_CHECKING:
    Model = Base
else:
    Model = db.Model


class User(Model):
    """A person registered in the app linked with favorite movies."""

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    movies: Mapped[list["Movie"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.name}>"


class Movie(Model):
    """A movie on a user's favorites list, with details from OMDb."""

    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    director: Mapped[str | None] = mapped_column(String(255))
    year: Mapped[str | None] = mapped_column(String(10))
    poster_url: Mapped[str | None] = mapped_column(String(500))

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="movies")

    def __repr__(self) -> str:
        return f"<Movie {self.title} ({self.year})>"
