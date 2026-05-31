"""Unit tests for ListModerationCasesUseCase."""

from __future__ import annotations

from apps.moderation.application.use_cases.list_cases import ListModerationCasesUseCase
from apps.moderation.tests.unit.fakes import FakeModerationCaseRepository, make_case


def _uc(cases=None) -> ListModerationCasesUseCase:
    return ListModerationCasesUseCase(repo=FakeModerationCaseRepository(cases or []))


def test_list_cases_returns_all_when_no_filter():
    """Without a status filter all cases are returned."""
    cases = [make_case(status="pending"), make_case(status="dismissed"), make_case(status="warned")]
    result = _uc(cases).execute(status=None)
    assert len(result) == 3


def test_list_cases_filters_by_status():
    """Only cases matching the given status are returned."""
    pending = make_case(status="pending")
    dismissed = make_case(status="dismissed")
    _uc([pending, dismissed]).execute(status="pending")
    result = _uc([pending, dismissed]).execute(status="pending")
    assert all(c.status == "pending" for c in result)
    assert len(result) == 1


def test_list_cases_returns_empty_list_when_none():
    """Returns an empty list when no cases exist."""
    result = _uc([]).execute(status=None)
    assert result == []


def test_list_cases_filters_under_review():
    """Filter by under_review status works correctly."""
    cases = [
        make_case(status="pending"),
        make_case(status="under_review"),
        make_case(status="under_review"),
        make_case(status="taken_down"),
    ]
    result = _uc(cases).execute(status="under_review")
    assert len(result) == 2
    assert all(c.status == "under_review" for c in result)
