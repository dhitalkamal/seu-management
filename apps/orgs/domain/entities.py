"""Pure Python domain entities for the orgs module with no framework dependencies."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class OrgEntity:
    """A platform organisation created by an organiser."""

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
    # ! subscription plan — determines platform fee and feature limits
    plan: str = "free"
    plan_expires_at: datetime | None = None


@dataclass(slots=True)
class OrgMemberEntity:
    """A single membership record linking a user to an organisation."""

    id: uuid.UUID
    organisation_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    is_active: bool
    joined_at: datetime
