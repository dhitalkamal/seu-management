"""Django ORM model for the moderation domain. Maps to the management schema."""

from __future__ import annotations

import uuid

from django.db import models

from apps.moderation.domain.entities import ModerationCaseEntity


class ModerationCase(models.Model):
    """A flagged content item tracked by superadmins."""

    class ContentType(models.TextChoices):
        EVENT = "event", "Event"
        POST = "post", "Post"
        COMMENT = "comment", "Comment"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        UNDER_REVIEW = "under_review", "Under Review"
        DISMISSED = "dismissed", "Dismissed"
        WARNED = "warned", "Warned"
        TAKEN_DOWN = "taken_down", "Taken Down"

    class Meta:
        db_table = '"management"."moderation_case"'
        indexes = [
            models.Index(fields=["status"], name="moderation_case_status_idx"),
            models.Index(fields=["created_at"], name="moderation_case_created_idx"),
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.CharField(max_length=20, choices=ContentType.choices)
    content_id = models.UUIDField()
    content_title = models.CharField(max_length=500)
    reporter_id = models.UUIDField(null=True, blank=True)
    organisation_id = models.UUIDField(null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewer_id = models.UUIDField(null=True, blank=True)
    reviewer_notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def to_entity(self) -> ModerationCaseEntity:
        """Map this ORM row to a pure-Python ModerationCaseEntity."""
        return ModerationCaseEntity(
            id=self.id,
            content_type=self.content_type,
            content_id=self.content_id,
            content_title=self.content_title,
            reporter_id=self.reporter_id,
            organisation_id=self.organisation_id,
            reason=self.reason,
            status=self.status,
            reviewer_id=self.reviewer_id,
            reviewer_notes=self.reviewer_notes,
            created_at=self.created_at,
            resolved_at=self.resolved_at,
        )

    @classmethod
    def from_entity(cls, entity: ModerationCaseEntity) -> "ModerationCase":
        """Build an unsaved ORM instance from a ModerationCaseEntity."""
        return cls(
            id=entity.id,
            content_type=entity.content_type,
            content_id=entity.content_id,
            content_title=entity.content_title,
            reporter_id=entity.reporter_id,
            organisation_id=entity.organisation_id,
            reason=entity.reason,
            status=entity.status,
            reviewer_id=entity.reviewer_id,
            reviewer_notes=entity.reviewer_notes,
            resolved_at=entity.resolved_at,
        )
