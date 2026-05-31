"""Use case: join a community."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.domain.entities import CommunityMemberEntity
from apps.community.domain.exceptions import AlreadyMemberError
from apps.community.domain.repositories import ICommunityMemberRepository, ICommunityRepository


class JoinCommunityUseCase:
    """Add a user to a community and increment the member count."""

    def __init__(self, repo: ICommunityRepository, member_repo: ICommunityMemberRepository) -> None:
        self._repo = repo
        self._member_repo = member_repo

    def execute(self, *, community_id: uuid.UUID, user_id: uuid.UUID) -> CommunityMemberEntity:
        """Validate community exists, check existing membership, then create it."""
        community = self._repo.get_by_id(community_id)

        existing = self._member_repo.get_membership(community_id, user_id)
        if existing is not None:
            raise AlreadyMemberError("You are already a member of this community.")

        member = CommunityMemberEntity(
            id=uuid.uuid4(),
            community_id=community_id,
            user_id=user_id,
            joined_at=datetime.now(timezone.utc),
        )
        self._member_repo.create(member)

        community.member_count += 1
        self._repo.update(community)

        return member
