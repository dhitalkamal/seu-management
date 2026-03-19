"""DRF API views for volunteers endpoints."""

from __future__ import annotations

import logging
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
from apps.volunteers.application.use_cases.checkin_volunteer import CheckInVolunteerUseCase
from apps.volunteers.application.use_cases.checkout_volunteer import CheckOutVolunteerUseCase
from apps.volunteers.application.use_cases.create_role import CreateVolunteerRoleUseCase
from apps.volunteers.application.use_cases.create_shift import CreateShiftUseCase
from apps.volunteers.application.use_cases.generate_certificate import GenerateCertificateUseCase
from apps.volunteers.application.use_cases.get_shift import GetShiftUseCase
from apps.volunteers.application.use_cases.list_applications import ListApplicationsUseCase
from apps.volunteers.application.use_cases.list_shifts_for_role import ListShiftsForRoleUseCase
from apps.volunteers.application.use_cases.rate_volunteer import RateVolunteerUseCase
from apps.volunteers.application.use_cases.reject_application import RejectApplicationUseCase
from apps.volunteers.application.use_cases.verify_certificate import VerifyCertificateUseCase
from apps.volunteers.domain.repositories import IEventPublisher
from apps.volunteers.infrastructure.pdf import ReportlabCertificatePdfGenerator
from apps.volunteers.infrastructure.repositories import (
    DjangoCertificateRepository,
    DjangoVolunteerApplicationRepository,
    DjangoVolunteerProfileRepository,
    DjangoVolunteerRoleRepository,
    DjangoVolunteerShiftRepository,
)
from apps.volunteers.infrastructure.storage import S3CertificateStorage
from apps.volunteers.presentation.serializers import (
    ApplySerializer,
    CertificateResponseSerializer,
    CreateRoleSerializer,
    CreateShiftSerializer,
    RateApplicationSerializer,
    VolunteerApplicationResponseSerializer,
    VolunteerProfileResponseSerializer,
    VolunteerRoleResponseSerializer,
    VolunteerShiftResponseSerializer,
)

_log = logging.getLogger(__name__)

# * ruff anchor assignments - prevent import stripping
_IS_AUTH = IsAuthenticated
_CREATED = created_response
_UUID = uuid.UUID
_CREATE_ROLE_UC = CreateVolunteerRoleUseCase
_APPLY_UC = ApplyToVolunteerRoleUseCase
_APPROVE_UC = ApproveApplicationUseCase
_REJECT_UC = RejectApplicationUseCase
_CANCEL_APP_UC = CancelApplicationUseCase
_LIST_APPS_UC = ListApplicationsUseCase
_CHECKIN_UC = CheckInVolunteerUseCase
_CHECKOUT_UC = CheckOutVolunteerUseCase
_RATE_UC = RateVolunteerUseCase
_GEN_CERT_UC = GenerateCertificateUseCase
_VERIFY_CERT_UC = VerifyCertificateUseCase
_CREATE_SHIFT_UC = CreateShiftUseCase
_LIST_SHIFTS_UC = ListShiftsForRoleUseCase
_GET_SHIFT_UC = GetShiftUseCase
_ROLE_REPO = DjangoVolunteerRoleRepository
_APP_REPO = DjangoVolunteerApplicationRepository
_CERT_REPO = DjangoCertificateRepository
_SHIFT_REPO = DjangoVolunteerShiftRepository
_PROFILE_REPO = DjangoVolunteerProfileRepository
_PDF_GEN = ReportlabCertificatePdfGenerator
_STORAGE = S3CertificateStorage
_CREATE_ROLE_SER = CreateRoleSerializer
_APPLY_SER = ApplySerializer
_RATE_SER = RateApplicationSerializer
_CREATE_SHIFT_SER = CreateShiftSerializer
_ROLE_RESP_SER = VolunteerRoleResponseSerializer
_APP_RESP_SER = VolunteerApplicationResponseSerializer
_SHIFT_RESP_SER = VolunteerShiftResponseSerializer
_CERT_RESP_SER = CertificateResponseSerializer
_PROFILE_RESP_SER = VolunteerProfileResponseSerializer


def _get_publisher() -> IEventPublisher:
    """Return a publisher instance, falling back to a logging no-op if RabbitMQ is unconfigured."""
    from django.conf import settings

    url = getattr(settings, "RABBITMQ_URL", None)
    if url:
        from apps.volunteers.infrastructure.publisher import RabbitMQEventPublisher

        return RabbitMQEventPublisher(url)

    class _LogPublisher(IEventPublisher):
        def publish(self, event_type: str, payload: dict) -> None:
            _log.info("event published (no broker): %s %s", event_type, payload)

    return _LogPublisher()


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
            organisation_id=d["organisation_id"],
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
            user_id=_UUID(str(request.user.id)),  # type: ignore[union-attr]
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
        """Set application status to approved and notify participation-service."""
        result = _APPROVE_UC(_APP_REPO(), _get_publisher()).execute(application_id=application_id)
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


class VolunteerApplicationCheckInView(APIView):
    """Check a volunteer in to their shift."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Check in volunteer",
        request=None,
        responses={
            200: OpenApiResponse(description="Volunteer checked in.", response=_APP_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Application not found."),
            409: OpenApiResponse(description="Already checked in."),
            422: OpenApiResponse(description="Application not in approved status."),
        },
    )
    def post(self, request: Request, application_id: uuid.UUID) -> Response:
        """Stamp check_in_at and transition status to confirmed."""
        result = _CHECKIN_UC(_APP_REPO()).execute(application_id)
        return success_response(_APP_RESP_SER(result).data, request=request)


class VolunteerApplicationCheckOutView(APIView):
    """Check a volunteer out after their shift."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Check out volunteer",
        request=None,
        responses={
            200: OpenApiResponse(description="Volunteer checked out.", response=_APP_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Application not found."),
            422: OpenApiResponse(description="Not checked in or already checked out."),
        },
    )
    def post(self, request: Request, application_id: uuid.UUID) -> Response:
        """Stamp check_out_at on the application."""
        result = _CHECKOUT_UC(_APP_REPO()).execute(application_id)
        return success_response(_APP_RESP_SER(result).data, request=request)


class VolunteerApplicationRateView(APIView):
    """Rate a volunteer after their shift."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Rate volunteer",
        request=_RATE_SER,
        responses={
            200: OpenApiResponse(description="Volunteer rated.", response=_APP_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Application not found."),
            422: OpenApiResponse(description="Application not ratable or invalid rating."),
        },
    )
    def post(self, request: Request, application_id: uuid.UUID) -> Response:
        """Save rating and feedback, update profile average."""
        ser = _RATE_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        result = _RATE_UC(_APP_REPO(), _PROFILE_REPO()).execute(
            application_id=application_id,
            rating=d["rating"],
            feedback=d["feedback"],
        )
        return success_response(_APP_RESP_SER(result).data, request=request)


class VolunteerCertificateGenerateView(APIView):
    """Generate and issue a participation certificate."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Generate certificate",
        request=None,
        responses={
            201: OpenApiResponse(description="Certificate issued.", response=_CERT_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Application not found."),
            409: OpenApiResponse(description="Certificate already issued."),
            422: OpenApiResponse(description="Application not eligible for certificate."),
        },
    )
    def post(self, request: Request, application_id: uuid.UUID) -> Response:
        """Generate PDF, upload, persist, and publish the certificate event."""
        use_case = _GEN_CERT_UC(
            _APP_REPO(),
            _CERT_REPO(),
            _PDF_GEN(),
            _STORAGE(),
            _get_publisher(),
            _PROFILE_REPO(),
        )
        result = use_case.execute(application_id)
        return _CREATED(_CERT_RESP_SER(result).data, request=request)


class VolunteerCertificateVerifyView(APIView):
    """Publicly verify a certificate by ID."""

    @extend_schema(
        tags=["Volunteers"],
        summary="Verify certificate",
        responses={
            200: OpenApiResponse(description="Certificate found.", response=_CERT_RESP_SER),
            404: OpenApiResponse(description="Certificate not found."),
        },
    )
    def get(self, request: Request, certificate_id: uuid.UUID) -> Response:
        """Return certificate details for public verification."""
        result = _VERIFY_CERT_UC(_CERT_REPO()).execute(certificate_id)
        return success_response(_CERT_RESP_SER(result).data, request=request)


class VolunteerShiftCreateView(APIView):
    """Create a shift slot for a volunteer role."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Create volunteer shift",
        request=_CREATE_SHIFT_SER,
        responses={
            201: OpenApiResponse(description="Shift created.", response=_SHIFT_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Role not found."),
        },
    )
    def post(self, request: Request, role_id: uuid.UUID) -> Response:
        """Create and persist a shift under the given role."""
        ser = _CREATE_SHIFT_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        result = _CREATE_SHIFT_UC(_ROLE_REPO(), _SHIFT_REPO()).execute(
            role_id=role_id,
            event_id=d["event_id"],
            starts_at=d["starts_at"],
            ends_at=d["ends_at"],
            capacity=d["capacity"],
            location=d["location"],
            description=d["description"],
        )
        return _CREATED(_SHIFT_RESP_SER(result).data, request=request)


class VolunteerShiftListView(APIView):
    """List all shifts for a volunteer role."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="List role shifts",
        responses={
            200: OpenApiResponse(description="Shifts.", response=_SHIFT_RESP_SER(many=True)),
            401: OpenApiResponse(description="Missing or invalid JWT."),
        },
    )
    def get(self, request: Request, role_id: uuid.UUID) -> Response:
        """Return all shifts for the role."""
        results = _LIST_SHIFTS_UC(_SHIFT_REPO()).execute(role_id)
        return success_response(_SHIFT_RESP_SER(results, many=True).data, request=request)


class VolunteerShiftDetailView(APIView):
    """Retrieve a single volunteer shift."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Get volunteer shift",
        responses={
            200: OpenApiResponse(description="Shift found.", response=_SHIFT_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Shift not found."),
        },
    )
    def get(self, request: Request, shift_id: uuid.UUID) -> Response:
        """Return a single shift by ID."""
        result = _GET_SHIFT_UC(_SHIFT_REPO()).execute(shift_id)
        return success_response(_SHIFT_RESP_SER(result).data, request=request)


class VolunteerProfileView(APIView):
    """Retrieve the authenticated volunteer's aggregate profile."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Volunteers"],
        summary="Get volunteer profile",
        responses={
            200: OpenApiResponse(description="Profile found.", response=_PROFILE_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
        },
    )
    def get(self, request: Request) -> Response:
        """Return or create the profile for the authenticated user."""
        user_id = _UUID(str(request.user.id))  # type: ignore[union-attr]
        profile = _PROFILE_REPO().get_or_create(user_id)
        return success_response(_PROFILE_RESP_SER(profile).data, request=request)
