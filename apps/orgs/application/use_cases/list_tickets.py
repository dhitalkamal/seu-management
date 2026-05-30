"""Use case: list all support tickets (admin)."""

from __future__ import annotations

from apps.orgs.domain.support_entities import SupportTicketEntity


class ListTicketsUseCase:
    """Return every support ticket ordered by created_at descending."""

    def __init__(self, repo: object) -> None:
        self._repo = repo

    def execute(self, submitted_by: object = None) -> list[SupportTicketEntity]:
        """Fetch all tickets, or only those by a specific user."""
        return self._repo.list_all(submitted_by=submitted_by)
