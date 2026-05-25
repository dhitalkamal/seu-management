"""Use case: organiser submits a performance rating for a completed volunteer application."""

from __future__ import annotations

import uuid

from apps.volunteers.domain.exceptions import ApplicationNotRatableError, InvalidRatingError
from apps.volunteers.domain.repositories import IVolunteerApplicationRepository

_MIN_RATING = 1
_MAX_RATING = 5


class RateVolunteerUseCase:
    """Submit a 1-5 rating and optional feedback for a checked-out volunteer."""

    def __init__(self, app_repo: IVolunteerApplicationRepository) -> None:
        self._apps = app_repo

    def execute(self, *, application_id: uuid.UUID, rating: int, feedback: str | None) -> None:
        """Validate and persist the rating. Raises if pre-conditions are not met."""
        if not (_MIN_RATING <= rating <= _MAX_RATING):
            raise InvalidRatingError(f"Rating must be between {_MIN_RATING} and {_MAX_RATING}, got {rating}.")

        app = self._apps.get_by_id(application_id)

        # ! only applications where the volunteer has fully completed their shift can be rated
        if app.check_in_at is None or app.check_out_at is None:
            raise ApplicationNotRatableError("Volunteer must have checked in and out before being rated.")

        app.rating = rating
        app.feedback = feedback
        self._apps.update(app)
