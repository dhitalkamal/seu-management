"""URL routes for the compliance controls endpoints."""

from __future__ import annotations

from django.urls import URLPattern, path

from .views import ComplianceControlDetailView, ComplianceControlListCreateView, ComplianceSummaryView

urlpatterns: list[URLPattern] = [
    path("controls/", ComplianceControlListCreateView.as_view(), name="compliance-control-list-create"),
    path("controls/<uuid:control_id>/", ComplianceControlDetailView.as_view(), name="compliance-control-detail"),
    path("summary/", ComplianceSummaryView.as_view(), name="compliance-summary"),
]
