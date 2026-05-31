"""Pure Python domain entities for the community module with no framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class PollEntity:
    """A community poll with multiple options and vote tracking."""

    id: uuid.UUID
    community_id: uuid.UUID
    author_id: uuid.UUID
    author_name: str
    question: str
    options: list[dict]  # [{"text": "Option A", "votes": 0}]
    total_votes: int
    created_at: datetime
    expires_at: datetime | None = None


@dataclass(slots=True)
class ActivityFeedEntry:
    """A single item in a community's activity stream."""

    id: uuid.UUID
    community_id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    user_avatar: str
    activity_type: str  # "registered", "posted", "joined", "commented", "liked"
    target_title: str  # event name or post snippet
    target_id: str
    created_at: datetime


@dataclass(slots=True)
class EventWallEntity:
    """A wall of posts associated with a specific event inside a community."""

    id: uuid.UUID
    community_id: uuid.UUID
    event_id: uuid.UUID
    event_title: str
    event_date: datetime
    post_count: int
    created_at: datetime


@dataclass(slots=True)
class MemberBadgeEntity:
    """Engagement stats and badge assignment for a community member."""

    id: uuid.UUID
    community_id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    user_avatar: str
    badge_type: str  # "early_adopter", "top_contributor", "event_veteran", "active_commenter"
    events_attended: int
    posts_count: int
    comments_count: int
    joined_at: datetime


@dataclass(slots=True)
class CommunityEntity:
    """A community group optionally linked to an organization."""

    id: uuid.UUID
    created_by: uuid.UUID
    name: str
    slug: str
    privacy: str
    member_count: int
    created_at: datetime
    organization_id: uuid.UUID | None = None
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
    author_name: str = ""


@dataclass(slots=True)
class PostLikeEntity:
    """A single like on a community post."""

    id: uuid.UUID
    post_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime


@dataclass(slots=True)
class PostCommentEntity:
    """A comment (or reply) on a community post."""

    id: uuid.UUID
    post_id: uuid.UUID
    author_id: uuid.UUID
    content: str
    # null = top-level comment, set = reply to another comment
    parent_id: uuid.UUID | None
    like_count: int
    reply_count: int
    created_at: datetime
    author_name: str = ""


@dataclass(slots=True)
class PostRepostEntity:
    """A repost of an existing community post into a target community."""

    id: uuid.UUID
    original_post_id: uuid.UUID
    user_id: uuid.UUID
    community_id: uuid.UUID
    caption: str
    created_at: datetime


@dataclass(slots=True)
class HashtagEntity:
    """A hashtag extracted from post content."""

    id: uuid.UUID
    # stored without the leading #
    name: str
    post_count: int
    created_at: datetime
