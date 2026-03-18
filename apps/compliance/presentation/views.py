"""DRF API views for the compliance controls endpoints."""

from __future__ import annotations

import uuid

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api.responses import created_response, error_response, success_response
from apps.common.permissions import IsSuperAdminFromAllowedIP
from apps.compliance.application.summary import compute_summary
from apps.compliance.models import ComplianceControl
from apps.compliance.presentation.serializers import (
    ComplianceControlCreateSerializer,
    ComplianceControlPatchSerializer,
    ComplianceControlResponseSerializer,
)

_RESP = ComplianceControlResponseSerializer


def _serialize_control(obj: ComplianceControl) -> dict:
    """Convert an ORM instance to a plain dict for the response serializer."""
    return {
        "id": str(obj.id),
        "category": obj.category,
        "name": obj.name,
        "description": obj.description,
        "status": obj.status,
        "last_checked": obj.last_checked.isoformat() if obj.last_checked else None,
        "updated_at": obj.updated_at.isoformat(),
        "created_at": obj.created_at.isoformat(),
    }


class ComplianceControlListCreateView(APIView):
    """GET /compliance/controls/ list, POST /compliance/controls/ create."""

    permission_classes = [IsSuperAdminFromAllowedIP]

    @extend_schema(
        tags=["Compliance"],
        summary="List all compliance controls",
        description="Returns every compliance control record ordered by category and name.",
        responses={
            200: OpenApiResponse(description="List of controls.", response=_RESP(many=True)),
            403: OpenApiResponse(description="Superadmin access required."),
        },
    )
    def get(self, request: Request) -> Response:
        """Return all controls in the database."""
        controls = ComplianceControl.objects.all()
        data = [_serialize_control(c) for c in controls]
        return success_response(data, request=request)

    @extend_schema(
        tags=["Compliance"],
        summary="Create a compliance control",
        description="Add a new SOC2-style compliance control that can be managed through the admin UI.",
        request=ComplianceControlCreateSerializer,
        responses={
            201: OpenApiResponse(description="Control created.", response=_RESP),
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="Superadmin access required."),
        },
    )
    def post(self, request: Request) -> Response:
        """Validate payload and persist a new compliance control."""
        ser = ComplianceControlCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        control = ComplianceControl.objects.create(
            category=d["category"],
            name=d["name"],
            description=d.get("description", ""),
            status=d["status"],
            last_checked=d.get("last_checked"),
        )
        return created_response(_serialize_control(control), request=request)


class ComplianceControlDetailView(APIView):
    """PATCH /compliance/controls/{id}/ update, DELETE /compliance/controls/{id}/ delete."""

    permission_classes = [IsSuperAdminFromAllowedIP]

    @extend_schema(
        tags=["Compliance"],
        summary="Update a compliance control",
        description="Partially update a compliance control (status, name, etc.).",
        request=ComplianceControlPatchSerializer,
        responses={
            200: OpenApiResponse(description="Control updated.", response=_RESP),
            400: OpenApiResponse(description="Validation error."),
            403: OpenApiResponse(description="Superadmin access required."),
            404: OpenApiResponse(description="Control not found."),
        },
    )
    def patch(self, request: Request, control_id: uuid.UUID) -> Response:
        """Apply partial updates to the compliance control record."""
        try:
            control = ComplianceControl.objects.get(pk=control_id)
        except ComplianceControl.DoesNotExist:
            return error_response(
                code="ERR_CONTROL_NOT_FOUND",
                message="Compliance control not found.",
                http_status=404,
                request=request,
            )
        ser = ComplianceControlPatchSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        update_fields: list[str] = []
        for field in ("category", "name", "description", "status", "last_checked"):
            if field in d:
                setattr(control, field, d[field])
                update_fields.append(field)
        if update_fields:
            control.save(update_fields=update_fields)
        return success_response(_serialize_control(control), request=request)

    @extend_schema(
        tags=["Compliance"],
        summary="Delete a compliance control",
        description="Permanently delete a compliance control record.",
        responses={
            204: OpenApiResponse(description="Control deleted."),
            403: OpenApiResponse(description="Superadmin access required."),
            404: OpenApiResponse(description="Control not found."),
        },
    )
    def delete(self, request: Request, control_id: uuid.UUID) -> Response:
        """Delete the compliance control by id."""
        try:
            control = ComplianceControl.objects.get(pk=control_id)
        except ComplianceControl.DoesNotExist:
            return error_response(
                code="ERR_CONTROL_NOT_FOUND",
                message="Compliance control not found.",
                http_status=404,
                request=request,
            )
        control.delete()
        return Response(status=204)


class ComplianceSummaryView(APIView):
    """GET /compliance/summary/ - aggregated counts across all controls."""

    permission_classes = [IsSuperAdminFromAllowedIP]

    @extend_schema(
        tags=["Compliance"],
        summary="Compliance summary statistics",
        description="Returns total, passing, failing counts plus a per-category breakdown.",
        responses={
            200: OpenApiResponse(description="Summary stats."),
            403: OpenApiResponse(description="Superadmin access required."),
        },
    )
    def get(self, request: Request) -> Response:
        """Compute and return the aggregated compliance summary."""
        controls = list(ComplianceControl.objects.values("category", "status"))
        summary = compute_summary(controls)
        return success_response(summary, request=request)
