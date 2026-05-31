"""Pure helper for computing compliance control summary statistics."""

from __future__ import annotations


def compute_summary(controls: list[dict]) -> dict:
    """Return totals and per-category breakdown from a list of control dicts.

    Each dict must have at least 'category' and 'status' keys.
    Status values: 'pass', 'fail', 'na'.
    """
    total = len(controls)
    passing = sum(1 for c in controls if c["status"] == "pass")
    failing = sum(1 for c in controls if c["status"] == "fail")
    na = sum(1 for c in controls if c["status"] == "na")

    by_category: dict[str, dict[str, int]] = {}
    for c in controls:
        cat = c["category"]
        if cat not in by_category:
            by_category[cat] = {"total": 0, "passing": 0, "failing": 0}
        by_category[cat]["total"] += 1
        if c["status"] == "pass":
            by_category[cat]["passing"] += 1
        elif c["status"] == "fail":
            by_category[cat]["failing"] += 1

    return {
        "total": total,
        "passing": passing,
        "failing": failing,
        "na": na,
        "by_category": by_category,
    }
