"""Helpers for cleaning and validating form text (names, titles)."""


def normalize_text(text: str) -> str:
    """Trim the text and collapse inner whitespace to single spaces."""
    return " ".join(text.split())


def parse_rating(raw: str) -> float | None:
    """Return the rating as a float from 0 to 10 (one decimal place).

    A blank value means "no rating" and returns None. Raises ValueError
    for anything that isn't a number in range.
    """
    raw = raw.strip()
    if not raw:
        return None

    rating = float(raw.replace(",", "."))
    if not 0 <= rating <= 10:  # also rejects NaN
        raise ValueError("Rating out of range.")
    return round(rating, 1)


def is_valid_text(text: str) -> bool:
    """Return True if the text contains at least one letter or digit."""
    return any(char.isalnum() for char in text)
