"""URL routes for the volunteers app."""

from __future__ import annotations

from django.urls import URLPattern, path

from .views import (
    VolunteerApplicationApproveView,
    VolunteerApplicationCancelView,
    VolunteerApplicationCheckInView,
    VolunteerApplicationCheckOutView,
    VolunteerApplicationListView,
    VolunteerApplicationRateView,
    VolunteerApplicationRejectView,
    VolunteerCertificateGenerateView,
    VolunteerCertificateVerifyView,
    VolunteerProfileView,
    VolunteerRoleApplyView,
    VolunteerRoleView,
    VolunteerShiftCreateView,
    VolunteerShiftDetailView,
    VolunteerShiftListView,
)

urlpatterns: list[URLPattern] = [
    path("roles/", VolunteerRoleView.as_view(), name="volunteer-role-create"),
    path("roles/<uuid:role_id>/apply/", VolunteerRoleApplyView.as_view(), name="volunteer-role-apply"),
    path("roles/<uuid:role_id>/applications/", VolunteerApplicationListView.as_view(), name="volunteer-application-list"),
    path("roles/<uuid:role_id>/shifts/", VolunteerShiftCreateView.as_view(), name="volunteer-shift-create"),
    path("roles/<uuid:role_id>/shifts/list/", VolunteerShiftListView.as_view(), name="volunteer-shift-list"),
    path("shifts/<uuid:shift_id>/", VolunteerShiftDetailView.as_view(), name="volunteer-shift-detail"),
    path("applications/<uuid:application_id>/approve/", VolunteerApplicationApproveView.as_view(), name="volunteer-application-approve"),
    path("applications/<uuid:application_id>/reject/", VolunteerApplicationRejectView.as_view(), name="volunteer-application-reject"),
    path("applications/<uuid:application_id>/cancel/", VolunteerApplicationCancelView.as_view(), name="volunteer-application-cancel"),
    path("applications/<uuid:application_id>/checkin/", VolunteerApplicationCheckInView.as_view(), name="volunteer-application-checkin"),
    path("applications/<uuid:application_id>/checkout/", VolunteerApplicationCheckOutView.as_view(), name="volunteer-application-checkout"),
    path("applications/<uuid:application_id>/rate/", VolunteerApplicationRateView.as_view(), name="volunteer-application-rate"),
    path(
        "applications/<uuid:application_id>/certificate/", VolunteerCertificateGenerateView.as_view(), name="volunteer-certificate-generate"
    ),
    path("certificates/<uuid:certificate_id>/verify/", VolunteerCertificateVerifyView.as_view(), name="volunteer-certificate-verify"),
    path("profile/", VolunteerProfileView.as_view(), name="volunteer-profile"),
]
