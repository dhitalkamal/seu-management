"""Use case: add a space to a venue."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.venues.domain.entities import VenueSpaceEntity
from apps.venues.domain.repositories import IVenueRepository, IVenueSpaceRepository


class AddVenueSpaceUseCase:
    """Add a named sub-space to an existing venue."""

    def __init__(self, repo: IVenueRepository, space_repo: IVenueSpaceRepository) -> None:
        self._repo = repo
        self._spaces = space_repo

    def execute(self, *, venue_id: uuid.UUID, name: str, capacity: int, floor: str = "") -> VenueSpaceEntity:
        """Validate the venue exists, then persist the new space."""
        self._repo.get_by_id(venue_id)
        space = VenueSpaceEntity(
            id=uuid.uuid4(),
            venue_id=venue_id,
            name=name,
            capacity=capacity,
            floor=floor,
            created_at=datetime.now(timezone.utc),
        )
        self._spaces.create(space)
        return space
