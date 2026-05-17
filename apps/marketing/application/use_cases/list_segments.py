"""Use case: list all audience segments."""

from __future__ import annotations

from apps.marketing.domain.entities import AudienceSegmentEntity
from apps.marketing.domain.repositories import IAudienceSegmentRepository


class ListSegmentsUseCase:
    """Return all audience segments."""

    def __init__(self, repo: IAudienceSegmentRepository) -> None:
        self._repo = repo

    def execute(self) -> list[AudienceSegmentEntity]:
        """Return all segments."""
        return self._repo.list_all()
