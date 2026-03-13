"""Internal service-to-service views, not exposed via Nginx."""

from __future__ import annotations

import uuid

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orgs.infrastructure.models import OrgMember


class InternalOrgRolesView(APIView):
    """Return a user's active org memberships as {org_id: role}.

    Trusted by network isolation - not authenticated. Only accessible
    within the Docker network, never routed through Nginx.
    """

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request: Request, user_id: uuid.UUID) -> Response:
        """Fetch all active memberships for the given user."""
        memberships = OrgMember.objects.filter(
            user_id=user_id,
            is_active=True,
        ).values_list("organisation_id", "role")

        org_roles = {str(org_id): role for org_id, role in memberships}
        return Response({"org_roles": org_roles})
