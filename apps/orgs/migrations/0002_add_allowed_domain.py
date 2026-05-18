"""Migration: add AllowedDomain table for org domain whitelisting."""

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orgs", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AllowedDomain",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="allowed_domains",
                        to="orgs.organisation",
                    ),
                ),
                ("domain", models.CharField(max_length=253)),
                (
                    "match_type",
                    models.CharField(
                        choices=[
                            ("exact", "Exact match (e.g. company.com)"),
                            ("wildcard", "Wildcard (e.g. *.company.com)"),
                        ],
                        default="exact",
                        max_length=10,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": '"orgs"."allowed_domain"'},
        ),
        migrations.AddConstraint(
            model_name="alloweddomain",
            constraint=models.UniqueConstraint(
                fields=["organisation", "domain"],
                name="unique_org_allowed_domain",
            ),
        ),
    ]
