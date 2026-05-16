"""Django app config for the volunteers module."""
from __future__ import annotations

from django.apps import AppConfig


class VolunteersConfig(AppConfig):
    """Registers the volunteers app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.volunteers"
    label = "volunteers"
