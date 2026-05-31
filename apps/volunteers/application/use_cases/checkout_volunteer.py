"""Use case: check a volunteer out after their shift ends."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.volunteers.domain.entities import VolunteerApplicationEntity
from apps.volunteers.domain.exceptions import NotCheckedInError
from apps.volunteers.domain.repositories import IVolunteerApplicationRepository


class CheckOutVolunteerUseCase:
    """Stamps check_out_at on a confirmed application that has already checked in."""

    def __init__(self, application_repo: IVolunteerApplicationRepository) -> None:
        self._app_repo = application_repo

    def execute(self, application_id: uuid.UUID) -> VolunteerApplicationEntity:
        """Perform the check-out. Raises if check-in is missing or already checked out."""
        app = self._app_repo.get_by_id(application_id)

        if app.check_in_at is None or app.check_out_at is not None:
            raise NotCheckedInError("Cannot check out: either volunteer was never checked in or is already checked out.")

        from dataclasses import replace

        updated = replace(app, check_out_at=datetime.now(timezone.utc))
        return self._app_repo.update(updated)
