"""Add profile fields to Organisation and create OrgDocument table."""

from __future__ import annotations

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """Extend Organisation with contact / social fields and add org_document table."""

    dependencies = [
        ("orgs", "0004_add_support_ticket"),
    ]

    operations = [
        # * ── New fields on Organisation ────────────────────────────────
        migrations.AddField(
            model_name="organisation",
            name="phone",
            field=models.CharField(max_length=20, blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="organisation",
            name="address",
            field=models.CharField(max_length=500, blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="organisation",
            name="city",
            field=models.CharField(max_length=100, blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="organisation",
            name="country",
            field=models.CharField(max_length=100, blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="organisation",
            name="org_type",
            field=models.CharField(
                max_length=30,
                choices=[
                    ("company", "Company"),
                    ("ngo", "NGO"),
                    ("community", "Community"),
                    ("educational", "Educational"),
                    ("government", "Government"),
                    ("individual", "Individual"),
                ],
                default="company",
            ),
        ),
        migrations.AddField(
            model_name="organisation",
            name="facebook_url",
            field=models.URLField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="organisation",
            name="twitter_url",
            field=models.URLField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="organisation",
            name="instagram_url",
            field=models.URLField(blank=True, default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="organisation",
            name="linkedin_url",
            field=models.URLField(blank=True, default=""),
            preserve_default=False,
        ),
        # * ── OrgDocument table ─────────────────────────────────────────
        migrations.CreateModel(
            name="OrgDocument",
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
                (
                    "doc_type",
                    models.CharField(
                        max_length=30,
                        choices=[
                            ("registration_cert", "Registration Certificate"),
                            ("pan_card", "PAN Card"),
                            ("tax_clearance", "Tax Clearance"),
                            ("logo", "Logo"),
                            ("other", "Other"),
                        ],
                    ),
                ),
                ("file_url", models.URLField()),
                ("file_name", models.CharField(max_length=255)),
                ("file_size", models.PositiveIntegerField(default=0)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to="orgs.organisation",
                    ),
                ),
            ],
            options={
                "db_table": "orgs_org_document",
            },
        ),
    ]
