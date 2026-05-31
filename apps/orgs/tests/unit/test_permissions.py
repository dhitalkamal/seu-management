"""Unit tests for apps.common.permissions DRF permission classes."""

from __future__ import annotations

from unittest.mock import MagicMock

from apps.common.permissions import (
    IsOrgAdmin,
    IsOrgMember,
    IsOrgOwner,
    IsSuperAdminFromAllowedIP,
)

# * helpers


def _make_request(org_id: str, role: str) -> MagicMock:
    """Build a mock request whose JWT org_roles maps org_id -> role."""
    token = MagicMock()
    token.payload = {"org_roles": {org_id: role}}
    user = MagicMock()
    user.token = token
    user.is_authenticated = True
    request = MagicMock()
    request.user = user
    request.data = {}
    request.query_params = {}
    return request


def _make_view(org_id: str) -> MagicMock:
    """Build a mock view whose kwargs carry org_id."""
    view = MagicMock()
    view.kwargs = {"org_id": org_id}
    del view.org_id  # force _extract_org_id to use kwargs path
    return view


ORG = "org-abc-123"


# * IsOrgAdmin


def test_is_org_admin_allows_owner() -> None:
    """IsOrgAdmin must grant access to org owners."""
    assert IsOrgAdmin().has_permission(_make_request(ORG, "owner"), _make_view(ORG)) is True


def test_is_org_admin_allows_admin() -> None:
    """IsOrgAdmin must grant access to org admins."""
    assert IsOrgAdmin().has_permission(_make_request(ORG, "admin"), _make_view(ORG)) is True


def test_is_org_admin_denies_member() -> None:
    """IsOrgAdmin must deny access to plain members."""
    assert IsOrgAdmin().has_permission(_make_request(ORG, "member"), _make_view(ORG)) is False


def test_is_org_admin_denies_manager() -> None:
    """IsOrgAdmin must deny access to managers (below admin)."""
    assert IsOrgAdmin().has_permission(_make_request(ORG, "manager"), _make_view(ORG)) is False


# * IsOrgOwner


def test_is_org_owner_allows_owner() -> None:
    """IsOrgOwner must grant access only to the owner role."""
    assert IsOrgOwner().has_permission(_make_request(ORG, "owner"), _make_view(ORG)) is True


def test_is_org_owner_denies_admin() -> None:
    """IsOrgOwner must deny access to admins."""
    assert IsOrgOwner().has_permission(_make_request(ORG, "admin"), _make_view(ORG)) is False


def test_is_org_owner_denies_member() -> None:
    """IsOrgOwner must deny access to members."""
    assert IsOrgOwner().has_permission(_make_request(ORG, "member"), _make_view(ORG)) is False


# * IsOrgMember


def test_is_org_member_allows_member() -> None:
    """IsOrgMember must grant access to any member role."""
    assert IsOrgMember().has_permission(_make_request(ORG, "member"), _make_view(ORG)) is True


def test_is_org_member_denies_unknown_role() -> None:
    """IsOrgMember must deny access to unrecognised roles."""
    assert IsOrgMember().has_permission(_make_request(ORG, "guest"), _make_view(ORG)) is False


# * IsSuperAdminFromAllowedIP


def test_super_admin_denies_non_staff() -> None:
    """IsSuperAdminFromAllowedIP must deny non-staff users."""
    user = MagicMock()
    user.is_authenticated = True
    user.is_staff = False
    request = MagicMock()
    request.user = user
    view = MagicMock()
    assert IsSuperAdminFromAllowedIP().has_permission(request, view) is False


def test_super_admin_denies_unauthenticated() -> None:
    """IsSuperAdminFromAllowedIP must deny unauthenticated requests."""
    user = MagicMock()
    user.is_authenticated = False
    request = MagicMock()
    request.user = user
    view = MagicMock()
    assert IsSuperAdminFromAllowedIP().has_permission(request, view) is False
