"""Use case: update an organisation's editable profile fields."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.repositories import IOrganisationRepository


class UpdateOrganisationUseCase:
    """Apply partial updates to an existing organisation's profile fields."""

    def __init__(self, org_repo: IOrganisationRepository) -> None:
        self._orgs = org_repo

    def execute(
        self,
        *,
        org_id: uuid.UUID,
        **fields: str,
    ) -> OrgEntity:
        """
        Fetch the org, patch any provided fields, and persist.

        Only profile-level fields are accepted (name, description, contact_email,
        website, logo_url, phone, address, city, country, org_type, social URLs).
        Status/plan changes are handled by dedicated use cases.

        @param org_id - the org to update
        @param fields - keyword args mapping field names to new values
        @returns the updated OrgEntity
        @raises OrgNotFoundError if the org does not exist
        """
        org = self._orgs.get_by_id(org_id)

        # ! only allow profile fields — never status, plan, or is_verified here
        allowed = {
            "name", "description", "contact_email", "website", "logo_url",
            "phone", "address", "city", "country", "org_type",
            "facebook_url", "twitter_url", "instagram_url", "linkedin_url",
        }

        # ! critical fields — changing these on an active org resets verification
        critical = {"name", "contact_email", "org_type"}
        needs_reverification = False

        for key, value in fields.items():
            if key in allowed and hasattr(org, key):
                # detect whether a critical field is actually changing
                if key in critical and getattr(org, key) != value and org.status == "active":
                    needs_reverification = True
                setattr(org, key, value)

        # ! if any critical field changed on an active org, reset to pending review
        if needs_reverification:
            org.status = "pending_review"
            org.is_verified = False

        return self._orgs.update(org)
