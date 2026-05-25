"""Create organizations and org_members tables."""

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Initial orgs tables."""

    dependencies = [
        ("orgs", "0000_create_orgs_schema"),
    ]

    operations = [
        migrations.CreateModel(
            name="Organization",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("created_by", models.UUIDField()),
                ("name", models.CharField(max_length=255)),
                ("slug", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
                ("contact_email", models.EmailField()),
                ("website", models.URLField(blank=True)),
                ("logo_url", models.URLField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending_review", "Pending Review"),
                            ("approved", "Approved"),
                            ("active", "Active"),
                            ("suspended", "Suspended"),
                        ],
                        default="pending_review",
                        max_length=30,
                    ),
                ),
                ("is_verified", models.BooleanField(default=False)),
                ("deleted_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": '"orgs"."organization"'},
        ),
        migrations.CreateModel(
            name="OrgMember",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="orgs.organization",
                    ),
                ),
                ("user_id", models.UUIDField()),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("owner", "Owner"),
                            ("admin", "Admin"),
                            ("manager", "Manager"),
                            ("member", "Member"),
                        ],
                        default="member",
                        max_length=20,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": '"orgs"."org_member"'},
        ),
        migrations.AddConstraint(
            model_name="orgmember",
            constraint=models.UniqueConstraint(
                fields=["organization", "user_id"],
                name="unique_org_member",
            ),
        ),
    ]
