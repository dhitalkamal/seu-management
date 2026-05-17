"""Django app config for the community module."""

from __future__ import annotations

from django.apps import AppConfig


class CommunityConfig(AppConfig):
    """Registers the community app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.community"
    label = "community"
