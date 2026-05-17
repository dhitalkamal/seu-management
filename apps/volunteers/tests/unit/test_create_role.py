"""Unit tests for CreateVolunteerRoleUseCase."""

from __future__ import annotations

import uuid

from apps.volunteers.application.use_cases.create_role import CreateVolunteerRoleUseCase
from apps.volunteers.tests.unit.fakes import FakeVolunteerRoleRepository


def _uc() -> CreateVolunteerRoleUseCase:
    return CreateVolunteerRoleUseCase(FakeVolunteerRoleRepository())


def test_create_role_is_active():
    """New volunteer roles are created with is_active=True."""
    result = _uc().execute(
        event_id=uuid.uuid4(),
        name="Stage Manager",
        description="Manage stage setup",
        capacity=5,
    )
    assert result.is_active is True
    assert result.capacity == 5


def test_create_role_default_capacity():
    """Omitting capacity defaults to 1."""
    result = _uc().execute(event_id=uuid.uuid4(), name="Helper", description="")
    assert result.capacity == 1
