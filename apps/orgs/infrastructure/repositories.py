"""Concrete repository implementations backed by the Django ORM."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity, OrgMemberEntity
from apps.orgs.domain.exceptions import OrgNotFoundError
from apps.orgs.domain.repositories import IOrganisationRepository, IOrgMemberRepository
from apps.orgs.infrastructure.models import Organisation, OrgDocument, OrgMember


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
        """Fetch the existing row, sync every mutable field, and save."""
        obj = Organisation.objects.get(id=entity.id)
        # * profile fields
        obj.name = entity.name
        obj.description = entity.description
        obj.contact_email = entity.contact_email
        obj.website = entity.website
        obj.logo_url = entity.logo_url
        obj.phone = entity.phone
        obj.address = entity.address
        obj.city = entity.city
        obj.country = entity.country
        obj.org_type = entity.org_type
        # * social links
        obj.facebook_url = entity.facebook_url
        obj.twitter_url = entity.twitter_url
        obj.instagram_url = entity.instagram_url
        obj.linkedin_url = entity.linkedin_url
        # * lifecycle + billing
        obj.status = entity.status
        obj.is_verified = entity.is_verified
        obj.deleted_at = entity.deleted_at
        obj.plan = entity.plan
        obj.plan_expires_at = entity.plan_expires_at
        # * review audit trail
        obj.reviewed_at = entity.reviewed_at
        obj.reviewed_by = entity.reviewed_by
        obj.save()
        return obj.to_entity()

    def list_by_user(self, user_id: uuid.UUID) -> list[OrgEntity]:
        """Return all non-deleted orgs where the user has an active membership."""
        org_ids = OrgMember.objects.filter(user_id=user_id, is_active=True).values_list("organisation_id", flat=True)
        return [obj.to_entity() for obj in Organisation.objects.filter(id__in=org_ids, deleted_at__isnull=True).order_by("-created_at")]


class DjangoOrgMemberRepository(IOrgMemberRepository):
    """Persists OrgMember entities using the Django ORM."""

    def create(self, entity: OrgMemberEntity) -> OrgMemberEntity:
        """Persist a new membership and return the saved entity."""
        obj = OrgMember.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def exists(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """True if an active membership exists for this (org, user) pair."""
        return OrgMember.objects.filter(organisation_id=org_id, user_id=user_id, is_active=True).exists()


class DjangoOrgDocumentRepository:
    """CRUD operations for OrgDocument backed by Django ORM."""

    def create(
        self,
        org_id: uuid.UUID,
        doc_type: str,
        file_url: str,
        file_name: str,
        file_size: int,
    ) -> OrgDocument:
        """Persist a new document record and return the ORM object."""
        return OrgDocument.objects.create(
            organisation_id=org_id,
            doc_type=doc_type,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
        )

    def list_for_org(self, org_id: uuid.UUID) -> list[OrgDocument]:
        """Return all documents for an organisation, newest first."""
        return list(OrgDocument.objects.filter(organisation_id=org_id).order_by("-uploaded_at"))

    def delete(self, doc_id: uuid.UUID) -> None:
        """Delete a document by primary key."""
        OrgDocument.objects.filter(pk=doc_id).delete()
