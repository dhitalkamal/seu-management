"""Domain errors raised by venues use cases and never swallowed silently."""

from __future__ import annotations


class VenueNotFoundError(Exception):
    """Raised when a venue cannot be found."""


class VenueAccessDeniedError(Exception):
    """Raised when a user tries to access a venue they do not own."""


class VenueConflictError(Exception):
    """Raised when a booking overlaps an existing confirmed booking for the same venue."""


class VenueBookingNotFoundError(Exception):
    """Raised when a venue booking cannot be found."""
