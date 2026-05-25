"""Unit tests for CheckInVolunteerUseCase and the hours_worked entity property."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from apps.volunteers.application.use_cases.checkin_volunteer import CheckInVolunteerUseCase
from apps.volunteers.domain.exceptions import (
    AlreadyCheckedInError,
    ApplicationNotFoundError,
    InvalidStatusTransitionError,
)
from apps.volunteers.tests.unit.fakes import (
    FakeVolunteerApplicationRepository,
    make_application,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


# * CheckInVolunteerUseCase tests


def test_checkin_sets_check_in_at():
    """Check-in sets check_in_at to a datetime close to now."""
    app = make_application(status="approved")
    repo = FakeVolunteerApplicationRepository([app])
    before = _now()

    CheckInVolunteerUseCase(app_repo=repo).execute(application_id=app.id)

    updated = repo.get_by_id(app.id)
    assert updated.check_in_at is not None
    assert updated.check_in_at >= before


def test_checkin_sets_status_confirmed():
    """Check-in transitions status from approved to confirmed."""
    app = make_application(status="approved")
    repo = FakeVolunteerApplicationRepository([app])

    CheckInVolunteerUseCase(app_repo=repo).execute(application_id=app.id)

    assert repo.get_by_id(app.id).status == "confirmed"


def test_checkin_raises_not_found():
    """Check-in raises ApplicationNotFoundError for an unknown application ID."""
    with pytest.raises(ApplicationNotFoundError):
        CheckInVolunteerUseCase(app_repo=FakeVolunteerApplicationRepository([])).execute(application_id=uuid.uuid4())


def test_checkin_raises_for_non_approved_status():
    """Check-in raises InvalidStatusTransitionError when status is not approved."""
    for bad_status in ("pending", "rejected", "cancelled"):
        app = make_application(status=bad_status)
        with pytest.raises(InvalidStatusTransitionError):
            CheckInVolunteerUseCase(app_repo=FakeVolunteerApplicationRepository([app])).execute(application_id=app.id)


def test_checkin_raises_if_already_checked_in():
    """Check-in raises AlreadyCheckedInError when check_in_at is already set."""
    app = make_application(status="confirmed", check_in_at=_now())
    with pytest.raises(AlreadyCheckedInError):
        CheckInVolunteerUseCase(app_repo=FakeVolunteerApplicationRepository([app])).execute(application_id=app.id)


# * hours_worked property tests


def test_hours_worked_returns_none_before_checkout():
    """hours_worked is None when check_out_at is not set."""
    app = make_application(check_in_at=_now())
    assert app.hours_worked is None


def test_hours_worked_calculated_correctly():
    """hours_worked returns elapsed hours, rounded to 2 decimal places."""
    check_in = _now() - timedelta(hours=2, minutes=30)
    check_out = check_in + timedelta(hours=2, minutes=30)
    app = make_application(check_in_at=check_in, check_out_at=check_out)
    assert app.hours_worked is not None
    assert abs(app.hours_worked - 2.5) < 0.01


def test_hours_worked_returns_none_if_no_checkin():
    """hours_worked is None when check_in_at is not set."""
    app = make_application()
    assert app.hours_worked is None
