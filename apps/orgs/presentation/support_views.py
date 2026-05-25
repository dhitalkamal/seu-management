"""DRF views for support ticket endpoints."""

from __future__ import annotations

import uuid

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api.responses import created_response, error_response, success_response
from apps.orgs.application.use_cases.create_ticket import CreateTicketUseCase
from apps.orgs.application.use_cases.list_tickets import ListTicketsUseCase
from apps.orgs.application.use_cases.update_ticket_status import UpdateTicketStatusUseCase
from apps.orgs.infrastructure.support_repository import DjangoSupportTicketRepository
from apps.orgs.presentation.support_serializers import (
    CreateTicketSerializer,
    TicketResponseSerializer,
    UpdateTicketStatusSerializer,
)


class TicketListCreateView(APIView):
    """GET /tickets/ lists all tickets (admin); POST /tickets/ creates one."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Support"],
        summary="List all support tickets",
        responses={200: TicketResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        """Return all tickets. Staff only."""
        if not request.user.is_staff:  # type: ignore[union-attr]
            return error_response(
                code="ERR_FORBIDDEN",
                message="Staff access required.",
                http_status=403,
                request=request,
            )
        tickets = ListTicketsUseCase(DjangoSupportTicketRepository()).execute()
        return success_response(TicketResponseSerializer(tickets, many=True).data, request=request)

    @extend_schema(
        tags=["Support"],
        summary="Submit a support ticket",
        request=CreateTicketSerializer,
        responses={201: TicketResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        """Create a new support ticket."""
        ser = CreateTicketSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        submitted_by = getattr(request.user, "id", None)
        ticket = CreateTicketUseCase(DjangoSupportTicketRepository()).execute(
            subject=d["subject"],
            message=d["message"],
            priority=d["priority"],
            org_id=d["org_id"],
            org_name=d["org_name"],
            submitted_by=uuid.UUID(str(submitted_by)) if submitted_by else None,
        )
        return created_response(TicketResponseSerializer(ticket).data, request=request)


class TicketStatusUpdateView(APIView):
    """PATCH /tickets/<uuid>/status/ updates ticket status (admin)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Support"],
        summary="Update ticket status",
        request=UpdateTicketStatusSerializer,
        responses={
            200: TicketResponseSerializer,
            404: OpenApiResponse(description="Ticket not found."),
        },
    )
    def patch(self, request: Request, ticket_id: uuid.UUID) -> Response:
        """Update the status of a support ticket. Staff only."""
        if not request.user.is_staff:  # type: ignore[union-attr]
            return error_response(
                code="ERR_FORBIDDEN",
                message="Staff access required.",
                http_status=403,
                request=request,
            )
        ser = UpdateTicketStatusSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        try:
            ticket = UpdateTicketStatusUseCase(DjangoSupportTicketRepository()).execute(
                ticket_id=ticket_id,
                status=d["status"],
                priority=d.get("priority"),
            )
        except Exception as exc:
            return error_response(
                code="ERR_NOT_FOUND",
                message="Ticket not found.",
                details=str(exc),
                http_status=404,
                request=request,
            )
        return success_response(TicketResponseSerializer(ticket).data, request=request)


class OrgAnalyticsView(APIView):
    """GET /admin/analytics/ returns aggregated platform stats for superadmin."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Admin"],
        summary="Platform analytics summary",
        responses={200: OpenApiResponse(description="Aggregated org and ticket stats.")},
    )
    def get(self, request: Request) -> Response:
        """Return aggregated org counts and ticket stats. Staff only."""
        if not request.user.is_staff:  # type: ignore[union-attr]
            return error_response(code="ERR_FORBIDDEN", message="Staff access required.", http_status=403, request=request)

        from datetime import datetime, timedelta, timezone

        from django.db.models import Count
        from django.db.models.functions import TruncMonth

        from apps.orgs.infrastructure.models import Organization
        from apps.orgs.infrastructure.support_models import SupportTicket

        now = datetime.now(timezone.utc)
        d30 = now - timedelta(days=30)
        d60 = now - timedelta(days=60)
        d365 = now - timedelta(days=365)

        total = Organization.objects.count()
        active = Organization.objects.filter(status="active").count()
        pending = Organization.objects.filter(status="pending_review").count()
        suspended = Organization.objects.filter(status="suspended").count()
        verified = Organization.objects.filter(is_verified=True).count()

        new_30d = Organization.objects.filter(created_at__gte=d30).count()
        prev_30d = Organization.objects.filter(created_at__gte=d60, created_at__lt=d30).count()

        plan_breakdown = {}
        for plan in Organization.Plan.values:
            count = Organization.objects.filter(plan=plan).count()
            if count > 0:
                plan_breakdown[plan] = count

        open_tickets = SupportTicket.objects.filter(status__in=["open", "in_progress"]).count()
        escalated_tickets = SupportTicket.objects.filter(status="escalated").count()

        monthly_qs = (
            Organization.objects.filter(created_at__gte=d365)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        month_map = {row["month"].strftime("%Y-%m"): row["count"] for row in monthly_qs}
        org_monthly_series = []
        for i in range(11, -1, -1):
            from datetime import timedelta as td

            dt = now.replace(day=1) - td(days=30 * i)
            key = dt.strftime("%Y-%m")
            org_monthly_series.append(month_map.get(key, 0))

        return success_response(
            {
                "orgs": {
                    "total": total,
                    "active": active,
                    "pending": pending,
                    "suspended": suspended,
                    "verified": verified,
                    "new_30d": new_30d,
                    "prev_30d": prev_30d,
                    "plan_breakdown": plan_breakdown,
                    "monthly_series": org_monthly_series,
                },
                "tickets": {
                    "open": open_tickets,
                    "escalated": escalated_tickets,
                },
            },
            request=request,
        )
