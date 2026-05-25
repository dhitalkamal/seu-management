"""Use case: record a volunteer's physical arrival at an event."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.volunteers.domain.exceptions import (
    AlreadyCheckedInError,
    InvalidStatusTransitionError,
)
from apps.volunteers.domain.repositories import IVolunteerApplicationRepository


class CheckInVolunteerUseCase:
    """Record check-in for an approved volunteer application."""

    def __init__(self, app_repo: IVolunteerApplicationRepository) -> None:
        self._apps = app_repo

    def execute(self, *, application_id: uuid.UUID) -> None:
        """
        Set check_in_at to now and transition status to confirmed.

        @raises ApplicationNotFoundError if the application does not exist
        @raises InvalidStatusTransitionError if status is not approved
        @raises AlreadyCheckedInError if check_in_at is already set
        """
        app = self._apps.get_by_id(application_id)

        if app.check_in_at is not None:
            raise AlreadyCheckedInError("Volunteer has already checked in.")

        # ! only approved applications can be checked in
        if app.status != "approved":
            raise InvalidStatusTransitionError(f"Cannot check in application with status '{app.status}'.")

        app.check_in_at = datetime.now(timezone.utc)
        app.status = "confirmed"
        self._apps.update(app)
