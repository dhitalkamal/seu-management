"""Use case: create a new community."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.domain.entities import CommunityEntity, CommunityMemberEntity
from apps.community.domain.exceptions import SlugAlreadyExistsError
from apps.community.domain.repositories import ICommunityMemberRepository, ICommunityRepository


class CreateCommunityUseCase:
    """Create a new community, enforcing unique slugs, and auto-join the creator."""

    def __init__(self, repo: ICommunityRepository, member_repo: ICommunityMemberRepository) -> None:
        self._repo = repo
        self._member_repo = member_repo

    def execute(
        self,
        *,
        created_by: uuid.UUID,
        name: str,
        slug: str,
        privacy: str,
        organization_id: uuid.UUID | None = None,
        description: str = "",
    ) -> CommunityEntity:
        """Validate slug uniqueness, persist the community, and add the creator as member."""
        if self._repo.slug_exists(slug):
            raise SlugAlreadyExistsError(f"The slug '{slug}' is already in use.")

        now = datetime.now(timezone.utc)
        community = CommunityEntity(
            id=uuid.uuid4(),
            created_by=created_by,
            name=name,
            slug=slug,
            privacy=privacy,
            # start at 1 because the creator is immediately joined below
            member_count=1,
            created_at=now,
            organization_id=organization_id,
            description=description,
        )
        self._repo.create(community)

        # auto-join the creator so they are always a member of their own community
        member = CommunityMemberEntity(
            id=uuid.uuid4(),
            community_id=community.id,
            user_id=created_by,
            joined_at=now,
        )
        self._member_repo.create(member)

        return community
