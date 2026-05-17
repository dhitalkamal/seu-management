"""Use case: soft-delete a venue."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.venues.domain.repositories import IVenueRepository


class DeleteVenueUseCase:
    """Soft-delete a venue by setting deleted_at."""

    def __init__(self, repo: IVenueRepository) -> None:
        self._repo = repo

    def execute(self, *, venue_id: uuid.UUID) -> None:
        """Set deleted_at on the venue."""
        venue = self._repo.get_by_id(venue_id)
        venue.deleted_at = datetime.now(timezone.utc)
        self._repo.update(venue)
