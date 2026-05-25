"""DRF API views for community endpoints."""

from __future__ import annotations

import uuid

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.api.responses import created_response, error_response, success_response
from apps.community.application.use_cases.create_comment import CreateCommentUseCase
from apps.community.application.use_cases.create_community import CreateCommunityUseCase
from apps.community.application.use_cases.create_post import CreatePostUseCase
from apps.community.application.use_cases.delete_comment import DeleteCommentUseCase
from apps.community.application.use_cases.delete_post import DeletePostUseCase
from apps.community.application.use_cases.get_community import GetCommunityUseCase
from apps.community.application.use_cases.join_community import JoinCommunityUseCase
from apps.community.application.use_cases.leave_community import LeaveCommunityUseCase
from apps.community.application.use_cases.list_comments import ListCommentsUseCase
from apps.community.application.use_cases.list_communities import ListCommunitiesUseCase
from apps.community.application.use_cases.list_posts import ListPostsUseCase
from apps.community.application.use_cases.list_reactions import ListReactionsUseCase
from apps.community.application.use_cases.react_to_comment import ReactToCommentUseCase
from apps.community.application.use_cases.react_to_post import ReactToPostUseCase
from apps.community.application.use_cases.remove_reaction import RemoveReactionUseCase
from apps.community.application.use_cases.update_comment import UpdateCommentUseCase
from apps.community.domain.exceptions import (
    AlreadyMemberError,
    CommentEditWindowExpiredError,
    CommentNotFoundError,
    CommunityNotFoundError,
    CommunityOwnerCannotLeaveError,
    CommunityPostNotFoundError,
    NotMemberError,
    ReactionNotFoundError,
    SlugAlreadyExistsError,
)
from apps.community.infrastructure.repositories import (
    DjangoCommentReactionRepository,
    DjangoCommunityMemberRepository,
    DjangoCommunityPostRepository,
    DjangoCommunityRepository,
    DjangoPostCommentRepository,
    DjangoPostReactionRepository,
)
from apps.community.presentation.serializers import (
    CommentReactionResponseSerializer,
    CommunityPostResponseSerializer,
    CommunityResponseSerializer,
    CreateCommentSerializer,
    CreateCommunitySerializer,
    CreatePostSerializer,
    PostCommentResponseSerializer,
    PostReactionResponseSerializer,
    ReactToCommentSerializer,
    ReactToPostSerializer,
    UpdateCommentSerializer,
)

_CREATED = created_response
_LIST_UC = ListCommunitiesUseCase
_CREATE_UC = CreateCommunityUseCase
_GET_UC = GetCommunityUseCase
_JOIN_UC = JoinCommunityUseCase
_LEAVE_UC = LeaveCommunityUseCase
_LIST_POSTS_UC = ListPostsUseCase
_CREATE_POST_UC = CreatePostUseCase
_DELETE_POST_UC = DeletePostUseCase
_REACT_UC = ReactToPostUseCase
_REMOVE_REACT_UC = RemoveReactionUseCase
_LIST_REACTIONS_UC = ListReactionsUseCase
_REPO = DjangoCommunityRepository
_MEMBER_REPO = DjangoCommunityMemberRepository
_POST_REPO = DjangoCommunityPostRepository
_REACTION_REPO = DjangoPostReactionRepository
_COMMENT_REPO = DjangoPostCommentRepository
_COMMENT_REACTION_REPO = DjangoCommentReactionRepository
_CREATE_COMMENT_UC = CreateCommentUseCase
_LIST_COMMENTS_UC = ListCommentsUseCase
_UPDATE_COMMENT_UC = UpdateCommentUseCase
_DELETE_COMMENT_UC = DeleteCommentUseCase
_REACT_TO_COMMENT_UC = ReactToCommentUseCase


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


class CommunityLeaveView(APIView):
    """DELETE /communities/{community_id}/leave/"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Leave community",
        responses={
            204: OpenApiResponse(description="Left successfully."),
            400: OpenApiResponse(description="Owner cannot leave without transferring ownership."),
            404: OpenApiResponse(description="Community not found or user is not a member."),
        },
    )
    def delete(self, request: Request, community_id: uuid.UUID) -> Response:
        """Remove the authenticated user from the community."""
        try:
            _LEAVE_UC(_REPO(), _MEMBER_REPO()).execute(
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
        except CommunityOwnerCannotLeaveError as exc:
            return error_response(
                code="ERR_COMMUNITY_OWNER_CANNOT_LEAVE",
                message=str(exc),
                http_status=400,
                request=request,
            )
        except NotMemberError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_MEMBER",
                message=str(exc),
                http_status=404,
                request=request,
            )
        return Response(status=204)


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


class PostReactionView(APIView):
    """POST /communities/posts/{post_id}/reactions/ - add or replace a reaction."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="React to post",
        request=ReactToPostSerializer,
        responses={
            201: OpenApiResponse(description="Reaction saved.", response=PostReactionResponseSerializer),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Post not found."),
        },
    )
    def post(self, request: Request, post_id: uuid.UUID) -> Response:
        """Upsert the authenticated user's reaction on a post."""
        ser = ReactToPostSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        result = _REACT_UC(_POST_REPO(), _REACTION_REPO()).execute(
            post_id=post_id,
            user_id=uuid.UUID(str(request.user.id)),
            reaction_type=ser.validated_data["reaction_type"],
        )
        return _CREATED(PostReactionResponseSerializer(result).data, request=request)

    @extend_schema(
        tags=["Community"],
        summary="List post reactions",
        responses={
            200: OpenApiResponse(description="Reactions.", response=PostReactionResponseSerializer(many=True)),
            401: OpenApiResponse(description="Missing or invalid JWT."),
        },
    )
    def get(self, request: Request, post_id: uuid.UUID) -> Response:
        """Return all reactions for the post."""
        results = _LIST_REACTIONS_UC(_REACTION_REPO()).execute(post_id=post_id)
        return success_response(PostReactionResponseSerializer(results, many=True).data, request=request)


class PostReactionDeleteView(APIView):
    """DELETE /communities/posts/{post_id}/reactions/{reaction_type}/"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Remove reaction",
        responses={
            204: OpenApiResponse(description="Reaction removed."),
            401: OpenApiResponse(description="Missing or invalid JWT."),
            404: OpenApiResponse(description="Reaction not found."),
        },
    )
    def delete(self, request: Request, post_id: uuid.UUID, reaction_type: str) -> Response:
        """Remove the authenticated user's reaction from a post."""
        try:
            _REMOVE_REACT_UC(_POST_REPO(), _REACTION_REPO()).execute(
                post_id=post_id,
                user_id=uuid.UUID(str(request.user.id)),
                reaction_type=reaction_type,
            )
        except ReactionNotFoundError as exc:
            return error_response(
                code="ERR_REACTION_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        return Response(status=204)


class PostCommentListCreateView(APIView):
    """GET /posts/{post_id}/comments/ - list; POST - create."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="List post comments",
        responses={200: PostCommentResponseSerializer(many=True)},
    )
    def get(self, request: Request, post_id: uuid.UUID) -> Response:
        """Return all non-deleted comments for a post."""
        comments = _LIST_COMMENTS_UC(_COMMENT_REPO()).execute(post_id=post_id)
        return success_response(PostCommentResponseSerializer(comments, many=True).data, request=request)

    @extend_schema(
        tags=["Community"],
        summary="Create post comment",
        request=CreateCommentSerializer,
        responses={
            201: PostCommentResponseSerializer,
            404: OpenApiResponse(description="Post not found."),
        },
    )
    def post(self, request: Request, post_id: uuid.UUID) -> Response:
        """Create a comment (or reply) on a post."""
        ser = CreateCommentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        try:
            comment = _CREATE_COMMENT_UC(_POST_REPO(), _COMMENT_REPO()).execute(
                post_id=post_id,
                user_id=uuid.UUID(str(request.user.id)),
                content=d["content"],
                parent_id=d.get("parent_id"),
            )
        except CommunityPostNotFoundError as exc:
            return error_response(
                code="ERR_POST_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        return _CREATED(PostCommentResponseSerializer(comment).data, request=request)


class PostCommentDetailView(APIView):
    """PATCH /comments/{comment_id}/ - update; DELETE - soft-delete."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Update comment",
        request=UpdateCommentSerializer,
        responses={
            200: PostCommentResponseSerializer,
            400: OpenApiResponse(description="Edit window expired."),
            404: OpenApiResponse(description="Not found."),
        },
    )
    def patch(self, request: Request, comment_id: uuid.UUID) -> Response:
        """Edit the comment content within 15 minutes of creation."""
        ser = UpdateCommentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            comment = _UPDATE_COMMENT_UC(_COMMENT_REPO()).execute(
                comment_id=comment_id,
                user_id=uuid.UUID(str(request.user.id)),
                content=ser.validated_data["content"],
            )
        except CommentNotFoundError as exc:
            return error_response(
                code="ERR_COMMENT_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        except CommentEditWindowExpiredError as exc:
            return error_response(
                code="ERR_COMMENT_EDIT_WINDOW_EXPIRED",
                message=str(exc),
                http_status=400,
                request=request,
            )
        return success_response(PostCommentResponseSerializer(comment).data, request=request)

    @extend_schema(
        tags=["Community"],
        summary="Delete comment",
        responses={
            204: OpenApiResponse(description="Deleted."),
            404: OpenApiResponse(description="Not found."),
        },
    )
    def delete(self, request: Request, comment_id: uuid.UUID) -> Response:
        """Soft-delete the comment."""
        try:
            _DELETE_COMMENT_UC(_POST_REPO(), _COMMENT_REPO()).execute(
                comment_id=comment_id,
                user_id=uuid.UUID(str(request.user.id)),
            )
        except CommentNotFoundError as exc:
            return error_response(
                code="ERR_COMMENT_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        return Response(status=204)


class CommentReactionView(APIView):
    """POST /comments/{comment_id}/reactions/ - add or replace a reaction."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="React to comment",
        request=ReactToCommentSerializer,
        responses={
            201: CommentReactionResponseSerializer,
            404: OpenApiResponse(description="Comment not found."),
        },
    )
    def post(self, request: Request, comment_id: uuid.UUID) -> Response:
        """Upsert the authenticated user's reaction on a comment."""
        ser = ReactToCommentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            result = _REACT_TO_COMMENT_UC(_COMMENT_REPO(), _COMMENT_REACTION_REPO()).execute(
                comment_id=comment_id,
                user_id=uuid.UUID(str(request.user.id)),
                reaction_type=ser.validated_data["reaction_type"],
            )
        except CommentNotFoundError as exc:
            return error_response(
                code="ERR_COMMENT_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        return _CREATED(CommentReactionResponseSerializer(result).data, request=request)
