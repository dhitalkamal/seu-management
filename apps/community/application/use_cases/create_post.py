"""Use case: create a post inside a community."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.domain.entities import CommunityPostEntity
from apps.community.domain.repositories import ICommunityPostRepository, ICommunityRepository


class CreatePostUseCase:
    """Create a new post inside a community."""

    def __init__(self, repo: ICommunityRepository, post_repo: ICommunityPostRepository) -> None:
        self._repo = repo
        self._post_repo = post_repo

    def execute(
        self,
        *,
        community_id: uuid.UUID,
        author_id: uuid.UUID,
        content: str,
        post_type: str = "text",
        media_urls: list[str] | None = None,
    ) -> CommunityPostEntity:
        """Validate the community exists, then persist the post."""
        self._repo.get_by_id(community_id)

        post = CommunityPostEntity(
            id=uuid.uuid4(),
            community_id=community_id,
            author_id=author_id,
            content=content,
            post_type=post_type,
            status="published",
            like_count=0,
            comment_count=0,
            report_count=0,
            is_pinned=False,
            created_at=datetime.now(timezone.utc),
            media_urls=media_urls or [],
        )
        self._post_repo.create(post)
        return post
