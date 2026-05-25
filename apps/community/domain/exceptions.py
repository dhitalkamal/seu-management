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


class ReactionNotFoundError(Exception):
    """Raised when a user tries to remove a reaction that does not exist."""


class CommentNotFoundError(Exception):
    """Raised when a comment cannot be found."""


class CommentEditWindowExpiredError(Exception):
    """Raised when a user tries to edit a comment outside the 15-minute window."""


class CommentReactionNotFoundError(Exception):
    """Raised when a user tries to remove a comment reaction that does not exist."""


class NotMemberError(Exception):
    """Raised when a user tries to leave a community they have not joined."""


class CommunityOwnerCannotLeaveError(Exception):
    """Raised when the community owner tries to leave; ownership transfer is required first."""
