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


class InvalidOrgStatusTransitionError(DomainError):
    """The requested status change is not permitted from the current status."""

    http_status = 422
    code = "ERR_ORG_INVALID_STATUS_TRANSITION"


class InviteNotFoundError(DomainError):
    """No invite matches the given identifier."""

    http_status = 404
    code = "ERR_ORG_INVITE_NOT_FOUND"


class InviteExpiredError(DomainError):
    """The invite has passed its expiry date and can no longer be accepted."""

    http_status = 410
    code = "ERR_ORG_INVITE_EXPIRED"


class InviteNotPendingError(DomainError):
    """The invite is not in pending status and cannot be acted upon."""

    http_status = 422
    code = "ERR_ORG_INVITE_NOT_PENDING"


class InviteAlreadyExistsError(DomainError):
    """A pending invite already exists for this email at this organisation."""

    http_status = 409
    code = "ERR_ORG_INVITE_ALREADY_EXISTS"
