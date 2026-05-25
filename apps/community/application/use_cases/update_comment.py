"""Use case: update comment content within the 15-minute edit window."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from apps.community.domain.entities import PostCommentEntity
from apps.community.domain.exceptions import CommentEditWindowExpiredError
from apps.community.domain.repositories import IPostCommentRepository

_EDIT_WINDOW = timedelta(minutes=15)


class UpdateCommentUseCase:
    """Allow the author to edit a comment within 15 minutes of creation."""

    def __init__(self, comment_repo: IPostCommentRepository) -> None:
        self._comments = comment_repo

    def execute(
        self,
        *,
        comment_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
    ) -> PostCommentEntity:
        """Load, validate the edit window, update content, and persist."""
        comment = self._comments.get_by_id(comment_id)
        now = datetime.now(timezone.utc)
        if now - comment.created_at > _EDIT_WINDOW:
            raise CommentEditWindowExpiredError("The 15-minute edit window has passed.")
        comment.content = content
        comment.updated_at = now
        self._comments.update(comment)
        return comment
