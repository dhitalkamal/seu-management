"""Use case: remove a user's reaction from a community post."""

from __future__ import annotations

import uuid

from apps.community.domain.repositories import ICommunityPostRepository, IPostReactionRepository


class RemoveReactionUseCase:
    """Delete the calling user's reaction and decrement the cached count."""

    def __init__(
        self,
        post_repo: ICommunityPostRepository,
        reaction_repo: IPostReactionRepository,
    ) -> None:
        self._posts = post_repo
        self._reactions = reaction_repo

    def execute(self, *, post_id: uuid.UUID, user_id: uuid.UUID, reaction_type: str) -> None:
        """Remove the reaction; raise ReactionNotFoundError if none exists."""
        post = self._posts.get_by_id(post_id)
        self._reactions.delete(post_id, user_id)
        current = post.reaction_counts.get(reaction_type, 0)
        post.reaction_counts[reaction_type] = max(0, current - 1)
        self._posts.update(post)
