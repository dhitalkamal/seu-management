"""Tests for LeaveCommunityUseCase."""

from __future__ import annotations

import uuid

import pytest

from apps.community.tests.unit.fakes import FakeCommunityMemberRepository, FakeCommunityRepository, make_community


class TestLeaveCommunityUseCase:
    """Unit tests for the leave community use case."""

    def _make_use_case(
        self,
        community_repo: FakeCommunityRepository,
        member_repo: FakeCommunityMemberRepository,
    ) -> object:
        from apps.community.application.use_cases.leave_community import LeaveCommunityUseCase

        return LeaveCommunityUseCase(repo=community_repo, member_repo=member_repo)

    def test_removes_membership(self) -> None:
        """A non-owner member can leave and membership is deleted."""
        from apps.community.application.use_cases.join_community import JoinCommunityUseCase
        from apps.community.application.use_cases.leave_community import LeaveCommunityUseCase

        community = make_community()
        user_id = uuid.uuid4()

        community_repo = FakeCommunityRepository(communities=[community])
        member_repo = FakeCommunityMemberRepository()

        JoinCommunityUseCase(repo=community_repo, member_repo=member_repo).execute(community_id=community.id, user_id=user_id)

        assert member_repo.get_membership(community.id, user_id) is not None

        LeaveCommunityUseCase(repo=community_repo, member_repo=member_repo).execute(community_id=community.id, user_id=user_id)

        assert member_repo.get_membership(community.id, user_id) is None

    def test_decrements_member_count(self) -> None:
        """Member count is decremented when a user leaves."""
        from apps.community.application.use_cases.join_community import JoinCommunityUseCase
        from apps.community.application.use_cases.leave_community import LeaveCommunityUseCase

        community = make_community()
        user_id = uuid.uuid4()

        community_repo = FakeCommunityRepository(communities=[community])
        member_repo = FakeCommunityMemberRepository()

        JoinCommunityUseCase(repo=community_repo, member_repo=member_repo).execute(community_id=community.id, user_id=user_id)
        assert community_repo.get_by_id(community.id).member_count == 1

        LeaveCommunityUseCase(repo=community_repo, member_repo=member_repo).execute(community_id=community.id, user_id=user_id)

        assert community_repo.get_by_id(community.id).member_count == 0

    def test_raises_if_not_a_member(self) -> None:
        """Leaving a community you did not join raises NotMemberError."""
        from apps.community.domain.exceptions import NotMemberError

        community = make_community()
        user_id = uuid.uuid4()

        community_repo = FakeCommunityRepository(communities=[community])
        member_repo = FakeCommunityMemberRepository()

        uc = self._make_use_case(community_repo, member_repo)
        with pytest.raises(NotMemberError):
            uc.execute(community_id=community.id, user_id=user_id)

    def test_raises_if_owner_tries_to_leave(self) -> None:
        """Community owner cannot leave; they must transfer ownership first."""
        from apps.community.application.use_cases.join_community import JoinCommunityUseCase
        from apps.community.domain.exceptions import CommunityOwnerCannotLeaveError

        community = make_community()
        owner_id = community.created_by

        community_repo = FakeCommunityRepository(communities=[community])
        member_repo = FakeCommunityMemberRepository()

        JoinCommunityUseCase(repo=community_repo, member_repo=member_repo).execute(community_id=community.id, user_id=owner_id)

        uc = self._make_use_case(community_repo, member_repo)
        with pytest.raises(CommunityOwnerCannotLeaveError):
            uc.execute(community_id=community.id, user_id=owner_id)
