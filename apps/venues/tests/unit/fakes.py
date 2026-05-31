"""In-memory fakes for venues unit tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from apps.venues.domain.entities import VenueBookingEntity, VenueEntity, VenueSpaceEntity
from apps.venues.domain.exceptions import VenueBookingNotFoundError, VenueNotFoundError
from apps.venues.domain.repositories import IVenueBookingRepository, IVenueRepository, IVenueSpaceRepository


def make_venue(organization_id: uuid.UUID | None = None) -> VenueEntity:
    """Build a VenueEntity with sensible defaults."""
    return VenueEntity(
        id=uuid.uuid4(),
        organization_id=organization_id or uuid.uuid4(),
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

    def list_by_org(self, organization_id: uuid.UUID) -> list[VenueEntity]:
        """Return all non-deleted venues for an organization."""
        return [v for v in self._store.values() if v.organization_id == organization_id and v.deleted_at is None]

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


def make_booking(
    *,
    venue_id: uuid.UUID | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    status: str = "confirmed",
) -> VenueBookingEntity:
    """Build a VenueBookingEntity with sensible defaults."""
    now = datetime.now(timezone.utc)
    return VenueBookingEntity(
        id=uuid.uuid4(),
        venue_id=venue_id or uuid.uuid4(),
        event_id=uuid.uuid4(),
        booked_by=uuid.uuid4(),
        start_time=start_time or now + timedelta(hours=1),
        end_time=end_time or now + timedelta(hours=2),
        status=status,
        created_at=now,
    )


class FakeVenueBookingRepository(IVenueBookingRepository):
    """In-memory venue booking store."""

    def __init__(self, bookings: list[VenueBookingEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, VenueBookingEntity] = {b.id: b for b in (bookings or [])}

    def list_by_venue(self, venue_id: uuid.UUID) -> list[VenueBookingEntity]:
        """Return all bookings for a venue."""
        return [b for b in self._store.values() if b.venue_id == venue_id]

    def get_by_id(self, booking_id: uuid.UUID) -> VenueBookingEntity:
        """Raise VenueBookingNotFoundError if not found."""
        b = self._store.get(booking_id)
        if b is None:
            raise VenueBookingNotFoundError("Booking not found.")
        return b

    def find_conflicts(
        self,
        venue_id: uuid.UUID,
        start_time: object,
        end_time: object,
    ) -> list[VenueBookingEntity]:
        """Return confirmed bookings overlapping the given time range."""
        return [
            b
            for b in self._store.values()
            if b.venue_id == venue_id
            and b.status == "confirmed"
            and b.start_time < end_time  # type: ignore[operator]
            and b.end_time > start_time  # type: ignore[operator]
        ]

    def create(self, booking: VenueBookingEntity) -> VenueBookingEntity:
        """Persist and return the booking."""
        self._store[booking.id] = booking
        return booking

    def update(self, booking: VenueBookingEntity) -> VenueBookingEntity:
        """Update and return the booking."""
        self._store[booking.id] = booking
        return booking
