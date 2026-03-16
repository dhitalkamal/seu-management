"""Unit tests for avg_review_hours computation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from apps.orgs.application.use_cases.compute_avg_review_hours import compute_avg_review_hours
from apps.orgs.tests.unit.fakes import make_org


def _now() -> datetime:
    return datetime.now(timezone.utc)


def test_avg_review_hours_no_reviewed_orgs():
    """Returns 0.0 when no org has been reviewed yet."""
    orgs = [make_org(reviewed_at=None), make_org(reviewed_at=None)]
    assert compute_avg_review_hours(orgs) == 0.0


def test_avg_review_hours_single_org():
    """Returns the elapsed hours for a single reviewed org."""
    now = _now()
    two_hours_ago = now - timedelta(hours=2)
    org = make_org(created_at=two_hours_ago, reviewed_at=now)
    assert compute_avg_review_hours([org]) == pytest.approx(2.0, abs=0.05)


def test_avg_review_hours_multiple_orgs():
    """Averages elapsed hours across multiple reviewed orgs."""
    now = _now()
    org_a = make_org(created_at=now - timedelta(hours=2), reviewed_at=now)
    org_b = make_org(created_at=now - timedelta(hours=4), reviewed_at=now)
    # avg of 2h and 4h = 3h
    assert compute_avg_review_hours([org_a, org_b]) == pytest.approx(3.0, abs=0.05)


def test_avg_review_hours_skips_unreviewed():
    """Unreviewed orgs (reviewed_at=None) are excluded from the average."""
    now = _now()
    reviewed = make_org(created_at=now - timedelta(hours=6), reviewed_at=now)
    unreviewed = make_org(reviewed_at=None)
    assert compute_avg_review_hours([reviewed, unreviewed]) == pytest.approx(6.0, abs=0.05)


def test_avg_review_hours_empty_list():
    """Returns 0.0 for an empty org list."""
    assert compute_avg_review_hours([]) == 0.0
