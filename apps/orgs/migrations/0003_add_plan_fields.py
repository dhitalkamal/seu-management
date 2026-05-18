"""Migration: add plan and plan_expires_at to Organisation for subscription billing."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orgs", "0002_add_allowed_domain"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="plan",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("free", "Free"),
                    ("starter", "Starter"),
                    ("pro", "Pro"),
                    ("ngo", "NGO"),
                    ("enterprise", "Enterprise"),
                ],
                default="free",
            ),
        ),
        migrations.AddField(
            model_name="organisation",
            name="plan_expires_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
