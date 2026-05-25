"""Django ORM models for the volunteers domain. Maps to the volunteers schema."""

from __future__ import annotations

import uuid

from django.db import models

from apps.volunteers.domain.entities import VolunteerApplicationEntity, VolunteerRoleEntity


class VolunteerRole(models.Model):
    """A volunteer position for an event."""

    class Meta:
        db_table = '"volunteers"."volunteer_role"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.UUIDField()
    organisation_id = models.UUIDField(null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> VolunteerRoleEntity:
        """Map this ORM row to a pure-Python VolunteerRoleEntity."""
        return VolunteerRoleEntity(
            id=self.id,
            event_id=self.event_id,
            name=self.name,
            capacity=self.capacity,
            is_active=self.is_active,
            created_at=self.created_at,
            organisation_id=self.organisation_id,
            description=self.description,
        )

    @classmethod
    def from_entity(cls, entity: VolunteerRoleEntity) -> "VolunteerRole":
        """Build an unsaved ORM instance from a VolunteerRoleEntity."""
        return cls(
            id=entity.id,
            event_id=entity.event_id,
            organisation_id=entity.organisation_id,
            name=entity.name,
            description=entity.description,
            capacity=entity.capacity,
            is_active=entity.is_active,
        )


class VolunteerApplication(models.Model):
    """A user's application to fill a volunteer role."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        CONFIRMED = "confirmed", "Confirmed"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    class Meta:
        db_table = '"volunteers"."volunteer_application"'
        constraints = [
            models.UniqueConstraint(
                fields=["volunteer_role", "user_id"],
                name="unique_volunteer_application",
            )
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    volunteer_role = models.ForeignKey(VolunteerRole, on_delete=models.CASCADE, related_name="applications")
    user_id = models.UUIDField()
    event_id = models.UUIDField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    check_in_at = models.DateTimeField(null=True, blank=True)
    check_out_at = models.DateTimeField(null=True, blank=True)
    rating = models.SmallIntegerField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_entity(self) -> VolunteerApplicationEntity:
        """Map this ORM row to a pure-Python VolunteerApplicationEntity."""
        return VolunteerApplicationEntity(
            id=self.id,
            volunteer_role_id=self.volunteer_role_id,
            user_id=self.user_id,
            event_id=self.event_id,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            check_in_at=self.check_in_at,
            check_out_at=self.check_out_at,
            rating=self.rating,
            feedback=self.feedback,
            certificate_issued=self.certificate_issued,
        )

    @classmethod
    def from_entity(cls, entity: VolunteerApplicationEntity) -> "VolunteerApplication":
        """Build an unsaved ORM instance from a VolunteerApplicationEntity."""
        return cls(
            id=entity.id,
            volunteer_role_id=entity.volunteer_role_id,
            user_id=entity.user_id,
            event_id=entity.event_id,
            status=entity.status,
            check_in_at=entity.check_in_at,
            check_out_at=entity.check_out_at,
            rating=entity.rating,
            feedback=entity.feedback,
            certificate_issued=entity.certificate_issued,
        )
