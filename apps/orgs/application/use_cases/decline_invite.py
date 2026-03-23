"""Use case: decline a pending organisation invite."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgInviteEntity
from apps.orgs.domain.exceptions import InviteNotPendingError
from apps.orgs.domain.repositories import IOrgInviteRepository


class DeclineInviteUseCase:
    """Mark a pending invite as declined by the invitee."""

    def __init__(self, invite_repo: IOrgInviteRepository) -> None:
        self._invites = invite_repo

    def execute(self, *, invite_id: uuid.UUID) -> OrgInviteEntity:
        """
        Set status=declined on a pending invite.

        @param invite_id - the invite to decline
        @returns the updated OrgInviteEntity with status=declined
        @raises InviteNotFoundError if the invite does not exist
        @raises InviteNotPendingError if the invite is not in pending status
        """
        invite = self._invites.get_by_id(invite_id)

        if invite.status != "pending":
            raise InviteNotPendingError("This invite is no longer pending.")

        declined = OrgInviteEntity(
            id=invite.id,
            org_id=invite.org_id,
            inviter_id=invite.inviter_id,
            invitee_email=invite.invitee_email,
            role=invite.role,
            status="declined",
            created_at=invite.created_at,
            expires_at=invite.expires_at,
            accepted_by=invite.accepted_by,
        )
        return self._invites.update(declined)
