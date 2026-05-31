"""URL routes for support ticket endpoints."""

from __future__ import annotations

from django.urls import URLPattern, path

from apps.orgs.presentation.support_views import TicketListCreateView, TicketStatusUpdateView

urlpatterns: list[URLPattern] = [
    path("", TicketListCreateView.as_view(), name="ticket-list-create"),
    path("<uuid:ticket_id>/status/", TicketStatusUpdateView.as_view(), name="ticket-status-update"),
]
