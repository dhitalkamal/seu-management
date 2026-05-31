"""Use case: fetch a single organization by id."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.repositories import IOrganizationRepository


class GetOrganizationUseCase:
    """Fetch an organization by its primary key."""

    def __init__(self, org_repo: IOrganizationRepository) -> None:
        self._orgs = org_repo

    def execute(self, *, org_id: uuid.UUID) -> OrgEntity:
        """Return the org or raise OrgNotFoundError if absent or soft-deleted."""
        return self._orgs.get_by_id(org_id)
