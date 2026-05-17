"""Use case: update an existing venue."""

from __future__ import annotations

import uuid

from apps.venues.domain.entities import VenueEntity
from apps.venues.domain.repositories import IVenueRepository


class UpdateVenueUseCase:
    """Apply partial updates to a venue."""

    def __init__(self, repo: IVenueRepository) -> None:
        self._repo = repo

    def execute(
        self,
        *,
        venue_id: uuid.UUID,
        name: str | None = None,
        address: str | None = None,
        city: str | None = None,
        country: str | None = None,
        capacity: int | None = None,
        description: str | None = None,
        website: str | None = None,
    ) -> VenueEntity:
        """Patch the venue with any provided fields and persist."""
        venue = self._repo.get_by_id(venue_id)
        if name is not None:
            venue.name = name
        if address is not None:
            venue.address = address
        if city is not None:
            venue.city = city
        if country is not None:
            venue.country = country
        if capacity is not None:
            venue.capacity = capacity
        if description is not None:
            venue.description = description
        if website is not None:
            venue.website = website
        self._repo.update(venue)
        return venue
