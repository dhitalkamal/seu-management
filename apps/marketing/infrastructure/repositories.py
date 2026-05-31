"""Concrete repository implementations backed by the Django ORM."""

from __future__ import annotations

import uuid

from apps.marketing.domain.entities import AudienceSegmentEntity, CampaignEntity
from apps.marketing.domain.exceptions import CampaignNotFoundError
from apps.marketing.domain.repositories import IAudienceSegmentRepository, ICampaignRepository
from apps.marketing.infrastructure.models import AudienceSegment, Campaign


class DjangoCampaignRepository(ICampaignRepository):
    """PostgreSQL-backed campaign repository."""

    def list_all(self) -> list[CampaignEntity]:
        """Return all campaigns."""
        return [c.to_entity() for c in Campaign.objects.all()]

    def get_by_id(self, campaign_id: uuid.UUID) -> CampaignEntity:
        """Raise CampaignNotFoundError if the campaign is not found."""
        try:
            return Campaign.objects.get(id=campaign_id).to_entity()
        except Campaign.DoesNotExist:
            raise CampaignNotFoundError(f"Campaign {campaign_id} not found.")

    def create(self, campaign: CampaignEntity) -> None:
        """Persist a new campaign."""
        Campaign.from_entity(campaign).save()

    def update(self, campaign: CampaignEntity) -> None:
        """Persist changes to an existing campaign."""
        Campaign.objects.filter(id=campaign.id).update(
            status=campaign.status,
            sent_at=campaign.sent_at,
        )


class DjangoAudienceSegmentRepository(IAudienceSegmentRepository):
    """PostgreSQL-backed audience segment repository."""

    def list_all(self) -> list[AudienceSegmentEntity]:
        """Return all segments."""
        return [s.to_entity() for s in AudienceSegment.objects.all()]

    def create(self, segment: AudienceSegmentEntity) -> None:
        """Persist a new segment."""
        AudienceSegment.from_entity(segment).save()
