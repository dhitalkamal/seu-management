"""Use case: create a new support ticket."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.orgs.domain.support_entities import SupportTicketEntity


class CreateTicketUseCase:
    """Persist a new support ticket and return the saved entity."""

    def __init__(self, repo: object) -> None:
        self._repo = repo

    def execute(
        self,
        subject: str,
        message: str,
        priority: str,
        org_id: uuid.UUID | None,
        org_name: str,
        submitted_by: uuid.UUID | None,
    ) -> SupportTicketEntity:
        """Create and save the ticket."""
        now = datetime.now(timezone.utc)
        ticket = SupportTicketEntity(
            id=uuid.uuid4(),
            subject=subject,
            message=message,
            priority=priority,
            status="open",
            org_id=org_id,
            org_name=org_name,
            submitted_by=submitted_by,
            created_at=now,
            updated_at=now,
        )
        return self._repo.save(ticket)
