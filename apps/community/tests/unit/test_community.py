"""Unit tests for community use cases."""

from __future__ import annotations

import uuid

import pytest

from apps.community.domain.exceptions import (
    AlreadyMemberError,
    CommunityNotFoundError,
    SlugAlreadyExistsError,
)
from apps.community.tests.unit.fakes import (
    FakeCommunityMemberRepository,
    FakeCommunityPostRepository,
    FakeCommunityRepository,
    make_community,
)


# * list communities
def test_list_communities_empty():
    """Returns empty list when no communities exist."""
    from apps.community.application.use_cases.list_communities import ListCommunitiesUseCase

    result = ListCommunitiesUseCase(FakeCommunityRepository()).execute()
    assert result == []


def test_list_communities_returns_all():
    """Returns all non-deleted communities."""
    from apps.community.application.use_cases.list_communities import ListCommunitiesUseCase

    communities = [make_community(), make_community()]
    result = ListCommunitiesUseCase(FakeCommunityRepository(communities)).execute()
    assert len(result) == 2


# * create community
def test_create_community_success():
    """Successfully creates a community and returns it."""
    from apps.community.application.use_cases.create_community import CreateCommunityUseCase

    repo = FakeCommunityRepository()
    result = CreateCommunityUseCase(repo).execute(
        created_by=uuid.uuid4(),
        name="Test Community",
        slug="test-community",
        privacy="public",
    )
    assert result.name == "Test Community"
    assert result.slug == "test-community"


def test_create_community_duplicate_slug_raises():
    """Raises SlugAlreadyExistsError when slug is taken."""
    from apps.community.application.use_cases.create_community import CreateCommunityUseCase

    repo = FakeCommunityRepository([make_community(slug="taken-slug")])
    with pytest.raises(SlugAlreadyExistsError):
        CreateCommunityUseCase(repo).execute(
            created_by=uuid.uuid4(),
            name="Another",
            slug="taken-slug",
            privacy="public",
        )


# * join community
def test_join_community_increments_member_count():
    """Joining increments the community's member_count."""
    from apps.community.application.use_cases.join_community import JoinCommunityUseCase

    community = make_community(member_count=5)
    repo = FakeCommunityRepository([community])
    member_repo = FakeCommunityMemberRepository()
    JoinCommunityUseCase(repo, member_repo).execute(community_id=community.id, user_id=uuid.uuid4())
    assert repo.get_by_id(community.id).member_count == 6


def test_join_community_already_member_raises():
    """Raises AlreadyMemberError when user is already a member."""
    from apps.community.application.use_cases.join_community import JoinCommunityUseCase

    community = make_community()
    user_id = uuid.uuid4()
    repo = FakeCommunityRepository([community])
    member_repo = FakeCommunityMemberRepository()
    # first join
    JoinCommunityUseCase(repo, member_repo).execute(community_id=community.id, user_id=user_id)
    # second join should raise
    with pytest.raises(AlreadyMemberError):
        JoinCommunityUseCase(repo, member_repo).execute(community_id=community.id, user_id=user_id)


def test_join_missing_community_raises():
    """Raises CommunityNotFoundError when community does not exist."""
    from apps.community.application.use_cases.join_community import JoinCommunityUseCase

    with pytest.raises(CommunityNotFoundError):
        JoinCommunityUseCase(FakeCommunityRepository(), FakeCommunityMemberRepository()).execute(
            community_id=uuid.uuid4(), user_id=uuid.uuid4()
        )


# * create post
def test_create_post_success():
    """Creating a post returns a CommunityPostEntity with correct fields."""
    from apps.community.application.use_cases.create_post import CreatePostUseCase

    community = make_community()
    author_id = uuid.uuid4()
    repo = FakeCommunityRepository([community])
    post_repo = FakeCommunityPostRepository()
    result = CreatePostUseCase(repo, post_repo).execute(
        community_id=community.id,
        author_id=author_id,
        content="Hello!",
        post_type="text",
    )
    assert result.content == "Hello!"
    assert result.author_id == author_id


def test_create_post_missing_community_raises():
    """Raises CommunityNotFoundError when community does not exist."""
    from apps.community.application.use_cases.create_post import CreatePostUseCase

    with pytest.raises(CommunityNotFoundError):
        CreatePostUseCase(FakeCommunityRepository(), FakeCommunityPostRepository()).execute(
            community_id=uuid.uuid4(),
            author_id=uuid.uuid4(),
            content="Hi",
            post_type="text",
        )
