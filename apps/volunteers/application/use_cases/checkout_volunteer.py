"""Use case: record a volunteer's departure and calculate hours worked."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.volunteers.domain.exceptions import (
    InvalidStatusTransitionError,
    NotCheckedInError,
)
from apps.volunteers.domain.repositories import IVolunteerApplicationRepository


class CheckOutVolunteerUseCase:
    """Record check-out for a confirmed (checked-in) volunteer application."""

    def __init__(self, app_repo: IVolunteerApplicationRepository) -> None:
        self._apps = app_repo

    def execute(self, *, application_id: uuid.UUID) -> None:
        """
        Set check_out_at to now.

        @raises ApplicationNotFoundError if the application does not exist
        @raises NotCheckedInError if check_in_at is not set
        @raises InvalidStatusTransitionError if already checked out
        """
        app = self._apps.get_by_id(application_id)

        if app.check_in_at is None:
            raise NotCheckedInError("Volunteer has not yet checked in.")

        # ! prevent double check-out
        if app.check_out_at is not None:
            raise InvalidStatusTransitionError("Volunteer has already checked out.")

        app.check_out_at = datetime.now(timezone.utc)
        self._apps.update(app)
