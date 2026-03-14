"""URL patterns for the moderation presentation layer."""

from __future__ import annotations

from django.urls import path

from apps.moderation.presentation.views import (
    ModerationCaseDetailView,
    ModerationCaseListCreateView,
    ModerationStatsView,
)

urlpatterns = [
    path("cases/", ModerationCaseListCreateView.as_view(), name="moderation-case-list-create"),
    path("cases/<uuid:case_id>/", ModerationCaseDetailView.as_view(), name="moderation-case-detail"),
    path("stats/", ModerationStatsView.as_view(), name="moderation-stats"),
]
