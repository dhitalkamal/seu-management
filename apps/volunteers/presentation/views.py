"""DRF API views for volunteers endpoints."""

from __future__ import annotations

import uuid

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api.responses import created_response, success_response
from apps.volunteers.application.use_cases.apply_to_role import ApplyToVolunteerRoleUseCase
from apps.volunteers.application.use_cases.approve_application import ApproveApplicationUseCase
from apps.volunteers.application.use_cases.cancel_application import CancelApplicationUseCase
from apps.volunteers.application.use_cases.create_role import CreateVolunteerRoleUseCase
from apps.volunteers.application.use_cases.list_applications import ListApplicationsUseCase
from apps.volunteers.application.use_cases.reject_application import RejectApplicationUseCase
from apps.volunteers.infrastructure.repositories import (
    DjangoVolunteerApplicationRepository,
    DjangoVolunteerRoleRepository,
)
from apps.volunteers.presentation.serializers import (
    ApplySerializer,
    CreateRoleSerializer,
    VolunteerApplicationResponseSerializer,
    VolunteerRoleResponseSerializer,
)

_IS_AUTH = IsAuthenticated
_CREATED = created_response
_UUID = uuid.UUID
_CREATE_ROLE_UC = CreateVolunteerRoleUseCase
_APPLY_UC = ApplyToVolunteerRoleUseCase
_APPROVE_UC = ApproveApplicationUseCase
_REJECT_UC = RejectApplicationUseCase
_CANCEL_APP_UC = CancelApplicationUseCase
_LIST_APPS_UC = ListApplicationsUseCase
_ROLE_REPO = DjangoVolunteerRoleRepository
_APP_REPO = DjangoVolunteerApplicationRepository
_CREATE_ROLE_SER = CreateRoleSerializer
_APPLY_SER = ApplySerializer
_ROLE_RESP_SER = VolunteerRoleResponseSerializer
_APP_RESP_SER = VolunteerApplicationResponseSerializer


class VolunteerRoleView(APIView):
    """Create a new volunteer role for an event."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Create volunteer role",
        request=_CREATE_ROLE_SER,
        responses={
            201: OpenApiResponse(description="Role created.", response=_ROLE_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
        },
    )
    def post(self, request: Request) -> Response:
        """Create and persist a volunteer role with is_active=True."""
        ser = _CREATE_ROLE_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        result = _CREATE_ROLE_UC(_ROLE_REPO()).execute(
            event_id=d["event_id"],
            name=d["name"],
            description=d["description"],
            capacity=d["capacity"],
            organization_id=d["organization_id"],
        )
        return _CREATED(_ROLE_RESP_SER(result).data, request=request)


class VolunteerRoleApplyView(APIView):
    """Apply to a volunteer role."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Apply to volunteer role",
        request=_APPLY_SER,
        responses={
            201: OpenApiResponse(description="Application submitted.", response=_APP_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Role not found or inactive."),
            409: OpenApiResponse(description="Already applied or role at capacity."),
        },
    )
    def post(self, request: Request, role_id: uuid.UUID) -> Response:
        """Submit a pending application for the authenticated user."""
        ser = _APPLY_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        result = _APPLY_UC(_ROLE_REPO(), _APP_REPO()).execute(
            role_id=role_id,
            user_id=_UUID(str(request.user.id)),
            event_id=ser.validated_data["event_id"],
        )
        return _CREATED(_APP_RESP_SER(result).data, request=request)


class VolunteerApplicationListView(APIView):
    """List all applications for a volunteer role."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="List role applications",
        responses={
            200: OpenApiResponse(description="Applications.", response=_APP_RESP_SER(many=True)),
            401: OpenApiResponse(description="Missing or invalid JWT."),
        },
    )
    def get(self, request: Request, role_id: uuid.UUID) -> Response:
        """Return all applications for the role."""
        results = _LIST_APPS_UC(_APP_REPO()).execute(role_id=role_id)
        return success_response(_APP_RESP_SER(results, many=True).data, request=request)


class VolunteerApplicationApproveView(APIView):
    """Approve a pending volunteer application."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Approve application",
        request=None,
        responses={
            200: OpenApiResponse(description="Application approved.", response=_APP_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Application not found."),
        },
    )
    def post(self, request: Request, application_id: uuid.UUID) -> Response:
        """Set application status to approved."""
        result = _APPROVE_UC(_APP_REPO()).execute(application_id=application_id)
        return success_response(_APP_RESP_SER(result).data, request=request)


class VolunteerApplicationRejectView(APIView):
    """Reject a pending volunteer application."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Reject application",
        request=None,
        responses={
            200: OpenApiResponse(description="Application rejected.", response=_APP_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Application not found."),
        },
    )
    def post(self, request: Request, application_id: uuid.UUID) -> Response:
        """Set application status to rejected."""
        result = _REJECT_UC(_APP_REPO()).execute(application_id=application_id)
        return success_response(_APP_RESP_SER(result).data, request=request)


class VolunteerApplicationCancelView(APIView):
    """Cancel a volunteer application."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Cancel application",
        request=None,
        responses={
            200: OpenApiResponse(description="Application cancelled.", response=_APP_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Application not found."),
        },
    )
    def post(self, request: Request, application_id: uuid.UUID) -> Response:
        """Set application status to cancelled."""
        result = _CANCEL_APP_UC(_APP_REPO()).execute(application_id=application_id)
        return success_response(_APP_RESP_SER(result).data, request=request)
