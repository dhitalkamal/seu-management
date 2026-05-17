"""Unit tests for ApplyToVolunteerRoleUseCase."""

from __future__ import annotations

import uuid

import pytest

from apps.volunteers.application.use_cases.apply_to_role import ApplyToVolunteerRoleUseCase
from apps.volunteers.domain.exceptions import (
    AlreadyAppliedError,
    RoleAtCapacityError,
    RoleNotFoundError,
)
from apps.volunteers.tests.unit.fakes import (
    FakeVolunteerApplicationRepository,
    FakeVolunteerRoleRepository,
    make_application,
    make_role,
)


def _uc(roles=None, applications=None, approved_count=None) -> ApplyToVolunteerRoleUseCase:
    return ApplyToVolunteerRoleUseCase(
        role_repo=FakeVolunteerRoleRepository(roles or [], approved_count or {}),
        app_repo=FakeVolunteerApplicationRepository(applications or []),
    )


def test_apply_creates_pending_application():
    """Successful application creates an entity with status=pending."""
    role = make_role()
    result = _uc(roles=[role]).execute(
        role_id=role.id, user_id=uuid.uuid4(), event_id=role.event_id
    )
    assert result.status == "pending"
    assert result.volunteer_role_id == role.id


def test_apply_inactive_role_raises():
    """Applying to an inactive role raises RoleNotFoundError."""
    role = make_role(is_active=False)
    with pytest.raises(RoleNotFoundError):
        _uc(roles=[role]).execute(role_id=role.id, user_id=uuid.uuid4(), event_id=role.event_id)


def test_apply_already_applied_raises():
    """Applying when an active application already exists raises AlreadyAppliedError."""
    role = make_role()
    user_id = uuid.uuid4()
    existing = make_application(volunteer_role_id=role.id, user_id=user_id, status="pending")
    with pytest.raises(AlreadyAppliedError):
        _uc(roles=[role], applications=[existing]).execute(
            role_id=role.id, user_id=user_id, event_id=role.event_id
        )


def test_apply_at_capacity_raises():
    """Applying to a full role raises RoleAtCapacityError."""
    role = make_role(capacity=1)
    with pytest.raises(RoleAtCapacityError):
        _uc(roles=[role], approved_count={role.id: 1}).execute(
            role_id=role.id, user_id=uuid.uuid4(), event_id=role.event_id
        )
