"""Use case: list bookings for a venue."""

from __future__ import annotations

import uuid

from apps.venues.domain.entities import VenueBookingEntity
from apps.venues.domain.repositories import IVenueBookingRepository


class ListVenueBookingsUseCase:
    """Return all bookings for a given venue."""

    def __init__(self, booking_repo: IVenueBookingRepository) -> None:
        self._bookings = booking_repo

    def execute(self, *, venue_id: uuid.UUID) -> list[VenueBookingEntity]:
        """Return all bookings for the venue ordered by start_time.

        @param venue_id - the venue to list bookings for
        @returns list of VenueBookingEntity sorted by start_time ascending
        """
        bookings = self._bookings.list_by_venue(venue_id)
        return sorted(bookings, key=lambda b: b.start_time)
