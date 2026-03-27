"""Concrete repository implementations backed by the Django ORM."""

from __future__ import annotations

import uuid

from apps.venues.domain.entities import VenueBookingEntity, VenueEntity, VenueSpaceEntity
from apps.venues.domain.exceptions import VenueBookingNotFoundError, VenueNotFoundError
from apps.venues.domain.repositories import IVenueBookingRepository, IVenueRepository, IVenueSpaceRepository
from apps.venues.infrastructure.models import Venue, VenueBooking, VenueSpace


class DjangoVenueRepository(IVenueRepository):
    """PostgreSQL-backed venue repository."""

    def list_by_org(self, organisation_id: uuid.UUID) -> list[VenueEntity]:
        """Return all non-deleted venues for an organisation."""
        return [v.to_entity() for v in Venue.objects.filter(organisation_id=organisation_id, deleted_at__isnull=True)]

    def get_by_id(self, venue_id: uuid.UUID) -> VenueEntity:
        """Raise VenueNotFoundError if the venue is not found."""
        try:
            return Venue.objects.get(id=venue_id, deleted_at__isnull=True).to_entity()
        except Venue.DoesNotExist:
            raise VenueNotFoundError(f"Venue {venue_id} not found.")

    def create(self, venue: VenueEntity) -> None:
        """Persist a new venue."""
        Venue.from_entity(venue).save()

    def update(self, venue: VenueEntity) -> None:
        """Persist changes to an existing venue."""
        Venue.objects.filter(id=venue.id).update(
            name=venue.name,
            address=venue.address,
            city=venue.city,
            country=venue.country,
            capacity=venue.capacity,
            description=venue.description,
            website=venue.website,
            deleted_at=venue.deleted_at,
            latitude=venue.latitude,
            longitude=venue.longitude,
        )


class DjangoVenueSpaceRepository(IVenueSpaceRepository):
    """PostgreSQL-backed venue space repository."""

    def list_by_venue(self, venue_id: uuid.UUID) -> list[VenueSpaceEntity]:
        """Return all spaces for a venue."""
        return [s.to_entity() for s in VenueSpace.objects.filter(venue_id=venue_id)]

    def create(self, space: VenueSpaceEntity) -> None:
        """Persist a new venue space."""
        VenueSpace.from_entity(space).save()


class DjangoVenueBookingRepository(IVenueBookingRepository):
    """PostgreSQL-backed venue booking repository."""

    def list_by_venue(self, venue_id: uuid.UUID) -> list[VenueBookingEntity]:
        """Return all bookings for a venue ordered by start_time."""
        return [b.to_entity() for b in VenueBooking.objects.filter(venue_id=venue_id).order_by("start_time")]

    def get_by_id(self, booking_id: uuid.UUID) -> VenueBookingEntity:
        """Raise VenueBookingNotFoundError if not found."""
        try:
            return VenueBooking.objects.get(id=booking_id).to_entity()
        except VenueBooking.DoesNotExist:
            raise VenueBookingNotFoundError(f"Booking {booking_id} not found.")

    def find_conflicts(
        self,
        venue_id: uuid.UUID,
        start_time: object,
        end_time: object,
    ) -> list[VenueBookingEntity]:
        """Return confirmed bookings that overlap start_time..end_time.

        Overlap: existing.start < new.end AND existing.end > new.start
        """
        qs = VenueBooking.objects.filter(
            venue_id=venue_id,
            status="confirmed",
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        return [b.to_entity() for b in qs]

    def create(self, booking: VenueBookingEntity) -> VenueBookingEntity:
        """Persist a new booking and return it."""
        obj = VenueBooking(
            id=booking.id,
            venue_id=booking.venue_id,
            event_id=booking.event_id,
            booked_by=booking.booked_by,
            start_time=booking.start_time,
            end_time=booking.end_time,
            status=booking.status,
        )
        obj.save()
        return obj.to_entity()

    def update(self, booking: VenueBookingEntity) -> VenueBookingEntity:
        """Persist changes to an existing booking and return it."""
        VenueBooking.objects.filter(id=booking.id).update(status=booking.status)
        return booking
