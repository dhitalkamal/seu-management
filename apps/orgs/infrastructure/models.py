"""Django ORM models for the orgs domain. Maps to the orgs schema."""

from __future__ import annotations

import uuid

from django.db import models

from apps.orgs.domain.entities import OrgEntity, OrgMemberEntity


class Organisation(models.Model):
    """A platform organisation."""

    class OrgType(models.TextChoices):
        COMPANY = "company", "Company"
        NGO = "ngo", "NGO"
        COMMUNITY = "community", "Community"
        EDUCATIONAL = "educational", "Educational"
        GOVERNMENT = "government", "Government"
        INDIVIDUAL = "individual", "Individual"

    class Status(models.TextChoices):
        PENDING_REVIEW = "pending_review", "Pending Review"
        APPROVED = "approved", "Approved"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"

    class Plan(models.TextChoices):
        FREE = "free", "Free"
        STARTER = "starter", "Starter"
        PRO = "pro", "Pro"
        NGO = "ngo", "NGO"
        ENTERPRISE = "enterprise", "Enterprise"

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
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    org_type = models.CharField(max_length=30, choices=OrgType.choices, default=OrgType.COMPANY)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING_REVIEW)
    is_verified = models.BooleanField(default=False)
    # ! subscription plan — determines platform fee rate and feature limits
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.FREE)
    plan_expires_at = models.DateTimeField(null=True, blank=True)
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
            phone=self.phone,
            address=self.address,
            city=self.city,
            country=self.country,
            org_type=self.org_type,
            facebook_url=self.facebook_url,
            twitter_url=self.twitter_url,
            instagram_url=self.instagram_url,
            linkedin_url=self.linkedin_url,
            deleted_at=self.deleted_at,
            plan=self.plan,
            plan_expires_at=self.plan_expires_at,
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
            phone=entity.phone,
            address=entity.address,
            city=entity.city,
            country=entity.country,
            org_type=entity.org_type,
            facebook_url=entity.facebook_url,
            twitter_url=entity.twitter_url,
            instagram_url=entity.instagram_url,
            linkedin_url=entity.linkedin_url,
            status=entity.status,
            is_verified=entity.is_verified,
            deleted_at=entity.deleted_at,
            plan=entity.plan,
            plan_expires_at=entity.plan_expires_at,
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


class OrgDocument(models.Model):
    """A verification document uploaded during org registration."""

    class DocType(models.TextChoices):
        REGISTRATION_CERT = "registration_cert", "Registration Certificate"
        PAN_CARD = "pan_card", "PAN Card"
        TAX_CLEARANCE = "tax_clearance", "Tax Clearance"
        LOGO = "logo", "Logo"
        OTHER = "other", "Other"

    class Meta:
        db_table = '"orgs"."org_document"'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="documents"
    )
    doc_type = models.CharField(max_length=30, choices=DocType.choices)
    file_url = models.URLField()
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
