"""Use case: create a new comment on a community post."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.domain.entities import PostCommentEntity
from apps.community.domain.repositories import ICommunityPostRepository, IPostCommentRepository


class CreateCommentUseCase:
    """Create a comment (or reply) on a post and increment the post's comment_count."""

    def __init__(
        self,
        post_repo: ICommunityPostRepository,
        comment_repo: IPostCommentRepository,
    ) -> None:
        self._posts = post_repo
        self._comments = comment_repo

    def execute(
        self,
        *,
        post_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str,
        parent_id: uuid.UUID | None = None,
    ) -> PostCommentEntity:
        """Validate the post exists, create the comment, and bump comment_count."""
        post = self._posts.get_by_id(post_id)
        now = datetime.now(timezone.utc)
        comment = PostCommentEntity(
            id=uuid.uuid4(),
            post_id=post_id,
            user_id=user_id,
            content=content,
            is_hidden=False,
            parent_id=parent_id,
            created_at=now,
            updated_at=now,
        )
        saved = self._comments.create(comment)
        post.comment_count += 1
        self._posts.update(post)
        return saved
