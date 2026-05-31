"""In-memory fakes for marketing unit tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.marketing.domain.entities import AudienceSegmentEntity, CampaignEntity
from apps.marketing.domain.exceptions import CampaignNotFoundError
from apps.marketing.domain.repositories import IAudienceSegmentRepository, ICampaignRepository
from apps.marketing.infrastructure.event_publisher import MarketingEventPublisher


def make_campaign(status: str = "draft") -> CampaignEntity:
    """Build a CampaignEntity with sensible defaults."""
    return CampaignEntity(
        id=uuid.uuid4(),
        created_by=uuid.uuid4(),
        name="Test Campaign",
        subject="Hello",
        body="<p>Hi</p>",
        status=status,
        segment_id=None,
        created_at=datetime.now(timezone.utc),
    )


def make_segment() -> AudienceSegmentEntity:
    """Build an AudienceSegmentEntity with sensible defaults."""
    return AudienceSegmentEntity(
        id=uuid.uuid4(),
        created_by=uuid.uuid4(),
        name="All Users",
        filters={},
        created_at=datetime.now(timezone.utc),
    )


class FakeCampaignRepository(ICampaignRepository):
    """In-memory campaign store for unit tests."""

    def __init__(self, campaigns: list[CampaignEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, CampaignEntity] = {c.id: c for c in (campaigns or [])}

    def list_all(self) -> list[CampaignEntity]:
        """Return all campaigns."""
        return list(self._store.values())

    def get_by_id(self, campaign_id: uuid.UUID) -> CampaignEntity:
        """Raise CampaignNotFoundError if not found."""
        c = self._store.get(campaign_id)
        if c is None:
            raise CampaignNotFoundError("Not found.")
        return c

    def create(self, campaign: CampaignEntity) -> None:
        """Store the campaign."""
        self._store[campaign.id] = campaign

    def update(self, campaign: CampaignEntity) -> None:
        """Update an existing campaign."""
        self._store[campaign.id] = campaign


class FakeAudienceSegmentRepository(IAudienceSegmentRepository):
    """In-memory segment store for unit tests."""

    def __init__(self) -> None:
        self._store: dict[uuid.UUID, AudienceSegmentEntity] = {}

    def list_all(self) -> list[AudienceSegmentEntity]:
        """Return all segments."""
        return list(self._store.values())

    def create(self, segment: AudienceSegmentEntity) -> None:
        """Store the segment."""
        self._store[segment.id] = segment


class FakeMarketingEventPublisher(MarketingEventPublisher):
    """Records published marketing events for assertion in tests."""

    def __init__(self) -> None:
        self.events: list[dict] = []

    def _publish(self, routing_key: str, payload: dict) -> None:
        """Record without touching RabbitMQ."""
        self.events.append({"routing_key": routing_key, "payload": payload})
