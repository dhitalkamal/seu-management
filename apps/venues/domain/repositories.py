"""Abstract repository interfaces for the venues module."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from apps.venues.domain.entities import VenueBookingEntity, VenueEntity, VenueSpaceEntity


class IVenueRepository(ABC):
    """Persistence interface for venue aggregates."""

    @abstractmethod
    def list_by_org(self, organization_id: uuid.UUID) -> list[VenueEntity]:
        """Return all non-deleted venues for an organization."""

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


class IVenueBookingRepository(ABC):
    """Persistence interface for venue bookings."""

    @abstractmethod
    def list_by_venue(self, venue_id: uuid.UUID) -> list[VenueBookingEntity]:
        """Return all bookings for a venue."""

    @abstractmethod
    def get_by_id(self, booking_id: uuid.UUID) -> VenueBookingEntity:
        """Return a booking, raising VenueBookingNotFoundError if absent."""

    @abstractmethod
    def find_conflicts(
        self,
        venue_id: uuid.UUID,
        start_time: object,
        end_time: object,
    ) -> list[VenueBookingEntity]:
        """Return confirmed bookings that overlap the given time range.

        Overlap condition: existing.start < new.end AND existing.end > new.start
        Adjacent bookings (exact touching endpoints) are NOT conflicts.
        """

    @abstractmethod
    def create(self, booking: VenueBookingEntity) -> VenueBookingEntity:
        """Persist a new booking and return it."""

    @abstractmethod
    def update(self, booking: VenueBookingEntity) -> VenueBookingEntity:
        """Persist changes to an existing booking and return it."""
