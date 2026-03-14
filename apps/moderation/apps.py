"""Django app configuration for the moderation module."""

from __future__ import annotations

from django.apps import AppConfig


class ModerationConfig(AppConfig):
    """Configuration for the moderation Django application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.moderation"
    label = "moderation"
