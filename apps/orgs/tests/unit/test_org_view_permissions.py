"""Unit tests for org-role DRF permission classes."""

from __future__ import annotations

from unittest.mock import MagicMock

from apps.common.permissions import IsOrgAdmin, IsOrgOwner


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


def test_is_org_admin_allows_admin() -> None:
    """IsOrgAdmin must grant access when the caller holds the admin role."""
    request = _make_request(ORG, "admin")
    view = _make_view(ORG)
    assert IsOrgAdmin().has_permission(request, view) is True


def test_is_org_admin_denies_member() -> None:
    """IsOrgAdmin must deny access when the caller only holds the member role."""
    request = _make_request(ORG, "member")
    view = _make_view(ORG)
    assert IsOrgAdmin().has_permission(request, view) is False


def test_is_org_owner_denies_admin() -> None:
    """IsOrgOwner must deny access when the caller holds the admin (not owner) role."""
    request = _make_request(ORG, "admin")
    view = _make_view(ORG)
    assert IsOrgOwner().has_permission(request, view) is False
