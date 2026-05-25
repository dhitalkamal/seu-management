"""Unit tests for volunteer application status management use cases."""

from __future__ import annotations

import uuid

import pytest

from apps.volunteers.application.use_cases.approve_application import ApproveApplicationUseCase
from apps.volunteers.application.use_cases.cancel_application import CancelApplicationUseCase
from apps.volunteers.application.use_cases.list_applications import ListApplicationsUseCase
from apps.volunteers.application.use_cases.reject_application import RejectApplicationUseCase
from apps.volunteers.domain.exceptions import ApplicationNotFoundError
from apps.volunteers.tests.unit.fakes import (
    FakeParticipationContextClient,
    FakeVolunteerApplicationRepository,
    make_application,
)


def test_approve_sets_status_approved():
    """Approving a pending application sets status=approved."""
    app = make_application(status="pending")
    repo = FakeVolunteerApplicationRepository([app])
    result = ApproveApplicationUseCase(repo).execute(application_id=app.id)
    assert result.status == "approved"


def test_approve_missing_raises():
    """Approving a non-existent application raises ApplicationNotFoundError."""
    with pytest.raises(ApplicationNotFoundError):
        ApproveApplicationUseCase(FakeVolunteerApplicationRepository()).execute(application_id=uuid.uuid4())


def test_reject_sets_status_rejected():
    """Rejecting a pending application sets status=rejected."""
    app = make_application(status="pending")
    repo = FakeVolunteerApplicationRepository([app])
    result = RejectApplicationUseCase(repo).execute(application_id=app.id)
    assert result.status == "rejected"


def test_cancel_sets_status_cancelled():
    """Cancelling an application sets status=cancelled."""
    app = make_application(status="pending")
    repo = FakeVolunteerApplicationRepository([app])
    result = CancelApplicationUseCase(repo).execute(application_id=app.id)
    assert result.status == "cancelled"


def test_list_applications_for_role():
    """ListApplicationsUseCase returns all applications for a role."""
    role_id = uuid.uuid4()
    apps = [make_application(volunteer_role_id=role_id) for _ in range(3)]
    other = make_application()
    repo = FakeVolunteerApplicationRepository(apps + [other])
    results = ListApplicationsUseCase(repo).execute(role_id=role_id)
    assert len(results) == 3
    assert all(r.volunteer_role_id == role_id for r in results)


def test_list_applications_empty():
    """ListApplicationsUseCase returns empty list when no applications exist for the role."""
    repo = FakeVolunteerApplicationRepository()
    assert ListApplicationsUseCase(repo).execute(role_id=uuid.uuid4()) == []


def test_approve_records_volunteer_context_via_client():
    """Approving calls set_volunteer on the context client with the application's event and user."""
    app = make_application(status="pending")
    repo = FakeVolunteerApplicationRepository([app])
    client = FakeParticipationContextClient()
    ApproveApplicationUseCase(repo, context_client=client).execute(application_id=app.id)
    assert (app.event_id, app.user_id) in client.volunteer_sets
