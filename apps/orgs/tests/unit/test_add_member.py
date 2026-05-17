"""Unit tests for AddOrgMemberUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from apps.orgs.application.use_cases.add_member import AddOrgMemberUseCase
from apps.orgs.domain.entities import OrgMemberEntity
from apps.orgs.domain.exceptions import MemberAlreadyExistsError, OrgNotFoundError
from apps.orgs.tests.unit.fakes import FakeOrgMemberRepository, FakeOrgRepository, make_org


def _uc(orgs=None, members=None) -> AddOrgMemberUseCase:
    return AddOrgMemberUseCase(
        org_repo=FakeOrgRepository(orgs or []),
        member_repo=FakeOrgMemberRepository(members or []),
    )


def test_add_member_creates_membership():
    """Adding a new user creates a membership with the given role."""
    org = make_org()
    user_id = uuid.uuid4()
    result = _uc(orgs=[org]).execute(org_id=org.id, user_id=user_id, role="member")
    assert result.organisation_id == org.id
    assert result.user_id == user_id
    assert result.role == "member"
    assert result.is_active is True


def test_add_member_duplicate_raises():
    """Adding a user who is already a member raises MemberAlreadyExistsError."""
    org = make_org()
    user_id = uuid.uuid4()
    existing = OrgMemberEntity(
        id=uuid.uuid4(),
        organisation_id=org.id,
        user_id=user_id,
        role="member",
        is_active=True,
        joined_at=datetime.now(timezone.utc),
    )
    with pytest.raises(MemberAlreadyExistsError):
        _uc(orgs=[org], members=[existing]).execute(org_id=org.id, user_id=user_id, role="admin")


def test_add_member_org_not_found_raises():
    """Adding a member to a non-existent org raises OrgNotFoundError."""
    with pytest.raises(OrgNotFoundError):
        _uc().execute(org_id=uuid.uuid4(), user_id=uuid.uuid4(), role="member")
