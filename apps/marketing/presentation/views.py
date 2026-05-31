"""DRF API views for marketing endpoints."""

from __future__ import annotations

import uuid

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api.responses import created_response, error_response, success_response
from apps.marketing.application.use_cases.create_campaign import CreateCampaignUseCase
from apps.marketing.application.use_cases.create_segment import CreateSegmentUseCase
from apps.marketing.application.use_cases.list_campaigns import ListCampaignsUseCase
from apps.marketing.application.use_cases.list_segments import ListSegmentsUseCase
from apps.marketing.application.use_cases.send_campaign import SendCampaignUseCase
from apps.marketing.domain.exceptions import CampaignAlreadySentError, CampaignNotFoundError
from apps.marketing.infrastructure.event_publisher import MarketingEventPublisher
from apps.marketing.infrastructure.repositories import (
    DjangoAudienceSegmentRepository,
    DjangoCampaignRepository,
)
from apps.marketing.presentation.serializers import (
    CampaignResponseSerializer,
    CreateCampaignSerializer,
    CreateSegmentSerializer,
    SegmentResponseSerializer,
)
from apps.orgs.infrastructure.audit_publisher import publish_audit

_CREATED = created_response
_CAMPAIGN_REPO = DjangoCampaignRepository
_SEGMENT_REPO = DjangoAudienceSegmentRepository
_LIST_CAMPAIGNS_UC = ListCampaignsUseCase
_CREATE_CAMPAIGN_UC = CreateCampaignUseCase
_SEND_CAMPAIGN_UC = SendCampaignUseCase
_LIST_SEGMENTS_UC = ListSegmentsUseCase
_CREATE_SEGMENT_UC = CreateSegmentUseCase


class CampaignListCreateView(APIView):
    """GET /campaigns/ - list all; POST /campaigns/ - create."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Marketing"],
        summary="List campaigns",
        responses={200: CampaignResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        """Return all campaigns."""
        campaigns = _LIST_CAMPAIGNS_UC(_CAMPAIGN_REPO()).execute()
        return success_response(CampaignResponseSerializer(campaigns, many=True).data, request=request)

    @extend_schema(
        tags=["Marketing"],
        summary="Create campaign",
        request=CreateCampaignSerializer,
        responses={201: CampaignResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        """Create a new campaign in draft status."""
        ser = CreateCampaignSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        campaign = _CREATE_CAMPAIGN_UC(_CAMPAIGN_REPO()).execute(
            created_by=uuid.UUID(str(request.user.id)),
            name=d["name"],
            subject=d["subject"],
            body=d["body"],
            segment_id=d.get("segment_id"),
        )
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="campaign.created",
            metadata={"campaign_id": str(campaign.id), "campaign_name": campaign.name},
        )
        return _CREATED(CampaignResponseSerializer(campaign).data, request=request)


class CampaignSendView(APIView):
    """POST /campaigns/{campaign_id}/send/"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Marketing"],
        summary="Send campaign",
        responses={
            200: CampaignResponseSerializer,
            400: OpenApiResponse(description="Campaign already sent."),
            404: OpenApiResponse(description="Not found."),
        },
    )
    def post(self, request: Request, campaign_id: uuid.UUID) -> Response:
        """Transition the campaign to sent status and publish the delivery event."""
        # * the caller resolves the recipient list before sending;
        #   user_emails is optional -- pass [] when no explicit list provided
        user_emails: list[str] = request.data.get("user_emails", [])
        org_id_raw: str = request.data.get("org_id", "")
        org_id: uuid.UUID | None = None
        if org_id_raw:
            try:
                org_id = uuid.UUID(org_id_raw)
            except ValueError:
                return error_response(
                    code="ERR_CAMPAIGN_INVALID_ORG",
                    message="Invalid org_id format.",
                    http_status=400,
                    request=request,
                )
        try:
            campaign = _SEND_CAMPAIGN_UC(
                _CAMPAIGN_REPO(),
                publisher=MarketingEventPublisher(),
            ).execute(
                campaign_id=campaign_id,
                user_emails=user_emails,
                org_id=org_id,
            )
        except CampaignNotFoundError as exc:
            return error_response(
                code="ERR_CAMPAIGN_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        except CampaignAlreadySentError as exc:
            return error_response(
                code="ERR_CAMPAIGN_ALREADY_SENT",
                message=str(exc),
                http_status=400,
                request=request,
            )
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="campaign.sent",
            metadata={"campaign_id": str(campaign_id)},
        )
        return success_response(CampaignResponseSerializer(campaign).data, request=request)


class SegmentListCreateView(APIView):
    """GET /segments/ - list all; POST /segments/ - create."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Marketing"],
        summary="List audience segments",
        responses={200: SegmentResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        """Return all audience segments."""
        segments = _LIST_SEGMENTS_UC(_SEGMENT_REPO()).execute()
        return success_response(SegmentResponseSerializer(segments, many=True).data, request=request)

    @extend_schema(
        tags=["Marketing"],
        summary="Create audience segment",
        request=CreateSegmentSerializer,
        responses={201: SegmentResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        """Create a new audience segment."""
        ser = CreateSegmentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        segment = _CREATE_SEGMENT_UC(_SEGMENT_REPO()).execute(
            created_by=uuid.UUID(str(request.user.id)),
            name=d["name"],
            filters=d.get("filters", {}),
        )
        return _CREATED(SegmentResponseSerializer(segment).data, request=request)


class SponsorListCreateView(APIView):
    """List or create sponsors for an organization."""

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Sponsors"], summary="List sponsors")
    def get(self, request: Request) -> Response:
        """Return sponsors for the given organization_id."""
        from apps.marketing.infrastructure.models import Sponsor

        org_id = request.query_params.get("organization_id")
        qs = Sponsor.objects.filter(is_active=True)
        if org_id:
            qs = qs.filter(organization_id=org_id)
        data = list(qs.values("id", "organization_id", "name", "logo_url", "website", "tier", "amount", "event_ids", "created_at"))
        for d in data:
            d["id"] = str(d["id"])
            d["organization_id"] = str(d["organization_id"])
            d["amount"] = str(d["amount"])
        return success_response(data, request=request)

    @extend_schema(tags=["Sponsors"], summary="Create sponsor")
    def post(self, request: Request) -> Response:
        """Create a new sponsor."""
        from rest_framework import serializers as s

        from apps.marketing.infrastructure.models import Sponsor

        class Ser(s.Serializer):
            organization_id = s.UUIDField()
            name = s.CharField(max_length=255)
            logo_url = s.URLField(required=False, default="", allow_blank=True)
            website = s.URLField(required=False, default="", allow_blank=True)
            tier = s.ChoiceField(choices=["platinum", "gold", "silver", "bronze"], default="gold")
            amount = s.DecimalField(max_digits=12, decimal_places=2, default=0)
            event_ids = s.ListField(child=s.CharField(), default=list)

        ser = Ser(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        sponsor = Sponsor.objects.create(**d)
        return _CREATED(
            {
                "id": str(sponsor.id),
                "organization_id": str(sponsor.organization_id),
                "name": sponsor.name,
                "logo_url": sponsor.logo_url,
                "website": sponsor.website,
                "tier": sponsor.tier,
                "amount": str(sponsor.amount),
                "event_ids": sponsor.event_ids,
                "created_at": sponsor.created_at.isoformat(),
            },
            request=request,
        )


class SponsorDetailView(APIView):
    """Update or delete a sponsor."""

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Sponsors"], summary="Update sponsor")
    def patch(self, request: Request, sponsor_id: uuid.UUID) -> Response:
        """Partially update a sponsor."""
        from apps.marketing.infrastructure.models import Sponsor

        try:
            sponsor = Sponsor.objects.get(id=sponsor_id)
        except Sponsor.DoesNotExist:
            return error_response(code="ERR_NOT_FOUND", message="Sponsor not found.", http_status=404, request=request)
        for field in ["name", "logo_url", "website", "tier", "amount", "event_ids"]:
            if field in request.data:
                setattr(sponsor, field, request.data[field])
        sponsor.save()
        return success_response({"id": str(sponsor.id), "name": sponsor.name}, request=request)

    @extend_schema(tags=["Sponsors"], summary="Delete sponsor")
    def delete(self, request: Request, sponsor_id: uuid.UUID) -> Response:
        """Soft-delete a sponsor."""
        from apps.marketing.infrastructure.models import Sponsor

        try:
            sponsor = Sponsor.objects.get(id=sponsor_id)
        except Sponsor.DoesNotExist:
            return error_response(code="ERR_NOT_FOUND", message="Sponsor not found.", http_status=404, request=request)
        sponsor.is_active = False
        sponsor.save(update_fields=["is_active"])
        return Response(status=204)
