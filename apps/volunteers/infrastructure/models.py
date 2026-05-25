"""Django ORM models for the volunteers domain. Maps to the volunteers schema."""

from __future__ import annotations

import uuid

from django.db import models

from apps.volunteers.domain.entities import (
    CertificateEntity,
    VolunteerApplicationEntity,
    VolunteerProfileEntity,
    VolunteerRoleEntity,
    VolunteerShiftEntity,
)


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
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"
        CONFIRMED = "confirmed", "Confirmed"

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
    feedback = models.TextField(blank=True, null=True)
    certificate_issued = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_entity(self) -> VolunteerApplicationEntity:
        """Map this ORM row to a pure-Python VolunteerApplicationEntity."""
        return VolunteerApplicationEntity(
            id=self.id,
            volunteer_role_id=self.volunteer_role_id,  # type: ignore[attr-defined]
            user_id=self.user_id,
            event_id=self.event_id,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
            check_in_at=self.check_in_at,
            check_out_at=self.check_out_at,
            rating=self.rating,
            certificate_issued=self.certificate_issued,
            feedback=self.feedback,
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


class Certificate(models.Model):
    """An issued participation certificate for a volunteer."""

    class Meta:
        db_table = '"volunteers"."certificate"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.OneToOneField(VolunteerApplication, on_delete=models.CASCADE, related_name="certificate")
    user_id = models.UUIDField()
    event_id = models.UUIDField()
    pdf_url = models.TextField()
    verify_url = models.TextField()
    issued_at = models.DateTimeField()

    def to_entity(self) -> CertificateEntity:
        """Map this ORM row to a pure-Python CertificateEntity."""
        return CertificateEntity(
            id=self.id,
            application_id=self.application_id,  # type: ignore[attr-defined]
            user_id=self.user_id,
            event_id=self.event_id,
            pdf_url=self.pdf_url,
            verify_url=self.verify_url,
            issued_at=self.issued_at,
        )

    @classmethod
    def from_entity(cls, entity: CertificateEntity) -> "Certificate":
        """Build an unsaved ORM instance from a CertificateEntity."""
        return cls(
            id=entity.id,
            application_id=entity.application_id,
            user_id=entity.user_id,
            event_id=entity.event_id,
            pdf_url=entity.pdf_url,
            verify_url=entity.verify_url,
            issued_at=entity.issued_at,
        )


class VolunteerShift(models.Model):
    """A time-boxed shift slot attached to a volunteer role."""

    class Meta:
        db_table = '"volunteers"."volunteer_shift"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(VolunteerRole, on_delete=models.CASCADE, related_name="shifts")
    event_id = models.UUIDField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> VolunteerShiftEntity:
        """Map this ORM row to a pure-Python VolunteerShiftEntity."""
        return VolunteerShiftEntity(
            id=self.id,
            role_id=self.role_id,  # type: ignore[attr-defined]
            event_id=self.event_id,
            starts_at=self.starts_at,
            ends_at=self.ends_at,
            capacity=self.capacity,
            created_at=self.created_at,
            location=self.location,
            description=self.description,
        )

    @classmethod
    def from_entity(cls, entity: VolunteerShiftEntity) -> "VolunteerShift":
        """Build an unsaved ORM instance from a VolunteerShiftEntity."""
        return cls(
            id=entity.id,
            role_id=entity.role_id,
            event_id=entity.event_id,
            starts_at=entity.starts_at,
            ends_at=entity.ends_at,
            capacity=entity.capacity,
            location=entity.location,
            description=entity.description,
        )


class VolunteerProfile(models.Model):
    """Aggregate stats for a single volunteer user across all events."""

    class Meta:
        db_table = '"volunteers"."volunteer_profile"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True)
    average_rating = models.FloatField(null=True, blank=True)
    total_ratings = models.PositiveIntegerField(default=0)
    total_hours = models.FloatField(default=0.0)
    certificate_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def to_entity(self) -> VolunteerProfileEntity:
        """Map this ORM row to a pure-Python VolunteerProfileEntity."""
        return VolunteerProfileEntity(
            id=self.id,
            user_id=self.user_id,
            average_rating=self.average_rating,
            total_ratings=self.total_ratings,
            total_hours=self.total_hours,
            certificate_count=self.certificate_count,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, entity: VolunteerProfileEntity) -> "VolunteerProfile":
        """Build an unsaved ORM instance from a VolunteerProfileEntity."""
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            average_rating=entity.average_rating,
            total_ratings=entity.total_ratings,
            total_hours=entity.total_hours,
            certificate_count=entity.certificate_count,
        )
