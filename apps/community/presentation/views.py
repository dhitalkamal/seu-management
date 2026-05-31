"""DRF API views for community endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from django.db import transaction
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
from apps.community.domain.entities import PostCommentEntity, PostLikeEntity, PostRepostEntity
from apps.community.domain.exceptions import (
    AlreadyMemberError,
    CommunityNotFoundError,
    CommunityPostNotFoundError,
    SlugAlreadyExistsError,
)
from apps.community.infrastructure.models import ActivityFeed, EventWall, Poll, PollVote
from apps.community.infrastructure.repositories import (
    DjangoCommunityMemberRepository,
    DjangoCommunityPostRepository,
    DjangoCommunityRepository,
    DjangoHashtagRepository,
    DjangoPostCommentRepository,
    DjangoPostLikeRepository,
    DjangoPostRepostRepository,
)
from apps.community.presentation.serializers import (
    ActivityFeedResponseSerializer,
    CommunityPostResponseSerializer,
    CommunityResponseSerializer,
    CreateCommunitySerializer,
    CreatePostSerializer,
    EventWallCreateSerializer,
    EventWallResponseSerializer,
    HashtagResponseSerializer,
    MemberDirectorySerializer,
    PollResponseSerializer,
    PollSerializer,
    PollVoteSerializer,
    PostCommentResponseSerializer,
    PostCommentSerializer,
    PostLikeResponseSerializer,
    PostRepostResponseSerializer,
    PostRepostSerializer,
)
from apps.orgs.infrastructure.audit_publisher import publish_audit

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
_LIKE_REPO = DjangoPostLikeRepository
_COMMENT_REPO = DjangoPostCommentRepository
_REPOST_REPO = DjangoPostRepostRepository
_HASHTAG_REPO = DjangoHashtagRepository


def _author_name(request: Request) -> str:
    """Build the display name from the JWT token claims."""
    token = getattr(request.user, "token", {})
    first = token.get("first_name", "")
    last = token.get("last_name", "")
    return f"{first} {last}".strip()


def _avatar_url(request: Request) -> str:
    """Extract the avatar URL from the JWT token claims."""
    return getattr(request.user, "token", {}).get("avatar_url", "")


def _record_activity(
    *,
    community_id: uuid.UUID,
    user_id: uuid.UUID,
    user_name: str,
    user_avatar: str,
    activity_type: str,
    target_title: str,
    target_id: str,
) -> None:
    """Persist one entry to the community activity feed.

    Failures are intentionally silent so that activity logging never
    blocks the main response path.
    """
    try:
        ActivityFeed.objects.create(
            id=uuid.uuid4(),
            community_id=community_id,
            user_id=user_id,
            user_name=user_name,
            user_avatar=user_avatar,
            activity_type=activity_type,
            target_title=target_title,
            target_id=target_id,
        )
    except Exception:
        import logging

        logging.getLogger(__name__).warning("Failed to record activity %s.", activity_type, exc_info=True)


class CommunityListCreateView(APIView):
    """GET /communities/ - list all; POST /communities/ - create new."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="List communities",
        responses={200: CommunityResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        """Return all active communities with is_member flag for the calling user."""
        communities = _LIST_UC(_REPO()).execute()
        user_id = uuid.UUID(str(request.user.id))
        member_repo = _MEMBER_REPO()
        data = []
        for community in communities:
            membership = member_repo.get_membership(community.id, user_id)
            serialized = CommunityResponseSerializer(community).data
            serialized["is_member"] = membership is not None
            data.append(serialized)
        return success_response(data, request=request)

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
        """Create a new community and auto-join the creator."""
        ser = CreateCommunitySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        try:
            community = _CREATE_UC(_REPO(), _MEMBER_REPO()).execute(
                created_by=uuid.UUID(str(request.user.id)),
                name=d["name"],
                slug=d["slug"],
                privacy=d["privacy"],
                organization_id=d.get("organization_id"),
                description=d.get("description", ""),
            )
        except SlugAlreadyExistsError as exc:
            return error_response(
                code="ERR_COMMUNITY_SLUG_TAKEN",
                message=str(exc),
                http_status=400,
                request=request,
            )
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="community.created",
            metadata={"community_id": str(community.id), "community_name": community.name},
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
        _record_activity(
            community_id=community_id,
            user_id=uuid.UUID(str(request.user.id)),
            user_name=_author_name(request),
            user_avatar=_avatar_url(request),
            activity_type="joined",
            target_title="",
            target_id=str(community_id),
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
        """Create a new post inside the community, extracting hashtags from content."""
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
                author_name=_author_name(request),
            )
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="post.created",
            metadata={"community_id": str(community_id), "post_id": str(post.id)},
        )
        _record_activity(
            community_id=community_id,
            user_id=uuid.UUID(str(request.user.id)),
            user_name=_author_name(request),
            user_avatar=_avatar_url(request),
            activity_type="posted",
            target_title=post.content[:100],
            target_id=str(post.id),
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
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="post.deleted",
            metadata={"post_id": str(post_id)},
        )
        return Response(status=204)


class PostLikeView(APIView):
    """POST /posts/{post_id}/like/ - like; DELETE - unlike."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Like a post",
        responses={
            201: PostLikeResponseSerializer,
            400: OpenApiResponse(description="Already liked."),
            404: OpenApiResponse(description="Post not found."),
        },
    )
    def post(self, request: Request, post_id: uuid.UUID) -> Response:
        """Like the given post. Returns 400 if already liked."""
        try:
            post = _POST_REPO().get_by_id(post_id)
        except CommunityPostNotFoundError as exc:
            return error_response(
                code="ERR_POST_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        user_id = uuid.UUID(str(request.user.id))
        like_repo = _LIKE_REPO()
        if like_repo.get(post_id, user_id) is not None:
            return error_response(
                code="ERR_ALREADY_LIKED",
                message="You have already liked this post.",
                http_status=400,
                request=request,
            )
        like = PostLikeEntity(
            id=uuid.uuid4(),
            post_id=post_id,
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
        )
        like_repo.create(like)
        # increment the post like count
        post.like_count += 1
        _POST_REPO().update(post)
        publish_audit(
            request=request,
            user_id=user_id,
            event_type="post.liked",
            metadata={"post_id": str(post_id)},
        )
        _record_activity(
            community_id=post.community_id,
            user_id=user_id,
            user_name=_author_name(request),
            user_avatar=_avatar_url(request),
            activity_type="liked",
            target_title=post.content[:100],
            target_id=str(post_id),
        )
        return _CREATED(PostLikeResponseSerializer(like).data, request=request)

    @extend_schema(
        tags=["Community"],
        summary="Unlike a post",
        responses={
            204: OpenApiResponse(description="Unliked."),
            404: OpenApiResponse(description="Post not found or not liked."),
        },
    )
    def delete(self, request: Request, post_id: uuid.UUID) -> Response:
        """Remove the like from the given post."""
        try:
            post = _POST_REPO().get_by_id(post_id)
        except CommunityPostNotFoundError as exc:
            return error_response(
                code="ERR_POST_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        user_id = uuid.UUID(str(request.user.id))
        like_repo = _LIKE_REPO()
        if like_repo.get(post_id, user_id) is None:
            return error_response(
                code="ERR_LIKE_NOT_FOUND",
                message="You have not liked this post.",
                http_status=404,
                request=request,
            )
        like_repo.delete(post_id, user_id)
        # decrement like count but never go below zero
        post.like_count = max(0, post.like_count - 1)
        _POST_REPO().update(post)
        publish_audit(
            request=request,
            user_id=user_id,
            event_type="post.unliked",
            metadata={"post_id": str(post_id)},
        )
        return Response(status=204)


class PostCommentListCreateView(APIView):
    """GET /posts/{post_id}/comments/ - list; POST - create comment or reply."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="List post comments",
        responses={
            200: PostCommentResponseSerializer(many=True),
            404: OpenApiResponse(description="Post not found."),
        },
    )
    def get(self, request: Request, post_id: uuid.UUID) -> Response:
        """Return all top-level comments with nested replies."""
        try:
            _POST_REPO().get_by_id(post_id)
        except CommunityPostNotFoundError as exc:
            return error_response(
                code="ERR_POST_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        comment_repo = _COMMENT_REPO()
        top_level = comment_repo.list_top_level(post_id)
        data = []
        for comment in top_level:
            replies = comment_repo.list_replies(comment.id)
            serialized = PostCommentResponseSerializer(comment).data
            serialized["replies"] = PostCommentResponseSerializer(replies, many=True).data
            data.append(serialized)
        return success_response(data, request=request)

    @extend_schema(
        tags=["Community"],
        summary="Create comment or reply",
        request=PostCommentSerializer,
        responses={
            201: PostCommentResponseSerializer,
            404: OpenApiResponse(description="Post or parent comment not found."),
        },
    )
    def post(self, request: Request, post_id: uuid.UUID) -> Response:
        """Create a top-level comment or a reply to an existing comment."""
        try:
            _post = _POST_REPO().get_by_id(post_id)
        except CommunityPostNotFoundError as exc:
            return error_response(
                code="ERR_POST_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        ser = PostCommentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        parent_id = d.get("parent_id")
        comment_repo = _COMMENT_REPO()

        # validate the parent comment exists if this is a reply
        if parent_id is not None:
            parent = comment_repo.get_by_id(parent_id)
            if parent is None:
                return error_response(
                    code="ERR_COMMENT_NOT_FOUND",
                    message=f"Parent comment {parent_id} not found.",
                    http_status=404,
                    request=request,
                )

        comment = PostCommentEntity(
            id=uuid.uuid4(),
            post_id=post_id,
            author_id=uuid.UUID(str(request.user.id)),
            author_name=_author_name(request),
            content=d["content"],
            parent_id=parent_id,
            like_count=0,
            reply_count=0,
            created_at=datetime.now(timezone.utc),
        )
        comment_repo.create(comment)
        comment_repo.increment_post_comment_count(post_id)

        # if this is a reply, increment the parent reply count
        if parent_id is not None:
            comment_repo.increment_reply_count(parent_id)

        _record_activity(
            community_id=_post.community_id,
            user_id=uuid.UUID(str(request.user.id)),
            user_name=_author_name(request),
            user_avatar=_avatar_url(request),
            activity_type="commented",
            target_title=_post.content[:100],
            target_id=str(post_id),
        )
        return _CREATED(PostCommentResponseSerializer(comment).data, request=request)


class PostRepostView(APIView):
    """POST /posts/{post_id}/repost/ - repost into another community."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Repost a post",
        request=PostRepostSerializer,
        responses={
            201: PostRepostResponseSerializer,
            400: OpenApiResponse(description="Already reposted."),
            404: OpenApiResponse(description="Post or community not found."),
        },
    )
    def post(self, request: Request, post_id: uuid.UUID) -> Response:
        """Repost the given post into the target community."""
        try:
            _POST_REPO().get_by_id(post_id)
        except CommunityPostNotFoundError as exc:
            return error_response(
                code="ERR_POST_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        ser = PostRepostSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        community_id = d["community_id"]
        try:
            _REPO().get_by_id(community_id)
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        user_id = uuid.UUID(str(request.user.id))
        repost_repo = _REPOST_REPO()
        if repost_repo.get(post_id, user_id) is not None:
            return error_response(
                code="ERR_ALREADY_REPOSTED",
                message="You have already reposted this post.",
                http_status=400,
                request=request,
            )
        repost = PostRepostEntity(
            id=uuid.uuid4(),
            original_post_id=post_id,
            user_id=user_id,
            community_id=community_id,
            caption=d.get("caption", ""),
            created_at=datetime.now(timezone.utc),
        )
        repost_repo.create(repost)
        publish_audit(
            request=request,
            user_id=user_id,
            event_type="post.reposted",
            metadata={"post_id": str(post_id), "community_id": str(community_id)},
        )
        return _CREATED(PostRepostResponseSerializer(repost).data, request=request)


class HashtagListView(APIView):
    """GET /hashtags/ - list all hashtags ordered by popularity."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="List hashtags",
        responses={200: HashtagResponseSerializer(many=True)},
    )
    def get(self, request: Request) -> Response:
        """Return all hashtags sorted by post count descending."""
        hashtags = _HASHTAG_REPO().list_by_popularity()
        return success_response(HashtagResponseSerializer(hashtags, many=True).data, request=request)


class HashtagPostsView(APIView):
    """GET /hashtags/{name}/posts/ - list posts for a hashtag."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="List posts by hashtag",
        responses={
            200: CommunityPostResponseSerializer(many=True),
            404: OpenApiResponse(description="Hashtag not found."),
        },
    )
    def get(self, request: Request, name: str) -> Response:
        """Return all posts tagged with the given hashtag (without the leading #)."""
        hashtag_repo = _HASHTAG_REPO()
        if hashtag_repo.get_by_name(name) is None:
            return error_response(
                code="ERR_HASHTAG_NOT_FOUND",
                message=f"Hashtag '{name}' not found.",
                http_status=404,
                request=request,
            )
        posts = hashtag_repo.list_posts_by_hashtag(name)
        return success_response(CommunityPostResponseSerializer(posts, many=True).data, request=request)


class PollListCreateView(APIView):
    """GET /communities/{community_id}/polls/ - list; POST - create."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="List polls",
        responses={200: PollResponseSerializer(many=True)},
    )
    def get(self, request: Request, community_id: uuid.UUID) -> Response:
        """Return all polls for the community, annotated with the caller's vote."""
        try:
            _REPO().get_by_id(community_id)
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        user_id = uuid.UUID(str(request.user.id))
        polls = Poll.objects.filter(community_id=community_id).order_by("-created_at")
        # fetch this user's votes in one query for efficiency
        voted = {v.poll_id: v.option_index for v in PollVote.objects.filter(poll__in=polls, user_id=user_id)}
        data = []
        for poll in polls:
            row = PollResponseSerializer(poll.to_entity()).data
            row["user_voted_index"] = voted.get(poll.id)
            data.append(row)
        return success_response(data, request=request)

    @extend_schema(
        tags=["Community"],
        summary="Create poll",
        request=PollSerializer,
        responses={
            201: PollResponseSerializer,
            400: OpenApiResponse(description="Validation error."),
            404: OpenApiResponse(description="Community not found."),
        },
    )
    def post(self, request: Request, community_id: uuid.UUID) -> Response:
        """Create a new poll inside the community."""
        try:
            _REPO().get_by_id(community_id)
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        ser = PollSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        # convert plain strings to option dicts
        options = [{"text": opt, "votes": 0} for opt in d["options"]]
        poll = Poll.objects.create(
            id=uuid.uuid4(),
            community_id=community_id,
            author_id=uuid.UUID(str(request.user.id)),
            author_name=_author_name(request),
            question=d["question"],
            options=options,
            total_votes=0,
            expires_at=d.get("expires_at"),
        )
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="poll.created",
            metadata={"community_id": str(community_id), "poll_id": str(poll.id)},
        )
        row = PollResponseSerializer(poll.to_entity()).data
        row["user_voted_index"] = None
        return _CREATED(row, request=request)


class PollVoteView(APIView):
    """POST /communities/polls/{poll_id}/vote/ - cast a vote."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Vote on a poll",
        request=PollVoteSerializer,
        responses={
            200: PollResponseSerializer,
            400: OpenApiResponse(description="Already voted or invalid option index."),
            404: OpenApiResponse(description="Poll not found."),
        },
    )
    def post(self, request: Request, poll_id: uuid.UUID) -> Response:
        """Record one vote per user per poll and update the option tally atomically."""
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return error_response(
                code="ERR_POLL_NOT_FOUND",
                message=f"Poll {poll_id} not found.",
                http_status=404,
                request=request,
            )
        user_id = uuid.UUID(str(request.user.id))
        if PollVote.objects.filter(poll_id=poll_id, user_id=user_id).exists():
            return error_response(
                code="ERR_ALREADY_VOTED",
                message="You have already voted on this poll.",
                http_status=400,
                request=request,
            )
        ser = PollVoteSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        option_index = ser.validated_data["option_index"]
        if option_index >= len(poll.options):
            return error_response(
                code="ERR_INVALID_OPTION",
                message=f"Option index {option_index} is out of range.",
                http_status=400,
                request=request,
            )
        with transaction.atomic():
            PollVote.objects.create(
                id=uuid.uuid4(),
                poll=poll,
                user_id=user_id,
                option_index=option_index,
            )
            # update in-place to avoid lost updates from concurrent votes
            options = list(poll.options)
            options[option_index] = {**options[option_index], "votes": options[option_index].get("votes", 0) + 1}
            Poll.objects.filter(id=poll_id).update(
                options=options,
                total_votes=poll.total_votes + 1,
            )
        # re-fetch to get updated state
        poll.refresh_from_db()
        _record_activity(
            community_id=poll.community_id,
            user_id=user_id,
            user_name=_author_name(request),
            user_avatar=_avatar_url(request),
            activity_type="voted",
            target_title=poll.question[:100],
            target_id=str(poll_id),
        )
        row = PollResponseSerializer(poll.to_entity()).data
        row["user_voted_index"] = option_index
        return success_response(row, request=request)


class ActivityFeedView(APIView):
    """GET /communities/{community_id}/activity/ - recent activity."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="List community activity feed",
        responses={200: ActivityFeedResponseSerializer(many=True)},
    )
    def get(self, request: Request, community_id: uuid.UUID) -> Response:
        """Return the 50 most recent activity entries for a community."""
        try:
            _REPO().get_by_id(community_id)
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        entries = ActivityFeed.objects.filter(community_id=community_id).order_by("-created_at")[:50]
        data = ActivityFeedResponseSerializer([e.to_entity() for e in entries], many=True).data
        return success_response(data, request=request)


class EventWallListView(APIView):
    """GET /communities/{community_id}/event-walls/ - list event walls."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="List event walls",
        responses={200: EventWallResponseSerializer(many=True)},
    )
    def get(self, request: Request, community_id: uuid.UUID) -> Response:
        """Return all event walls for the community."""
        try:
            _REPO().get_by_id(community_id)
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        walls = EventWall.objects.filter(community_id=community_id).order_by("-event_date")
        data = EventWallResponseSerializer([w.to_entity() for w in walls], many=True).data
        return success_response(data, request=request)


class EventWallCreateView(APIView):
    """POST /communities/{community_id}/event-walls/create/ - create an event wall."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Create event wall",
        request=EventWallCreateSerializer,
        responses={
            201: EventWallResponseSerializer,
            400: OpenApiResponse(description="Validation error."),
            404: OpenApiResponse(description="Community not found."),
        },
    )
    def post(self, request: Request, community_id: uuid.UUID) -> Response:
        """Create an event wall linking a community to a specific event."""
        try:
            _REPO().get_by_id(community_id)
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        ser = EventWallCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        wall = EventWall.objects.create(
            id=uuid.uuid4(),
            community_id=community_id,
            event_id=d["event_id"],
            event_title=d["event_title"],
            event_date=d["event_date"],
            post_count=0,
        )
        publish_audit(
            request=request,
            user_id=uuid.UUID(str(request.user.id)),
            event_type="event_wall.created",
            metadata={"community_id": str(community_id), "event_wall_id": str(wall.id)},
        )
        return _CREATED(EventWallResponseSerializer(wall.to_entity()).data, request=request)


class MemberDirectoryView(APIView):
    """GET /communities/{community_id}/members/directory/ - engagement directory."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Member directory",
        responses={200: MemberDirectorySerializer(many=True)},
    )
    def get(self, request: Request, community_id: uuid.UUID) -> Response:
        """Return all members with post/comment counts and an assigned badge."""
        try:
            _REPO().get_by_id(community_id)
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        from apps.community.infrastructure.models import CommunityMember, CommunityPost, PostComment

        members = CommunityMember.objects.filter(community_id=community_id)
        result = []
        for member in members:
            posts_count = CommunityPost.objects.filter(
                community_id=community_id,
                author_id=member.user_id,
                status="published",
            ).count()
            comments_count = PostComment.objects.filter(
                post__community_id=community_id,
                author_id=member.user_id,
            ).count()
            # badge assignment - most specific match wins
            if posts_count > 10:
                badge_type = "top_contributor"
            elif comments_count > 20:
                badge_type = "active_commenter"
            else:
                badge_type = "early_adopter"
            result.append(
                {
                    "user_id": member.user_id,
                    "user_name": "",
                    "user_avatar": member.avatar_url,
                    "badge_type": badge_type,
                    "events_attended": 0,
                    "posts_count": posts_count,
                    "comments_count": comments_count,
                    "joined_at": member.joined_at,
                }
            )
        return success_response(MemberDirectorySerializer(result, many=True).data, request=request)


class PinPostView(APIView):
    """POST /communities/posts/{post_id}/pin/ - toggle pin on a post."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Community"],
        summary="Toggle post pin",
        responses={
            200: CommunityPostResponseSerializer,
            403: OpenApiResponse(description="Only the community creator can pin posts."),
            404: OpenApiResponse(description="Post not found."),
        },
    )
    def post(self, request: Request, post_id: uuid.UUID) -> Response:
        """Toggle is_pinned on the post. Only the community creator may call this."""
        try:
            post = _POST_REPO().get_by_id(post_id)
        except CommunityPostNotFoundError as exc:
            return error_response(
                code="ERR_POST_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        try:
            community = _REPO().get_by_id(post.community_id)
        except CommunityNotFoundError as exc:
            return error_response(
                code="ERR_COMMUNITY_NOT_FOUND",
                message=str(exc),
                http_status=404,
                request=request,
            )
        user_id = uuid.UUID(str(request.user.id))
        if community.created_by != user_id:
            return error_response(
                code="ERR_FORBIDDEN",
                message="Only the community creator can pin posts.",
                http_status=403,
                request=request,
            )
        post.is_pinned = not post.is_pinned
        _POST_REPO().update(post)
        publish_audit(
            request=request,
            user_id=user_id,
            event_type="post.pinned" if post.is_pinned else "post.unpinned",
            metadata={"post_id": str(post_id), "community_id": str(post.community_id)},
        )
        return success_response(CommunityPostResponseSerializer(post).data, request=request)
