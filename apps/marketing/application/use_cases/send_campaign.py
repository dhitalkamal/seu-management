"""Use case: send a marketing campaign."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.marketing.domain.entities import CampaignEntity
from apps.marketing.domain.exceptions import CampaignAlreadySentError
from apps.marketing.domain.repositories import ICampaignRepository


class SendCampaignUseCase:
    """Mark a campaign as sent."""

    def __init__(self, repo: ICampaignRepository) -> None:
        self._repo = repo

    def execute(self, *, campaign_id: uuid.UUID) -> CampaignEntity:
        """Validate draft status, set sent_at, persist, and return."""
        campaign = self._repo.get_by_id(campaign_id)
        # ! campaigns can only be sent once
        if campaign.status == "sent":
            raise CampaignAlreadySentError("This campaign has already been sent.")
        campaign.status = "sent"
        campaign.sent_at = datetime.now(timezone.utc)
        self._repo.update(campaign)
        return campaign
