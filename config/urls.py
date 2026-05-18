"""Root URL configuration for the management-service."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.orgs.presentation.support_views import OrgAnalyticsView
from apps.orgs.presentation.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health/", HealthCheckView.as_view(), name="health"),
    path("api/v1/organisations/", include("apps.orgs.presentation.urls")),
    path("api/v1/tickets/", include("apps.orgs.presentation.ticket_urls")),
    path("api/v1/admin/analytics/", OrgAnalyticsView.as_view(), name="admin-analytics"),
    path("api/v1/venues/", include("apps.venues.presentation.urls")),
    path("api/v1/volunteers/", include("apps.volunteers.presentation.urls")),
    path("api/v1/communities/", include("apps.community.presentation.urls")),
    path("api/v1/campaigns/", include("apps.marketing.presentation.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Use relative URL so the browser resolves it through the correct nginx prefix
    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(url="../?format=json"),
        name="swagger-ui",
    ),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url="../?format=json"), name="redoc"),
]
