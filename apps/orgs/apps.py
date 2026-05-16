"""Django app config for the orgs module."""
from __future__ import annotations

from django.apps import AppConfig


class OrgsConfig(AppConfig):
    """Registers the orgs app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.orgs"
    label = "orgs"
