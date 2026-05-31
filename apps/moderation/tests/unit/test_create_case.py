"""Unit tests for CreateModerationCaseUseCase."""

from __future__ import annotations

import uuid

import pytest

from apps.moderation.application.use_cases.create_case import CreateModerationCaseUseCase
from apps.moderation.domain.exceptions import InvalidContentTypeError
from apps.moderation.tests.unit.fakes import FakeModerationCaseRepository


def _uc(cases=None) -> CreateModerationCaseUseCase:
    return CreateModerationCaseUseCase(repo=FakeModerationCaseRepository(cases or []))


def test_create_case_status_is_pending():
    """New moderation cases always start as pending."""
    result = _uc().execute(
        content_type="event",
        content_id=uuid.uuid4(),
        content_title="Some Event",
        reason="Spam",
        reporter_id=uuid.uuid4(),
        organization_id=uuid.uuid4(),
    )
    assert result.status == "pending"
    assert result.reviewer_id is None
    assert result.reviewer_notes == ""
    assert result.resolved_at is None


def test_create_case_stores_all_fields():
    """Created case preserves all provided fields."""
    content_id = uuid.uuid4()
    reporter_id = uuid.uuid4()
    org_id = uuid.uuid4()
    repo = FakeModerationCaseRepository()
    result = CreateModerationCaseUseCase(repo=repo).execute(
        content_type="post",
        content_id=content_id,
        content_title="Offensive Post",
        reason="Hate speech",
        reporter_id=reporter_id,
        organization_id=org_id,
    )
    assert result.content_type == "post"
    assert result.content_id == content_id
    assert result.content_title == "Offensive Post"
    assert result.reason == "Hate speech"
    assert result.reporter_id == reporter_id
    assert result.organization_id == org_id
    # case is saved in the repo
    assert len(repo._store) == 1


def test_create_case_invalid_content_type_raises():
    """Creating a case with an unknown content_type raises InvalidContentTypeError."""
    with pytest.raises(InvalidContentTypeError):
        _uc().execute(
            content_type="banana",
            content_id=uuid.uuid4(),
            content_title="Test",
            reason="reason",
        )


def test_create_case_without_reporter_is_allowed():
    """A case can be created without a reporter (system-generated reports)."""
    result = _uc().execute(
        content_type="comment",
        content_id=uuid.uuid4(),
        content_title="Flagged Comment",
        reason="Auto-flagged",
        reporter_id=None,
        organization_id=None,
    )
    assert result.reporter_id is None
    assert result.organization_id is None
