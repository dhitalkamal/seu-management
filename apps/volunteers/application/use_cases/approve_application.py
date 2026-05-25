"""Use case: approve a pending volunteer application."""

from __future__ import annotations

import uuid

from apps.volunteers.domain.entities import VolunteerApplicationEntity
from apps.volunteers.domain.repositories import IParticipationContextClient, IVolunteerApplicationRepository


class ApproveApplicationUseCase:
    """Transition a volunteer application from pending to approved."""

    def __init__(
        self,
        app_repo: IVolunteerApplicationRepository,
        context_client: IParticipationContextClient | None = None,
    ) -> None:
        self._apps = app_repo
        self._context = context_client

    def execute(self, *, application_id: uuid.UUID) -> VolunteerApplicationEntity:
        """
        Set application status to approved.

        @raises ApplicationNotFoundError if the application does not exist
        """
        app = self._apps.get_by_id(application_id)
        app.status = "approved"
        result = self._apps.update(app)
        # ! notify participation service so it can enforce the attendee/volunteer exclusivity rule
        if self._context is not None:
            self._context.set_volunteer(app.event_id, app.user_id)
        return result
