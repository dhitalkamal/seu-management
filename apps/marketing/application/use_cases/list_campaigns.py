"""Use case: list all campaigns."""

from __future__ import annotations

from apps.marketing.domain.entities import CampaignEntity
from apps.marketing.domain.repositories import ICampaignRepository


class ListCampaignsUseCase:
    """Return all campaigns."""

    def __init__(self, repo: ICampaignRepository) -> None:
        self._repo = repo

    def execute(self) -> list[CampaignEntity]:
        """Return all campaigns."""
        return self._repo.list_all()
