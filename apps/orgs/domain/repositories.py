"""Abstract repository interfaces for the orgs module."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from apps.orgs.domain.entities import OrgEntity, OrgMemberEntity


class IOrganisationRepository(ABC):
    """Persistence contract for Organisation aggregates."""

    @abstractmethod
    def create(self, entity: OrgEntity) -> OrgEntity: ...

    @abstractmethod
    def get_by_id(self, org_id: uuid.UUID) -> OrgEntity: ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> OrgEntity | None: ...

    @abstractmethod
    def list_by_user(self, user_id: uuid.UUID) -> list[OrgEntity]: ...


class IOrgMemberRepository(ABC):
    """Persistence contract for OrgMember records."""

    @abstractmethod
    def create(self, entity: OrgMemberEntity) -> OrgMemberEntity: ...

    @abstractmethod
    def exists(self, org_id: uuid.UUID, user_id: uuid.UUID) -> bool: ...
