"""Use case: leave a community."""

from __future__ import annotations

import uuid

from apps.community.domain.exceptions import CommunityOwnerCannotLeaveError, NotMemberError
from apps.community.domain.repositories import ICommunityMemberRepository, ICommunityRepository


class LeaveCommunityUseCase:
    """Remove the requesting user from a community."""

    def __init__(self, repo: ICommunityRepository, member_repo: ICommunityMemberRepository) -> None:
        self._repo = repo
        self._member_repo = member_repo

    def execute(self, *, community_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Leave the community; raise if the user is the owner or not a member."""
        community = self._repo.get_by_id(community_id)
        if community.created_by == user_id:
            raise CommunityOwnerCannotLeaveError("Community owner cannot leave; transfer ownership first.")
        existing = self._member_repo.get_membership(community_id, user_id)
        if existing is None:
            raise NotMemberError(f"User {user_id} is not a member of community {community_id}.")
        self._member_repo.delete(community_id, user_id)
        community.member_count -= 1
        self._repo.update(community)
