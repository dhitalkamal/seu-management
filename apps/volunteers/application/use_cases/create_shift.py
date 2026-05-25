"""Use case: create a shift template for a volunteer role."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.volunteers.domain.entities import VolunteerShiftEntity
from apps.volunteers.domain.repositories import IVolunteerRoleRepository, IVolunteerShiftRepository


class CreateShiftUseCase:
    """Creates a shift slot attached to an existing active role."""

    def __init__(
        self,
        role_repo: IVolunteerRoleRepository,
        shift_repo: IVolunteerShiftRepository,
    ) -> None:
        self._role_repo = role_repo
        self._shift_repo = shift_repo

    def execute(
        self,
        role_id: uuid.UUID,
        event_id: uuid.UUID,
        starts_at: datetime,
        ends_at: datetime,
        capacity: int,
        location: str | None,
        description: str | None,
    ) -> VolunteerShiftEntity:
        """Validate the role exists, then persist the shift."""
        self._role_repo.get_by_id(role_id)

        shift = VolunteerShiftEntity(
            id=uuid.uuid4(),
            role_id=role_id,
            event_id=event_id,
            starts_at=starts_at,
            ends_at=ends_at,
            capacity=capacity,
            created_at=datetime.now(timezone.utc),
            location=location,
            description=description,
        )
        return self._shift_repo.create(shift)
