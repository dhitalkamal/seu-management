"""Utility: compute average review time in hours from a list of org entities."""

from __future__ import annotations

from apps.orgs.domain.entities import OrgEntity


def compute_avg_review_hours(orgs: list[OrgEntity]) -> float:
    """
    Return the mean hours between created_at and reviewed_at for reviewed orgs.

    Orgs where reviewed_at is None are excluded. Returns 0.0 when no reviewed
    org exists.
    """
    reviewed = [o for o in orgs if o.reviewed_at is not None]
    if not reviewed:
        return 0.0
    deltas = [(o.reviewed_at - o.created_at).total_seconds() / 3600 for o in reviewed]  # type: ignore[operator]
    return round(sum(deltas) / len(deltas), 1)
