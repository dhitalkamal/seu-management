"""Use case: create a pending invitation for a user to join an organisation."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from apps.orgs.domain.entities import OrgInviteEntity
from apps.orgs.domain.exceptions import InviteAlreadyExistsError
from apps.orgs.domain.repositories import IOrganisationRepository, IOrgInviteRepository

# invites expire after 7 days
_INVITE_TTL_DAYS = 7


class CreateInviteUseCase:
    """Send an invitation to an email address to join an organisation."""

    def __init__(
        self,
        org_repo: IOrganisationRepository,
        invite_repo: IOrgInviteRepository,
    ) -> None:
        self._orgs = org_repo
        self._invites = invite_repo

    def execute(
        self,
        *,
        org_id: uuid.UUID,
        inviter_id: uuid.UUID,
        invitee_email: str,
        role: str,
    ) -> OrgInviteEntity:
        """
        Verify the org exists, guard against duplicate pending invites, then persist.

        @param org_id - target organisation
        @param inviter_id - user sending the invite
        @param invitee_email - recipient email address
        @param role - role the invitee will receive on acceptance
        @returns the new OrgInviteEntity with status=pending
        @raises OrgNotFoundError if the org does not exist
        @raises InviteAlreadyExistsError if a pending invite for this email already exists
        """
        self._orgs.get_by_id(org_id)

        existing = self._invites.get_pending_by_email(org_id, invitee_email)
        if existing is not None:
            raise InviteAlreadyExistsError(f"A pending invite for {invitee_email} already exists for this organisation.")

        now = datetime.now(timezone.utc)
        invite = OrgInviteEntity(
            id=uuid.uuid4(),
            org_id=org_id,
            inviter_id=inviter_id,
            invitee_email=invitee_email,
            role=role,
            status="pending",
            created_at=now,
            expires_at=now + timedelta(days=_INVITE_TTL_DAYS),
            accepted_by=None,
        )
        return self._invites.create(invite)
