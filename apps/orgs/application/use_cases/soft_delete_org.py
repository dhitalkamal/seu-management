"""Use case: soft-delete an organisation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.repositories import IOrganisationRepository


class SoftDeleteOrganisationUseCase:
    """Set deleted_at on an organisation, effectively removing it from all queries."""

    def __init__(self, org_repo: IOrganisationRepository) -> None:
        self._orgs = org_repo

    def execute(self, *, org_id: uuid.UUID) -> OrgEntity:
        """
        Soft-delete the organisation by setting deleted_at=now.

        @raises OrgNotFoundError if the organisation does not exist
        """
        org = self._orgs.get_by_id(org_id)
        org.deleted_at = datetime.now(timezone.utc)
        return self._orgs.update(org)
