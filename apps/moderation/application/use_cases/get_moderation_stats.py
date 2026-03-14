"""Use case: compute KPI stats for the moderation dashboard."""

from __future__ import annotations

from apps.moderation.domain.repositories import IModerationCaseRepository


class GetModerationStatsUseCase:
    """Return aggregated stats for the moderation dashboard KPI cards."""

    def __init__(self, repo: IModerationCaseRepository) -> None:
        self._repo = repo

    def execute(self) -> dict:
        """
        Fetch and return moderation KPIs.

        Returns a dict with keys:
            total, pending, under_review, dismissed, warned, taken_down,
            decided, approval_rate, avg_resolution_hours
        """
        return self._repo.get_stats()
