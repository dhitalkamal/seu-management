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
    FakeEventPublisher,
    FakeVolunteerApplicationRepository,
    make_application,
)


def test_approve_sets_status_approved():
    """Approving a pending application sets status=approved."""
    app = make_application(status="pending")
    repo = FakeVolunteerApplicationRepository([app])
    result = ApproveApplicationUseCase(repo).execute(application_id=app.id)
    assert result.status == "approved"


def test_approve_publishes_volunteer_application_approved_event():
    """Approving an application publishes volunteer.application.approved with user_id and event_id."""
    app = make_application(status="pending")
    repo = FakeVolunteerApplicationRepository([app])
    publisher = FakeEventPublisher()
    ApproveApplicationUseCase(repo, publisher).execute(application_id=app.id)
    assert len(publisher.events) == 1
    event = publisher.events[0]
    assert event["type"] == "volunteer.application.approved"
    assert event["payload"]["user_id"] == str(app.user_id)
    assert event["payload"]["event_id"] == str(app.event_id)


def test_approve_without_publisher_does_not_raise():
    """Approving without a publisher succeeds silently (publisher is optional)."""
    app = make_application(status="pending")
    repo = FakeVolunteerApplicationRepository([app])
    # no publisher passed -- must not raise
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
