"""Abstract repository interfaces for the moderation module."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from apps.moderation.domain.entities import ModerationCaseEntity


class IModerationCaseRepository(ABC):
    """Persistence contract for ModerationCase aggregates."""

    @abstractmethod
    def list_all(self, status: str | None = None) -> list[ModerationCaseEntity]:
        """Return all cases, optionally filtered by status."""
        ...

    @abstractmethod
    def get_by_id(self, case_id: uuid.UUID) -> ModerationCaseEntity:
        """Fetch a single case by id. Raises ModerationCaseNotFoundError if absent."""
        ...

    @abstractmethod
    def save(self, entity: ModerationCaseEntity) -> ModerationCaseEntity:
        """Persist a new or updated case and return the saved entity."""
        ...

    @abstractmethod
    def update_status(
        self,
        case_id: uuid.UUID,
        status: str,
        reviewer_id: uuid.UUID | None,
        notes: str,
    ) -> ModerationCaseEntity:
        """Update status, reviewer, and notes on an existing case."""
        ...

    @abstractmethod
    def get_stats(self) -> dict:
        """Return KPI counts: pending, decided, approval rate, avg resolution time."""
        ...
