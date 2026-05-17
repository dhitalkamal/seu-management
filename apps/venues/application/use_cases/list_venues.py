"""Use case: list all venues for an organisation."""

from __future__ import annotations

import uuid

from apps.venues.domain.entities import VenueEntity
from apps.venues.domain.repositories import IVenueRepository


class ListVenuesUseCase:
    """Return all non-deleted venues owned by an organisation."""

    def __init__(self, repo: IVenueRepository) -> None:
        self._repo = repo

    def execute(self, *, organisation_id: uuid.UUID) -> list[VenueEntity]:
        """Return venues belonging to the given organisation."""
        return self._repo.list_by_org(organisation_id)
