"""Use case: fetch a single organisation by id."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.repositories import IOrganisationRepository


class GetOrganisationUseCase:
    """Fetch an organisation by its primary key."""

    def __init__(self, org_repo: IOrganisationRepository) -> None:
        self._orgs = org_repo

    def execute(self, *, org_id: uuid.UUID) -> OrgEntity:
        """Return the org or raise OrgNotFoundError if absent or soft-deleted."""
        return self._orgs.get_by_id(org_id)
