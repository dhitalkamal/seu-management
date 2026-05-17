"""Use case: create a new audience segment."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.marketing.domain.entities import AudienceSegmentEntity
from apps.marketing.domain.repositories import IAudienceSegmentRepository


class CreateSegmentUseCase:
    """Create a new audience segment."""

    def __init__(self, repo: IAudienceSegmentRepository) -> None:
        self._repo = repo

    def execute(
        self,
        *,
        created_by: uuid.UUID,
        name: str,
        filters: dict,
    ) -> AudienceSegmentEntity:
        """Persist a new segment and return it."""
        segment = AudienceSegmentEntity(
            id=uuid.uuid4(),
            created_by=created_by,
            name=name,
            filters=filters,
            created_at=datetime.now(timezone.utc),
        )
        self._repo.create(segment)
        return segment
