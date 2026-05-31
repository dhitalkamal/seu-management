"""Use case: update the status of a moderation case."""

from __future__ import annotations

import uuid

from apps.moderation.domain.entities import ModerationCaseEntity
from apps.moderation.domain.exceptions import InvalidStatusTransitionError
from apps.moderation.domain.repositories import IModerationCaseRepository

# valid transitions: current_status -> set of allowed next statuses
# terminal statuses (dismissed, warned, taken_down) cannot be changed
_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"under_review"},
    "under_review": {"dismissed", "warned", "taken_down"},
    "dismissed": set(),
    "warned": set(),
    "taken_down": set(),
}


class UpdateCaseStatusUseCase:
    """Change the status of a moderation case, enforcing allowed transitions."""

    def __init__(self, repo: IModerationCaseRepository) -> None:
        self._repo = repo

    def execute(
        self,
        *,
        case_id: uuid.UUID,
        status: str,
        reviewer_id: uuid.UUID | None,
        reviewer_notes: str,
    ) -> ModerationCaseEntity:
        """
        Validate the transition and persist the status change.

        @param case_id - UUID of the case to update
        @param status - target status to transition to
        @param reviewer_id - UUID of the admin performing the review
        @param reviewer_notes - free-text notes from the reviewer
        @returns updated ModerationCaseEntity
        @raises ModerationCaseNotFoundError if the case does not exist
        @raises InvalidStatusTransitionError if the transition is not allowed
        """
        entity = self._repo.get_by_id(case_id)

        allowed = _TRANSITIONS.get(entity.status, set())
        if status not in allowed:
            raise InvalidStatusTransitionError(f"Cannot transition from '{entity.status}' to '{status}'.")

        return self._repo.update_status(
            case_id=case_id,
            status=status,
            reviewer_id=reviewer_id,
            notes=reviewer_notes,
        )
