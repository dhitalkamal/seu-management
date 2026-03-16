"""Unit tests for review timestamp behaviour on approve/reject use cases."""

from __future__ import annotations

from datetime import datetime, timezone

from apps.orgs.application.use_cases.approve_org import ApproveOrganisationUseCase
from apps.orgs.application.use_cases.reject_org import RejectOrganisationUseCase
from apps.orgs.tests.unit.fakes import FakeOrgRepository, make_org


def _now() -> datetime:
    return datetime.now(timezone.utc)


def test_approve_sets_reviewed_at():
    """Approving a pending_review org stamps reviewed_at with the current time."""
    org = make_org(status="pending_review")
    repo = FakeOrgRepository([org])

    before = _now()
    result = ApproveOrganisationUseCase(repo).execute(org_id=org.id)
    after = _now()

    assert result.reviewed_at is not None
    assert before <= result.reviewed_at <= after


def test_approve_sets_reviewed_by_when_provided():
    """Approving with a reviewer id stores that id on the org."""
    import uuid

    org = make_org(status="pending_review")
    repo = FakeOrgRepository([org])
    reviewer = uuid.uuid4()

    result = ApproveOrganisationUseCase(repo).execute(org_id=org.id, reviewed_by=reviewer)

    assert result.reviewed_by == reviewer


def test_approve_reviewed_by_defaults_to_none():
    """Approving without passing reviewed_by leaves it as None."""
    org = make_org(status="pending_review")
    repo = FakeOrgRepository([org])

    result = ApproveOrganisationUseCase(repo).execute(org_id=org.id)

    assert result.reviewed_by is None


def test_reject_sets_reviewed_at():
    """Rejecting a pending_review org stamps reviewed_at with the current time."""
    org = make_org(status="pending_review")
    repo = FakeOrgRepository([org])

    before = _now()
    result = RejectOrganisationUseCase(repo).execute(org_id=org.id)
    after = _now()

    assert result.reviewed_at is not None
    assert before <= result.reviewed_at <= after


def test_reject_sets_reviewed_by_when_provided():
    """Rejecting with a reviewer id stores that id on the org."""
    import uuid

    org = make_org(status="pending_review")
    repo = FakeOrgRepository([org])
    reviewer = uuid.uuid4()

    result = RejectOrganisationUseCase(repo).execute(org_id=org.id, reviewed_by=reviewer)

    assert result.reviewed_by == reviewer
