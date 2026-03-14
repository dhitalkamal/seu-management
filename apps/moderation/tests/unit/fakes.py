"""Hand-rolled in-memory fakes for moderation repository interfaces."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Sequence

from apps.moderation.domain.entities import ModerationCaseEntity
from apps.moderation.domain.exceptions import ModerationCaseNotFoundError
from apps.moderation.domain.repositories import IModerationCaseRepository


def _now() -> datetime:
    return datetime.now(timezone.utc)


def make_case(**kwargs: object) -> ModerationCaseEntity:
    """Build a ModerationCaseEntity with sensible defaults for testing."""
    now = _now()
    defaults: dict = {
        "id": uuid.uuid4(),
        "content_type": "event",
        "content_id": uuid.uuid4(),
        "content_title": "Test Event",
        "reporter_id": uuid.uuid4(),
        "organisation_id": uuid.uuid4(),
        "reason": "Inappropriate content",
        "status": "pending",
        "reviewer_id": None,
        "reviewer_notes": "",
        "created_at": now,
        "resolved_at": None,
    }
    defaults.update(kwargs)
    return ModerationCaseEntity(**defaults)  # type: ignore[arg-type]


class FakeModerationCaseRepository(IModerationCaseRepository):
    """In-memory moderation case store for unit tests."""

    def __init__(self, cases: Sequence[ModerationCaseEntity] | None = None) -> None:
        self._store: dict[uuid.UUID, ModerationCaseEntity] = {c.id: c for c in (cases or [])}

    def list_all(self, status: str | None = None) -> list[ModerationCaseEntity]:
        """Return all cases, optionally filtered by status."""
        cases = list(self._store.values())
        if status is not None:
            cases = [c for c in cases if c.status == status]
        return sorted(cases, key=lambda c: c.created_at, reverse=True)

    def get_by_id(self, case_id: uuid.UUID) -> ModerationCaseEntity:
        """Raise ModerationCaseNotFoundError if absent."""
        entity = self._store.get(case_id)
        if entity is None:
            raise ModerationCaseNotFoundError(f"Moderation case {case_id} not found.")
        return entity

    def save(self, entity: ModerationCaseEntity) -> ModerationCaseEntity:
        """Persist and return the entity."""
        self._store[entity.id] = entity
        return entity

    def update_status(
        self,
        case_id: uuid.UUID,
        status: str,
        reviewer_id: uuid.UUID | None,
        notes: str,
    ) -> ModerationCaseEntity:
        """Update status fields and return the updated entity."""
        entity = self.get_by_id(case_id)
        now = _now()
        resolved_at = entity.resolved_at
        # mark resolved_at when the case reaches a terminal status
        terminal = {"dismissed", "warned", "taken_down"}
        if status in terminal and resolved_at is None:
            resolved_at = now
        updated = ModerationCaseEntity(
            id=entity.id,
            content_type=entity.content_type,
            content_id=entity.content_id,
            content_title=entity.content_title,
            reporter_id=entity.reporter_id,
            organisation_id=entity.organisation_id,
            reason=entity.reason,
            status=status,
            reviewer_id=reviewer_id,
            reviewer_notes=notes,
            created_at=entity.created_at,
            resolved_at=resolved_at,
        )
        self._store[entity.id] = updated
        return updated

    def get_stats(self) -> dict:
        """Compute KPI stats from in-memory store."""
        cases = list(self._store.values())
        total = len(cases)
        pending = sum(1 for c in cases if c.status == "pending")
        under_review = sum(1 for c in cases if c.status == "under_review")
        dismissed = sum(1 for c in cases if c.status == "dismissed")
        warned = sum(1 for c in cases if c.status == "warned")
        taken_down = sum(1 for c in cases if c.status == "taken_down")
        decided = dismissed + warned + taken_down

        # approval rate = cases NOT taken down out of decided cases
        approval_rate = round((dismissed + warned) / decided * 100, 1) if decided > 0 else 0.0

        # avg resolution time in hours for resolved cases
        resolved = [c for c in cases if c.resolved_at is not None]
        if resolved:
            deltas = [(c.resolved_at - c.created_at).total_seconds() / 3600 for c in resolved]
            avg_resolution_hours = round(sum(deltas) / len(deltas), 1)
        else:
            avg_resolution_hours = 0.0

        return {
            "total": total,
            "pending": pending,
            "under_review": under_review,
            "dismissed": dismissed,
            "warned": warned,
            "taken_down": taken_down,
            "decided": decided,
            "approval_rate": approval_rate,
            "avg_resolution_hours": avg_resolution_hours,
        }
