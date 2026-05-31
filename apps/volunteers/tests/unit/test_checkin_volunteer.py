"""Unit tests for CheckInVolunteerUseCase."""

from __future__ import annotations

import uuid

import pytest

from apps.volunteers.application.use_cases.checkin_volunteer import CheckInVolunteerUseCase
from apps.volunteers.domain.exceptions import AlreadyCheckedInError, ApplicationNotFoundError, InvalidStatusTransitionError
from apps.volunteers.tests.unit.fakes import FakeVolunteerApplicationRepository, make_application


def test_checkin_sets_status_and_timestamp() -> None:
    """Approved application transitions to confirmed with a check_in_at timestamp."""
    app = make_application(status="approved")
    repo = FakeVolunteerApplicationRepository([app])
    use_case = CheckInVolunteerUseCase(repo)

    result = use_case.execute(app.id)

    assert result.status == "confirmed"
    assert result.check_in_at is not None
    stored = repo.get_by_id(app.id)
    assert stored.status == "confirmed"
    assert stored.check_in_at is not None


def test_checkin_raises_if_not_approved() -> None:
    """Only approved applications may be checked in."""
    app = make_application(status="pending")
    repo = FakeVolunteerApplicationRepository([app])
    use_case = CheckInVolunteerUseCase(repo)

    with pytest.raises(InvalidStatusTransitionError):
        use_case.execute(app.id)


def test_checkin_raises_if_already_checked_in() -> None:
    """Attempting to check in again raises AlreadyCheckedInError."""
    from datetime import datetime, timezone

    app = make_application(status="confirmed", check_in_at=datetime.now(timezone.utc))
    repo = FakeVolunteerApplicationRepository([app])
    use_case = CheckInVolunteerUseCase(repo)

    with pytest.raises(AlreadyCheckedInError):
        use_case.execute(app.id)


def test_checkin_raises_if_not_found() -> None:
    """Non-existent application raises ApplicationNotFoundError."""
    repo = FakeVolunteerApplicationRepository()
    use_case = CheckInVolunteerUseCase(repo)

    with pytest.raises(ApplicationNotFoundError):
        use_case.execute(uuid.uuid4())
