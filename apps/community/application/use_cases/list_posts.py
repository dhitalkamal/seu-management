"""Use case: list posts for a community."""

from __future__ import annotations

import uuid

from apps.community.domain.entities import CommunityPostEntity
from apps.community.domain.repositories import ICommunityPostRepository, ICommunityRepository


class ListPostsUseCase:
    """Return all published posts for a given community."""

    def __init__(self, repo: ICommunityRepository, post_repo: ICommunityPostRepository) -> None:
        self._repo = repo
        self._post_repo = post_repo

    def execute(self, *, community_id: uuid.UUID) -> list[CommunityPostEntity]:
        """Validate the community exists, then return its posts."""
        self._repo.get_by_id(community_id)
        return self._post_repo.list_by_community(community_id)
