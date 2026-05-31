"""Use case: create a new volunteer role for an event."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.volunteers.domain.entities import VolunteerRoleEntity
from apps.volunteers.domain.repositories import IVolunteerRoleRepository


class CreateVolunteerRoleUseCase:
    """Create a volunteer role with is_active=True."""

    def __init__(self, role_repo: IVolunteerRoleRepository) -> None:
        self._roles = role_repo

    def execute(
        self,
        *,
        event_id: uuid.UUID,
        name: str,
        description: str = "",
        capacity: int = 1,
        organization_id: uuid.UUID | None = None,
    ) -> VolunteerRoleEntity:
        """
        Create and persist a volunteer role.

        @param event_id - the event this role belongs to
        @param name - role title
        @param description - optional description
        @param capacity - maximum number of volunteers, defaults to 1
        @param organization_id - optional owning organization
        @returns the persisted VolunteerRoleEntity
        """
        role = VolunteerRoleEntity(
            id=uuid.uuid4(),
            event_id=event_id,
            name=name,
            description=description,
            capacity=capacity,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            organization_id=organization_id,
        )
        return self._roles.create(role)
