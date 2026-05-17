"""Pure Python domain entities for the community module with no framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class CommunityEntity:
    """A community group optionally linked to an organisation."""

    id: uuid.UUID
    created_by: uuid.UUID
    name: str
    slug: str
    privacy: str
    member_count: int
    created_at: datetime
    organisation_id: uuid.UUID | None = None
    description: str = ""
    deleted_at: datetime | None = None


@dataclass(slots=True)
class CommunityMemberEntity:
    """A single membership record linking a user to a community."""

    id: uuid.UUID
    community_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime


@dataclass(slots=True)
class CommunityPostEntity:
    """A post authored inside a community."""

    id: uuid.UUID
    community_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    post_type: str
    status: str
    like_count: int
    comment_count: int
    report_count: int
    is_pinned: bool
    created_at: datetime
    media_urls: list[str] = field(default_factory=list)
    deleted_at: datetime | None = None
