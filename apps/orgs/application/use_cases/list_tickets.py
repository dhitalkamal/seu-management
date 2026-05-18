"""Use case: list all support tickets (admin)."""

from __future__ import annotations

from apps.orgs.domain.support_entities import SupportTicketEntity


class ListTicketsUseCase:
    """Return every support ticket ordered by created_at descending."""

    def __init__(self, repo: object) -> None:
        self._repo = repo

    def execute(self) -> list[SupportTicketEntity]:
        """Fetch all tickets."""
        return self._repo.list_all()
