"""DRF API views for moderation endpoints."""

from __future__ import annotations

import uuid

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api.responses import created_response, success_response
from apps.common.permissions import IsSuperAdminFromAllowedIP
from apps.moderation.application.use_cases.create_case import CreateModerationCaseUseCase
from apps.moderation.application.use_cases.get_case import GetModerationCaseUseCase
from apps.moderation.application.use_cases.get_moderation_stats import GetModerationStatsUseCase
from apps.moderation.application.use_cases.list_cases import ListModerationCasesUseCase
from apps.moderation.application.use_cases.update_case_status import UpdateCaseStatusUseCase
from apps.moderation.infrastructure.repositories import DjangoModerationCaseRepository
from apps.moderation.presentation.serializers import (
    CreateModerationCaseSerializer,
    ModerationCaseSerializer,
    ModerationStatsSerializer,
    UpdateCaseStatusSerializer,
)
from apps.orgs.infrastructure.audit_publisher import publish_audit

_REPO = DjangoModerationCaseRepository
_CASE_SER = ModerationCaseSerializer
_CREATE_SER = CreateModerationCaseSerializer
_UPDATE_SER = UpdateCaseStatusSerializer
_STATS_SER = ModerationStatsSerializer
_PERM = IsSuperAdminFromAllowedIP


class ModerationCaseListCreateView(APIView):
    """List all moderation cases or create a new one."""

    permission_classes = [_PERM]

    @extend_schema(
        tags=["Moderation"],
        summary="List moderation cases",
        description="Returns all flagged content cases. Superadmin only. Optional ?status= filter.",
        parameters=[
            OpenApiParameter(
                name="status",
                location=OpenApiParameter.QUERY,
                description="Filter by status: pending | under_review | dismissed | warned | taken_down",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(description="List of moderation cases.", response=_CASE_SER(many=True)),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            403: OpenApiResponse(description="Superadmin access required."),
        },
    )
    def get(self, request: Request) -> Response:
        """Return all moderation cases, filtered by ?status= if provided."""
        status_filter = request.query_params.get("status") or None
        cases = ListModerationCasesUseCase(repo=_REPO()).execute(status=status_filter)
        return success_response(_CASE_SER(cases, many=True).data, request=request)

    @extend_schema(
        tags=["Moderation"],
        summary="Create moderation case",
        description="Report a piece of content for moderation review. Superadmin only.",
        request=_CREATE_SER,
        responses={
            201: OpenApiResponse(description="Moderation case created.", response=_CASE_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            403: OpenApiResponse(description="Superadmin access required."),
            422: OpenApiResponse(description="Validation error or invalid content_type."),
        },
    )
    def post(self, request: Request) -> Response:
        """Create a new moderation case for the reported content."""
        ser = _CREATE_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        # reporter is the authenticated admin making the call
        reporter_id = uuid.UUID(str(request.user.id))
        result = CreateModerationCaseUseCase(repo=_REPO()).execute(
            content_type=d["content_type"],
            content_id=d["content_id"],
            content_title=d["content_title"],
            reason=d["reason"],
            reporter_id=reporter_id,
            organization_id=d.get("organization_id"),
        )
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="moderation.case.created",
            metadata={"case_id": str(result.id), "content_type": result.content_type},
        )
        return created_response(_CASE_SER(result).data, request=request)


class ModerationCaseDetailView(APIView):
    """Retrieve or update a single moderation case by id."""

    permission_classes = [_PERM]

    @extend_schema(
        tags=["Moderation"],
        summary="Get moderation case",
        responses={
            200: OpenApiResponse(description="Moderation case found.", response=_CASE_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            403: OpenApiResponse(description="Superadmin access required."),
            404: OpenApiResponse(description="Case not found."),
        },
    )
    def get(self, request: Request, case_id: uuid.UUID) -> Response:
        """Return the moderation case matching the given id."""
        result = GetModerationCaseUseCase(repo=_REPO()).execute(case_id=case_id)
        return success_response(_CASE_SER(result).data, request=request)

    @extend_schema(
        tags=["Moderation"],
        summary="Update case status",
        description="Transition a moderation case to a new status. Superadmin only.",
        request=_UPDATE_SER,
        responses={
            200: OpenApiResponse(description="Case status updated.", response=_CASE_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            403: OpenApiResponse(description="Superadmin access required."),
            404: OpenApiResponse(description="Case not found."),
            422: OpenApiResponse(description="Invalid status transition."),
        },
    )
    def patch(self, request: Request, case_id: uuid.UUID) -> Response:
        """Change the status of a moderation case."""
        ser = _UPDATE_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        reviewer_id = uuid.UUID(str(request.user.id))
        result = UpdateCaseStatusUseCase(repo=_REPO()).execute(
            case_id=case_id,
            status=d["status"],
            reviewer_id=reviewer_id,
            reviewer_notes=d.get("reviewer_notes", ""),
        )
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="moderation.case.updated",
            metadata={"case_id": str(case_id), "status": d["status"]},
        )
        return success_response(_CASE_SER(result).data, request=request)


class ModerationStatsView(APIView):
    """Return aggregated KPI stats for the moderation dashboard."""

    permission_classes = [_PERM]

    @extend_schema(
        tags=["Moderation"],
        summary="Get moderation stats",
        description="Returns counts by status, approval rate, and average resolution time. Superadmin only.",
        responses={
            200: OpenApiResponse(description="Moderation KPI stats.", response=_STATS_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            403: OpenApiResponse(description="Superadmin access required."),
        },
    )
    def get(self, request: Request) -> Response:
        """Return aggregated moderation KPI data for the dashboard."""
        stats = GetModerationStatsUseCase(repo=_REPO()).execute()
        return success_response(_STATS_SER(stats).data, request=request)
