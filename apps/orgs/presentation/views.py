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
from apps.common.permissions import IsOrgAdmin, IsOrgOwner, IsSuperAdminFromAllowedIP
from apps.orgs.application.use_cases.accept_invite import AcceptInviteUseCase
from apps.orgs.application.use_cases.add_member import AddOrgMemberUseCase
from apps.orgs.application.use_cases.approve_org import ApproveOrganizationUseCase
from apps.orgs.application.use_cases.create_invite import CreateInviteUseCase
from apps.orgs.application.use_cases.create_org import CreateOrganizationUseCase
from apps.orgs.application.use_cases.decline_invite import DeclineInviteUseCase
from apps.orgs.application.use_cases.get_org import GetOrganizationUseCase
from apps.orgs.application.use_cases.list_invites import ListInvitesUseCase
from apps.orgs.application.use_cases.list_orgs import ListOrganizationsUseCase
from apps.orgs.application.use_cases.reinstate_org import ReinstateOrganizationUseCase
from apps.orgs.application.use_cases.reject_org import RejectOrganizationUseCase
from apps.orgs.application.use_cases.revoke_invite import RevokeInviteUseCase
from apps.orgs.application.use_cases.soft_delete_org import SoftDeleteOrganizationUseCase
from apps.orgs.application.use_cases.suspend_org import SuspendOrganizationUseCase
from apps.orgs.application.use_cases.update_org import UpdateOrganizationUseCase
from apps.orgs.infrastructure.audit_publisher import publish_audit
from apps.orgs.infrastructure.event_publisher import OrgEventPublisher
from apps.orgs.infrastructure.repositories import DjangoOrgInviteRepository, DjangoOrgMemberRepository, DjangoOrgRepository
from apps.orgs.presentation.serializers import (
    AcceptInviteSerializer,
    AddMemberSerializer,
    CreateInviteSerializer,
    CreateOrgSerializer,
    OrgDocumentResponseSerializer,
    OrgInviteResponseSerializer,
    OrgMemberResponseSerializer,
    OrgResponseSerializer,
    UpdateOrgSerializer,
    UploadOrgDocumentSerializer,
)

_IS_AUTH = IsAuthenticated
_CREATED = created_response
_UUID = uuid.UUID
_PAGINATION = StandardPagination
_CREATE_ORG_UC = CreateOrganizationUseCase
_GET_ORG_UC = GetOrganizationUseCase
_LIST_ORGS_UC = ListOrganizationsUseCase
_ADD_MEMBER_UC = AddOrgMemberUseCase
_APPROVE_UC = ApproveOrganizationUseCase
_REJECT_UC = RejectOrganizationUseCase
_SUSPEND_UC = SuspendOrganizationUseCase
_REINSTATE_UC = ReinstateOrganizationUseCase
_SOFT_DELETE_UC = SoftDeleteOrganizationUseCase
_ORG_REPO = DjangoOrgRepository
_MEMBER_REPO = DjangoOrgMemberRepository
_CREATE_ORG_SER = CreateOrgSerializer
_ORG_RESP_SER = OrgResponseSerializer
_UPDATE_ORG_UC = UpdateOrganizationUseCase
_UPDATE_ORG_SER = UpdateOrgSerializer
_ADD_MEMBER_SER = AddMemberSerializer
_MEMBER_RESP_SER = OrgMemberResponseSerializer
_INVITE_REPO = DjangoOrgInviteRepository
_CREATE_INVITE_UC = CreateInviteUseCase
_ACCEPT_INVITE_UC = AcceptInviteUseCase
_DECLINE_INVITE_UC = DeclineInviteUseCase
_REVOKE_INVITE_UC = RevokeInviteUseCase
_LIST_INVITES_UC = ListInvitesUseCase
_CREATE_INVITE_SER = CreateInviteSerializer
_INVITE_RESP_SER = OrgInviteResponseSerializer
_ACCEPT_INVITE_SER = AcceptInviteSerializer

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
            "Checks connectivity to PostgreSQL, Redis, and RabbitMQ. Returns 200 when all dependencies are healthy, 503 when any are down."
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
    """List the authenticated user's organizations or create a new one."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Organizations"],
        summary="List my organizations",
        responses={200: OpenApiResponse(description="Paginated org list.", response=_ORG_RESP_SER(many=True))},
    )
    def get(self, request: Request) -> Response:
        """Return orgs where the user is a member, or all orgs for staff/superadmin."""
        is_staff = getattr(request.user, "is_staff", False)
        if is_staff:
            orgs = _ORG_REPO().list_all()
        else:
            user_id = _UUID(str(request.user.id))
            orgs = _LIST_ORGS_UC(_ORG_REPO()).execute(user_id=user_id)
        paginator = _PAGINATION()
        page = paginator.paginate_queryset(orgs, request)
        return paginator.get_paginated_response(_ORG_RESP_SER(page, many=True).data)

    @extend_schema(
        tags=["Organizations"],
        summary="Create an organization",
        request=_CREATE_ORG_SER,
        responses={
            201: OpenApiResponse(description="Organization created.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            409: OpenApiResponse(description="Slug already taken."),
        },
    )
    def post(self, request: Request) -> Response:
        """Create a new organization; creator is assigned owner membership."""
        ser = _CREATE_ORG_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        creator_id = _UUID(str(request.user.id))
        result = _CREATE_ORG_UC(_ORG_REPO(), _MEMBER_REPO()).execute(
            created_by=creator_id,
            name=d["name"],
            slug=d["slug"],
            contact_email=d["contact_email"],
            description=d["description"],
            website=d["website"],
            logo_url=d["logo_url"],
            phone=d["phone"],
            address=d["address"],
            city=d["city"],
            country=d["country"],
            org_type=d["org_type"],
            facebook_url=d["facebook_url"],
            twitter_url=d["twitter_url"],
            instagram_url=d["instagram_url"],
            linkedin_url=d["linkedin_url"],
        )
        publisher = OrgEventPublisher()
        # notify IAM service so it can seed the owner's cached org roles
        publisher.publish_member_added(
            org_id=result.id,
            user_id=creator_id,
            role="owner",
        )
        # broadcast org lifecycle event for notification-service and analytics
        publisher.publish_org_created(
            org_id=result.id,
            org_name=result.name,
            creator_id=creator_id,
            contact_email=result.contact_email,
        )
        publish_audit(
            request=request,
            user_id=_UUID(str(request.user.id)),
            event_type="org.created",
            metadata={"org_id": str(result.id), "org_name": result.name},
        )
        return _CREATED(_ORG_RESP_SER(result).data, request=request)


class OrgDetailView(APIView):
    """Retrieve or update a single organization by id."""

    # GET is open to any authenticated member; PATCH requires at least admin
    permission_classes = [IsAuthenticated]

    def get_permissions(self) -> list:
        """Return IsOrgAdmin for PATCH; fall back to IsAuthenticated for GET."""
        if self.request.method == "PATCH":
            return [IsOrgAdmin()]
        return super().get_permissions()

    @extend_schema(
        tags=["Organizations"],
        summary="Get organization",
        responses={
            200: OpenApiResponse(description="Organization found.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organization not found."),
        },
    )
    def get(self, request: Request, org_id: uuid.UUID) -> Response:
        """Return the organization matching the given id."""
        result = _GET_ORG_UC(_ORG_REPO()).execute(org_id=org_id)
        return success_response(_ORG_RESP_SER(result).data, request=request)

    @extend_schema(
        tags=["Organizations"],
        summary="Update organization",
        request=_UPDATE_ORG_SER,
        responses={
            200: OpenApiResponse(description="Organization updated.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organization not found."),
        },
    )
    def patch(self, request: Request, org_id: uuid.UUID) -> Response:
        """Partial-update profile fields on an existing organization."""
        ser = _UPDATE_ORG_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        result = _UPDATE_ORG_UC(_ORG_REPO()).execute(org_id=org_id, **ser.validated_data)
        publish_audit(
            request=request,
            user_id=_UUID(str(request.user.id)),
            event_type="org.updated",
            metadata={"org_id": str(org_id)},
        )
        return success_response(_ORG_RESP_SER(result).data, request=request)


class OrgMembersView(APIView):
    """Add a member to an organization."""

    permission_classes = [IsOrgAdmin]

    @extend_schema(
        tags=["Organizations"],
        summary="Add org member",
        request=_ADD_MEMBER_SER,
        responses={
            201: OpenApiResponse(description="Member added.", response=_MEMBER_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organization not found."),
            409: OpenApiResponse(description="User is already a member."),
        },
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Add the given user as a member of this organization."""
        ser = _ADD_MEMBER_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        result = _ADD_MEMBER_UC(_ORG_REPO(), _MEMBER_REPO()).execute(
            org_id=org_id,
            user_id=d["user_id"],
            role=d["role"],
        )
        # notify IAM service to invalidate any stale cached roles for this user+org
        OrgEventPublisher().publish_member_added(
            org_id=org_id,
            user_id=result.user_id,
            role=result.role,
        )
        publish_audit(
            request=request,
            user_id=_UUID(str(request.user.id)),
            event_type="org.member.added",
            metadata={"org_id": str(org_id), "member_user_id": str(result.user_id)},
        )
        return _CREATED(_MEMBER_RESP_SER(result).data, request=request)


class OrgApproveView(APIView):
    """Approve a pending_review organization (superadmin only)."""

    permission_classes = [IsSuperAdminFromAllowedIP]

    @extend_schema(
        tags=["Organizations"],
        summary="Approve organization",
        request=None,
        responses={
            200: OpenApiResponse(description="Organization approved.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organization not found."),
            422: OpenApiResponse(description="Invalid status transition."),
        },
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Transition the organization from pending_review to active."""
        result = _APPROVE_UC(_ORG_REPO()).execute(org_id=org_id)
        OrgEventPublisher().publish_org_approved(
            org_id=result.id,
            org_name=result.name,
            contact_email=result.contact_email,
        )
        publish_audit(
            request=request,
            user_id=_UUID(str(request.user.id)),
            event_type="org.approved",
            metadata={"org_id": str(result.id)},
        )
        return success_response(_ORG_RESP_SER(result).data, request=request)


class OrgRejectView(APIView):
    """Reject a pending_review organization (superadmin only)."""

    permission_classes = [IsSuperAdminFromAllowedIP]

    @extend_schema(
        tags=["Organizations"],
        summary="Reject organization",
        request=None,
        responses={
            200: OpenApiResponse(description="Organization rejected.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organization not found."),
            422: OpenApiResponse(description="Invalid status transition."),
        },
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Transition the organization from pending_review to suspended."""
        result = _REJECT_UC(_ORG_REPO()).execute(org_id=org_id)
        OrgEventPublisher().publish_org_rejected(
            org_id=result.id,
            org_name=result.name,
            reason="",
            contact_email=result.contact_email,
        )
        publish_audit(
            request=request,
            user_id=_UUID(str(request.user.id)),
            event_type="org.rejected",
            metadata={"org_id": str(result.id)},
        )
        return success_response(_ORG_RESP_SER(result).data, request=request)


class OrgSuspendView(APIView):
    """Suspend an active organization (superadmin only)."""

    permission_classes = [IsSuperAdminFromAllowedIP]

    @extend_schema(
        tags=["Organizations"],
        summary="Suspend organization",
        request=None,
        responses={
            200: OpenApiResponse(description="Organization suspended.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organization not found."),
            422: OpenApiResponse(description="Invalid status transition."),
        },
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Transition the organization from active to suspended."""
        result = _SUSPEND_UC(_ORG_REPO()).execute(org_id=org_id)
        publish_audit(
            request=request,
            user_id=_UUID(str(request.user.id)),
            event_type="org.suspended",
            metadata={"org_id": str(result.id)},
        )
        return success_response(_ORG_RESP_SER(result).data, request=request)


class OrgReinstateView(APIView):
    """Reinstate a suspended organization (superadmin only)."""

    permission_classes = [IsSuperAdminFromAllowedIP]

    @extend_schema(
        tags=["Organizations"],
        summary="Reinstate organization",
        request=None,
        responses={
            200: OpenApiResponse(description="Organization reinstated.", response=_ORG_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organization not found."),
            422: OpenApiResponse(description="Invalid status transition."),
        },
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Transition the organization from suspended to active."""
        result = _REINSTATE_UC(_ORG_REPO()).execute(org_id=org_id)
        publish_audit(
            request=request,
            user_id=_UUID(str(request.user.id)),
            event_type="org.reinstated",
            metadata={"org_id": str(result.id)},
        )
        return success_response(_ORG_RESP_SER(result).data, request=request)


class OrgDeleteView(APIView):
    """Soft-delete an organization (owner only)."""

    permission_classes = [IsOrgOwner]

    @extend_schema(
        tags=["Organizations"],
        summary="Soft-delete organization",
        request=None,
        responses={
            204: OpenApiResponse(description="Organization deleted."),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organization not found."),
        },
    )
    def delete(self, request: Request, org_id: uuid.UUID) -> Response:
        """Set deleted_at on the organization."""
        _SOFT_DELETE_UC(_ORG_REPO()).execute(org_id=org_id)
        publish_audit(
            request=request,
            user_id=_UUID(str(request.user.id)),
            event_type="org.deleted",
            metadata={"org_id": str(org_id)},
        )
        return Response(status=204)


# * organization document endpoints


_DOC_RESP_SER = OrgDocumentResponseSerializer
_UPLOAD_DOC_SER = UploadOrgDocumentSerializer


class OrgDocumentListCreateView(APIView):
    """List or upload documents for an organization."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, org_id: uuid.UUID) -> Response:
        """Return all documents belonging to the given organization."""
        from apps.orgs.infrastructure.models import OrgDocument as OrgDocModel

        docs = OrgDocModel.objects.filter(organization_id=org_id).order_by("-uploaded_at")
        return success_response(_DOC_RESP_SER(docs, many=True).data, request=request)

    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Upload a new document for the given organization."""
        from apps.orgs.infrastructure.models import OrgDocument as OrgDocModel

        ser = _UPLOAD_DOC_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        doc = OrgDocModel.objects.create(
            organization_id=org_id,
            doc_type=d["doc_type"],
            file_url=d["file_url"],
            file_name=d["file_name"],
            file_size=d.get("file_size", 0),
        )
        return _CREATED(_DOC_RESP_SER(doc).data, request=request)


class OrgDocumentDeleteView(APIView):
    """Delete a single document from an organization."""

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, org_id: uuid.UUID, doc_id: uuid.UUID) -> Response:
        """Remove the specified document."""
        from apps.orgs.infrastructure.models import OrgDocument as OrgDocModel

        OrgDocModel.objects.filter(id=doc_id, organization_id=org_id).delete()
        return Response(status=204)


class OrgDocumentUploadView(APIView):
    """POST /organizations/<org_id>/documents/upload/ - upload a real file to MinIO."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Org Documents"],
        summary="Upload a verification document to MinIO",
        description="Accepts a multipart file, stores it in MinIO, and saves the document record.",
        responses={201: OpenApiResponse(description="Document uploaded and saved.")},
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Upload file to MinIO and save the document record for the organization."""
        from apps.common.storage import upload_file
        from apps.orgs.infrastructure.models import OrgDocument as OrgDocModel

        file_obj = request.FILES.get("file")
        doc_type = request.data.get("doc_type", "other")

        if not file_obj:
            return error_response(
                code="ERR_NO_FILE",
                message="file is required.",
                http_status=422,
                request=request,
            )

        try:
            file_url = upload_file(
                file_obj,
                file_obj.name,
                file_obj.content_type or "application/octet-stream",
            )
        except Exception as exc:
            return error_response(
                code="ERR_UPLOAD_FAILED",
                message=f"File upload failed: {exc}",
                http_status=500,
                request=request,
            )

        doc = OrgDocModel.objects.create(
            organization_id=org_id,
            doc_type=doc_type,
            file_url=file_url,
            file_name=file_obj.name,
            file_size=file_obj.size,
        )

        return created_response(
            {
                "id": str(doc.id),
                "org_id": str(doc.organization_id),
                "doc_type": doc.doc_type,
                "file_url": doc.file_url,
                "file_name": doc.file_name,
                "file_size": doc.file_size,
                "uploaded_at": doc.uploaded_at.isoformat(),
            },
            request=request,
        )


# * org invite endpoints


class OrgInviteListCreateView(APIView):
    """List pending invites for an org or send a new invite."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Org Invites"],
        summary="List pending invites",
        responses={
            200: OpenApiResponse(description="Pending invite list.", response=_INVITE_RESP_SER(many=True)),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organization not found."),
        },
    )
    def get(self, request: Request, org_id: uuid.UUID) -> Response:
        """Return all pending invites for the given organization."""
        invites = _LIST_INVITES_UC(_ORG_REPO(), _INVITE_REPO()).execute(org_id=org_id)
        return success_response(_INVITE_RESP_SER(invites, many=True).data, request=request)

    @extend_schema(
        tags=["Org Invites"],
        summary="Create an invite",
        request=_CREATE_INVITE_SER,
        responses={
            201: OpenApiResponse(description="Invite created.", response=_INVITE_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Organization not found."),
            409: OpenApiResponse(description="Pending invite already exists for this email."),
        },
    )
    def post(self, request: Request, org_id: uuid.UUID) -> Response:
        """Send an invite to join this organization."""
        ser = _CREATE_INVITE_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        result = _CREATE_INVITE_UC(_ORG_REPO(), _INVITE_REPO()).execute(
            org_id=org_id,
            inviter_id=_UUID(str(request.user.id)),
            invitee_email=d["invitee_email"],
            role=d["role"],
        )
        publish_audit(
            request=request,
            user_id=_UUID(str(request.user.id)),
            event_type="org.invite.sent",
            metadata={"org_id": str(org_id), "invitee_email": d["invitee_email"]},
        )
        return _CREATED(_INVITE_RESP_SER(result).data, request=request)


class OrgInviteAcceptView(APIView):
    """Accept a pending invite by token."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Org Invites"],
        summary="Accept an invite",
        request=_ACCEPT_INVITE_SER,
        responses={
            200: OpenApiResponse(description="Invite accepted; membership created.", response=_INVITE_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Invite not found."),
            410: OpenApiResponse(description="Invite has expired."),
            422: OpenApiResponse(description="Invite is not pending."),
        },
    )
    def post(self, request: Request, invite_id: uuid.UUID) -> Response:
        """Accept the invite and create an org membership."""
        ser = _ACCEPT_INVITE_SER(data=request.data)
        ser.is_valid(raise_exception=True)
        user_id = ser.validated_data["user_id"]
        result = _ACCEPT_INVITE_UC(_INVITE_REPO(), _MEMBER_REPO()).execute(
            invite_id=invite_id,
            user_id=user_id,
        )
        # invite carries the role; notify IAM after the membership is created
        OrgEventPublisher().publish_member_added(
            org_id=result.org_id,
            user_id=user_id,
            role=result.role,
        )
        publish_audit(
            request=request,
            user_id=_UUID(str(request.user.id)),
            event_type="org.invite.accepted",
            metadata={"org_id": str(result.org_id)},
        )
        return success_response(_INVITE_RESP_SER(result).data, request=request)


class OrgInviteDetailView(APIView):
    """Decline or revoke a single invite."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Org Invites"],
        summary="Decline an invite",
        request=None,
        responses={
            200: OpenApiResponse(description="Invite declined.", response=_INVITE_RESP_SER),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Invite not found."),
            422: OpenApiResponse(description="Invite is not pending."),
        },
    )
    def post(self, request: Request, invite_id: uuid.UUID) -> Response:
        """Decline the invite (invitee action)."""
        result = _DECLINE_INVITE_UC(_INVITE_REPO()).execute(invite_id=invite_id)
        return success_response(_INVITE_RESP_SER(result).data, request=request)

    @extend_schema(
        tags=["Org Invites"],
        summary="Revoke an invite",
        request=None,
        responses={
            204: OpenApiResponse(description="Invite revoked."),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Invite not found."),
            422: OpenApiResponse(description="Invite is not pending."),
        },
    )
    def delete(self, request: Request, invite_id: uuid.UUID) -> Response:
        """Revoke the invite (inviter/admin action)."""
        _REVOKE_INVITE_UC(_INVITE_REPO()).execute(invite_id=invite_id)
        return Response(status=204)
