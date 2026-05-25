"""Unit tests for org approval, rejection, suspension, and reinstatement use cases."""

from __future__ import annotations

import pytest

from apps.orgs.application.use_cases.approve_org import ApproveOrganisationUseCase
from apps.orgs.application.use_cases.reinstate_org import ReinstateOrganisationUseCase
from apps.orgs.application.use_cases.reject_org import RejectOrganisationUseCase
from apps.orgs.application.use_cases.suspend_org import SuspendOrganisationUseCase
from apps.orgs.domain.exceptions import InvalidOrgStatusTransitionError, OrgNotFoundError
from apps.orgs.tests.unit.fakes import FakeOrgRepository, make_org


def test_approve_sets_status_active():
    """Approving a pending_review org sets status=active."""
    org = make_org(status="pending_review")
    repo = FakeOrgRepository([org])
    result = ApproveOrganisationUseCase(repo).execute(org_id=org.id)
    assert result.status == "active"


def test_approve_wrong_status_raises():
    """Approving an already active org raises InvalidOrgStatusTransitionError."""
    org = make_org(status="active")
    repo = FakeOrgRepository([org])
    with pytest.raises(InvalidOrgStatusTransitionError):
        ApproveOrganisationUseCase(repo).execute(org_id=org.id)


def test_approve_missing_org_raises():
    """Approving a non-existent org raises OrgNotFoundError."""
    import uuid

    repo = FakeOrgRepository()
    with pytest.raises(OrgNotFoundError):
        ApproveOrganisationUseCase(repo).execute(org_id=uuid.uuid4())


def test_reject_sets_status_suspended():
    """Rejecting a pending_review org sets status=suspended."""
    org = make_org(status="pending_review")
    repo = FakeOrgRepository([org])
    result = RejectOrganisationUseCase(repo).execute(org_id=org.id)
    assert result.status == "suspended"


def test_reject_wrong_status_raises():
    """Rejecting an already active org raises InvalidOrgStatusTransitionError."""
    org = make_org(status="active")
    repo = FakeOrgRepository([org])
    with pytest.raises(InvalidOrgStatusTransitionError):
        RejectOrganisationUseCase(repo).execute(org_id=org.id)


def test_suspend_sets_status_suspended():
    """Suspending an active org sets status=suspended."""
    org = make_org(status="active")
    repo = FakeOrgRepository([org])
    result = SuspendOrganisationUseCase(repo).execute(org_id=org.id)
    assert result.status == "suspended"


def test_suspend_wrong_status_raises():
    """Suspending a non-active org raises InvalidOrgStatusTransitionError."""
    org = make_org(status="pending_review")
    repo = FakeOrgRepository([org])
    with pytest.raises(InvalidOrgStatusTransitionError):
        SuspendOrganisationUseCase(repo).execute(org_id=org.id)


def test_reinstate_sets_status_active():
    """Reinstating a suspended org sets status=active."""
    org = make_org(status="suspended")
    repo = FakeOrgRepository([org])
    result = ReinstateOrganisationUseCase(repo).execute(org_id=org.id)
    assert result.status == "active"


def test_reinstate_wrong_status_raises():
    """Reinstating a non-suspended org raises InvalidOrgStatusTransitionError."""
    org = make_org(status="active")
    repo = FakeOrgRepository([org])
    with pytest.raises(InvalidOrgStatusTransitionError):
        ReinstateOrganisationUseCase(repo).execute(org_id=org.id)
