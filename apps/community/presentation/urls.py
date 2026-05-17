"""URL patterns for all community endpoints."""

from __future__ import annotations

from django.urls import URLPattern, path

from .views import (
    CommunityDetailView,
    CommunityJoinView,
    CommunityListCreateView,
    CommunityPostDetailView,
    CommunityPostListCreateView,
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
]
