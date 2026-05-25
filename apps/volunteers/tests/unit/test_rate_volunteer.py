"""Unit tests for RateVolunteerUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest

from apps.volunteers.application.use_cases.rate_volunteer import RateVolunteerUseCase
from apps.volunteers.domain.exceptions import ApplicationNotFoundError, ApplicationNotRatableError, InvalidRatingError
from apps.volunteers.tests.unit.fakes import (
    FakeVolunteerApplicationRepository,
    FakeVolunteerProfileRepository,
    make_application,
    make_profile,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def test_rating_persists_on_application() -> None:
    """Rating 1-5 is saved on the application."""
    app = make_application(status="confirmed", check_in_at=_now(), check_out_at=_now())
    app_repo = FakeVolunteerApplicationRepository([app])
    profile_repo = FakeVolunteerProfileRepository()
    use_case = RateVolunteerUseCase(app_repo, profile_repo)

    result = use_case.execute(app.id, rating=4, feedback="Great work")

    assert result.rating == 4
    assert result.feedback == "Great work"


def test_rating_updates_profile_average() -> None:
    """Profile average_rating is recalculated after rating."""
    app = make_application(status="confirmed", check_in_at=_now(), check_out_at=_now())
    existing_profile = make_profile(user_id=app.user_id, average_rating=3.0, total_ratings=2)
    app_repo = FakeVolunteerApplicationRepository([app])
    profile_repo = FakeVolunteerProfileRepository([existing_profile])
    use_case = RateVolunteerUseCase(app_repo, profile_repo)

    use_case.execute(app.id, rating=5, feedback=None)

    profile = profile_repo.get_by_user_id(app.user_id)
    # (3.0 * 2 + 5) / 3 = 11/3 ≈ 3.667
    assert profile.total_ratings == 3
    assert profile.average_rating is not None
    assert abs(profile.average_rating - (11 / 3)) < 0.001


def test_rating_creates_profile_if_missing() -> None:
    """A new profile is created when none exists for this user."""
    app = make_application(status="confirmed", check_in_at=_now(), check_out_at=_now())
    app_repo = FakeVolunteerApplicationRepository([app])
    profile_repo = FakeVolunteerProfileRepository()
    use_case = RateVolunteerUseCase(app_repo, profile_repo)

    use_case.execute(app.id, rating=5, feedback=None)

    profile = profile_repo.get_by_user_id(app.user_id)
    assert profile.average_rating == 5.0
    assert profile.total_ratings == 1


def test_rating_raises_if_not_ratable() -> None:
    """Missing check_in_at or check_out_at raises ApplicationNotRatableError."""
    app = make_application(status="confirmed", check_in_at=_now(), check_out_at=None)
    app_repo = FakeVolunteerApplicationRepository([app])
    profile_repo = FakeVolunteerProfileRepository()
    use_case = RateVolunteerUseCase(app_repo, profile_repo)

    with pytest.raises(ApplicationNotRatableError):
        use_case.execute(app.id, rating=4, feedback=None)


def test_rating_raises_for_invalid_rating() -> None:
    """Rating outside 1-5 raises InvalidRatingError."""
    app = make_application(status="confirmed", check_in_at=_now(), check_out_at=_now())
    app_repo = FakeVolunteerApplicationRepository([app])
    profile_repo = FakeVolunteerProfileRepository()
    use_case = RateVolunteerUseCase(app_repo, profile_repo)

    with pytest.raises(InvalidRatingError):
        use_case.execute(app.id, rating=6, feedback=None)


def test_rating_raises_if_not_found() -> None:
    """Non-existent application raises ApplicationNotFoundError."""
    app_repo = FakeVolunteerApplicationRepository()
    profile_repo = FakeVolunteerProfileRepository()
    use_case = RateVolunteerUseCase(app_repo, profile_repo)

    with pytest.raises(ApplicationNotFoundError):
        use_case.execute(uuid.uuid4(), rating=4, feedback=None)
