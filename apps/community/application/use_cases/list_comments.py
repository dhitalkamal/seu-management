"""Use case: list all non-deleted comments for a post."""

from __future__ import annotations

import uuid

from apps.community.domain.entities import PostCommentEntity
from apps.community.domain.repositories import IPostCommentRepository


class ListCommentsUseCase:
    """Return all non-deleted comments for a given post."""

    def __init__(self, comment_repo: IPostCommentRepository) -> None:
        self._comments = comment_repo

    def execute(self, *, post_id: uuid.UUID) -> list[PostCommentEntity]:
        """Delegate to the repository; filtering is handled there."""
        return self._comments.list_by_post(post_id)
