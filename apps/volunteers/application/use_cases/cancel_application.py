"""Use case: cancel a volunteer application."""

from __future__ import annotations

import uuid

from apps.volunteers.domain.entities import VolunteerApplicationEntity
from apps.volunteers.domain.repositories import IVolunteerApplicationRepository


class CancelApplicationUseCase:
    """Set a volunteer application status to cancelled."""

    def __init__(self, app_repo: IVolunteerApplicationRepository) -> None:
        self._apps = app_repo

    def execute(self, *, application_id: uuid.UUID) -> VolunteerApplicationEntity:
        """
        Set application status to cancelled.

        @raises ApplicationNotFoundError if the application does not exist
        """
        app = self._apps.get_by_id(application_id)
        app.status = "cancelled"
        return self._apps.update(app)
