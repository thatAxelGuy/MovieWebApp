"""Fetch movie details from the OMDb API."""

import os
from typing import TypedDict

import requests
from dotenv import load_dotenv

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

BASE_URL = "https://www.omdbapi.com/"


class OMDbAPIError(Exception):
    """Custom exception for OMDb API errors."""


def _validate_api_key() -> None:
    """Validate the OMDb API key."""
    if not OMDB_API_KEY:
        raise ValueError(
            "OMDb API key is not set. Please set it in the .env file."
        )


def _clean_data(value: str | None) -> str | None:
    """Clean the data returned from the OMDb API.

    Args:
        value (str | None): The value to clean.

    Returns:
        str | None: The cleaned value,
        or None if the value is None, "N/A", or an empty string.
    """
    if value in (None, "N/A", ""):
        return None
    return value


class MovieDetails(TypedDict):
    """Type dictionary for movie details."""

    title: str
    director: str | None
    year: str | None
    poster_url: str | None


def fetch_movie_details(title: str) -> MovieDetails | None:
    """Fetch movie details from the OMDb API."""
    _validate_api_key()

    try:
        response = requests.get(
            BASE_URL, params={"t": title, "apikey": OMDB_API_KEY}, timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        raise OMDbAPIError(f"OMDb request for {title!r} failed.") from error

    if data.get("Response") == "True":
        details = MovieDetails(
            title=_clean_data(data.get("Title"))
            or title,  # Use the provided title if the API doesn't return one
            director=_clean_data(data.get("Director")),
            year=_clean_data(data.get("Year")),
            poster_url=_clean_data(data.get("Poster")),
        )

        return details
    return None
