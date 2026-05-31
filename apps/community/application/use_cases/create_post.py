"""Use case: create a post inside a community."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from apps.community.domain.entities import CommunityPostEntity
from apps.community.domain.repositories import ICommunityPostRepository, ICommunityRepository
from apps.community.infrastructure.repositories import DjangoHashtagRepository

# matches #word, capturing the word without the leading #
_HASHTAG_RE = re.compile(r"#(\w+)")


class CreatePostUseCase:
    """Create a new post inside a community, extracting and linking hashtags."""

    def __init__(self, repo: ICommunityRepository, post_repo: ICommunityPostRepository) -> None:
        self._repo = repo
        self._post_repo = post_repo
        self._hashtag_repo = DjangoHashtagRepository()

    def execute(
        self,
        *,
        community_id: uuid.UUID,
        author_id: uuid.UUID,
        content: str,
        post_type: str = "text",
        media_urls: list[str] | None = None,
        author_name: str = "",
    ) -> CommunityPostEntity:
        """Validate the community exists, persist the post, then link any hashtags."""
        self._repo.get_by_id(community_id)

        post = CommunityPostEntity(
            id=uuid.uuid4(),
            community_id=community_id,
            author_id=author_id,
            author_name=author_name,
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

        # extract hashtags and upsert each one
        tag_names = set(_HASHTAG_RE.findall(content))
        for tag_name in tag_names:
            hashtag = self._hashtag_repo.get_or_create(tag_name.lower())
            self._hashtag_repo.increment_post_count(hashtag.name)
            self._hashtag_repo.link_post(post.id, hashtag.id)

        return post
