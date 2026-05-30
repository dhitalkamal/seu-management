"""Use case: approve a pending organization."""

from __future__ import annotations

import uuid

from django.utils import timezone

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.exceptions import InvalidOrgStatusTransitionError
from apps.orgs.domain.repositories import IOrganizationRepository

# ! only pending_review orgs may be approved
_ALLOWED_FROM: frozenset[str] = frozenset({"pending_review"})


class ApproveOrganizationUseCase:
    """Transition an organization from pending_review to active."""

    def __init__(self, org_repo: IOrganizationRepository) -> None:
        self._orgs = org_repo

    def execute(self, *, org_id: uuid.UUID, reviewed_by: uuid.UUID | None = None) -> OrgEntity:
        """
        Validate current status then set status=active.

        Sets reviewed_at to now and optionally records the reviewer's user id.

        @raises OrgNotFoundError if the org does not exist
        @raises InvalidOrgStatusTransitionError if status is not pending_review
        """
        org = self._orgs.get_by_id(org_id)
        if org.status not in _ALLOWED_FROM:
            raise InvalidOrgStatusTransitionError(f"Cannot approve an organization with status '{org.status}'.")
        org.status = "active"
        org.is_verified = True
        org.reviewed_at = timezone.now()
        org.reviewed_by = reviewed_by

        # ngo-type orgs get the ngo plan automatically on approval
        if org.org_type == "ngo":
            org.plan = "ngo"

        return self._orgs.update(org)
