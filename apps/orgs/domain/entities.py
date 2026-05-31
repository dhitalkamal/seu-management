"""Pure Python domain entities for the orgs module with no framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class OrgEntity:
    """A platform organization created by an organizer."""

    id: uuid.UUID
    created_by: uuid.UUID
    name: str
    slug: str
    contact_email: str
    status: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    description: str = ""
    website: str = ""
    logo_url: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    country: str = ""
    org_type: str = "company"
    facebook_url: str = ""
    twitter_url: str = ""
    instagram_url: str = ""
    linkedin_url: str = ""
    deleted_at: datetime | None = None
    # ! subscription plan - determines platform fee and feature limits
    plan: str = "free"
    plan_expires_at: datetime | None = None
    # * set by approve/reject use cases to record when the review decision was made
    reviewed_at: datetime | None = None
    reviewed_by: uuid.UUID | None = None


@dataclass(slots=True)
class OrgMemberEntity:
    """A single membership record linking a user to an organization."""

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    is_active: bool
    joined_at: datetime


@dataclass(slots=True)
class OrgInviteEntity:
    """An invitation to join an organization sent to an email address."""

    id: uuid.UUID
    org_id: uuid.UUID
    inviter_id: uuid.UUID
    invitee_email: str
    role: str
    status: str  # pending | accepted | declined | revoked | expired
    created_at: datetime
    expires_at: datetime
    accepted_by: uuid.UUID | None = None
