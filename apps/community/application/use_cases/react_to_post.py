"""Use case: react to a community post (upsert one reaction per user)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.domain.entities import PostReactionEntity
from apps.community.domain.repositories import ICommunityPostRepository, IPostReactionRepository

_VALID_TYPES = {"like", "love", "fire", "laugh", "sad", "angry"}


class ReactToPostUseCase:
    """Upsert a user's reaction on a post, replacing any prior reaction."""

    def __init__(
        self,
        post_repo: ICommunityPostRepository,
        reaction_repo: IPostReactionRepository,
    ) -> None:
        self._posts = post_repo
        self._reactions = reaction_repo

    def execute(
        self,
        *,
        post_id: uuid.UUID,
        user_id: uuid.UUID,
        reaction_type: str,
    ) -> PostReactionEntity:
        """Validate, upsert reaction, and update cached counts on the post."""
        post = self._posts.get_by_id(post_id)

        existing = self._reactions.get_by_post_and_user(post_id, user_id)
        if existing is not None:
            old_count = post.reaction_counts.get(existing.reaction_type, 0)
            post.reaction_counts[existing.reaction_type] = max(0, old_count - 1)

        reaction = PostReactionEntity(
            id=uuid.uuid4(),
            post_id=post_id,
            user_id=user_id,
            reaction_type=reaction_type,
            created_at=datetime.now(timezone.utc),
        )
        saved = self._reactions.upsert(reaction)

        post.reaction_counts[reaction_type] = post.reaction_counts.get(reaction_type, 0) + 1
        self._posts.update(post)

        return saved
