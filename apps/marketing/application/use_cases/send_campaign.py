"""Use case: send a marketing campaign."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.marketing.domain.entities import CampaignEntity
from apps.marketing.domain.exceptions import CampaignAlreadySentError
from apps.marketing.domain.repositories import ICampaignRepository
from apps.marketing.infrastructure.event_publisher import MarketingEventPublisher


class SendCampaignUseCase:
    """Mark a campaign as sent and publish the event for notification-service delivery."""

    def __init__(
        self,
        repo: ICampaignRepository,
        publisher: MarketingEventPublisher | None = None,
    ) -> None:
        self._repo = repo
        self._publisher = publisher

    def execute(
        self,
        *,
        campaign_id: uuid.UUID,
        user_emails: list[str] | None = None,
        org_id: uuid.UUID | None = None,
    ) -> CampaignEntity:
        """
        Validate draft status, set sent_at, persist, publish the RabbitMQ event.

        The publisher fan-outs the email list to notification-service which handles
        per-recipient delivery. Passing an empty or missing user_emails list is
        valid -- the publisher fires with an empty list and notification-service
        skips delivery silently.

        @param campaign_id  - the campaign to send
        @param user_emails  - resolved recipient email list (caller resolves segment)
        @param org_id       - the owning organization's UUID for routing metadata
        @returns the updated CampaignEntity
        @raises CampaignAlreadySentError if status is already sent
        """
        campaign = self._repo.get_by_id(campaign_id)
        # ! campaigns can only be sent once
        if campaign.status == "sent":
            raise CampaignAlreadySentError("This campaign has already been sent.")
        campaign.status = "sent"
        campaign.sent_at = datetime.now(timezone.utc)
        self._repo.update(campaign)

        if self._publisher is not None:
            self._publisher.publish_campaign_sent(
                campaign_id=campaign.id,
                subject=campaign.subject,
                body=campaign.body,
                org_id=org_id,
                segment_id=campaign.segment_id,
                user_emails=user_emails or [],
            )

        return campaign
