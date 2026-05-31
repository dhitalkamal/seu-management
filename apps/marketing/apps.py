"""Django app config for the marketing module."""

from __future__ import annotations

from django.apps import AppConfig


class MarketingConfig(AppConfig):
    """Registers the marketing app with Django."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.marketing"
    label = "marketing"
