"""Abstract repository interfaces for the venues module."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from apps.venues.domain.entities import VenueEntity, VenueSpaceEntity


class IVenueRepository(ABC):
    """Persistence interface for venue aggregates."""

    @abstractmethod
    def list_by_org(self, organisation_id: uuid.UUID) -> list[VenueEntity]:
        """Return all non-deleted venues for an organisation."""

    @abstractmethod
    def get_by_id(self, venue_id: uuid.UUID) -> VenueEntity:
        """Return a venue, raising VenueNotFoundError if absent."""

    @abstractmethod
    def create(self, venue: VenueEntity) -> None:
        """Persist a new venue."""

    @abstractmethod
    def update(self, venue: VenueEntity) -> None:
        """Persist changes to an existing venue."""


class IVenueSpaceRepository(ABC):
    """Persistence interface for venue spaces."""

    @abstractmethod
    def list_by_venue(self, venue_id: uuid.UUID) -> list[VenueSpaceEntity]:
        """Return all spaces for a venue."""

    @abstractmethod
    def create(self, space: VenueSpaceEntity) -> None:
        """Persist a new venue space."""
