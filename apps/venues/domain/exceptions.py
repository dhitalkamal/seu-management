"""Domain errors raised by venues use cases and never swallowed silently."""

from __future__ import annotations


class VenueNotFoundError(Exception):
    """Raised when a venue cannot be found."""


class VenueAccessDeniedError(Exception):
    """Raised when a user tries to access a venue they do not own."""
