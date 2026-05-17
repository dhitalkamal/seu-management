"""Use case: apply to a volunteer role."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.volunteers.domain.entities import VolunteerApplicationEntity
from apps.volunteers.domain.exceptions import (
    AlreadyAppliedError,
    RoleAtCapacityError,
    RoleNotFoundError,
)
from apps.volunteers.domain.repositories import (
    IVolunteerApplicationRepository,
    IVolunteerRoleRepository,
)


class ApplyToVolunteerRoleUseCase:
    """Submit a pending application to a volunteer role."""

    def __init__(
        self,
        role_repo: IVolunteerRoleRepository,
        app_repo: IVolunteerApplicationRepository,
    ) -> None:
        self._roles = role_repo
        self._apps = app_repo

    def execute(
        self,
        *,
        role_id: uuid.UUID,
        user_id: uuid.UUID,
        event_id: uuid.UUID,
    ) -> VolunteerApplicationEntity:
        """
        Validate capacity and uniqueness, then create a pending application.

        @param role_id - the volunteer role to apply for
        @param user_id - UUID from JWT
        @param event_id - the event this application is for
        @returns the created VolunteerApplicationEntity with status=pending
        @raises RoleNotFoundError if the role is missing or inactive
        @raises AlreadyAppliedError if a non-cancelled application exists
        @raises RoleAtCapacityError if approved count has reached capacity
        """
        role = self._roles.get_by_id(role_id)

        if not role.is_active:
            raise RoleNotFoundError("This volunteer role is not accepting applications.")

        if self._apps.has_active(role_id, user_id):
            raise AlreadyAppliedError("You have already applied to this role.")

        if self._roles.count_approved(role_id) >= role.capacity:
            raise RoleAtCapacityError("This volunteer role is at capacity.")

        now = datetime.now(timezone.utc)
        application = VolunteerApplicationEntity(
            id=uuid.uuid4(),
            volunteer_role_id=role_id,
            user_id=user_id,
            event_id=event_id,
            status="pending",
            created_at=now,
            updated_at=now,
        )
        return self._apps.create(application)
