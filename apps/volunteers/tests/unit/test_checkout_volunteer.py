"""Unit tests for CheckOutVolunteerUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from apps.volunteers.application.use_cases.checkout_volunteer import CheckOutVolunteerUseCase
from apps.volunteers.domain.exceptions import ApplicationNotFoundError, NotCheckedInError
from apps.volunteers.tests.unit.fakes import FakeVolunteerApplicationRepository, make_application


def _now() -> datetime:
    return datetime.now(timezone.utc)


def test_checkout_sets_timestamp() -> None:
    """Confirmed application with check_in_at gets check_out_at set."""
    app = make_application(status="confirmed", check_in_at=_now())
    repo = FakeVolunteerApplicationRepository([app])
    use_case = CheckOutVolunteerUseCase(repo)

    result = use_case.execute(app.id)

    assert result.check_out_at is not None
    stored = repo.get_by_id(app.id)
    assert stored.check_out_at is not None


def test_checkout_raises_if_not_checked_in() -> None:
    """Application without check_in_at raises NotCheckedInError."""
    app = make_application(status="approved", check_in_at=None)
    repo = FakeVolunteerApplicationRepository([app])
    use_case = CheckOutVolunteerUseCase(repo)

    with pytest.raises(NotCheckedInError):
        use_case.execute(app.id)


def test_checkout_raises_if_already_checked_out() -> None:
    """Already checked-out application raises NotCheckedInError."""
    app = make_application(status="confirmed", check_in_at=_now(), check_out_at=_now())
    repo = FakeVolunteerApplicationRepository([app])
    use_case = CheckOutVolunteerUseCase(repo)

    with pytest.raises(NotCheckedInError):
        use_case.execute(app.id)


def test_checkout_raises_if_not_found() -> None:
    """Non-existent application raises ApplicationNotFoundError."""
    repo = FakeVolunteerApplicationRepository()
    use_case = CheckOutVolunteerUseCase(repo)

    with pytest.raises(ApplicationNotFoundError):
        use_case.execute(uuid.uuid4())
