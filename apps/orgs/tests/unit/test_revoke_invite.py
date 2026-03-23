"""Unit tests for RevokeInviteUseCase - see test_invite_use_cases.py for full suite."""

from apps.orgs.tests.unit.test_invite_use_cases import (
    test_revoke_invite_marks_revoked,
    test_revoke_invite_raises_when_not_pending,
)

__all__ = [
    "test_revoke_invite_marks_revoked",
    "test_revoke_invite_raises_when_not_pending",
]
