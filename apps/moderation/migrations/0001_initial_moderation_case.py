"""Initial migration for moderation_case table in the management schema."""

from __future__ import annotations

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    """Create the moderation_case table with all required fields and indexes."""

    initial = True
    dependencies: list = []

    operations = [
        migrations.CreateModel(
            name="ModerationCase",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "content_type",
                    models.CharField(
                        choices=[("event", "Event"), ("post", "Post"), ("comment", "Comment")],
                        max_length=20,
                    ),
                ),
                ("content_id", models.UUIDField()),
                ("content_title", models.CharField(max_length=500)),
                ("reporter_id", models.UUIDField(blank=True, null=True)),
                ("organisation_id", models.UUIDField(blank=True, null=True)),
                ("reason", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("under_review", "Under Review"),
                            ("dismissed", "Dismissed"),
                            ("warned", "Warned"),
                            ("taken_down", "Taken Down"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("reviewer_id", models.UUIDField(blank=True, null=True)),
                ("reviewer_notes", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": '"management"."moderation_case"',
            },
        ),
        migrations.AddIndex(
            model_name="moderationcase",
            index=models.Index(fields=["status"], name="moderation_case_status_idx"),
        ),
        migrations.AddIndex(
            model_name="moderationcase",
            index=models.Index(fields=["created_at"], name="moderation_case_created_idx"),
        ),
    ]
