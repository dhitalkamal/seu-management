"""Django ORM model for compliance controls."""

from __future__ import annotations

import uuid

from django.db import models


class ComplianceControl(models.Model):
    """An individual SOC2-style compliance control that can be admin-edited."""

    class Status(models.TextChoices):
        PASS = "pass", "Pass"
        FAIL = "fail", "Fail"
        NA = "na", "N/A"

    class Meta:
        db_table = '"orgs"."compliance_control"'
        ordering = ["category", "name"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=Status.choices)
    last_checked = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """Return a human-readable label for admin and debugging."""
        return f"[{self.category}] {self.name} ({self.status})"
