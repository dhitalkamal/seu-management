"""Django admin registrations for volunteers domain models."""

from __future__ import annotations

from django.contrib import admin

from apps.volunteers.infrastructure.models import VolunteerApplication, VolunteerRole

admin.site.register(VolunteerRole)
admin.site.register(VolunteerApplication)
