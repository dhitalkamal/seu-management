"""Unit tests for UpdateCaseStatusUseCase - tests all valid status transitions."""

from __future__ import annotations

import uuid

import pytest

from apps.moderation.application.use_cases.update_case_status import UpdateCaseStatusUseCase
from apps.moderation.domain.exceptions import InvalidStatusTransitionError, ModerationCaseNotFoundError
from apps.moderation.tests.unit.fakes import FakeModerationCaseRepository, make_case


def _uc(cases=None) -> UpdateCaseStatusUseCase:
    return UpdateCaseStatusUseCase(repo=FakeModerationCaseRepository(cases or []))


def test_update_pending_to_under_review():
    """Reviewer can move a pending case into under_review."""
    case = make_case(status="pending")
    reviewer_id = uuid.uuid4()
    result = _uc([case]).execute(
        case_id=case.id,
        status="under_review",
        reviewer_id=reviewer_id,
        reviewer_notes="Starting review",
    )
    assert result.status == "under_review"
    assert result.reviewer_id == reviewer_id
    assert result.reviewer_notes == "Starting review"
    assert result.resolved_at is None


def test_update_under_review_to_dismissed():
    """Reviewer can dismiss a case under review."""
    case = make_case(status="under_review")
    reviewer_id = uuid.uuid4()
    result = _uc([case]).execute(
        case_id=case.id,
        status="dismissed",
        reviewer_id=reviewer_id,
        reviewer_notes="Not a violation",
    )
    assert result.status == "dismissed"
    assert result.resolved_at is not None


def test_update_under_review_to_warned():
    """Reviewer can issue a warning for a case under review."""
    case = make_case(status="under_review")
    result = _uc([case]).execute(
        case_id=case.id,
        status="warned",
        reviewer_id=uuid.uuid4(),
        reviewer_notes="First offence - warning issued",
    )
    assert result.status == "warned"
    assert result.resolved_at is not None


def test_update_under_review_to_taken_down():
    """Reviewer can take down content for a case under review."""
    case = make_case(status="under_review")
    result = _uc([case]).execute(
        case_id=case.id,
        status="taken_down",
        reviewer_id=uuid.uuid4(),
        reviewer_notes="Severe violation - content removed",
    )
    assert result.status == "taken_down"
    assert result.resolved_at is not None


def test_update_pending_to_dismissed_raises():
    """Cannot go directly from pending to dismissed - must go through under_review."""
    case = make_case(status="pending")
    with pytest.raises(InvalidStatusTransitionError):
        _uc([case]).execute(
            case_id=case.id,
            status="dismissed",
            reviewer_id=uuid.uuid4(),
            reviewer_notes="",
        )


def test_update_terminal_status_raises():
    """Cannot change status of an already-resolved case."""
    case = make_case(status="dismissed")
    with pytest.raises(InvalidStatusTransitionError):
        _uc([case]).execute(
            case_id=case.id,
            status="warned",
            reviewer_id=uuid.uuid4(),
            reviewer_notes="",
        )


def test_update_nonexistent_case_raises():
    """Updating a case that does not exist raises ModerationCaseNotFoundError."""
    with pytest.raises(ModerationCaseNotFoundError):
        _uc([]).execute(
            case_id=uuid.uuid4(),
            status="under_review",
            reviewer_id=uuid.uuid4(),
            reviewer_notes="",
        )
