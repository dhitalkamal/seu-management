"""Unit tests for SoftDeleteOrganisationUseCase."""

from __future__ import annotations

import uuid

import pytest

from apps.orgs.application.use_cases.soft_delete_org import SoftDeleteOrganisationUseCase
from apps.orgs.domain.exceptions import OrgNotFoundError
from apps.orgs.tests.unit.fakes import FakeOrgRepository, make_org


def test_soft_delete_sets_deleted_at():
    """SoftDeleteOrganisationUseCase sets deleted_at to a non-None timestamp."""
    org = make_org(status="active")
    repo = FakeOrgRepository([org])
    SoftDeleteOrganisationUseCase(repo).execute(org_id=org.id)
    updated = repo._store[org.id]
    assert updated.deleted_at is not None


def test_soft_deleted_org_excluded_from_get():
    """get_by_id raises OrgNotFoundError for a soft-deleted org."""
    org = make_org(status="active")
    repo = FakeOrgRepository([org])
    SoftDeleteOrganisationUseCase(repo).execute(org_id=org.id)
    with pytest.raises(OrgNotFoundError):
        repo.get_by_id(org.id)


def test_soft_delete_missing_org_raises():
    """Raises OrgNotFoundError when org does not exist."""
    repo = FakeOrgRepository()
    with pytest.raises(OrgNotFoundError):
        SoftDeleteOrganisationUseCase(repo).execute(org_id=uuid.uuid4())
