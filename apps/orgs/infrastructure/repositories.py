"""Concrete repository implementations backed by the Django ORM."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity, OrgInviteEntity, OrgMemberEntity
from apps.orgs.domain.exceptions import InviteNotFoundError, OrgNotFoundError
from apps.orgs.domain.repositories import IOrganizationRepository, IOrgInviteRepository, IOrgMemberRepository
from apps.orgs.infrastructure.models import Organization, OrgDocument, OrgInvite, OrgMember


class DjangoOrgRepository(IOrganizationRepository):
    """Persists Organization entities using the Django ORM."""

    def create(self, entity: OrgEntity) -> OrgEntity:
        """Persist a new organization and return the saved entity."""
        obj = Organization.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def get_by_id(self, org_id: uuid.UUID) -> OrgEntity:
        """Fetch by id, excluding soft-deleted rows. Raises OrgNotFoundError if absent."""
        try:
            return Organization.objects.get(id=org_id, deleted_at__isnull=True).to_entity()
        except Organization.DoesNotExist:
            raise OrgNotFoundError("Organization not found.")

    def get_by_slug(self, slug: str) -> OrgEntity | None:
        """Return the org with this slug or None."""
        try:
            return Organization.objects.get(slug=slug).to_entity()
        except Organization.DoesNotExist:
            return None

    def update(self, entity: OrgEntity) -> OrgEntity:
        """Fetch the existing row, sync every mutable field, and save."""
        obj = Organization.objects.get(id=entity.id)
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
        org_ids = OrgMember.objects.filter(user_id=user_id, is_active=True).values_list("organization_id", flat=True)
        return [obj.to_entity() for obj in Organization.objects.filter(id__in=org_ids, deleted_at__isnull=True).order_by("-created_at")]

    def list_all(self) -> list[OrgEntity]:
        """Return all non-deleted orgs (superadmin use)."""
        return [obj.to_entity() for obj in Organization.objects.filter(deleted_at__isnull=True).order_by("-created_at")]


class DjangoOrgMemberRepository(IOrgMemberRepository):
    """Persists OrgMember entities using the Django ORM."""

    def create(self, entity: OrgMemberEntity) -> OrgMemberEntity:
        """Persist a new membership and return the saved entity."""
        obj = OrgMember.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def exists(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """True if an active membership exists for this (org, user) pair."""
        return OrgMember.objects.filter(organization_id=org_id, user_id=user_id, is_active=True).exists()

    def list_by_org(self, org_id: uuid.UUID) -> list:
        """Return all active members for this organization."""
        return list(OrgMember.objects.filter(organization_id=org_id, is_active=True).order_by("-joined_at"))


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
            organization_id=org_id,
            doc_type=doc_type,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size,
        )

    def list_for_org(self, org_id: uuid.UUID) -> list[OrgDocument]:
        """Return all documents for an organization, newest first."""
        return list(OrgDocument.objects.filter(organization_id=org_id).order_by("-uploaded_at"))

    def delete(self, doc_id: uuid.UUID) -> None:
        """Delete a document by primary key."""
        OrgDocument.objects.filter(pk=doc_id).delete()


class DjangoOrgInviteRepository(IOrgInviteRepository):
    """Persists OrgInvite entities using the Django ORM."""

    def create(self, entity: OrgInviteEntity) -> OrgInviteEntity:
        """Persist a new invite and return the saved entity."""
        obj = OrgInvite.from_entity(entity)
        obj.save(using="default")
        return obj.to_entity()

    def get_by_id(self, invite_id: uuid.UUID) -> OrgInviteEntity:
        """Fetch by primary key. Raises InviteNotFoundError if absent."""
        try:
            return OrgInvite.objects.get(id=invite_id).to_entity()
        except OrgInvite.DoesNotExist:
            raise InviteNotFoundError("Invite not found.")

    def update(self, entity: OrgInviteEntity) -> OrgInviteEntity:
        """Overwrite status and accepted_by on the stored row."""
        OrgInvite.objects.filter(id=entity.id).update(
            status=entity.status,
            accepted_by=entity.accepted_by,
        )
        return entity

    def list_pending_for_org(self, org_id: uuid.UUID) -> list[OrgInviteEntity]:
        """Return all pending invites for an org, newest first."""
        qs = OrgInvite.objects.filter(org_id=org_id, status="pending").order_by("-created_at")
        return [obj.to_entity() for obj in qs]

    def get_pending_by_email(self, org_id: uuid.UUID, email: str) -> OrgInviteEntity | None:
        """Return the pending invite for this email at this org, or None."""
        try:
            return OrgInvite.objects.get(org_id=org_id, invitee_email__iexact=email, status="pending").to_entity()
        except OrgInvite.DoesNotExist:
            return None
