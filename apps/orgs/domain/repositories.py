"""Abstract repository interfaces for the orgs module."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from apps.orgs.domain.entities import OrgEntity, OrgInviteEntity, OrgMemberEntity


class IOrganizationRepository(ABC):
    """Persistence contract for Organization aggregates."""

    @abstractmethod
    def create(self, entity: OrgEntity) -> OrgEntity: ...

    @abstractmethod
    def get_by_id(self, org_id: uuid.UUID) -> OrgEntity: ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> OrgEntity | None: ...

    @abstractmethod
    def update(self, entity: OrgEntity) -> OrgEntity: ...

    @abstractmethod
    def list_by_user(self, user_id: uuid.UUID) -> list[OrgEntity]: ...


class IOrgMemberRepository(ABC):
    """Persistence contract for OrgMember records."""

    @abstractmethod
    def create(self, entity: OrgMemberEntity) -> OrgMemberEntity: ...

    @abstractmethod
    def exists(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool: ...

    @abstractmethod
    def list_by_org(self, org_id: uuid.UUID) -> list[OrgMemberEntity]: ...


class IOrgInviteRepository(ABC):
    """Persistence contract for OrgInvite records."""

    @abstractmethod
    def create(self, entity: OrgInviteEntity) -> OrgInviteEntity: ...

    @abstractmethod
    def get_by_id(self, invite_id: uuid.UUID) -> OrgInviteEntity: ...

    @abstractmethod
    def update(self, entity: OrgInviteEntity) -> OrgInviteEntity: ...

    @abstractmethod
    def list_pending_for_org(self, org_id: uuid.UUID) -> list[OrgInviteEntity]: ...

    @abstractmethod
    def get_pending_by_email(self, org_id: uuid.UUID, email: str) -> OrgInviteEntity | None: ...
