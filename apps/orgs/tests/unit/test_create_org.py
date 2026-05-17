"""Unit tests for CreateOrganisationUseCase."""

from __future__ import annotations

import uuid

import pytest

from apps.orgs.application.use_cases.create_org import CreateOrganisationUseCase
from apps.orgs.domain.exceptions import OrgSlugTakenError
from apps.orgs.tests.unit.fakes import FakeOrgMemberRepository, FakeOrgRepository, make_org


def _uc(orgs=None) -> CreateOrganisationUseCase:
    return CreateOrganisationUseCase(
        org_repo=FakeOrgRepository(orgs or []),
        member_repo=FakeOrgMemberRepository(),
    )


def test_create_org_status_is_pending_review():
    """New organisations always start as pending_review."""
    result = _uc().execute(
        created_by=uuid.uuid4(),
        name="Sansaar Events",
        slug="sansaar-events",
        contact_email="org@example.com",
    )
    assert result.status == "pending_review"
    assert result.is_verified is False


def test_create_org_creator_assigned_owner_membership():
    """The creator is automatically added as an owner member."""
    creator_id = uuid.uuid4()
    member_repo = FakeOrgMemberRepository()
    CreateOrganisationUseCase(
        org_repo=FakeOrgRepository(),
        member_repo=member_repo,
    ).execute(
        created_by=creator_id,
        name="Test Org",
        slug="test-org",
        contact_email="org@example.com",
    )
    members = list(member_repo._store.values())
    assert len(members) == 1
    assert members[0].user_id == creator_id
    assert members[0].role == "owner"


def test_create_org_duplicate_slug_raises():
    """Creating an org with an already-taken slug raises OrgSlugTakenError."""
    existing = make_org(slug="taken-slug")
    with pytest.raises(OrgSlugTakenError):
        _uc(orgs=[existing]).execute(
            created_by=uuid.uuid4(),
            name="Another Org",
            slug="taken-slug",
            contact_email="other@example.com",
        )
