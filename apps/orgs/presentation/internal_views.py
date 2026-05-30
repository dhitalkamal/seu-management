"""Internal service-to-service views, not exposed via Nginx."""

from __future__ import annotations

import uuid

from django.utils import timezone as dj_tz
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orgs.infrastructure.models import Organization, OrgMember


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
        ).values_list("organization_id", "role")

        org_roles = {str(org_id): role for org_id, role in memberships}
        return Response({"org_roles": org_roles})


class InternalOrgPlanView(APIView):
    """Return an org's subscription plan and expiry.

    Used by participation-service and payment-service to enforce
    plan-based limits (registration caps, platform fees).
    """

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request: Request, org_id: uuid.UUID) -> Response:
        """Return plan and plan_expires_at for the given org.

        If plan_expires_at is in the past, downgrade the org to free
        and return 'free' so callers enforce the correct limits.
        """
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response({"error": "org not found"}, status=404)

        plan = org.plan
        # auto-downgrade expired paid plans to free
        if plan != "free" and org.plan_expires_at and org.plan_expires_at < dj_tz.now():
            org.plan = "free"
            org.plan_expires_at = None
            org.save(update_fields=["plan", "plan_expires_at"])
            plan = "free"

        return Response(
            {
                "plan": plan,
                "plan_expires_at": org.plan_expires_at.isoformat() if org.plan_expires_at else None,
            }
        )
