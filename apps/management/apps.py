"""Django app config for the management module."""
from __future__ import annotations

from django.apps import AppConfig


class ManagementConfig(AppConfig):
    """Registers the management app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.management"
    label = "management"
