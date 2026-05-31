"""Concrete repository implementations backed by the Django ORM."""

from __future__ import annotations

import uuid

from apps.volunteers.domain.entities import (
    CertificateEntity,
    VolunteerApplicationEntity,
    VolunteerProfileEntity,
    VolunteerRoleEntity,
    VolunteerShiftEntity,
)
from apps.volunteers.domain.exceptions import (
    ApplicationNotFoundError,
    CertificateNotFoundError,
    RoleNotFoundError,
    ShiftNotFoundError,
)
from apps.volunteers.domain.repositories import (
    ICertificateRepository,
    IVolunteerApplicationRepository,
    IVolunteerProfileRepository,
    IVolunteerRoleRepository,
    IVolunteerShiftRepository,
)
from apps.volunteers.infrastructure.models import (
    Certificate,
    VolunteerApplication,
    VolunteerProfile,
    VolunteerRole,
    VolunteerShift,
)


class DjangoVolunteerRoleRepository(IVolunteerRoleRepository):
    """Persists VolunteerRole entities using the Django ORM."""

    def create(self, entity: VolunteerRoleEntity) -> VolunteerRoleEntity:
        """Persist a new role and return the saved entity."""
        obj = VolunteerRole.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def get_by_id(self, role_id: uuid.UUID) -> VolunteerRoleEntity:
        """Fetch by id. Raises RoleNotFoundError if absent."""
        try:
            return VolunteerRole.objects.get(id=role_id).to_entity()
        except VolunteerRole.DoesNotExist:
            raise RoleNotFoundError("Volunteer role not found.")

    def count_approved(self, role_id: uuid.UUID) -> int:
        """Count approved applications for this role (used for capacity check)."""
        return VolunteerApplication.objects.filter(volunteer_role_id=role_id, status="approved").count()


class DjangoVolunteerApplicationRepository(IVolunteerApplicationRepository):
    """Persists VolunteerApplication entities using the Django ORM."""

    def create(self, entity: VolunteerApplicationEntity) -> VolunteerApplicationEntity:
        """Persist a new application and return the saved entity."""
        obj = VolunteerApplication.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def has_active(self, role_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """True if a non-cancelled application exists for this (role, user) pair."""
        return VolunteerApplication.objects.filter(volunteer_role_id=role_id, user_id=user_id).exclude(status="cancelled").exists()

    def get_by_id(self, application_id: uuid.UUID) -> VolunteerApplicationEntity:
        """Fetch by ID. Raises ApplicationNotFoundError if absent."""
        try:
            return VolunteerApplication.objects.get(id=application_id).to_entity()
        except VolunteerApplication.DoesNotExist:
            raise ApplicationNotFoundError("Application not found.")

    def update(self, entity: VolunteerApplicationEntity) -> VolunteerApplicationEntity:
        """Update all mutable fields and return the entity."""
        VolunteerApplication.objects.filter(id=entity.id).update(
            status=entity.status,
            check_in_at=entity.check_in_at,
            check_out_at=entity.check_out_at,
            rating=entity.rating,
            feedback=entity.feedback,
            certificate_issued=entity.certificate_issued,
        )
        return entity

    def list_by_role(self, role_id: uuid.UUID) -> list[VolunteerApplicationEntity]:
        """Return all applications for the given role, newest first."""
        return [obj.to_entity() for obj in VolunteerApplication.objects.filter(volunteer_role_id=role_id).order_by("-created_at")]


class DjangoCertificateRepository(ICertificateRepository):
    """Persists Certificate entities using the Django ORM."""

    def create(self, entity: CertificateEntity) -> CertificateEntity:
        """Persist a new certificate and return the saved entity."""
        obj = Certificate.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def get_by_id(self, certificate_id: uuid.UUID) -> CertificateEntity:
        """Fetch by ID. Raises CertificateNotFoundError if absent."""
        try:
            return Certificate.objects.get(id=certificate_id).to_entity()
        except Certificate.DoesNotExist:
            raise CertificateNotFoundError("Certificate not found.")


class DjangoVolunteerShiftRepository(IVolunteerShiftRepository):
    """Persists VolunteerShift entities using the Django ORM."""

    def create(self, entity: VolunteerShiftEntity) -> VolunteerShiftEntity:
        """Persist a new shift and return the saved entity."""
        obj = VolunteerShift.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def get_by_id(self, shift_id: uuid.UUID) -> VolunteerShiftEntity:
        """Fetch by ID. Raises ShiftNotFoundError if absent."""
        try:
            return VolunteerShift.objects.get(id=shift_id).to_entity()
        except VolunteerShift.DoesNotExist:
            raise ShiftNotFoundError("Volunteer shift not found.")

    def list_by_role(self, role_id: uuid.UUID) -> list[VolunteerShiftEntity]:
        """Return all shifts for the given role, ordered by start time."""
        return [obj.to_entity() for obj in VolunteerShift.objects.filter(role_id=role_id).order_by("starts_at")]


class DjangoVolunteerProfileRepository(IVolunteerProfileRepository):
    """Persists VolunteerProfile entities using the Django ORM."""

    def get_or_create(self, user_id: uuid.UUID) -> VolunteerProfileEntity:
        """Return existing profile or create a blank one for this user."""
        import uuid as _uuid

        obj, _ = VolunteerProfile.objects.get_or_create(
            user_id=user_id,
            defaults={"id": _uuid.uuid4()},
        )
        return obj.to_entity()

    def get_by_user_id(self, user_id: uuid.UUID) -> VolunteerProfileEntity:
        """Delegate to get_or_create."""
        return self.get_or_create(user_id)

    def update(self, entity: VolunteerProfileEntity) -> VolunteerProfileEntity:
        """Update mutable stats fields and return the entity."""
        VolunteerProfile.objects.filter(user_id=entity.user_id).update(
            average_rating=entity.average_rating,
            total_ratings=entity.total_ratings,
            total_hours=entity.total_hours,
            certificate_count=entity.certificate_count,
        )
        return entity
