"""Use case: list all shifts for a given volunteer role."""

from __future__ import annotations

import uuid

from apps.volunteers.domain.entities import VolunteerShiftEntity
from apps.volunteers.domain.repositories import IVolunteerShiftRepository


class ListShiftsForRoleUseCase:
    """Returns all shifts belonging to the specified role."""

    def __init__(self, shift_repo: IVolunteerShiftRepository) -> None:
        self._shift_repo = shift_repo

    def execute(self, role_id: uuid.UUID) -> list[VolunteerShiftEntity]:
        """Fetch and return the list."""
        return self._shift_repo.list_by_role(role_id)
