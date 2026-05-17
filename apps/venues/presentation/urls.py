"""URL patterns for all venue endpoints."""

from __future__ import annotations

from django.urls import URLPattern, path

from .views import VenueDetailView, VenueListCreateView, VenueSpaceListCreateView

urlpatterns: list[URLPattern] = [
    path("", VenueListCreateView.as_view(), name="venue-list-create"),
    path("<uuid:venue_id>/", VenueDetailView.as_view(), name="venue-detail"),
    path(
        "<uuid:venue_id>/spaces/",
        VenueSpaceListCreateView.as_view(),
        name="venue-space-list-create",
    ),
]
