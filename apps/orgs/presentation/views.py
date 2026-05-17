"""DRF API views for orgs endpoints."""

from __future__ import annotations

import uuid

from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api.pagination import StandardPagination
from apps.common.api.responses import created_response, error_response, success_response
from apps.common.health import check_database, check_rabbitmq, check_redis
from apps.orgs.application.use_cases.add_member import AddOrgMemberUseCase
from apps.orgs.application.use_cases.approve_org import ApproveOrganisationUseCase
from apps.orgs.application.use_cases.create_org import CreateOrganisationUseCase
from apps.orgs.application.use_cases.get_org import GetOrganisationUseCase
from apps.orgs.application.use_cases.list_orgs import ListOrganisationsUseCase
from apps.orgs.application.use_cases.reinstate_org import ReinstateOrganisationUseCase
from apps.orgs.application.use_cases.reject_org import RejectOrganisationUseCase
from apps.orgs.application.use_cases.soft_delete_org import SoftDeleteOrganisationUseCase
from apps.orgs.application.use_cases.suspend_org import SuspendOrganisationUseCase
from apps.orgs.infrastructure.repositories import DjangoOrgMemberRepository, DjangoOrgRepository
from apps.orgs.presentation.serializers import (
    AddMemberSerializer,
    CreateOrgSerializer,
    OrgMemberResponseSerializer,
    OrgResponseSerializer,
)

_IS_AUTH = IsAuthenticated
_CREATED = created_response
_UUID = uuid.UUID
_PAGINATION = StandardPagination
_CREATE_ORG_UC = CreateOrganisationUseCase
_GET_ORG_UC = GetOrganisationUseCase
_LIST_ORGS_UC = ListOrganisationsUseCase
_ADD_MEMBER_UC = AddOrgMemberUseCase
_APPROVE_UC = ApproveOrganisationUseCase
_REJECT_UC = RejectOrganisationUseCase
_SUSPEND_UC = SuspendOrganisationUseCase
_REINSTATE_UC = ReinstateOrganisationUseCase
_SOFT_DELETE_UC = SoftDeleteOrganisationUseCase
_ORG_REPO = DjangoOrgRepository
_MEMBER_REPO = DjangoOrgMemberRepository
_CREATE_ORG_SER = CreateOrgSerializer
_ORG_RESP_SER = OrgResponseSerializer
_ADD_MEMBER_SER = AddMemberSerializer
_MEMBER_RESP_SER = OrgMemberResponseSerializer

_CHECKS = inline_serializer(
    name="DependencyChecks",
    fields={
        "database": serializers.ChoiceField(choices=["healthy", "unhealthy"]),
        "redis": serializers.ChoiceField(choices=["healthy", "unhealthy"]),
        "rabbitmq": serializers.ChoiceField(choices=["healthy", "unhealthy"]),
    },
)
_META_SCHEMA = inline_serializer(
    name="ResponseMeta",
    fields={
        "request_id": serializers.CharField(),
        "timestamp": serializers.CharField(),
    },
)


class HealthCheckView(APIView):
    """Reports the operational status of all external dependencies."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Health"],
        summary="Service health check",
        description=(
            "Checks connectivity to PostgreSQL, Redis, and RabbitMQ. "
            "Returns 200 when all dependencies are healthy, 503 when any are down."
        ),
        auth=[],
        responses={
            200: OpenApiResponse(
                description="All dependencies are healthy.",
                response=inline_serializer(
                    name="HealthyResponse",
                    fields={
                        "data": inline_serializer(
                            name="HealthyData",
                            fields={
                                "service": serializers.CharField(),
                                "status": serializers.CharField(),
                                "version": serializers.CharField(),
                                "checks": _CHECKS,
                            },
                        ),
                        "error": serializers.JSONField(allow_null=True),
                        "meta": _META_SCHEMA,
                    },
                ),
            ),
            503: OpenApiResponse(
                description="One or more dependencies are unavailable.",
                response=inline_serializer(
                    name="UnhealthyResponse",
                    fields={
                        "data": serializers.JSONField(allow_null=True),
                        "error": inline_serializer(
                            name="HealthError",
                            fields={
                                "code": serializers.CharField(),
                                "message": serializers.CharField(),
                                "details": serializers.JSONField(allow_null=True),
                            },
                        ),
                        "meta": _META_SCHEMA,
                    },
                ),
            ),
        },
    )
    def get(self, request: Request) -> Response:
        """Check DB, Redis, and RabbitMQ and return an aggregated status."""
        db_status, db_err = check_database()
        redis_status, redis_err = check_redis()
        rmq_status, rmq_err = check_rabbitmq()

        checks: dict = {
            "database": db_status,
            "redis": redis_status,
            "rabbitmq": rmq_status,
        }
        dep_errors: dict = {
            k: v
            for k, v in {
                "database": db_err,
                "redis": redis_err,
                "rabbitmq": rmq_err,
            }.items()
            if v is not None
        }

        all_healthy = all(s == "healthy" for s in checks.values())

        if all_healthy:
            return success_response(
                {
                    "service": settings.SERVICE_NAME,
                    "status": "healthy",
                    "version": "0.1.0",
                    "checks": checks,
                },
                request=request,
            )

        return error_response(
            code="ERR_SERVICE_UNHEALTHY",
            message="One or more dependencies are unavailable.",
            details={"checks": checks, **({"errors": dep_errors} if dep_errors else {})},
            http_status=503,
            request=request,
        )


class OrgListCreateView(APIView):
    """List the authenticated user's organisations or create a new one."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Organisations"],
        summary="List my organisations",
        responses={
            200: OpenApiResponse(
                description="Paginated org list.", response=_ORG_RESP_SER(many=True)
            )
        },
    )
    def get(self, request: Request) -> Response:
        """Return orgs where the authenticated user is an active member."""
        user_id = _UUID(str(request.user.id))
        orgs = _LIST_ORGS_UC(_ORG_REPO()).execute(user_id=user_id)
        paginator = _PAGINATION()
        page = paginator.paginate_queryset(orgs, request)
        return paginator.get_paginated_response(_ORG_RESP_SER(page, many=True).data)

    @extend_schema(
        tags=["Organisations"],
        summary="Create an organisation",
        request=_CREATE_ORG_SER,
        responses={
            201: OpenApiResponse(description="Organisation created.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            409: OpenApiResponse(description="Slug already taken."),
        },
    )
    def post(self, request: Request) -> Response:
        """Create a new organisation; creator is assigned owner membership."""
        ser = _CREATE_ORG_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        result = _CREATE_ORG_UC(_ORG_REPO(), _MEMBER_REPO()).execute(
            created_by=_UUID(str(request.user.id)),
            name=d["name"],
            slug=d["slug"],
            contact_email=d["contact_email"],
            description=d["description"],
            website=d["website"],
            logo_url=d["logo_url"],
        )
        return _CREATED(_ORG_RESP_SER(result).data, request=request)


class OrgDetailView(APIView):
    """Retrieve a single organisation by id."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Organisations"],
        summary="Get organisation",
        responses={
            200: OpenApiResponse(description="Organisation found.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organisation not found."),
        },
    )
    def get(self, request: Request, org_id: uuid.UUID) -> Response:
        """Return the organisation matching the given id."""
        result = _GET_ORG_UC(_ORG_REPO()).execute(org_id=org_id)
        return success_response(_ORG_RESP_SER(result).data, request=request)


class OrgMembersView(APIView):
    """Add a member to an organisation."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Organisations"],
        summary="Add org member",
        request=_ADD_MEMBER_SER,
        responses={
            201: OpenApiResponse(description="Member added.", response=_MEMBER_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organisation not found."),
            409: OpenApiResponse(description="User is already a member."),
        },
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Add the given user as a member of this organisation."""
        ser = _ADD_MEMBER_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        result = _ADD_MEMBER_UC(_ORG_REPO(), _MEMBER_REPO()).execute(
            org_id=org_id,
            user_id=d["user_id"],
            role=d["role"],
        )
        return _CREATED(_MEMBER_RESP_SER(result).data, request=request)


class OrgApproveView(APIView):
    """Approve a pending_review organisation (superadmin only)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Organisations"],
        summary="Approve organisation",
        request=None,
        responses={
            200: OpenApiResponse(description="Organisation approved.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organisation not found."),
            422: OpenApiResponse(description="Invalid status transition."),
        },
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Transition the organisation from pending_review to active."""
        result = _APPROVE_UC(_ORG_REPO()).execute(org_id=org_id)
        return success_response(_ORG_RESP_SER(result).data, request=request)


class OrgRejectView(APIView):
    """Reject a pending_review organisation (superadmin only)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Organisations"],
        summary="Reject organisation",
        request=None,
        responses={
            200: OpenApiResponse(description="Organisation rejected.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organisation not found."),
            422: OpenApiResponse(description="Invalid status transition."),
        },
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Transition the organisation from pending_review to suspended."""
        result = _REJECT_UC(_ORG_REPO()).execute(org_id=org_id)
        return success_response(_ORG_RESP_SER(result).data, request=request)


class OrgSuspendView(APIView):
    """Suspend an active organisation (superadmin only)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Organisations"],
        summary="Suspend organisation",
        request=None,
        responses={
            200: OpenApiResponse(description="Organisation suspended.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organisation not found."),
            422: OpenApiResponse(description="Invalid status transition."),
        },
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Transition the organisation from active to suspended."""
        result = _SUSPEND_UC(_ORG_REPO()).execute(org_id=org_id)
        return success_response(_ORG_RESP_SER(result).data, request=request)


class OrgReinstateView(APIView):
    """Reinstate a suspended organisation (superadmin only)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Organisations"],
        summary="Reinstate organisation",
        request=None,
        responses={
            200: OpenApiResponse(description="Organisation reinstated.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organisation not found."),
            422: OpenApiResponse(description="Invalid status transition."),
        },
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Transition the organisation from suspended to active."""
        result = _REINSTATE_UC(_ORG_REPO()).execute(org_id=org_id)
        return success_response(_ORG_RESP_SER(result).data, request=request)


class OrgDeleteView(APIView):
    """Soft-delete an organisation (owner only)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Organisations"],
        summary="Soft-delete organisation",
        request=None,
        responses={
            204: OpenApiResponse(description="Organisation deleted."),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organisation not found."),
        },
    )
    def delete(self, request: Request, org_id: uuid.UUID) -> Response:
        """Set deleted_at on the organisation."""
        _SOFT_DELETE_UC(_ORG_REPO()).execute(org_id=org_id)
        return Response(status=204)
