"""URL routes for the orgs app."""

from __future__ import annotations

from django.urls import URLPattern, path

from .views import OrgDetailView, OrgListCreateView, OrgMembersView

urlpatterns: list[URLPattern] = [
    path("", OrgListCreateView.as_view(), name="org-list-create"),
    path("<uuid:org_id>/", OrgDetailView.as_view(), name="org-detail"),
    path("<uuid:org_id>/members/", OrgMembersView.as_view(), name="org-members"),
]
