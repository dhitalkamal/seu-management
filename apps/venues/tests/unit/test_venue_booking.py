"""Unit tests for venue booking use cases."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from apps.venues.domain.exceptions import VenueConflictError
from apps.venues.tests.unit.fakes import FakeVenueBookingRepository, FakeVenueRepository, make_booking, make_venue


def _now() -> datetime:
    return datetime.now(timezone.utc)


def test_create_booking_success():
    """CreateBookingUseCase persists and returns a confirmed booking."""
    from apps.venues.application.use_cases.create_booking import CreateBookingUseCase

    venue = make_venue()
    repo = FakeVenueRepository([venue])
    booking_repo = FakeVenueBookingRepository()
    now = _now()

    result = CreateBookingUseCase(repo, booking_repo).execute(
        venue_id=venue.id,
        event_id=uuid.uuid4(),
        booked_by=uuid.uuid4(),
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
    )
    assert result.venue_id == venue.id
    assert result.status == "confirmed"


def test_create_booking_conflict_raises():
    """CreateBookingUseCase raises VenueConflictError when time overlaps existing confirmed booking."""
    from apps.venues.application.use_cases.create_booking import CreateBookingUseCase

    venue = make_venue()
    repo = FakeVenueRepository([venue])
    now = _now()
    existing = make_booking(
        venue_id=venue.id,
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
        status="confirmed",
    )
    booking_repo = FakeVenueBookingRepository([existing])

    with pytest.raises(VenueConflictError):
        CreateBookingUseCase(repo, booking_repo).execute(
            venue_id=venue.id,
            event_id=uuid.uuid4(),
            booked_by=uuid.uuid4(),
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=4),
        )


def test_create_booking_no_conflict_with_cancelled():
    """Cancelled bookings do not block new bookings for the same time slot."""
    from apps.venues.application.use_cases.create_booking import CreateBookingUseCase

    venue = make_venue()
    repo = FakeVenueRepository([venue])
    now = _now()
    cancelled = make_booking(
        venue_id=venue.id,
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
        status="cancelled",
    )
    booking_repo = FakeVenueBookingRepository([cancelled])

    result = CreateBookingUseCase(repo, booking_repo).execute(
        venue_id=venue.id,
        event_id=uuid.uuid4(),
        booked_by=uuid.uuid4(),
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
    )
    assert result.status == "confirmed"


def test_create_booking_adjacent_does_not_conflict():
    """A booking starting exactly when another ends is not a conflict."""
    from apps.venues.application.use_cases.create_booking import CreateBookingUseCase

    venue = make_venue()
    repo = FakeVenueRepository([venue])
    now = _now()
    existing = make_booking(
        venue_id=venue.id,
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
        status="confirmed",
    )
    booking_repo = FakeVenueBookingRepository([existing])

    # starts exactly at the end of the existing booking
    result = CreateBookingUseCase(repo, booking_repo).execute(
        venue_id=venue.id,
        event_id=uuid.uuid4(),
        booked_by=uuid.uuid4(),
        start_time=now + timedelta(hours=3),
        end_time=now + timedelta(hours=5),
    )
    assert result.status == "confirmed"


def test_cancel_booking_sets_status():
    """CancelBookingUseCase sets booking status to cancelled."""
    from apps.venues.application.use_cases.cancel_booking import CancelBookingUseCase

    venue = make_venue()
    now = _now()
    booking = make_booking(
        venue_id=venue.id,
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
        status="confirmed",
    )
    booking_repo = FakeVenueBookingRepository([booking])

    CancelBookingUseCase(booking_repo).execute(booking_id=booking.id)
    updated = booking_repo.get_by_id(booking.id)
    assert updated.status == "cancelled"


def test_list_bookings_for_venue():
    """ListVenueBookingsUseCase returns all bookings for a venue."""
    from apps.venues.application.use_cases.list_bookings import ListVenueBookingsUseCase

    venue_id = uuid.uuid4()
    other_venue_id = uuid.uuid4()
    now = _now()

    b1 = make_booking(venue_id=venue_id, start_time=now + timedelta(hours=1), end_time=now + timedelta(hours=2))
    b2 = make_booking(venue_id=venue_id, start_time=now + timedelta(hours=3), end_time=now + timedelta(hours=4))
    other = make_booking(venue_id=other_venue_id, start_time=now + timedelta(hours=1), end_time=now + timedelta(hours=2))

    booking_repo = FakeVenueBookingRepository([b1, b2, other])
    results = ListVenueBookingsUseCase(booking_repo).execute(venue_id=venue_id)
    assert len(results) == 2
    assert all(b.venue_id == venue_id for b in results)
