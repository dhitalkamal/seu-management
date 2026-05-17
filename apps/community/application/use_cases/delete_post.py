"""Use case: soft-delete a community post."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.domain.exceptions import CommunityPostNotFoundError
from apps.community.domain.repositories import ICommunityPostRepository


class DeletePostUseCase:
    """Soft-delete a community post by setting deleted_at."""

    def __init__(self, post_repo: ICommunityPostRepository) -> None:
        self._post_repo = post_repo

    def execute(self, *, post_id: uuid.UUID, requester_id: uuid.UUID) -> None:
        """Validate ownership and soft-delete the post."""
        post = self._post_repo.get_by_id(post_id)
        # ! only the author can delete their own post
        if post.author_id != requester_id:
            raise CommunityPostNotFoundError("Post not found.")
        post.status = "removed"
        post.deleted_at = datetime.now(timezone.utc)
        self._post_repo.update(post)
