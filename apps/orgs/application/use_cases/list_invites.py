"""Use case: list pending invites for an organisation."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgInviteEntity
from apps.orgs.domain.repositories import IOrganisationRepository, IOrgInviteRepository


class ListInvitesUseCase:
    """Return all pending invites for a given organisation."""

    def __init__(
        self,
        org_repo: IOrganisationRepository,
        invite_repo: IOrgInviteRepository,
    ) -> None:
        self._orgs = org_repo
        self._invites = invite_repo

    def execute(self, *, org_id: uuid.UUID) -> list[OrgInviteEntity]:
        """
        Verify the org exists then return all pending invites.

        @param org_id - target organisation
        @returns list of OrgInviteEntity with status=pending
        @raises OrgNotFoundError if the org does not exist
        """
        self._orgs.get_by_id(org_id)
        return self._invites.list_pending_for_org(org_id)
