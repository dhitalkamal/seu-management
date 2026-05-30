"""Django admin registrations for orgs domain models."""

from __future__ import annotations

from django.contrib import admin

from apps.orgs.infrastructure.models import Organization, OrgMember

admin.site.register(Organization)
admin.site.register(OrgMember)
