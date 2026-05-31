"""URL patterns for all marketing endpoints."""

from __future__ import annotations

from django.urls import URLPattern, path

from .views import CampaignListCreateView, CampaignSendView, SegmentListCreateView, SponsorDetailView, SponsorListCreateView

urlpatterns: list[URLPattern] = [
    path("", CampaignListCreateView.as_view(), name="campaign-list-create"),
    path("<uuid:campaign_id>/send/", CampaignSendView.as_view(), name="campaign-send"),
    path("segments/", SegmentListCreateView.as_view(), name="segment-list-create"),
    path("sponsors/", SponsorListCreateView.as_view(), name="sponsor-list-create"),
    path("sponsors/<uuid:sponsor_id>/", SponsorDetailView.as_view(), name="sponsor-detail"),
]
