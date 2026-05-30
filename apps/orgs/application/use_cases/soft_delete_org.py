"""Use case: soft-delete an organization."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.repositories import IOrganizationRepository


class SoftDeleteOrganizationUseCase:
    """Set deleted_at on an organization, effectively removing it from all queries."""

    def __init__(self, org_repo: IOrganizationRepository) -> None:
        self._orgs = org_repo

    def execute(self, *, org_id: uuid.UUID) -> OrgEntity:
        """
        Soft-delete the organization by setting deleted_at=now.

        @raises OrgNotFoundError if the organization does not exist
        """
        org = self._orgs.get_by_id(org_id)
        org.deleted_at = datetime.now(timezone.utc)
        return self._orgs.update(org)
