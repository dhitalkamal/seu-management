"""Use case: list all reactions for a community post."""

from __future__ import annotations

import uuid

from apps.community.domain.entities import PostReactionEntity
from apps.community.domain.repositories import IPostReactionRepository


class ListReactionsUseCase:
    """Return every reaction recorded against a post."""

    def __init__(self, reaction_repo: IPostReactionRepository) -> None:
        self._reactions = reaction_repo

    def execute(self, *, post_id: uuid.UUID) -> list[PostReactionEntity]:
        """Delegate to the repository and return the raw list."""
        return self._reactions.list_by_post(post_id)
