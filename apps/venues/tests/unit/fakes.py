"""In-memory fakes for venues unit tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.venues.domain.entities import VenueEntity, VenueSpaceEntity
from apps.venues.domain.exceptions import VenueNotFoundError
from apps.venues.domain.repositories import IVenueRepository, IVenueSpaceRepository


def make_venue(organisation_id: uuid.UUID | None = None) -> VenueEntity:
    """Build a VenueEntity with sensible defaults."""
    return VenueEntity(
        id=uuid.uuid4(),
        organisation_id=organisation_id or uuid.uuid4(),
        created_by=uuid.uuid4(),
        name="Test Venue",
        address="123 Test Street",
        city="Kathmandu",
        country="Nepal",
        capacity=500,
        created_at=datetime.now(timezone.utc),
    )


def make_space(venue_id: uuid.UUID | None = None) -> VenueSpaceEntity:
    """Build a VenueSpaceEntity with sensible defaults."""
    return VenueSpaceEntity(
        id=uuid.uuid4(),
        venue_id=venue_id or uuid.uuid4(),
        name="Main Hall",
        capacity=200,
        floor="Ground",
        created_at=datetime.now(timezone.utc),
    )


class FakeVenueRepository(IVenueRepository):
    """In-memory venue store."""

    def __init__(self, venues: list[VenueEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, VenueEntity] = {v.id: v for v in (venues or [])}

    def list_by_org(self, organisation_id: uuid.UUID) -> list[VenueEntity]:
        """Return all non-deleted venues for an organisation."""
        return [v for v in self._store.values() if v.organisation_id == organisation_id and v.deleted_at is None]

    def get_by_id(self, venue_id: uuid.UUID) -> VenueEntity:
        """Raise VenueNotFoundError if not found."""
        v = self._store.get(venue_id)
        if v is None or v.deleted_at is not None:
            raise VenueNotFoundError("Venue not found.")
        return v

    def create(self, venue: VenueEntity) -> None:
        """Store the venue."""
        self._store[venue.id] = venue

    def update(self, venue: VenueEntity) -> None:
        """Update the venue."""
        self._store[venue.id] = venue


class FakeVenueSpaceRepository(IVenueSpaceRepository):
    """In-memory venue space store."""

    def __init__(self) -> None:
        self._store: dict[uuid.UUID, VenueSpaceEntity] = {}

    def list_by_venue(self, venue_id: uuid.UUID) -> list[VenueSpaceEntity]:
        """Return all spaces for a venue."""
        return [s for s in self._store.values() if s.venue_id == venue_id]

    def create(self, space: VenueSpaceEntity) -> None:
        """Store the space."""
        self._store[space.id] = space
