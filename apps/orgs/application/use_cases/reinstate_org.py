"""Use case: reinstate a suspended organization."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.exceptions import InvalidOrgStatusTransitionError
from apps.orgs.domain.repositories import IOrganizationRepository

_ALLOWED_FROM: frozenset[str] = frozenset({"suspended"})


class ReinstateOrganizationUseCase:
    """Transition an organization from suspended back to active."""

    def __init__(self, org_repo: IOrganizationRepository) -> None:
        self._orgs = org_repo

    def execute(self, *, org_id: uuid.UUID) -> OrgEntity:
        """
        Validate current status then set status=active.

        @raises OrgNotFoundError if the org does not exist
        @raises InvalidOrgStatusTransitionError if status is not suspended
        """
        org = self._orgs.get_by_id(org_id)
        if org.status not in _ALLOWED_FROM:
            raise InvalidOrgStatusTransitionError(f"Cannot reinstate an organization with status '{org.status}'.")
        org.status = "active"
        return self._orgs.update(org)
