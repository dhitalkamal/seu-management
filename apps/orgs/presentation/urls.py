"""URL routes for the orgs app."""

from __future__ import annotations

from django.urls import URLPattern, path

from .views import (
    OrgApproveView,
    OrgDeleteView,
    OrgDetailView,
    OrgDocumentDeleteView,
    OrgDocumentListCreateView,
    OrgDocumentUploadView,
    OrgListCreateView,
    OrgMembersView,
    OrgReinstateView,
    OrgRejectView,
    OrgSuspendView,
)

urlpatterns: list[URLPattern] = [
    path("", OrgListCreateView.as_view(), name="org-list-create"),
    path("<uuid:org_id>/", OrgDetailView.as_view(), name="org-detail"),
    path("<uuid:org_id>/members/", OrgMembersView.as_view(), name="org-members"),
    path("<uuid:org_id>/approve/", OrgApproveView.as_view(), name="org-approve"),
    path("<uuid:org_id>/reject/", OrgRejectView.as_view(), name="org-reject"),
    path("<uuid:org_id>/suspend/", OrgSuspendView.as_view(), name="org-suspend"),
    path("<uuid:org_id>/reinstate/", OrgReinstateView.as_view(), name="org-reinstate"),
    path("<uuid:org_id>/delete/", OrgDeleteView.as_view(), name="org-delete"),
    path("<uuid:org_id>/documents/", OrgDocumentListCreateView.as_view(), name="org-documents"),
    path(
        "<uuid:org_id>/documents/<uuid:doc_id>/",
        OrgDocumentDeleteView.as_view(),
        name="org-document-delete",
    ),
    path(
        "<uuid:org_id>/documents/upload/",
        OrgDocumentUploadView.as_view(),
        name="org-document-upload",
    ),
]
