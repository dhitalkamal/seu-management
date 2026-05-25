"""Unit tests for RateVolunteerUseCase."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from apps.volunteers.application.use_cases.rate_volunteer import RateVolunteerUseCase
from apps.volunteers.domain.exceptions import (
    ApplicationNotFoundError,
    ApplicationNotRatableError,
    InvalidRatingError,
)
from apps.volunteers.tests.unit.fakes import (
    FakeVolunteerApplicationRepository,
    make_application,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _checked_out_app(**kwargs: object) -> object:
    """Build a volunteer application that has completed check-in and check-out."""
    now = _now()
    defaults = {
        "status": "confirmed",
        "check_in_at": now - timedelta(hours=4),
        "check_out_at": now - timedelta(hours=1),
    }
    defaults.update(kwargs)
    return make_application(**defaults)


def test_rate_saves_rating():
    """Rate saves the submitted rating on the application."""
    app = _checked_out_app()
    repo = FakeVolunteerApplicationRepository([app])

    RateVolunteerUseCase(app_repo=repo).execute(application_id=app.id, rating=4, feedback=None)

    updated = repo.get_by_id(app.id)
    assert updated.rating == 4


def test_rate_saves_optional_feedback():
    """Feedback text is persisted alongside the rating."""
    app = _checked_out_app()
    repo = FakeVolunteerApplicationRepository([app])

    RateVolunteerUseCase(app_repo=repo).execute(application_id=app.id, rating=5, feedback="Great work!")

    updated = repo.get_by_id(app.id)
    assert updated.feedback == "Great work!"


def test_rate_with_no_feedback_stores_none():
    """Passing None for feedback stores None on the application."""
    app = _checked_out_app()
    repo = FakeVolunteerApplicationRepository([app])

    RateVolunteerUseCase(app_repo=repo).execute(application_id=app.id, rating=3, feedback=None)

    assert repo.get_by_id(app.id).feedback is None


def test_rate_raises_not_found():
    """Raises ApplicationNotFoundError for an unknown application ID."""
    with pytest.raises(ApplicationNotFoundError):
        RateVolunteerUseCase(app_repo=FakeVolunteerApplicationRepository([])).execute(application_id=uuid.uuid4(), rating=4, feedback=None)


def test_rate_raises_not_ratable_if_not_checked_out():
    """Raises ApplicationNotRatableError when check_out_at is not set."""
    app = make_application(status="confirmed", check_in_at=_now())
    with pytest.raises(ApplicationNotRatableError):
        RateVolunteerUseCase(app_repo=FakeVolunteerApplicationRepository([app])).execute(application_id=app.id, rating=4, feedback=None)


def test_rate_raises_not_ratable_if_not_checked_in():
    """Raises ApplicationNotRatableError when the volunteer never checked in."""
    app = make_application(status="approved")
    with pytest.raises(ApplicationNotRatableError):
        RateVolunteerUseCase(app_repo=FakeVolunteerApplicationRepository([app])).execute(application_id=app.id, rating=4, feedback=None)


def test_rate_raises_invalid_rating_below_1():
    """Raises InvalidRatingError when rating is 0."""
    app = _checked_out_app()
    with pytest.raises(InvalidRatingError):
        RateVolunteerUseCase(app_repo=FakeVolunteerApplicationRepository([app])).execute(application_id=app.id, rating=0, feedback=None)


def test_rate_raises_invalid_rating_above_5():
    """Raises InvalidRatingError when rating exceeds 5."""
    app = _checked_out_app()
    with pytest.raises(InvalidRatingError):
        RateVolunteerUseCase(app_repo=FakeVolunteerApplicationRepository([app])).execute(application_id=app.id, rating=6, feedback=None)


def test_rate_accepts_boundary_ratings():
    """Ratings of exactly 1 and 5 are accepted without error."""
    for r in (1, 5):
        app = _checked_out_app()
        repo = FakeVolunteerApplicationRepository([app])
        RateVolunteerUseCase(app_repo=repo).execute(application_id=app.id, rating=r, feedback=None)
        assert repo.get_by_id(app.id).rating == r
