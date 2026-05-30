"""Create the compliance_control table in the orgs schema."""

from __future__ import annotations

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    """Creates the ComplianceControl table."""

    initial = True
    dependencies: list = []

    operations = [
        migrations.CreateModel(
            name="ComplianceControl",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("category", models.CharField(max_length=50)),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                (
                    "status",
                    models.CharField(
                        choices=[("pass", "Pass"), ("fail", "Fail"), ("na", "N/A")],
                        max_length=20,
                    ),
                ),
                ("last_checked", models.DateTimeField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "orgs_compliance_control",
                "ordering": ["category", "name"],
            },
        ),
    ]
