"""Unit tests for resubmit organization use case."""

from __future__ import annotations

import pytest

from apps.orgs.application.use_cases.resubmit_org import ResubmitOrganizationUseCase
from apps.orgs.domain.exceptions import InvalidOrgStatusTransitionError
from apps.orgs.tests.unit.fakes import FakeOrgRepository, make_org


class TestResubmitOrganization:
    """Verify that only rejected orgs can be resubmitted."""

    def test_rejected_org_transitions_to_pending_review(self) -> None:
        org = make_org(status="rejected")
        repo = FakeOrgRepository([org])
        result = ResubmitOrganizationUseCase(repo).execute(org_id=org.id)
        assert result.status == "pending_review"

    def test_pending_org_cannot_be_resubmitted(self) -> None:
        org = make_org(status="pending_review")
        repo = FakeOrgRepository([org])
        with pytest.raises(InvalidOrgStatusTransitionError):
            ResubmitOrganizationUseCase(repo).execute(org_id=org.id)

    def test_active_org_cannot_be_resubmitted(self) -> None:
        org = make_org(status="active")
        repo = FakeOrgRepository([org])
        with pytest.raises(InvalidOrgStatusTransitionError):
            ResubmitOrganizationUseCase(repo).execute(org_id=org.id)
