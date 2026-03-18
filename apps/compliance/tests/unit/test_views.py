"""Unit tests for compliance views serializer logic."""

from __future__ import annotations

import uuid


def test_create_serializer_default_description_empty():
    """Description defaults to empty string when omitted."""
    from apps.compliance.presentation.serializers import ComplianceControlCreateSerializer

    ser = ComplianceControlCreateSerializer(
        data={
            "category": "security",
            "name": "MFA enforcement",
            "status": "pass",
        }
    )
    assert ser.is_valid(), ser.errors
    assert ser.validated_data.get("description", "") == ""


def test_patch_serializer_last_checked_accepted():
    """Patch serializer accepts last_checked datetime."""
    from apps.compliance.presentation.serializers import ComplianceControlPatchSerializer

    ser = ComplianceControlPatchSerializer(data={"last_checked": "2026-01-01T00:00:00Z"})
    assert ser.is_valid(), ser.errors


def test_response_serializer_last_checked_nullable():
    """Response serializer allows null last_checked."""
    from apps.compliance.presentation.serializers import ComplianceControlResponseSerializer

    data = {
        "id": str(uuid.uuid4()),
        "category": "security",
        "name": "Test",
        "description": "",
        "status": "pass",
        "last_checked": None,
        "updated_at": "2026-01-01T00:00:00Z",
        "created_at": "2026-01-01T00:00:00Z",
    }
    ser = ComplianceControlResponseSerializer(data=data)
    assert ser.is_valid(), ser.errors
