"""Use case: update ticket status (admin)."""

from __future__ import annotations

import uuid

from apps.orgs.domain.support_entities import SupportTicketEntity


class UpdateTicketStatusUseCase:
    """Set the status (and optionally priority) on an existing ticket."""

    def __init__(self, repo: object) -> None:
        self._repo = repo

    def execute(
        self,
        ticket_id: uuid.UUID,
        status: str,
        priority: str | None = None,
    ) -> SupportTicketEntity:
        """Update status and return the modified entity."""
        ticket = self._repo.get(ticket_id)
        ticket.status = status
        if priority is not None:
            ticket.priority = priority
        return self._repo.save(ticket)
