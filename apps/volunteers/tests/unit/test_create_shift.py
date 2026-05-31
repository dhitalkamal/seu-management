"""Unit tests for CreateShiftUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from apps.volunteers.application.use_cases.create_shift import CreateShiftUseCase
from apps.volunteers.domain.exceptions import RoleNotFoundError
from apps.volunteers.tests.unit.fakes import (
    FakeVolunteerRoleRepository,
    FakeVolunteerShiftRepository,
    make_role,
)


def _future(offset_hours: int = 1) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=offset_hours)


def test_create_shift_persists_entity() -> None:
    """A shift is created and stored for an active role."""
    role = make_role(is_active=True)
    role_repo = FakeVolunteerRoleRepository([role])
    shift_repo = FakeVolunteerShiftRepository()
    use_case = CreateShiftUseCase(role_repo, shift_repo)

    shift = use_case.execute(
        role_id=role.id,
        event_id=role.event_id,
        starts_at=_future(1),
        ends_at=_future(3),
        capacity=10,
        location="Stage A",
        description="Morning shift",
    )

    assert shift.role_id == role.id
    assert shift.capacity == 10
    stored = shift_repo.get_by_id(shift.id)
    assert stored.id == shift.id


def test_create_shift_raises_if_role_not_found() -> None:
    """Non-existent role raises RoleNotFoundError."""
    role_repo = FakeVolunteerRoleRepository()
    shift_repo = FakeVolunteerShiftRepository()
    use_case = CreateShiftUseCase(role_repo, shift_repo)

    with pytest.raises(RoleNotFoundError):
        use_case.execute(
            role_id=uuid.uuid4(),
            event_id=uuid.uuid4(),
            starts_at=_future(1),
            ends_at=_future(3),
            capacity=5,
            location=None,
            description=None,
        )
