"""Use case: list all organisations the given user is a member of."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.repositories import IOrganisationRepository


class ListOrganisationsUseCase:
    """Return all non-deleted organisations the user belongs to."""

    def __init__(self, org_repo: IOrganisationRepository) -> None:
        self._orgs = org_repo

    def execute(self, *, user_id: uuid.UUID) -> list[OrgEntity]:
        """Return the list of orgs; empty list is valid."""
        return self._orgs.list_by_user(user_id)
