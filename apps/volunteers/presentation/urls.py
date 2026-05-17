"""URL routes for the volunteers app."""

from __future__ import annotations

from django.urls import URLPattern, path

from .views import VolunteerRoleApplyView, VolunteerRoleView

urlpatterns: list[URLPattern] = [
    path("roles/", VolunteerRoleView.as_view(), name="volunteer-role-create"),
    path(
        "roles/<uuid:role_id>/apply/", VolunteerRoleApplyView.as_view(), name="volunteer-role-apply"
    ),
]
