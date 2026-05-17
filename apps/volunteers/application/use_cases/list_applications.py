"""Use case: list all applications for a volunteer role."""

from __future__ import annotations

import uuid

from apps.volunteers.domain.entities import VolunteerApplicationEntity
from apps.volunteers.domain.repositories import IVolunteerApplicationRepository


class ListApplicationsUseCase:
    """Return all volunteer applications for a given role."""

    def __init__(self, app_repo: IVolunteerApplicationRepository) -> None:
        self._apps = app_repo

    def execute(self, *, role_id: uuid.UUID) -> list[VolunteerApplicationEntity]:
        """Return all applications for the given role."""
        return self._apps.list_by_role(role_id)
