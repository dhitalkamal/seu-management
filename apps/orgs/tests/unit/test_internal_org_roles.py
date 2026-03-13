"""Unit tests for the internal org roles endpoint."""

from __future__ import annotations

import uuid
from unittest.mock import patch

from rest_framework.test import APIRequestFactory


def _get(user_id: uuid.UUID):
    """Issue a GET to the internal-org-roles view for the given user_id."""
    # import here so the module is loaded after Django is configured
    from apps.orgs.presentation.internal_views import InternalOrgRolesView

    factory = APIRequestFactory()
    request = factory.get(f"/internal/users/{user_id}/org-roles/")
    view = InternalOrgRolesView.as_view()
    return view(request, user_id=user_id)


def test_returns_empty_when_no_memberships():
    """GET for an unknown user id returns an empty org_roles dict."""
    user_id = uuid.uuid4()
    with patch("apps.orgs.presentation.internal_views.OrgMember.objects.filter") as mock_filter:
        mock_filter.return_value.values_list.return_value = []
        response = _get(user_id)

    assert response.status_code == 200
    assert response.data == {"org_roles": {}}


def test_returns_role_map_for_active_memberships():
    """Active memberships are included in the response keyed by org_id."""
    user_id = uuid.uuid4()
    org_id = uuid.uuid4()

    with patch("apps.orgs.presentation.internal_views.OrgMember.objects.filter") as mock_filter:
        mock_filter.return_value.values_list.return_value = [(org_id, "admin")]
        response = _get(user_id)

    assert response.status_code == 200
    assert response.data == {"org_roles": {str(org_id): "admin"}}


def test_excludes_inactive_memberships():
    """Inactive memberships must not appear: filter is called with is_active=True."""
    user_id = uuid.uuid4()

    with patch("apps.orgs.presentation.internal_views.OrgMember.objects.filter") as mock_filter:
        mock_filter.return_value.values_list.return_value = []
        response = _get(user_id)

    # confirm the filter was called with is_active=True
    mock_filter.assert_called_once_with(user_id=user_id, is_active=True)
    assert response.data == {"org_roles": {}}
