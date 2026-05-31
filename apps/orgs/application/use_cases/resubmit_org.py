"""Use case: resubmit a rejected organization for review."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.exceptions import InvalidOrgStatusTransitionError
from apps.orgs.domain.repositories import IOrganizationRepository


class ResubmitOrganizationUseCase:
    """Transition an organization from rejected back to pending_review."""

    def __init__(self, org_repo: IOrganizationRepository) -> None:
        self._orgs = org_repo

    def execute(self, *, org_id: uuid.UUID) -> OrgEntity:
        """
        Allow org owner to resubmit after rejection.

        Only rejected orgs can be resubmitted.
        """
        org = self._orgs.get_by_id(org_id)
        if org.status != "rejected":
            raise InvalidOrgStatusTransitionError(f"Only rejected organizations can be resubmitted, current status is '{org.status}'.")
        org.status = "pending_review"
        org.reviewed_at = None
        org.reviewed_by = None
        return self._orgs.update(org)
