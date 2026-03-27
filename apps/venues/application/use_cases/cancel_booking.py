"""Use case: cancel a venue booking."""

from __future__ import annotations

import uuid

from apps.venues.domain.repositories import IVenueBookingRepository


class CancelBookingUseCase:
    """Set a booking status to cancelled."""

    def __init__(self, booking_repo: IVenueBookingRepository) -> None:
        self._bookings = booking_repo

    def execute(self, *, booking_id: uuid.UUID) -> None:
        """Cancel the booking by setting status=cancelled.

        @param booking_id - the booking to cancel
        @raises VenueBookingNotFoundError if the booking does not exist
        """
        booking = self._bookings.get_by_id(booking_id)
        booking.status = "cancelled"
        self._bookings.update(booking)
