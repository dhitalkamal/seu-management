"""Django ORM model for support tickets, stored in the orgs schema."""

from __future__ import annotations

import uuid

from django.db import models

from apps.orgs.domain.support_entities import SupportTicketEntity


class SupportTicket(models.Model):
    """A platform support ticket."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MED = "med", "Med"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        ESCALATED = "escalated", "Escalated"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    class Meta:
        db_table = "orgs_support_ticket"
        ordering = ["-created_at"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=500)
    message = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MED)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    org_id = models.UUIDField(null=True, blank=True)
    org_name = models.CharField(max_length=255, blank=True)
    submitted_by = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_entity(self) -> SupportTicketEntity:
        """Convert to domain entity."""
        return SupportTicketEntity(
            id=self.id,
            subject=self.subject,
            message=self.message,
            priority=self.priority,
            status=self.status,
            org_id=self.org_id,
            org_name=self.org_name,
            submitted_by=self.submitted_by,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )
