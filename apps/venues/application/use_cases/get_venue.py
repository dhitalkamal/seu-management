"""Use case: get a single venue by id."""

from __future__ import annotations

import uuid

from apps.venues.domain.entities import VenueEntity
from apps.venues.domain.repositories import IVenueRepository


class GetVenueUseCase:
    """Fetch a single venue by primary key."""

    def __init__(self, repo: IVenueRepository) -> None:
        self._repo = repo

    def execute(self, *, venue_id: uuid.UUID) -> VenueEntity:
        """Return the venue, raising VenueNotFoundError if absent."""
        return self._repo.get_by_id(venue_id)
