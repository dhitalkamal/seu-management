"""Django app config for the compliance module."""

from __future__ import annotations

from django.apps import AppConfig


class ComplianceConfig(AppConfig):
    """Compliance controls app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.compliance"
    verbose_name = "Compliance"
