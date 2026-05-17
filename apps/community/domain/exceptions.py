"""Domain errors raised by community use cases and never swallowed silently."""

from __future__ import annotations


class CommunityNotFoundError(Exception):
    """Raised when a community cannot be found."""


class CommunityPostNotFoundError(Exception):
    """Raised when a community post cannot be found."""


class AlreadyMemberError(Exception):
    """Raised when a user tries to join a community they already belong to."""


class SlugAlreadyExistsError(Exception):
    """Raised when a slug is already taken."""
