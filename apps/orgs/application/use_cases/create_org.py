"""Use case: create a new organization and assign the creator as owner."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.orgs.domain.entities import OrgEntity, OrgMemberEntity
from apps.orgs.domain.exceptions import OrgSlugTakenError
from apps.orgs.domain.repositories import IOrganizationRepository, IOrgMemberRepository


class CreateOrganizationUseCase:
    """Create an organization in pending_review status and assign the creator as owner."""

    def __init__(
        self,
        org_repo: IOrganizationRepository,
        member_repo: IOrgMemberRepository,
    ) -> None:
        self._orgs = org_repo
        self._members = member_repo

    def execute(
        self,
        *,
        created_by: uuid.UUID,
        name: str,
        slug: str,
        contact_email: str,
        description: str = "",
        website: str = "",
        logo_url: str = "",
        phone: str = "",
        address: str = "",
        city: str = "",
        country: str = "",
        org_type: str = "company",
        facebook_url: str = "",
        twitter_url: str = "",
        instagram_url: str = "",
        linkedin_url: str = "",
    ) -> OrgEntity:
        """
        Validate slug uniqueness, persist the org, and create the owner membership.

        @param created_by - UUID from JWT; becomes the first owner member
        @param name - organization display name
        @param slug - URL-safe unique identifier
        @param contact_email - primary contact email
        @returns the persisted OrgEntity with status=pending_review
        @raises OrgSlugTakenError if the slug is already in use
        """
        if self._orgs.get_by_slug(slug) is not None:
            raise OrgSlugTakenError(f"The slug '{slug}' is already taken.")

        now = datetime.now(timezone.utc)
        org = OrgEntity(
            id=uuid.uuid4(),
            created_by=created_by,
            name=name,
            slug=slug,
            contact_email=contact_email,
            description=description,
            website=website,
            logo_url=logo_url,
            phone=phone,
            address=address,
            city=city,
            country=country,
            org_type=org_type,
            facebook_url=facebook_url,
            twitter_url=twitter_url,
            instagram_url=instagram_url,
            linkedin_url=linkedin_url,
            status="pending_review",
            is_verified=False,
            created_at=now,
            updated_at=now,
        )
        saved = self._orgs.create(org)

        owner = OrgMemberEntity(
            id=uuid.uuid4(),
            organization_id=saved.id,
            user_id=created_by,
            role="owner",
            is_active=True,
            joined_at=now,
        )
        self._members.create(owner)

        return saved
