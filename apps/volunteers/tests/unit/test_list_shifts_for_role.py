"""Unit tests for ListShiftsForRoleUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from apps.volunteers.application.use_cases.list_shifts_for_role import ListShiftsForRoleUseCase
from apps.volunteers.tests.unit.fakes import FakeVolunteerShiftRepository, make_shift


def _future(offset_hours: int = 1) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=offset_hours)


def test_list_returns_shifts_for_role() -> None:
    """Only shifts belonging to the given role are returned."""
    role_id = uuid.uuid4()
    other_role_id = uuid.uuid4()
    s1 = make_shift(role_id=role_id)
    s2 = make_shift(role_id=role_id)
    s3 = make_shift(role_id=other_role_id)
    repo = FakeVolunteerShiftRepository([s1, s2, s3])
    use_case = ListShiftsForRoleUseCase(repo)

    result = use_case.execute(role_id)

    ids = {s.id for s in result}
    assert s1.id in ids
    assert s2.id in ids
    assert s3.id not in ids


def test_list_returns_empty_when_none() -> None:
    """Empty list returned when role has no shifts."""
    repo = FakeVolunteerShiftRepository()
    use_case = ListShiftsForRoleUseCase(repo)

    result = use_case.execute(uuid.uuid4())

    assert result == []
