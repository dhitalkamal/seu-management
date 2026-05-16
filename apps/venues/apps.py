"""Django app config for the venues module."""
from __future__ import annotations

from django.apps import AppConfig


class VenuesConfig(AppConfig):
    """Registers the venues app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.venues"
    label = "venues"
