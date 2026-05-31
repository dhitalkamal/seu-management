"""Unit tests for CreateInviteUseCase - see test_invite_use_cases.py for full suite."""

from apps.orgs.tests.unit.test_invite_use_cases import (
    test_create_invite_raises_when_duplicate_pending,
    test_create_invite_raises_when_org_not_found,
    test_create_invite_returns_entity,
)

__all__ = [
    "test_create_invite_returns_entity",
    "test_create_invite_raises_when_org_not_found",
    "test_create_invite_raises_when_duplicate_pending",
]
