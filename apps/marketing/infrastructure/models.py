"""Django ORM models for the marketing domain. Maps to the marketing schema."""

from __future__ import annotations

import uuid

from django.db import models

from apps.marketing.domain.entities import AudienceSegmentEntity, CampaignEntity


class AudienceSegment(models.Model):
    """A named filter set that defines a group of recipients."""

    class Meta:
        db_table = '"marketing"."audience_segment"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.UUIDField()
    name = models.CharField(max_length=255)
    filters = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> AudienceSegmentEntity:
        """Map this ORM row to a pure-Python AudienceSegmentEntity."""
        return AudienceSegmentEntity(
            id=self.id,
            created_by=self.created_by,
            name=self.name,
            filters=self.filters or {},
            created_at=self.created_at,
        )

    @classmethod
    def from_entity(cls, entity: AudienceSegmentEntity) -> "AudienceSegment":
        """Build an unsaved ORM instance from an AudienceSegmentEntity."""
        return cls(
            id=entity.id,
            created_by=entity.created_by,
            name=entity.name,
            filters=entity.filters,
        )


class Campaign(models.Model):
    """An email or push marketing campaign."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        CANCELLED = "cancelled", "Cancelled"

    class Meta:
        db_table = '"marketing"."campaign"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.UUIDField()
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=500)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    segment = models.ForeignKey(
        AudienceSegment, null=True, blank=True, on_delete=models.SET_NULL, related_name="campaigns"
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> CampaignEntity:
        """Map this ORM row to a pure-Python CampaignEntity."""
        return CampaignEntity(
            id=self.id,
            created_by=self.created_by,
            name=self.name,
            subject=self.subject,
            body=self.body,
            status=self.status,
            segment_id=self.segment_id,
            created_at=self.created_at,
            sent_at=self.sent_at,
        )

    @classmethod
    def from_entity(cls, entity: CampaignEntity) -> "Campaign":
        """Build an unsaved ORM instance from a CampaignEntity."""
        return cls(
            id=entity.id,
            created_by=entity.created_by,
            name=entity.name,
            subject=entity.subject,
            body=entity.body,
            status=entity.status,
            segment_id=entity.segment_id,
            sent_at=entity.sent_at,
        )
