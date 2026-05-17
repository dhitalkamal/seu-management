"""Use case: create a new community."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.domain.entities import CommunityEntity
from apps.community.domain.exceptions import SlugAlreadyExistsError
from apps.community.domain.repositories import ICommunityRepository


class CreateCommunityUseCase:
    """Create a new community, enforcing unique slugs."""

    def __init__(self, repo: ICommunityRepository) -> None:
        self._repo = repo

    def execute(
        self,
        *,
        created_by: uuid.UUID,
        name: str,
        slug: str,
        privacy: str,
        organisation_id: uuid.UUID | None = None,
        description: str = "",
    ) -> CommunityEntity:
        """Validate slug uniqueness and persist the new community."""
        if self._repo.slug_exists(slug):
            raise SlugAlreadyExistsError(f"The slug '{slug}' is already in use.")

        now = datetime.now(timezone.utc)
        community = CommunityEntity(
            id=uuid.uuid4(),
            created_by=created_by,
            name=name,
            slug=slug,
            privacy=privacy,
            member_count=0,
            created_at=now,
            organisation_id=organisation_id,
            description=description,
        )
        self._repo.create(community)
        return community
