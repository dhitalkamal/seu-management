"""Use case: rate a volunteer after their shift is complete."""

from __future__ import annotations

import uuid
from dataclasses import replace
from datetime import datetime, timezone

from apps.volunteers.domain.entities import VolunteerApplicationEntity
from apps.volunteers.domain.exceptions import ApplicationNotRatableError, InvalidRatingError
from apps.volunteers.domain.repositories import (
    IVolunteerApplicationRepository,
    IVolunteerProfileRepository,
)


class RateVolunteerUseCase:
    """Saves a 1-5 rating on the application and updates the volunteer's profile average."""

    def __init__(
        self,
        application_repo: IVolunteerApplicationRepository,
        profile_repo: IVolunteerProfileRepository,
    ) -> None:
        self._app_repo = application_repo
        self._profile_repo = profile_repo

    def execute(self, application_id: uuid.UUID, rating: int, feedback: str | None) -> VolunteerApplicationEntity:
        """Apply the rating. Raises if attendance is incomplete or rating is out of range."""
        app = self._app_repo.get_by_id(application_id)

        if app.check_in_at is None or app.check_out_at is None:
            raise ApplicationNotRatableError("Application cannot be rated until check-in and check-out are both recorded.")

        if rating < 1 or rating > 5:
            raise InvalidRatingError(f"Rating must be between 1 and 5, got {rating}.")

        updated_app = replace(app, rating=rating, feedback=feedback)
        self._app_repo.update(updated_app)

        profile = self._profile_repo.get_or_create(app.user_id)
        prev_sum = (profile.average_rating or 0.0) * profile.total_ratings
        new_count = profile.total_ratings + 1
        new_avg = (prev_sum + rating) / new_count
        updated_profile = replace(
            profile,
            average_rating=new_avg,
            total_ratings=new_count,
            updated_at=datetime.now(timezone.utc),
        )
        self._profile_repo.update(updated_profile)

        return updated_app
