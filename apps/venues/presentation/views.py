"""DRF API views for venues endpoints."""

from __future__ import annotations

import uuid

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api.responses import created_response, error_response, success_response
from apps.orgs.infrastructure.audit_publisher import publish_audit
from apps.venues.application.use_cases.add_space import AddVenueSpaceUseCase
from apps.venues.application.use_cases.cancel_booking import CancelBookingUseCase
from apps.venues.application.use_cases.create_booking import CreateBookingUseCase
from apps.venues.application.use_cases.create_venue import CreateVenueUseCase
from apps.venues.application.use_cases.delete_venue import DeleteVenueUseCase
from apps.venues.application.use_cases.get_venue import GetVenueUseCase
from apps.venues.application.use_cases.list_bookings import ListVenueBookingsUseCase
from apps.venues.application.use_cases.list_spaces import ListVenueSpacesUseCase
from apps.venues.application.use_cases.list_venues import ListVenuesUseCase
from apps.venues.application.use_cases.update_venue import UpdateVenueUseCase
from apps.venues.domain.exceptions import VenueBookingNotFoundError, VenueConflictError, VenueNotFoundError
from apps.venues.infrastructure.repositories import (
    DjangoVenueBookingRepository,
    DjangoVenueRepository,
    DjangoVenueSpaceRepository,
)
from apps.venues.presentation.serializers import (
    CreateVenueBookingSerializer,
    CreateVenueSerializer,
    CreateVenueSpaceSerializer,
    UpdateVenueSerializer,
    VenueBookingResponseSerializer,
    VenueResponseSerializer,
    VenueSpaceResponseSerializer,
)

_CREATED = created_response
_REPO = DjangoVenueRepository
_SPACE_REPO = DjangoVenueSpaceRepository
_BOOKING_REPO = DjangoVenueBookingRepository
_LIST_UC = ListVenuesUseCase
_CREATE_UC = CreateVenueUseCase
_GET_UC = GetVenueUseCase
_UPDATE_UC = UpdateVenueUseCase
_DELETE_UC = DeleteVenueUseCase
_LIST_SPACES_UC = ListVenueSpacesUseCase
_ADD_SPACE_UC = AddVenueSpaceUseCase
_CREATE_BOOKING_UC = CreateBookingUseCase
_LIST_BOOKINGS_UC = ListVenueBookingsUseCase
_CANCEL_BOOKING_UC = CancelBookingUseCase


class VenueListCreateView(APIView):
    """GET /venues/?organization_id=... - list; POST /venues/ - create."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Venues"],
        summary="List org venues",
        responses={200: VenueResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        """Return all non-deleted venues for the given organization."""
        org_id_str = request.query_params.get("organization_id")
        if not org_id_str:
            return error_response(
                code="ERR_VENUE_ORG_REQUIRED",
                message="organization_id query param is required.",
                http_status=400,
                request=request,
            )
        try:
            org_id = uuid.UUID(org_id_str)
        except ValueError:
            return error_response(
                code="ERR_VENUE_INVALID_ORG_ID",
                message="Invalid organization_id.",
                http_status=400,
                request=request,
            )
        venues = _LIST_UC(_REPO()).execute(organization_id=org_id)
        return success_response(VenueResponseSerializer(venues, many=True).data, request=request)

    @extend_schema(
        tags=["Venues"],
        summary="Create venue",
        request=CreateVenueSerializer,
        responses={201: VenueResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        """Create a new venue for an organization."""
        ser = CreateVenueSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        venue = _CREATE_UC(_REPO()).execute(
            organization_id=d["organization_id"],
            created_by=uuid.UUID(str(request.user.id)),
            name=d["name"],
            address=d["address"],
            city=d["city"],
            country=d["country"],
            capacity=d["capacity"],
            description=d.get("description", ""),
            website=d.get("website", ""),
        )
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="venue.created",
            metadata={"venue_id": str(venue.id), "venue_name": venue.name},
        )
        return _CREATED(VenueResponseSerializer(venue).data, request=request)


class VenueDetailView(APIView):
    """GET /venues/{venue_id}/ - get; PUT /venues/{venue_id}/ - update; DELETE - delete."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Venues"],
        summary="Get venue",
        responses={
            200: VenueResponseSerializer,
            404: OpenApiResponse(description="Not found."),
        },
    )
    def get(self, request: Request, venue_id: uuid.UUID) -> Response:
        """Return a single venue."""
        try:
            venue = _GET_UC(_REPO()).execute(venue_id=venue_id)
        except VenueNotFoundError as exc:
            return error_response(code="ERR_VENUE_NOT_FOUND", message=str(exc), http_status=404, request=request)
        return success_response(VenueResponseSerializer(venue).data, request=request)

    @extend_schema(
        tags=["Venues"],
        summary="Update venue",
        request=UpdateVenueSerializer,
        responses={
            200: VenueResponseSerializer,
            404: OpenApiResponse(description="Not found."),
        },
    )
    def put(self, request: Request, venue_id: uuid.UUID) -> Response:
        """Partially update a venue."""
        ser = UpdateVenueSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        try:
            venue = _UPDATE_UC(_REPO()).execute(venue_id=venue_id, **d)
        except VenueNotFoundError as exc:
            return error_response(code="ERR_VENUE_NOT_FOUND", message=str(exc), http_status=404, request=request)
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="venue.updated",
            metadata={"venue_id": str(venue_id)},
        )
        return success_response(VenueResponseSerializer(venue).data, request=request)

    @extend_schema(
        tags=["Venues"],
        summary="Delete venue",
        responses={
            204: OpenApiResponse(description="Deleted."),
            404: OpenApiResponse(description="Not found."),
        },
    )
    def delete(self, request: Request, venue_id: uuid.UUID) -> Response:
        """Soft-delete a venue."""
        try:
            _DELETE_UC(_REPO()).execute(venue_id=venue_id)
        except VenueNotFoundError as exc:
            return error_response(code="ERR_VENUE_NOT_FOUND", message=str(exc), http_status=404, request=request)
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="venue.deleted",
            metadata={"venue_id": str(venue_id)},
        )
        return Response(status=204)


class VenueSpaceListCreateView(APIView):
    """GET /venues/{venue_id}/spaces/ - list; POST - add."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Venues"],
        summary="List venue spaces",
        responses={
            200: VenueSpaceResponseSerializer(many=True),
            404: OpenApiResponse(description="Venue not found."),
        },
    )
    def get(self, request: Request, venue_id: uuid.UUID) -> Response:
        """Return all spaces for a venue."""
        try:
            spaces = _LIST_SPACES_UC(_REPO(), _SPACE_REPO()).execute(venue_id=venue_id)
        except VenueNotFoundError as exc:
            return error_response(code="ERR_VENUE_NOT_FOUND", message=str(exc), http_status=404, request=request)
        return success_response(VenueSpaceResponseSerializer(spaces, many=True).data, request=request)

    @extend_schema(
        tags=["Venues"],
        summary="Add venue space",
        request=CreateVenueSpaceSerializer,
        responses={
            201: VenueSpaceResponseSerializer,
            404: OpenApiResponse(description="Venue not found."),
        },
    )
    def post(self, request: Request, venue_id: uuid.UUID) -> Response:
        """Add a new space to a venue."""
        ser = CreateVenueSpaceSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        try:
            space = _ADD_SPACE_UC(_REPO(), _SPACE_REPO()).execute(
                venue_id=venue_id,
                name=d["name"],
                capacity=d["capacity"],
                floor=d.get("floor", ""),
            )
        except VenueNotFoundError as exc:
            return error_response(code="ERR_VENUE_NOT_FOUND", message=str(exc), http_status=404, request=request)
        return _CREATED(VenueSpaceResponseSerializer(space).data, request=request)


class VenueBookingListCreateView(APIView):
    """GET /venues/{venue_id}/bookings/ - list; POST - create booking."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Venues"],
        summary="List venue bookings",
        responses={
            200: VenueBookingResponseSerializer(many=True),
            404: OpenApiResponse(description="Venue not found."),
        },
    )
    def get(self, request: Request, venue_id: uuid.UUID) -> Response:
        """Return all bookings for the venue ordered by start_time."""
        bookings = _LIST_BOOKINGS_UC(_BOOKING_REPO()).execute(venue_id=venue_id)
        return success_response(VenueBookingResponseSerializer(bookings, many=True).data, request=request)

    @extend_schema(
        tags=["Venues"],
        summary="Create a venue booking",
        description=("Book a venue for a specific event and time range. Returns 409 if any confirmed booking overlaps the requested time."),
        request=CreateVenueBookingSerializer,
        responses={
            201: VenueBookingResponseSerializer,
            404: OpenApiResponse(description="Venue not found."),
            409: OpenApiResponse(description="Booking conflict."),
            422: OpenApiResponse(description="Validation error."),
        },
    )
    def post(self, request: Request, venue_id: uuid.UUID) -> Response:
        """Validate, check conflicts, and persist the booking."""
        ser = CreateVenueBookingSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        try:
            booking = _CREATE_BOOKING_UC(_REPO(), _BOOKING_REPO()).execute(
                venue_id=venue_id,
                event_id=d["event_id"],
                booked_by=uuid.UUID(str(request.user.id)),
                start_time=d["start_time"],
                end_time=d["end_time"],
            )
        except VenueNotFoundError as exc:
            return error_response(code="ERR_VENUE_NOT_FOUND", message=str(exc), http_status=404, request=request)
        except VenueConflictError as exc:
            return error_response(code="ERR_VENUE_CONFLICT", message=str(exc), http_status=409, request=request)
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="venue.booking.created",
            metadata={"venue_id": str(venue_id), "booking_id": str(booking.id)},
        )
        return _CREATED(VenueBookingResponseSerializer(booking).data, request=request)


class VenueBookingDetailView(APIView):
    """DELETE /venues/{venue_id}/bookings/{booking_id}/ - cancel a booking."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Venues"],
        summary="Cancel a venue booking",
        responses={
            200: OpenApiResponse(description="Booking cancelled."),
            404: OpenApiResponse(description="Booking not found."),
        },
    )
    def delete(self, request: Request, venue_id: uuid.UUID, booking_id: uuid.UUID) -> Response:
        """Set the booking status to cancelled."""
        try:
            _CANCEL_BOOKING_UC(_BOOKING_REPO()).execute(booking_id=booking_id)
        except VenueBookingNotFoundError as exc:
            return error_response(code="ERR_BOOKING_NOT_FOUND", message=str(exc), http_status=404, request=request)
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="venue.booking.cancelled",
            metadata={"venue_id": str(venue_id), "booking_id": str(booking_id)},
        )
        return success_response({"cancelled": True}, request=request)
