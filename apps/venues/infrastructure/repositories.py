"""Concrete repository implementations backed by the Django ORM."""

from __future__ import annotations

import uuid

from apps.venues.domain.entities import VenueEntity, VenueSpaceEntity
from apps.venues.domain.exceptions import VenueNotFoundError
from apps.venues.domain.repositories import IVenueRepository, IVenueSpaceRepository
from apps.venues.infrastructure.models import Venue, VenueSpace


class DjangoVenueRepository(IVenueRepository):
    """PostgreSQL-backed venue repository."""

    def list_by_org(self, organization_id: uuid.UUID) -> list[VenueEntity]:
        """Return all non-deleted venues for an organization."""
        return [v.to_entity() for v in Venue.objects.filter(organization_id=organization_id, deleted_at__isnull=True)]

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
        )


class DjangoVenueSpaceRepository(IVenueSpaceRepository):
    """PostgreSQL-backed venue space repository."""

    def list_by_venue(self, venue_id: uuid.UUID) -> list[VenueSpaceEntity]:
        """Return all spaces for a venue."""
        return [s.to_entity() for s in VenueSpace.objects.filter(venue_id=venue_id)]

    def create(self, space: VenueSpaceEntity) -> None:
        """Persist a new venue space."""
        VenueSpace.from_entity(space).save()
