"""Use case: approve a pending volunteer application."""

from __future__ import annotations

import uuid

from apps.volunteers.domain.entities import VolunteerApplicationEntity
from apps.volunteers.domain.repositories import IEventPublisher, IVolunteerApplicationRepository


class ApproveApplicationUseCase:
    """Transition a volunteer application from pending to approved."""

    def __init__(
        self,
        app_repo: IVolunteerApplicationRepository,
        publisher: IEventPublisher | None = None,
    ) -> None:
        self._apps = app_repo
        # publisher is optional -- omitting it disables event emission (useful in tests)
        self._publisher = publisher

    def execute(self, *, application_id: uuid.UUID) -> VolunteerApplicationEntity:
        """
        Set application status to approved and publish volunteer.application.approved.

        @raises ApplicationNotFoundError if the application does not exist
        """
        app = self._apps.get_by_id(application_id)
        app.status = "approved"
        result = self._apps.update(app)

        # notify participation-service so it can set the volunteer context
        if self._publisher is not None:
            self._publisher.publish(
                "volunteer.application.approved",
                {
                    "user_id": str(result.user_id),
                    "event_id": str(result.event_id),
                    "application_id": str(result.id),
                },
            )

        return result
