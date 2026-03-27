"""Use case: create a venue booking with conflict detection."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.venues.domain.entities import VenueBookingEntity
from apps.venues.domain.exceptions import VenueConflictError
from apps.venues.domain.repositories import IVenueBookingRepository, IVenueRepository


class CreateBookingUseCase:
    """Create a venue booking, rejecting if any confirmed booking overlaps."""

    def __init__(self, venue_repo: IVenueRepository, booking_repo: IVenueBookingRepository) -> None:
        self._venues = venue_repo
        self._bookings = booking_repo

    def execute(
        self,
        *,
        venue_id: uuid.UUID,
        event_id: uuid.UUID,
        booked_by: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
    ) -> VenueBookingEntity:
        """Validate venue exists, check for overlapping bookings, and persist.

        @param venue_id - the venue to book
        @param event_id - the event this booking is for
        @param booked_by - user UUID from the JWT
        @param start_time - booking start (timezone-aware)
        @param end_time - booking end, must be strictly after start_time
        @returns the persisted VenueBookingEntity with status=confirmed
        @raises VenueNotFoundError if the venue does not exist
        @raises VenueConflictError if the time range overlaps an existing confirmed booking
        """
        # ! validates venue exists; raises VenueNotFoundError when absent
        self._venues.get_by_id(venue_id)

        conflicts = self._bookings.find_conflicts(venue_id, start_time, end_time)
        if conflicts:
            raise VenueConflictError(f"Venue is already booked during the requested time. Conflicts: {[str(c.id) for c in conflicts]}")

        booking = VenueBookingEntity(
            id=uuid.uuid4(),
            venue_id=venue_id,
            event_id=event_id,
            booked_by=booked_by,
            start_time=start_time,
            end_time=end_time,
            status="confirmed",
            created_at=datetime.now(timezone.utc),
        )
        return self._bookings.create(booking)
