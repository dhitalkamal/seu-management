"""Domain errors raised by orgs use cases and never swallowed silently."""

from __future__ import annotations

from apps.common.api.exceptions import DomainError


class OrgNotFoundError(DomainError):
    """No organisation matches the given identifier."""

    http_status = 404
    code = "ERR_ORG_NOT_FOUND"


class OrgSlugTakenError(DomainError):
    """The requested slug is already in use by another organisation."""

    http_status = 409
    code = "ERR_ORG_SLUG_TAKEN"


class MemberAlreadyExistsError(DomainError):
    """The user is already an active member of this organisation."""

    http_status = 409
    code = "ERR_ORG_MEMBER_ALREADY_EXISTS"
