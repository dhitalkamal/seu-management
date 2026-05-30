"""Create volunteer_roles and volunteer_applications tables."""

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Initial volunteers tables."""

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="VolunteerRole",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("event_id", models.UUIDField()),
                ("organisation_id", models.UUIDField(blank=True, null=True)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("capacity", models.PositiveIntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "volunteers_volunteer_role"},
        ),
        migrations.CreateModel(
            name="VolunteerApplication",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "volunteer_role",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="volunteers.volunteerrole",
                    ),
                ),
                ("user_id", models.UUIDField()),
                ("event_id", models.UUIDField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("check_in_at", models.DateTimeField(blank=True, null=True)),
                ("check_out_at", models.DateTimeField(blank=True, null=True)),
                ("rating", models.SmallIntegerField(blank=True, null=True)),
                ("certificate_issued", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "volunteers_volunteer_application"},
        ),
        migrations.AddConstraint(
            model_name="volunteerapplication",
            constraint=models.UniqueConstraint(
                fields=["volunteer_role", "user_id"],
                name="unique_volunteer_application",
            ),
        ),
    ]
