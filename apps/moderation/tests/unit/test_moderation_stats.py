"""Unit tests for GetModerationStatsUseCase."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from apps.moderation.application.use_cases.get_moderation_stats import GetModerationStatsUseCase
from apps.moderation.tests.unit.fakes import FakeModerationCaseRepository, make_case


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uc(cases=None) -> GetModerationStatsUseCase:
    return GetModerationStatsUseCase(repo=FakeModerationCaseRepository(cases or []))


def test_stats_empty_repo():
    """All stats are zero when there are no cases."""
    stats = _uc([]).execute()
    assert stats["total"] == 0
    assert stats["pending"] == 0
    assert stats["decided"] == 0
    assert stats["approval_rate"] == 0.0
    assert stats["avg_resolution_hours"] == 0.0


def test_stats_counts_by_status():
    """Each status bucket is counted independently."""
    cases = [
        make_case(status="pending"),
        make_case(status="pending"),
        make_case(status="under_review"),
        make_case(status="dismissed"),
        make_case(status="warned"),
        make_case(status="taken_down"),
    ]
    stats = _uc(cases).execute()
    assert stats["total"] == 6
    assert stats["pending"] == 2
    assert stats["under_review"] == 1
    assert stats["dismissed"] == 1
    assert stats["warned"] == 1
    assert stats["taken_down"] == 1
    # decided = dismissed + warned + taken_down
    assert stats["decided"] == 3


def test_stats_approval_rate():
    """Approval rate is (dismissed + warned) / decided * 100."""
    cases = [
        make_case(status="dismissed"),
        make_case(status="warned"),
        make_case(status="taken_down"),
    ]
    stats = _uc(cases).execute()
    # 2 approved (dismissed + warned) out of 3 decided = 66.7%
    assert stats["approval_rate"] == pytest.approx(66.7, abs=0.2)


def test_stats_approval_rate_all_taken_down():
    """Approval rate is 0.0 when all decided cases are taken_down."""
    cases = [make_case(status="taken_down"), make_case(status="taken_down")]
    stats = _uc(cases).execute()
    assert stats["approval_rate"] == 0.0


def test_stats_avg_resolution_hours():
    """Average resolution hours is computed from resolved cases only."""
    now = _now()
    two_hours_ago = now - timedelta(hours=2)
    four_hours_ago = now - timedelta(hours=4)

    case1 = make_case(status="dismissed", created_at=two_hours_ago, resolved_at=now)
    case2 = make_case(status="warned", created_at=four_hours_ago, resolved_at=now)
    # pending case should not affect avg
    pending = make_case(status="pending", created_at=now, resolved_at=None)

    stats = _uc([case1, case2, pending]).execute()
    # avg of 2h and 4h = 3h
    assert stats["avg_resolution_hours"] == pytest.approx(3.0, abs=0.1)


def test_stats_avg_resolution_hours_no_resolved():
    """Returns 0.0 when no cases have been resolved yet."""
    cases = [make_case(status="pending"), make_case(status="under_review")]
    stats = _uc(cases).execute()
    assert stats["avg_resolution_hours"] == 0.0
