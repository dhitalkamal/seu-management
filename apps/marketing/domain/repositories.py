"""Abstract repository interfaces for the marketing module."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from apps.marketing.domain.entities import AudienceSegmentEntity, CampaignEntity


class ICampaignRepository(ABC):
    """Persistence interface for campaign aggregates."""

    @abstractmethod
    def list_all(self) -> list[CampaignEntity]:
        """Return all campaigns."""

    @abstractmethod
    def get_by_id(self, campaign_id: uuid.UUID) -> CampaignEntity:
        """Return a campaign by id, raising CampaignNotFoundError if absent."""

    @abstractmethod
    def create(self, campaign: CampaignEntity) -> None:
        """Persist a new campaign."""

    @abstractmethod
    def update(self, campaign: CampaignEntity) -> None:
        """Persist changes to an existing campaign."""


class IAudienceSegmentRepository(ABC):
    """Persistence interface for audience segments."""

    @abstractmethod
    def list_all(self) -> list[AudienceSegmentEntity]:
        """Return all segments."""

    @abstractmethod
    def create(self, segment: AudienceSegmentEntity) -> None:
        """Persist a new segment."""
