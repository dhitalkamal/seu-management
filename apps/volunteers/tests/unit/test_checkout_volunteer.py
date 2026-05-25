"""Unit tests for CheckOutVolunteerUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from apps.volunteers.application.use_cases.checkout_volunteer import CheckOutVolunteerUseCase
from apps.volunteers.domain.exceptions import (
    ApplicationNotFoundError,
    InvalidStatusTransitionError,
    NotCheckedInError,
)
from apps.volunteers.tests.unit.fakes import (
    FakeVolunteerApplicationRepository,
    make_application,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def test_checkout_sets_check_out_at():
    """Check-out sets check_out_at to a datetime close to now."""
    check_in = _now()
    app = make_application(status="confirmed", check_in_at=check_in)
    repo = FakeVolunteerApplicationRepository([app])
    before = _now()

    CheckOutVolunteerUseCase(app_repo=repo).execute(application_id=app.id)

    updated = repo.get_by_id(app.id)
    assert updated.check_out_at is not None
    assert updated.check_out_at >= before


def test_checkout_raises_not_found():
    """Check-out raises ApplicationNotFoundError for an unknown application ID."""
    with pytest.raises(ApplicationNotFoundError):
        CheckOutVolunteerUseCase(app_repo=FakeVolunteerApplicationRepository([])).execute(application_id=uuid.uuid4())


def test_checkout_raises_if_not_checked_in():
    """Check-out raises NotCheckedInError when check_in_at is not set."""
    app = make_application(status="approved")
    with pytest.raises(NotCheckedInError):
        CheckOutVolunteerUseCase(app_repo=FakeVolunteerApplicationRepository([app])).execute(application_id=app.id)


def test_checkout_raises_if_already_checked_out():
    """Check-out raises InvalidStatusTransitionError when already checked out."""
    check_in = _now() - timedelta(hours=2)
    check_out = _now() - timedelta(hours=1)
    app = make_application(status="confirmed", check_in_at=check_in, check_out_at=check_out)
    with pytest.raises(InvalidStatusTransitionError):
        CheckOutVolunteerUseCase(app_repo=FakeVolunteerApplicationRepository([app])).execute(application_id=app.id)
