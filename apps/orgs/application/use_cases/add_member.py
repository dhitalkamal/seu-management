"""Use case: add a user to an organisation with a given role."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.orgs.domain.entities import OrgMemberEntity
from apps.orgs.domain.exceptions import MemberAlreadyExistsError
from apps.orgs.domain.repositories import IOrganisationRepository, IOrgMemberRepository


class AddOrgMemberUseCase:
    """Add a new active membership to an organisation."""

    def __init__(
        self,
        org_repo: IOrganisationRepository,
        member_repo: IOrgMemberRepository,
    ) -> None:
        self._orgs = org_repo
        self._members = member_repo

    def execute(
        self,
        *,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
    ) -> OrgMemberEntity:
        """
        Verify the org exists and the user is not already a member, then create the membership.

        @param org_id - the organisation to join
        @param user_id - the user to add
        @param role - owner | admin | manager | member
        @returns the new OrgMemberEntity
        @raises OrgNotFoundError if the org does not exist
        @raises MemberAlreadyExistsError if the user is already an active member
        """
        self._orgs.get_by_id(org_id)

        if self._members.exists(org_id, user_id):
            raise MemberAlreadyExistsError("This user is already a member of the organisation.")

        member = OrgMemberEntity(
            id=uuid.uuid4(),
            organisation_id=org_id,
            user_id=user_id,
            role=role,
            is_active=True,
            joined_at=datetime.now(timezone.utc),
        )
        return self._members.create(member)
