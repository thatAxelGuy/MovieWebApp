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


def _poster_is_reachable(url: str) -> bool:
    """Check that a poster URL actually serves an image.

    Network errors count as reachable so a temporary hiccup
    doesn't drop a poster; the template falls back if it fails to load.
    """
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
    except requests.RequestException:
        return True
    content_type = response.headers.get("Content-Type", "")
    return response.ok and content_type.startswith("image/")


class MovieDetails(TypedDict):
    """Type dictionary for movie details."""

    title: str
    director: str | None
    year: str | None
    poster_url: str | None
    imdb_id: str


class SearchResult(TypedDict):
    """Type dictionary for movie search results."""

    title: str
    year: str | None
    poster_url: str | None
    imdb_id: str


def _get(params: dict) -> dict:
    """Return response data for given params."""
    _validate_api_key()

    try:
        response = requests.get(
            BASE_URL,
            params={**params, "apikey": OMDB_API_KEY},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        raise OMDbAPIError("OMDb request failed.") from error
    return data


def search_movies(query: str) -> list[SearchResult]:
    """Search movies on OMDb based on user query."""
    params = {"s": query, "type": "movie"}
    data = _get(params)

    if data.get("Response") != "True":
        return []

    movie_results: list[SearchResult] = []
    for item in data.get("Search") or []:
        imdb = _clean_data(item.get("imdbID"))
        title = _clean_data(item.get("Title"))

        if not imdb or not title:
            continue

        search_result: SearchResult = {
            "title": title,
            "year": _clean_data(item.get("Year")),
            "poster_url": _clean_data(item.get("Poster")),
            "imdb_id": imdb,
        }
        movie_results.append(search_result)

    return movie_results


def fetch_movie_by_id(imdb_id: str) -> MovieDetails | None:
    """Fetch a movie by its IMDb ID."""
    params = {"i": imdb_id, "type": "movie"}
    data = _get(params)

    if data.get("Response") == "True":
        imdb = _clean_data(data.get("imdbID"))
        title = _clean_data(data.get("Title"))

        if not imdb or not title:
            raise OMDbAPIError("OMDb returned a movie without imdb or title")

        poster_url = _clean_data(data.get("Poster"))
        if poster_url and not _poster_is_reachable(poster_url):
            poster_url = None

        details = MovieDetails(
            title=title,
            director=_clean_data(data.get("Director")),
            year=_clean_data(data.get("Year")),
            poster_url=poster_url,
            imdb_id=imdb,
        )
        return details

    return None
