"""Use case: fetch a single volunteer shift by ID."""

from __future__ import annotations

import uuid

from apps.volunteers.domain.entities import VolunteerShiftEntity
from apps.volunteers.domain.repositories import IVolunteerShiftRepository


class GetShiftUseCase:
    """Returns a single shift by its ID."""

    def __init__(self, shift_repo: IVolunteerShiftRepository) -> None:
        self._shift_repo = shift_repo

    def execute(self, shift_id: uuid.UUID) -> VolunteerShiftEntity:
        """Fetch and return. Raises ShiftNotFoundError if absent."""
        return self._shift_repo.get_by_id(shift_id)
