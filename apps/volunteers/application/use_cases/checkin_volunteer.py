"""Use case: check a volunteer in to their confirmed shift."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.volunteers.domain.entities import VolunteerApplicationEntity
from apps.volunteers.domain.exceptions import (
    AlreadyCheckedInError,
    InvalidStatusTransitionError,
)
from apps.volunteers.domain.repositories import IVolunteerApplicationRepository


class CheckInVolunteerUseCase:
    """Transitions an approved application to confirmed and stamps check_in_at."""

    def __init__(self, application_repo: IVolunteerApplicationRepository) -> None:
        self._app_repo = application_repo

    def execute(self, application_id: uuid.UUID) -> VolunteerApplicationEntity:
        """Perform the check-in. Raises if status is wrong or already checked in."""
        app = self._app_repo.get_by_id(application_id)

        if app.check_in_at is not None:
            raise AlreadyCheckedInError("Volunteer is already checked in.")

        if app.status != "approved":
            raise InvalidStatusTransitionError(f"Cannot check in application with status '{app.status}'.")

        from dataclasses import replace

        updated = replace(
            app,
            status="confirmed",
            check_in_at=datetime.now(timezone.utc),
        )
        return self._app_repo.update(updated)
