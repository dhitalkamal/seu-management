"""Use case: list pending invites for an organization."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgInviteEntity
from apps.orgs.domain.repositories import IOrganizationRepository, IOrgInviteRepository


class ListInvitesUseCase:
    """Return all pending invites for a given organization."""

    def __init__(
        self,
        org_repo: IOrganizationRepository,
        invite_repo: IOrgInviteRepository,
    ) -> None:
        self._orgs = org_repo
        self._invites = invite_repo

    def execute(self, *, org_id: uuid.UUID) -> list[OrgInviteEntity]:
        """
        Verify the org exists then return all pending invites.

        @param org_id - target organization
        @returns list of OrgInviteEntity with status=pending
        @raises OrgNotFoundError if the org does not exist
        """
        self._orgs.get_by_id(org_id)
        return self._invites.list_pending_for_org(org_id)
