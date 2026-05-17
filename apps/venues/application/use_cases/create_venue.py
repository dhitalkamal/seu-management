"""Use case: create a new venue."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.venues.domain.entities import VenueEntity
from apps.venues.domain.repositories import IVenueRepository


class CreateVenueUseCase:
    """Create and persist a new venue for an organisation."""

    def __init__(self, repo: IVenueRepository) -> None:
        self._repo = repo

    def execute(
        self,
        *,
        organisation_id: uuid.UUID,
        created_by: uuid.UUID,
        name: str,
        address: str,
        city: str,
        country: str,
        capacity: int,
        description: str = "",
        website: str = "",
    ) -> VenueEntity:
        """Persist a new venue and return it."""
        venue = VenueEntity(
            id=uuid.uuid4(),
            organisation_id=organisation_id,
            created_by=created_by,
            name=name,
            address=address,
            city=city,
            country=country,
            capacity=capacity,
            created_at=datetime.now(timezone.utc),
            description=description,
            website=website,
        )
        self._repo.create(venue)
        return venue
