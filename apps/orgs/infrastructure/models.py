"""Django ORM models for the orgs domain. Maps to the orgs schema."""

from __future__ import annotations

import uuid

from django.db import models

from apps.orgs.domain.entities import OrgEntity, OrgMemberEntity


class Organisation(models.Model):
    """A platform organisation."""

    class Status(models.TextChoices):
        PENDING_REVIEW = "pending_review", "Pending Review"
        APPROVED = "approved", "Approved"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"

    class Meta:
        db_table = '"orgs"."organisation"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.UUIDField()
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    contact_email = models.EmailField()
    website = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING_REVIEW)
    is_verified = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_entity(self) -> OrgEntity:
        """Map this ORM row to a pure-Python OrgEntity."""
        return OrgEntity(
            id=self.id,
            created_by=self.created_by,
            name=self.name,
            slug=self.slug,
            contact_email=self.contact_email,
            status=self.status,
            is_verified=self.is_verified,
            created_at=self.created_at,
            updated_at=self.updated_at,
            description=self.description,
            website=self.website,
            logo_url=self.logo_url,
            deleted_at=self.deleted_at,
        )

    @classmethod
    def from_entity(cls, entity: OrgEntity) -> "Organisation":
        """Build an unsaved ORM instance from an OrgEntity."""
        return cls(
            id=entity.id,
            created_by=entity.created_by,
            name=entity.name,
            slug=entity.slug,
            contact_email=entity.contact_email,
            description=entity.description,
            website=entity.website,
            logo_url=entity.logo_url,
            status=entity.status,
            is_verified=entity.is_verified,
            deleted_at=entity.deleted_at,
        )


class OrgMember(models.Model):
    """A membership record linking a user to an organisation."""

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        MEMBER = "member", "Member"

    class Meta:
        db_table = '"orgs"."org_member"'
        constraints = [
            models.UniqueConstraint(
                fields=["organisation", "user_id"],
                name="unique_org_member",
            )
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name="members")
    user_id = models.UUIDField()
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def to_entity(self) -> OrgMemberEntity:
        """Map this ORM row to a pure-Python OrgMemberEntity."""
        return OrgMemberEntity(
            id=self.id,
            organisation_id=self.organisation_id,
            user_id=self.user_id,
            role=self.role,
            is_active=self.is_active,
            joined_at=self.joined_at,
        )

    @classmethod
    def from_entity(cls, entity: OrgMemberEntity) -> "OrgMember":
        """Build an unsaved ORM instance from an OrgMemberEntity."""
        return cls(
            id=entity.id,
            organisation_id=entity.organisation_id,
            user_id=entity.user_id,
            role=entity.role,
            is_active=entity.is_active,
        )


class AllowedDomain(models.Model):
    """Whitelisted email domain for an organisation's private events."""

    class MatchType(models.TextChoices):
        EXACT = "exact", "Exact match (e.g. company.com)"
        WILDCARD = "wildcard", "Wildcard (e.g. *.company.com)"

    class Meta:
        db_table = '"orgs"."allowed_domain"'
        constraints = [
            models.UniqueConstraint(
                fields=["organisation", "domain"],
                name="unique_org_allowed_domain",
            )
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="allowed_domains"
    )
    domain = models.CharField(max_length=253)
    match_type = models.CharField(max_length=10, choices=MatchType.choices, default=MatchType.EXACT)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
