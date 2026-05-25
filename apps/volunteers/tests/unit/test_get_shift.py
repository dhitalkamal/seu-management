"""Unit tests for GetShiftUseCase."""

from __future__ import annotations

import uuid

import pytest

from apps.volunteers.application.use_cases.get_shift import GetShiftUseCase
from apps.volunteers.domain.exceptions import ShiftNotFoundError
from apps.volunteers.tests.unit.fakes import FakeVolunteerShiftRepository, make_shift


def test_get_shift_returns_entity() -> None:
    """Existing shift is returned by ID."""
    shift = make_shift()
    repo = FakeVolunteerShiftRepository([shift])
    use_case = GetShiftUseCase(repo)

    result = use_case.execute(shift.id)

    assert result.id == shift.id
    assert result.role_id == shift.role_id


def test_get_shift_raises_if_not_found() -> None:
    """Non-existent shift ID raises ShiftNotFoundError."""
    repo = FakeVolunteerShiftRepository()
    use_case = GetShiftUseCase(repo)

    with pytest.raises(ShiftNotFoundError):
        use_case.execute(uuid.uuid4())
