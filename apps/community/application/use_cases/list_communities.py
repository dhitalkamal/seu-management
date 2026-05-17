"""Use case: list all non-deleted communities."""

from __future__ import annotations

from apps.community.domain.entities import CommunityEntity
from apps.community.domain.repositories import ICommunityRepository


class ListCommunitiesUseCase:
    """Return all active communities on the platform."""

    def __init__(self, repo: ICommunityRepository) -> None:
        self._repo = repo

    def execute(self) -> list[CommunityEntity]:
        """Return all non-deleted communities."""
        return self._repo.list_all()
