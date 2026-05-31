"""Use case: change an organization's subscription plan."""

from __future__ import annotations

import uuid
from datetime import datetime

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.repositories import IOrganizationRepository

# ! valid plan names — must stay in sync with Organization.Plan choices
VALID_PLANS: frozenset[str] = frozenset({"free", "starter", "pro", "ngo", "enterprise"})


class ChangePlanUseCase:
    """Update an organization's subscription plan and expiry date."""

    def __init__(self, org_repo: IOrganizationRepository) -> None:
        self._orgs = org_repo

    def execute(
        self,
        *,
        org_id: uuid.UUID,
        plan: str,
        plan_expires_at: datetime | None = None,
    ) -> OrgEntity:
        """
        Set the org's plan and optional expiry timestamp.

        Called by the subscription webhook consumer when a payment is confirmed,
        or by a superadmin manually assigning a plan.

        @param org_id - the organization to update
        @param plan - one of free, starter, pro, ngo, enterprise
        @param plan_expires_at - when the current billing period ends (None for free/ngo)
        @raises ValueError if the plan name is invalid
        @raises OrgNotFoundError if the org doesn't exist
        """
        if plan not in VALID_PLANS:
            raise ValueError(f"Invalid plan: {plan}. Must be one of {sorted(VALID_PLANS)}")

        org = self._orgs.get_by_id(org_id)
        org.plan = plan
        org.plan_expires_at = plan_expires_at
        return self._orgs.update(org)
