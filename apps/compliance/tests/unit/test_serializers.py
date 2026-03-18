"""Unit tests for ComplianceControl serializers and summary logic."""

from __future__ import annotations

import uuid


def test_compliance_control_create_valid():
    """A control with category, name, and status is valid."""
    from apps.compliance.presentation.serializers import ComplianceControlCreateSerializer

    ser = ComplianceControlCreateSerializer(
        data={
            "category": "security",
            "name": "Encryption at rest",
            "description": "All data must be encrypted at rest.",
            "status": "pass",
        }
    )
    assert ser.is_valid(), ser.errors
    assert ser.validated_data["category"] == "security"
    assert ser.validated_data["status"] == "pass"


def test_compliance_control_invalid_status():
    """An unknown status fails validation."""
    from apps.compliance.presentation.serializers import ComplianceControlCreateSerializer

    ser = ComplianceControlCreateSerializer(
        data={
            "category": "security",
            "name": "MFA enforcement",
            "status": "unknown",
        }
    )
    assert not ser.is_valid()
    assert "status" in ser.errors


def test_compliance_control_missing_name():
    """Missing name field fails validation."""
    from apps.compliance.presentation.serializers import ComplianceControlCreateSerializer

    ser = ComplianceControlCreateSerializer(
        data={
            "category": "availability",
            "status": "fail",
        }
    )
    assert not ser.is_valid()
    assert "name" in ser.errors


def test_compliance_control_patch_status():
    """Patch serializer accepts a status change."""
    from apps.compliance.presentation.serializers import ComplianceControlPatchSerializer

    ser = ComplianceControlPatchSerializer(data={"status": "fail"})
    assert ser.is_valid(), ser.errors
    assert ser.validated_data["status"] == "fail"


def test_compliance_control_patch_name():
    """Patch serializer accepts a name change."""
    from apps.compliance.presentation.serializers import ComplianceControlPatchSerializer

    ser = ComplianceControlPatchSerializer(data={"name": "Updated control name"})
    assert ser.is_valid(), ser.errors
    assert ser.validated_data["name"] == "Updated control name"


def test_compliance_summary_logic():
    """Summary helper counts totals, passing, failing, and by category correctly."""
    from apps.compliance.application.summary import compute_summary

    controls = [
        {"category": "security", "status": "pass"},
        {"category": "security", "status": "fail"},
        {"category": "availability", "status": "pass"},
        {"category": "confidentiality", "status": "na"},
    ]
    summary = compute_summary(controls)
    assert summary["total"] == 4
    assert summary["passing"] == 2
    assert summary["failing"] == 1
    assert summary["by_category"]["security"] == {"total": 2, "passing": 1, "failing": 1}
    assert summary["by_category"]["availability"] == {"total": 1, "passing": 1, "failing": 0}
    assert summary["by_category"]["confidentiality"] == {"total": 1, "passing": 0, "failing": 0}


def test_compliance_control_response_shape():
    """Response serializer produces expected fields."""
    from apps.compliance.presentation.serializers import ComplianceControlResponseSerializer

    data = {
        "id": str(uuid.uuid4()),
        "category": "security",
        "name": "Encryption in transit",
        "description": "TLS everywhere.",
        "status": "pass",
        "last_checked": None,
        "updated_at": "2026-01-01T00:00:00Z",
        "created_at": "2026-01-01T00:00:00Z",
    }
    ser = ComplianceControlResponseSerializer(data=data)
    assert ser.is_valid(), ser.errors
    assert "category" in ser.validated_data
    assert "status" in ser.validated_data
