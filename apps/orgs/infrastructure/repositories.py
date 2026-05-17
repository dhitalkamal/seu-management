"""Concrete repository implementations backed by the Django ORM."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity, OrgMemberEntity
from apps.orgs.domain.exceptions import OrgNotFoundError
from apps.orgs.domain.repositories import IOrganisationRepository, IOrgMemberRepository
from apps.orgs.infrastructure.models import Organisation, OrgMember


class DjangoOrgRepository(IOrganisationRepository):
    """Persists Organisation entities using the Django ORM."""

    def create(self, entity: OrgEntity) -> OrgEntity:
        """Persist a new organisation and return the saved entity."""
        obj = Organisation.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def get_by_id(self, org_id: uuid.UUID) -> OrgEntity:
        """Fetch by id, excluding soft-deleted rows. Raises OrgNotFoundError if absent."""
        try:
            return Organisation.objects.get(id=org_id, deleted_at__isnull=True).to_entity()
        except Organisation.DoesNotExist:
            raise OrgNotFoundError("Organisation not found.")

    def get_by_slug(self, slug: str) -> OrgEntity | None:
        """Return the org with this slug or None."""
        try:
            return Organisation.objects.get(slug=slug).to_entity()
        except Organisation.DoesNotExist:
            return None

    def update(self, entity: OrgEntity) -> OrgEntity:
        """Fetch the existing row, update mutable fields, and save."""
        obj = Organisation.objects.get(id=entity.id)
        obj.status = entity.status
        obj.is_verified = entity.is_verified
        obj.deleted_at = entity.deleted_at
        obj.save()
        return obj.to_entity()

    def list_by_user(self, user_id: uuid.UUID) -> list[OrgEntity]:
        """Return all non-deleted orgs where the user has an active membership."""
        org_ids = OrgMember.objects.filter(user_id=user_id, is_active=True).values_list(
            "organisation_id", flat=True
        )
        return [
            obj.to_entity()
            for obj in Organisation.objects.filter(
                id__in=org_ids, deleted_at__isnull=True
            ).order_by("-created_at")
        ]


class DjangoOrgMemberRepository(IOrgMemberRepository):
    """Persists OrgMember entities using the Django ORM."""

    def create(self, entity: OrgMemberEntity) -> OrgMemberEntity:
        """Persist a new membership and return the saved entity."""
        obj = OrgMember.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def exists(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """True if an active membership exists for this (org, user) pair."""
        return OrgMember.objects.filter(
            organisation_id=org_id, user_id=user_id, is_active=True
        ).exists()
