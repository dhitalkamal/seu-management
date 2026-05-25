"""URL routes for the volunteers app."""

from __future__ import annotations

from django.urls import URLPattern, path

from .views import (
    RateVolunteerView,
    VolunteerApplicationApproveView,
    VolunteerApplicationCancelView,
    VolunteerApplicationListView,
    VolunteerApplicationRejectView,
    VolunteerCheckInView,
    VolunteerCheckOutView,
    VolunteerRoleApplyView,
    VolunteerRoleView,
)

urlpatterns: list[URLPattern] = [
    path("roles/", VolunteerRoleView.as_view(), name="volunteer-role-create"),
    path("roles/<uuid:role_id>/apply/", VolunteerRoleApplyView.as_view(), name="volunteer-role-apply"),
    path(
        "roles/<uuid:role_id>/applications/",
        VolunteerApplicationListView.as_view(),
        name="volunteer-application-list",
    ),
    path(
        "applications/<uuid:application_id>/approve/",
        VolunteerApplicationApproveView.as_view(),
        name="volunteer-application-approve",
    ),
    path(
        "applications/<uuid:application_id>/reject/",
        VolunteerApplicationRejectView.as_view(),
        name="volunteer-application-reject",
    ),
    path(
        "applications/<uuid:application_id>/cancel/",
        VolunteerApplicationCancelView.as_view(),
        name="volunteer-application-cancel",
    ),
    path(
        "applications/<uuid:application_id>/checkin/",
        VolunteerCheckInView.as_view(),
        name="volunteer-application-checkin",
    ),
    path(
        "applications/<uuid:application_id>/checkout/",
        VolunteerCheckOutView.as_view(),
        name="volunteer-application-checkout",
    ),
    path(
        "applications/<uuid:application_id>/rate/",
        RateVolunteerView.as_view(),
        name="volunteer-application-rate",
    ),
]
