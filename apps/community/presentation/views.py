"""DRF API views for community endpoints."""

from __future__ import annotations

import uuid

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api.responses import created_response, error_response, success_response
from apps.community.application.use_cases.create_community import CreateCommunityUseCase
from apps.community.application.use_cases.create_post import CreatePostUseCase
from apps.community.application.use_cases.delete_post import DeletePostUseCase
from apps.community.application.use_cases.get_community import GetCommunityUseCase
from apps.community.application.use_cases.join_community import JoinCommunityUseCase
from apps.community.application.use_cases.list_communities import ListCommunitiesUseCase
from apps.community.application.use_cases.list_posts import ListPostsUseCase
from apps.community.domain.exceptions import (
    AlreadyMemberError,
    CommunityNotFoundError,
    CommunityPostNotFoundError,
    SlugAlreadyExistsError,
)
from apps.community.infrastructure.repositories import (
    DjangoCommunityMemberRepository,
    DjangoCommunityPostRepository,
    DjangoCommunityRepository,
)
from apps.community.presentation.serializers import (
    CommunityPostResponseSerializer,
    CommunityResponseSerializer,
    CreateCommunitySerializer,
    CreatePostSerializer,
)

_CREATED = created_response
_LIST_UC = ListCommunitiesUseCase
_CREATE_UC = CreateCommunityUseCase
_GET_UC = GetCommunityUseCase
_JOIN_UC = JoinCommunityUseCase
_LIST_POSTS_UC = ListPostsUseCase
_CREATE_POST_UC = CreatePostUseCase
_DELETE_POST_UC = DeletePostUseCase
_REPO = DjangoCommunityRepository
_MEMBER_REPO = DjangoCommunityMemberRepository
_POST_REPO = DjangoCommunityPostRepository


class CommunityListCreateView(APIView):
    """GET /communities/ - list all; POST /communities/ - create new."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="List communities",
        responses={200: CommunityResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        """Return all active communities."""
        communities = _LIST_UC(_REPO()).execute()
        return success_response(CommunityResponseSerializer(communities, many=True).data, request=request)

    @extend_schema(
        tags=["Community"],
        summary="Create community",
        request=CreateCommunitySerializer,
        responses={
            201: CommunityResponseSerializer,
            400: OpenApiResponse(description="Slug already taken."),
        },
    )
    def post(self, request: Request) -> Response:
        """Create a new community."""
        ser = CreateCommunitySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        try:
            community = _CREATE_UC(_REPO()).execute(
                created_by=uuid.UUID(str(request.user.id)),
                name=d["name"],
                slug=d["slug"],
                privacy=d["privacy"],
                organisation_id=d.get("organisation_id"),
                description=d.get("description", ""),
            )
        except SlugAlreadyExistsError as exc:
            return error_response(
                code="ERR_COMMUNITY_SLUG_TAKEN",
                message=str(exc),
                http_status=400,
                request=request,
            )
        return _CREATED(CommunityResponseSerializer(community).data, request=request)


class CommunityDetailView(APIView):
    """GET /communities/{community_id}/"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Get community",
        responses={
            200: CommunityResponseSerializer,
            404: OpenApiResponse(description="Not found."),
        },
    )
    def get(self, request: Request, community_id: uuid.UUID) -> Response:
        """Return a single community."""
        try:
            community = _GET_UC(_REPO()).execute(community_id=community_id)
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        return success_response(CommunityResponseSerializer(community).data, request=request)


class CommunityJoinView(APIView):
    """POST /communities/{community_id}/join/"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Join community",
        responses={
            201: OpenApiResponse(description="Joined."),
            400: OpenApiResponse(description="Already a member."),
            404: OpenApiResponse(description="Not found."),
        },
    )
    def post(self, request: Request, community_id: uuid.UUID) -> Response:
        """Join the community as the authenticated user."""
        try:
            _JOIN_UC(_REPO(), _MEMBER_REPO()).execute(
                community_id=community_id,
                user_id=uuid.UUID(str(request.user.id)),
            )
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        except AlreadyMemberError as exc:
            return error_response(
                code="ERR_COMMUNITY_ALREADY_MEMBER",
                message=str(exc),
                http_status=400,
                request=request,
            )
        return _CREATED({"joined": True}, request=request)


class CommunityPostListCreateView(APIView):
    """GET /communities/{community_id}/posts/ - list; POST - create."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="List community posts",
        responses={
            200: CommunityPostResponseSerializer(many=True),
            404: OpenApiResponse(description="Community not found."),
        },
    )
    def get(self, request: Request, community_id: uuid.UUID) -> Response:
        """Return all published posts for a community."""
        try:
            posts = _LIST_POSTS_UC(_REPO(), _POST_REPO()).execute(community_id=community_id)
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        return success_response(CommunityPostResponseSerializer(posts, many=True).data, request=request)

    @extend_schema(
        tags=["Community"],
        summary="Create community post",
        request=CreatePostSerializer,
        responses={
            201: CommunityPostResponseSerializer,
            404: OpenApiResponse(description="Community not found."),
        },
    )
    def post(self, request: Request, community_id: uuid.UUID) -> Response:
        """Create a new post inside the community."""
        ser = CreatePostSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        try:
            post = _CREATE_POST_UC(_REPO(), _POST_REPO()).execute(
                community_id=community_id,
                author_id=uuid.UUID(str(request.user.id)),
                content=d["content"],
                post_type=d.get("post_type", "text"),
                media_urls=d.get("media_urls", []),
            )
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        return _CREATED(CommunityPostResponseSerializer(post).data, request=request)


class CommunityPostDetailView(APIView):
    """DELETE /communities/posts/{post_id}/"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Delete community post",
        responses={
            204: OpenApiResponse(description="Deleted."),
            404: OpenApiResponse(description="Not found."),
        },
    )
    def delete(self, request: Request, post_id: uuid.UUID) -> Response:
        """Soft-delete the post (author only)."""
        try:
            _DELETE_POST_UC(_POST_REPO()).execute(
                post_id=post_id,
                requester_id=uuid.UUID(str(request.user.id)),
            )
        except CommunityPostNotFoundError as exc:
            return error_response(
                code="ERR_POST_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        return Response(status=204)
