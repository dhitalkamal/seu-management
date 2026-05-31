"""URL patterns for all community endpoints."""

from __future__ import annotations

from django.urls import URLPattern, path

from .views import (
    ActivityFeedView,
    CommunityDetailView,
    CommunityJoinView,
    CommunityListCreateView,
    CommunityPostDetailView,
    CommunityPostListCreateView,
    EventWallCreateView,
    EventWallListView,
    HashtagListView,
    HashtagPostsView,
    MemberDirectoryView,
    PinPostView,
    PollListCreateView,
    PollVoteView,
    PostCommentListCreateView,
    PostLikeView,
    PostRepostView,
)

urlpatterns: list[URLPattern] = [
    path("", CommunityListCreateView.as_view(), name="community-list-create"),
    path("<uuid:community_id>/", CommunityDetailView.as_view(), name="community-detail"),
    path("<uuid:community_id>/join/", CommunityJoinView.as_view(), name="community-join"),
    path(
        "<uuid:community_id>/posts/",
        CommunityPostListCreateView.as_view(),
        name="community-post-list-create",
    ),
    path("posts/<uuid:post_id>/", CommunityPostDetailView.as_view(), name="community-post-detail"),
    path("posts/<uuid:post_id>/like/", PostLikeView.as_view(), name="post-like"),
    path("posts/<uuid:post_id>/comments/", PostCommentListCreateView.as_view(), name="post-comments"),
    path("posts/<uuid:post_id>/repost/", PostRepostView.as_view(), name="post-repost"),
    path("posts/<uuid:post_id>/pin/", PinPostView.as_view(), name="post-pin"),
    path("hashtags/", HashtagListView.as_view(), name="hashtag-list"),
    path("hashtags/<str:name>/posts/", HashtagPostsView.as_view(), name="hashtag-posts"),
    path("<uuid:community_id>/polls/", PollListCreateView.as_view(), name="community-polls"),
    path("polls/<uuid:poll_id>/vote/", PollVoteView.as_view(), name="poll-vote"),
    path("<uuid:community_id>/activity/", ActivityFeedView.as_view(), name="community-activity"),
    path("<uuid:community_id>/event-walls/", EventWallListView.as_view(), name="community-event-walls"),
    path(
        "<uuid:community_id>/event-walls/create/",
        EventWallCreateView.as_view(),
        name="community-event-wall-create",
    ),
    path(
        "<uuid:community_id>/members/directory/",
        MemberDirectoryView.as_view(),
        name="community-member-directory",
    ),
]
