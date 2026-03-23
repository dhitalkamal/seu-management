"""Use case: accept a pending organisation invite and create the membership."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.orgs.domain.entities import OrgInviteEntity, OrgMemberEntity
from apps.orgs.domain.exceptions import InviteExpiredError, InviteNotPendingError
from apps.orgs.domain.repositories import IOrgInviteRepository, IOrgMemberRepository


class AcceptInviteUseCase:
    """Accept a pending invite, add the user as an org member, and mark the invite accepted."""

    def __init__(
        self,
        invite_repo: IOrgInviteRepository,
        member_repo: IOrgMemberRepository,
    ) -> None:
        self._invites = invite_repo
        self._members = member_repo

    def execute(
        self,
        *,
        invite_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> OrgInviteEntity:
        """
        Validate the invite is pending and unexpired, create the membership, mark accepted.

        @param invite_id - the invite to accept
        @param user_id - the user accepting the invite
        @returns the updated OrgInviteEntity with status=accepted
        @raises InviteNotFoundError if the invite does not exist
        @raises InviteNotPendingError if the invite is not in pending status
        @raises InviteExpiredError if the invite has passed its expiry date
        """
        invite = self._invites.get_by_id(invite_id)

        if invite.status != "pending":
            raise InviteNotPendingError("This invite is no longer pending.")

        now = datetime.now(timezone.utc)
        if now > invite.expires_at:
            raise InviteExpiredError("This invite has expired.")

        member = OrgMemberEntity(
            id=uuid.uuid4(),
            organisation_id=invite.org_id,
            user_id=user_id,
            role=invite.role,
            is_active=True,
            joined_at=now,
        )
        self._members.create(member)

        accepted = OrgInviteEntity(
            id=invite.id,
            org_id=invite.org_id,
            inviter_id=invite.inviter_id,
            invitee_email=invite.invitee_email,
            role=invite.role,
            status="accepted",
            created_at=invite.created_at,
            expires_at=invite.expires_at,
            accepted_by=user_id,
        )
        return self._invites.update(accepted)
