"""Django ORM repository for support tickets."""

from __future__ import annotations

import uuid

from apps.orgs.domain.support_entities import SupportTicketEntity
from apps.orgs.infrastructure.support_models import SupportTicket


class DjangoSupportTicketRepository:
    """CRUD operations for SupportTicket backed by Django ORM."""

    def list_all(self) -> list[SupportTicketEntity]:
        """Return all tickets ordered by created_at descending."""
        return [t.to_entity() for t in SupportTicket.objects.all()]

    def get(self, ticket_id: uuid.UUID) -> SupportTicketEntity:
        """Raise DoesNotExist if ticket not found."""
        return SupportTicket.objects.get(pk=ticket_id).to_entity()

    def save(self, entity: SupportTicketEntity) -> SupportTicketEntity:
        """Insert or update the ticket and return the saved entity."""
        obj, _ = SupportTicket.objects.update_or_create(
            pk=entity.id,
            defaults={
                "subject": entity.subject,
                "message": entity.message,
                "priority": entity.priority,
                "status": entity.status,
                "org_id": entity.org_id,
                "org_name": entity.org_name,
                "submitted_by": entity.submitted_by,
            },
        )
        return obj.to_entity()
