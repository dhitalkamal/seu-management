"""Use case: list spaces for a venue."""

from __future__ import annotations

import uuid

from apps.venues.domain.entities import VenueSpaceEntity
from apps.venues.domain.repositories import IVenueRepository, IVenueSpaceRepository


class ListVenueSpacesUseCase:
    """Return all spaces belonging to a venue."""

    def __init__(self, repo: IVenueRepository, space_repo: IVenueSpaceRepository) -> None:
        self._repo = repo
        self._spaces = space_repo

    def execute(self, *, venue_id: uuid.UUID) -> list[VenueSpaceEntity]:
        """Validate the venue exists, then return its spaces."""
        self._repo.get_by_id(venue_id)
        return self._spaces.list_by_venue(venue_id)
