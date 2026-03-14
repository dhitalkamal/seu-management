"""Use case: retrieve a single moderation case by id."""

from __future__ import annotations

import uuid

from apps.moderation.domain.entities import ModerationCaseEntity
from apps.moderation.domain.repositories import IModerationCaseRepository


class GetModerationCaseUseCase:
    """Fetch a single moderation case by primary key."""

    def __init__(self, repo: IModerationCaseRepository) -> None:
        self._repo = repo

    def execute(self, case_id: uuid.UUID) -> ModerationCaseEntity:
        """
        Return the case matching case_id.

        @param case_id - UUID of the moderation case
        @returns ModerationCaseEntity
        @raises ModerationCaseNotFoundError if absent
        """
        return self._repo.get_by_id(case_id)
