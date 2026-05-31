"""Add OrgInvite model to the orgs schema."""

from __future__ import annotations

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orgs", "0005_add_org_profile_fields_and_documents"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrgInvite",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("org_id", models.UUIDField()),
                ("inviter_id", models.UUIDField()),
                ("invitee_email", models.EmailField()),
                ("role", models.CharField(default="member", max_length=20)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("accepted", "Accepted"),
                            ("declined", "Declined"),
                            ("revoked", "Revoked"),
                            ("expired", "Expired"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("accepted_by", models.UUIDField(blank=True, null=True)),
                ("expires_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "orgs_org_invite",
                "indexes": [
                    models.Index(fields=["org_id", "status"], name="idx_org_invite_org_status"),
                    models.Index(fields=["invitee_email", "status"], name="idx_org_invite_email"),
                ],
            },
        ),
    ]
