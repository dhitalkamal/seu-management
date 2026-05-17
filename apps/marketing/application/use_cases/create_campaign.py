"""Use case: create a new marketing campaign."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.marketing.domain.entities import CampaignEntity
from apps.marketing.domain.repositories import ICampaignRepository


class CreateCampaignUseCase:
    """Create a new campaign in draft status."""

    def __init__(self, repo: ICampaignRepository) -> None:
        self._repo = repo

    def execute(
        self,
        *,
        created_by: uuid.UUID,
        name: str,
        subject: str,
        body: str,
        segment_id: uuid.UUID | None = None,
    ) -> CampaignEntity:
        """Persist a new campaign and return it."""
        campaign = CampaignEntity(
            id=uuid.uuid4(),
            created_by=created_by,
            name=name,
            subject=subject,
            body=body,
            status="draft",
            segment_id=segment_id,
            created_at=datetime.now(timezone.utc),
        )
        self._repo.create(campaign)
        return campaign
