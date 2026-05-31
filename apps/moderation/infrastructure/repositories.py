"""Concrete repository implementation backed by the Django ORM."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.moderation.domain.entities import ModerationCaseEntity
from apps.moderation.domain.exceptions import ModerationCaseNotFoundError
from apps.moderation.domain.repositories import IModerationCaseRepository
from apps.moderation.infrastructure.models import ModerationCase

# terminal statuses that set resolved_at when reached
_TERMINAL_STATUSES = {"dismissed", "warned", "taken_down"}


class DjangoModerationCaseRepository(IModerationCaseRepository):
    """Persists ModerationCase entities using the Django ORM."""

    def list_all(self, status: str | None = None) -> list[ModerationCaseEntity]:
        """Return all cases ordered by created_at descending, filtered by status if given."""
        qs = ModerationCase.objects.all().order_by("-created_at")
        if status is not None:
            qs = qs.filter(status=status)
        return [obj.to_entity() for obj in qs]

    def get_by_id(self, case_id: uuid.UUID) -> ModerationCaseEntity:
        """Fetch by id. Raises ModerationCaseNotFoundError if absent."""
        try:
            return ModerationCase.objects.get(id=case_id).to_entity()
        except ModerationCase.DoesNotExist:
            raise ModerationCaseNotFoundError(f"Moderation case {case_id} not found.")

    def save(self, entity: ModerationCaseEntity) -> ModerationCaseEntity:
        """Persist a new case and return the saved entity."""
        obj = ModerationCase.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def update_status(
        self,
        case_id: uuid.UUID,
        status: str,
        reviewer_id: uuid.UUID | None,
        notes: str,
    ) -> ModerationCaseEntity:
        """Update status, reviewer, and notes. Sets resolved_at for terminal statuses."""
        try:
            obj = ModerationCase.objects.get(id=case_id)
        except ModerationCase.DoesNotExist:
            raise ModerationCaseNotFoundError(f"Moderation case {case_id} not found.")

        obj.status = status
        obj.reviewer_id = reviewer_id
        obj.reviewer_notes = notes

        # set resolved_at the first time a terminal status is reached
        if status in _TERMINAL_STATUSES and obj.resolved_at is None:
            obj.resolved_at = datetime.now(timezone.utc)

        obj.save(update_fields=["status", "reviewer_id", "reviewer_notes", "resolved_at"])
        return obj.to_entity()

    def get_stats(self) -> dict:
        """Compute KPI counts and averages from the database."""
        qs = ModerationCase.objects.all()

        total = qs.count()
        pending = qs.filter(status="pending").count()
        under_review = qs.filter(status="under_review").count()
        dismissed = qs.filter(status="dismissed").count()
        warned = qs.filter(status="warned").count()
        taken_down = qs.filter(status="taken_down").count()
        decided = dismissed + warned + taken_down

        approval_rate = round((dismissed + warned) / decided * 100, 1) if decided > 0 else 0.0

        # avg resolution time in hours using database-side arithmetic
        resolved_qs = qs.filter(resolved_at__isnull=False)
        avg_hours = 0.0
        if resolved_qs.exists():
            # compute duration in seconds per row then average
            durations = [(obj.resolved_at - obj.created_at).total_seconds() / 3600 for obj in resolved_qs]
            avg_hours = round(sum(durations) / len(durations), 1)

        return {
            "total": total,
            "pending": pending,
            "under_review": under_review,
            "dismissed": dismissed,
            "warned": warned,
            "taken_down": taken_down,
            "decided": decided,
            "approval_rate": approval_rate,
            "avg_resolution_hours": avg_hours,
        }
