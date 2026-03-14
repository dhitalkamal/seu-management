"""Use case: list moderation cases with an optional status filter."""

from __future__ import annotations

from apps.moderation.domain.entities import ModerationCaseEntity
from apps.moderation.domain.repositories import IModerationCaseRepository


class ListModerationCasesUseCase:
    """Return all moderation cases, optionally filtered by status."""

    def __init__(self, repo: IModerationCaseRepository) -> None:
        self._repo = repo

    def execute(self, status: str | None = None) -> list[ModerationCaseEntity]:
        """
        Fetch cases from the repository.

        @param status - optional filter; returns all cases if None
        @returns list of ModerationCaseEntity ordered by created_at descending
        """
        return self._repo.list_all(status=status)
