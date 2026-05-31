"""Unit tests for the compliance summary computation helper."""

from __future__ import annotations


def test_summary_empty_controls():
    """Empty controls list returns zeros."""
    from apps.compliance.application.summary import compute_summary

    result = compute_summary([])
    assert result["total"] == 0
    assert result["passing"] == 0
    assert result["failing"] == 0
    assert result["by_category"] == {}


def test_summary_all_passing():
    """All-pass controls give passing count equal to total."""
    from apps.compliance.application.summary import compute_summary

    controls = [
        {"category": "security", "status": "pass"},
        {"category": "security", "status": "pass"},
    ]
    result = compute_summary(controls)
    assert result["total"] == 2
    assert result["passing"] == 2
    assert result["failing"] == 0


def test_summary_all_failing():
    """All-fail controls give failing count equal to total."""
    from apps.compliance.application.summary import compute_summary

    controls = [
        {"category": "availability", "status": "fail"},
    ]
    result = compute_summary(controls)
    assert result["failing"] == 1
    assert result["passing"] == 0


def test_summary_na_does_not_count_as_pass_or_fail():
    """N/A controls are counted in total but not in passing or failing."""
    from apps.compliance.application.summary import compute_summary

    controls = [
        {"category": "confidentiality", "status": "na"},
    ]
    result = compute_summary(controls)
    assert result["total"] == 1
    assert result["passing"] == 0
    assert result["failing"] == 0


def test_summary_by_category_mixed():
    """Multiple categories are tallied independently."""
    from apps.compliance.application.summary import compute_summary

    controls = [
        {"category": "security", "status": "pass"},
        {"category": "security", "status": "fail"},
        {"category": "availability", "status": "pass"},
    ]
    result = compute_summary(controls)
    assert result["by_category"]["security"]["total"] == 2
    assert result["by_category"]["security"]["passing"] == 1
    assert result["by_category"]["security"]["failing"] == 1
    assert result["by_category"]["availability"]["total"] == 1
