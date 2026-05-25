"""Use case: approve a pending organization."""

from __future__ import annotations

import uuid

from apps.orgs.domain.entities import OrgEntity
from apps.orgs.domain.exceptions import InvalidOrgStatusTransitionError
from apps.orgs.domain.repositories import IOrganizationRepository

# ! only pending_review orgs may be approved
_ALLOWED_FROM: frozenset[str] = frozenset({"pending_review"})


class ApproveOrganizationUseCase:
    """Transition an organization from pending_review to active."""

    def __init__(self, org_repo: IOrganizationRepository) -> None:
        self._orgs = org_repo

    def execute(self, *, org_id: uuid.UUID) -> OrgEntity:
        """
        Validate current status then set status=active.

        @raises OrgNotFoundError if the org does not exist
        @raises InvalidOrgStatusTransitionError if status is not pending_review
        """
        org = self._orgs.get_by_id(org_id)
        if org.status not in _ALLOWED_FROM:
            raise InvalidOrgStatusTransitionError(f"Cannot approve an organization with status '{org.status}'.")
        org.status = "active"
        org.is_verified = True
        saved = self._orgs.update(org)

        try:
            from apps.orgs.infrastructure.publisher import publish_event

            publish_event(
                routing_key="org.approved",
                payload={
                    "org_id": str(saved.id),
                    "org_name": saved.name,
                    "created_by": str(saved.created_by),
                    "contact_email": saved.contact_email,
                },
            )
        except Exception:
            pass

        return saved
