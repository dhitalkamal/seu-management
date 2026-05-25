"""Use case: soft-delete a comment and decrement the post's comment_count."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.domain.repositories import ICommunityPostRepository, IPostCommentRepository


class DeleteCommentUseCase:
    """Soft-delete a comment by setting deleted_at and decrement the post's comment_count."""

    def __init__(
        self,
        post_repo: ICommunityPostRepository,
        comment_repo: IPostCommentRepository,
    ) -> None:
        self._posts = post_repo
        self._comments = comment_repo

    def execute(self, *, comment_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Mark the comment deleted and update the parent post count."""
        comment = self._comments.get_by_id(comment_id)
        comment.deleted_at = datetime.now(timezone.utc)
        self._comments.update(comment)
        post = self._posts.get_by_id(comment.post_id)
        post.comment_count = max(0, post.comment_count - 1)
        self._posts.update(post)
