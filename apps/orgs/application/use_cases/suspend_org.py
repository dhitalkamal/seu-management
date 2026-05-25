"""Use case: suspend an active organization."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.exceptions import InvalidOrgStatusTransitionError
from apps.orgs.domain.repositories import IOrganizationRepository

_ALLOWED_FROM: frozenset[str] = frozenset({"active"})


class SuspendOrganizationUseCase:
    """Transition an organization from active to suspended."""

    def __init__(self, org_repo: IOrganizationRepository) -> None:
        self._orgs = org_repo

    def execute(self, *, org_id: uuid.UUID) -> OrgEntity:
        """
        Validate current status then set status=suspended.

        @raises OrgNotFoundError if the org does not exist
        @raises InvalidOrgStatusTransitionError if status is not active
        """
        org = self._orgs.get_by_id(org_id)
        if org.status not in _ALLOWED_FROM:
            raise InvalidOrgStatusTransitionError(f"Cannot suspend an organization with status '{org.status}'.")
        org.status = "suspended"
        return self._orgs.update(org)
