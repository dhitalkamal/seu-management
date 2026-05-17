"""Django admin registrations for orgs domain models."""

from __future__ import annotations

from django.contrib import admin

from apps.orgs.infrastructure.models import Organisation, OrgMember

admin.site.register(Organisation)
admin.site.register(OrgMember)
