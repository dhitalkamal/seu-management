"""Use case: get a single community by id."""

from __future__ import annotations

import uuid

from apps.community.domain.entities import CommunityEntity
from apps.community.domain.repositories import ICommunityRepository


class GetCommunityUseCase:
    """Fetch a single community by primary key."""

    def __init__(self, repo: ICommunityRepository) -> None:
        self._repo = repo

    def execute(self, *, community_id: uuid.UUID) -> CommunityEntity:
        """Return the community, raising CommunityNotFoundError if absent."""
        return self._repo.get_by_id(community_id)
