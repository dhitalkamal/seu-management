"""Add support_ticket table to the orgs schema."""

from __future__ import annotations

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    """Creates the support_ticket table."""

    dependencies = [
        ("orgs", "0003_add_plan_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="SupportTicket",
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
                ("subject", models.CharField(max_length=500)),
                ("message", models.TextField(blank=True)),
                (
                    "priority",
                    models.CharField(
                        choices=[
                            ("low", "Low"),
                            ("med", "Med"),
                            ("high", "High"),
                            ("critical", "Critical"),
                        ],
                        default="med",
                        max_length=20,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_progress", "In Progress"),
                            ("escalated", "Escalated"),
                            ("resolved", "Resolved"),
                            ("closed", "Closed"),
                        ],
                        default="open",
                        max_length=20,
                    ),
                ),
                ("org_id", models.UUIDField(blank=True, null=True)),
                ("org_name", models.CharField(blank=True, max_length=255)),
                ("submitted_by", models.UUIDField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": '"orgs"."support_ticket"',
                "ordering": ["-created_at"],
            },
        ),
    ]
