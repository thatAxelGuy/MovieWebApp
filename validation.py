"""Helpers for cleaning and validating form text (names, titles)."""


def normalize_text(text: str) -> str:
    """Trim the text and collapse inner whitespace to single spaces."""
    return " ".join(text.split())


def is_valid_text(text: str) -> bool:
    """Return True if the text contains at least one letter or digit."""
    return any(char.isalnum() for char in text)
