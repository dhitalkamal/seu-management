"""Domain errors raised by moderation use cases."""

from __future__ import annotations

from apps.common.api.exceptions import DomainError


class ModerationCaseNotFoundError(DomainError):
    """No moderation case matches the given identifier."""

    http_status = 404
    code = "ERR_MODERATION_CASE_NOT_FOUND"


class InvalidContentTypeError(DomainError):
    """The reported content_type is not one of the accepted values."""

    http_status = 422
    code = "ERR_MODERATION_INVALID_CONTENT_TYPE"


class InvalidStatusTransitionError(DomainError):
    """The requested status transition is not allowed from the current status."""

    http_status = 422
    code = "ERR_MODERATION_INVALID_STATUS_TRANSITION"
