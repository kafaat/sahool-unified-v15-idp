"""
Tests for drift detection baseline comparison.
اختبارات مقارنة الحالة الأساسية لكشف الانحراف.

Covers create_baseline, load_baseline, compare_with_baseline,
and baseline-aware get_ci_exit_code.
"""

from __future__ import annotations

import json

import pytest

from shared.drift_detection.engine import (
    DriftDetectionEngine,
    compare_with_baseline,
    create_baseline,
    load_baseline,
)
from shared.drift_detection.models import (
    DriftCategory,
    DriftReport,
    DriftResult,
    DriftSeverity,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _report_with_counts(
    critical: int = 0,
    high: int = 0,
    medium: int = 0,
    category: DriftCategory = DriftCategory.SECURITY,
) -> DriftReport:
    results = []
    for _ in range(critical):
        results.append(DriftResult(category=category, severity=DriftSeverity.CRITICAL))
    for _ in range(high):
        results.append(DriftResult(category=category, severity=DriftSeverity.HIGH))
    for _ in range(medium):
        results.append(DriftResult(category=category, severity=DriftSeverity.MEDIUM))
    return DriftReport(results=results, environment="development")


# ---------------------------------------------------------------------------
# create_baseline
# ---------------------------------------------------------------------------


class TestCreateBaseline:
    def test_empty_report(self):
        report = DriftReport()
        bl = create_baseline(report)
        assert bl["version"] == 1
        assert bl["total"] == 0
        assert bl["critical"] == 0
        assert bl["high"] == 0
        assert bl["by_category"] == {}

    def test_populated_report(self):
        report = _report_with_counts(critical=2, high=5, medium=3)
        bl = create_baseline(report)
        assert bl["total"] == 10
        assert bl["critical"] == 2
        assert bl["high"] == 5
        assert bl["environment"] == "development"
        assert "security" in bl["by_category"]
        assert bl["by_category"]["security"]["critical"] == 2
        assert bl["by_category"]["security"]["high"] == 5
        assert bl["by_category"]["security"]["medium"] == 3

    def test_multi_category(self):
        results = [
            DriftResult(category=DriftCategory.SECURITY, severity=DriftSeverity.CRITICAL),
            DriftResult(category=DriftCategory.CONFIG, severity=DriftSeverity.HIGH),
            DriftResult(category=DriftCategory.CONFIG, severity=DriftSeverity.MEDIUM),
        ]
        report = DriftReport(results=results)
        bl = create_baseline(report)
        assert bl["total"] == 3
        assert bl["critical"] == 1
        assert bl["high"] == 1
        assert "security" in bl["by_category"]
        assert "config" in bl["by_category"]

    def test_has_generated_at(self):
        bl = create_baseline(DriftReport())
        assert "generated_at" in bl


# ---------------------------------------------------------------------------
# load_baseline
# ---------------------------------------------------------------------------


class TestLoadBaseline:
    def test_missing_file(self, tmp_path):
        result = load_baseline(str(tmp_path / "nonexistent.json"))
        assert result is None

    def test_valid_file(self, tmp_path):
        bl_data = {"version": 1, "total": 10, "critical": 2, "high": 5}
        path = tmp_path / "baseline.json"
        path.write_text(json.dumps(bl_data))
        result = load_baseline(str(path))
        assert result == bl_data

    def test_invalid_json(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("not json {{{")
        result = load_baseline(str(path))
        assert result is None

    def test_empty_file(self, tmp_path):
        path = tmp_path / "empty.json"
        path.write_text("")
        result = load_baseline(str(path))
        assert result is None


# ---------------------------------------------------------------------------
# compare_with_baseline
# ---------------------------------------------------------------------------


class TestCompareWithBaseline:
    def test_no_regression(self):
        """Same counts as baseline → zero deltas."""
        report = _report_with_counts(critical=2, high=5, medium=3)
        baseline = {
            "total": 10,
            "critical": 2,
            "high": 5,
            "by_category": {
                "security": {"critical": 2, "high": 5, "medium": 3},
            },
        }
        delta = compare_with_baseline(report, baseline)
        assert delta["total"] == 0
        assert delta["critical"] == 0
        assert delta["high"] == 0
        assert delta["by_category"] == {}

    def test_improvement(self):
        """Fewer drifts than baseline → zero deltas (no negative)."""
        report = _report_with_counts(critical=1, high=3)
        baseline = {"total": 10, "critical": 2, "high": 5, "by_category": {}}
        delta = compare_with_baseline(report, baseline)
        assert delta["total"] == 0
        assert delta["critical"] == 0
        assert delta["high"] == 0

    def test_regression_critical(self):
        """More criticals than baseline → positive delta."""
        report = _report_with_counts(critical=5, high=5)
        baseline = {"total": 8, "critical": 2, "high": 5, "by_category": {}}
        delta = compare_with_baseline(report, baseline)
        assert delta["critical"] == 3
        assert delta["total"] == 2

    def test_regression_high(self):
        """More high drifts than baseline → positive delta."""
        report = _report_with_counts(high=10)
        baseline = {"total": 5, "critical": 0, "high": 5, "by_category": {}}
        delta = compare_with_baseline(report, baseline)
        assert delta["high"] == 5
        assert delta["total"] == 5

    def test_regression_medium_only(self):
        """More medium drifts → total increases but critical/high stay zero."""
        report = _report_with_counts(medium=15)
        baseline = {"total": 10, "critical": 0, "high": 0, "by_category": {}}
        delta = compare_with_baseline(report, baseline)
        assert delta["critical"] == 0
        assert delta["high"] == 0
        assert delta["total"] == 5

    def test_new_category(self):
        """Drifts in a category not in the baseline → counted as regression."""
        report = _report_with_counts(high=3, category=DriftCategory.CONFIG)
        baseline = {"total": 0, "critical": 0, "high": 0, "by_category": {}}
        delta = compare_with_baseline(report, baseline)
        assert delta["by_category"]["config"] == 3

    def test_category_regression(self):
        """More drifts in a specific category than baseline."""
        report = _report_with_counts(high=5, category=DriftCategory.SECURITY)
        baseline = {
            "total": 3,
            "critical": 0,
            "high": 3,
            "by_category": {
                "security": {"high": 3},
            },
        }
        delta = compare_with_baseline(report, baseline)
        assert delta["by_category"]["security"] == 2

    def test_empty_baseline(self):
        """Empty baseline → all drifts are regressions."""
        report = _report_with_counts(critical=2, high=3)
        baseline = {"total": 0, "critical": 0, "high": 0, "by_category": {}}
        delta = compare_with_baseline(report, baseline)
        assert delta["total"] == 5
        assert delta["critical"] == 2
        assert delta["high"] == 3

    def test_metadata_fields(self):
        """Delta includes baseline_total and current_total."""
        report = _report_with_counts(high=5)
        baseline = {"total": 3, "critical": 0, "high": 3, "by_category": {}}
        delta = compare_with_baseline(report, baseline)
        assert delta["baseline_total"] == 3
        assert delta["current_total"] == 5


# ---------------------------------------------------------------------------
# get_ci_exit_code with baseline
# ---------------------------------------------------------------------------


class TestCIExitCodeWithBaseline:
    def test_no_baseline_strict_mode(self):
        """Without baseline, original strict behaviour applies."""
        engine = DriftDetectionEngine()
        report = _report_with_counts(critical=1)
        assert engine.get_ci_exit_code(report) == 1

    def test_baseline_no_regression_returns_0(self):
        """All drifts within baseline → exit 0."""
        engine = DriftDetectionEngine()
        report = _report_with_counts(critical=5, high=10, medium=20)
        baseline = {"total": 35, "critical": 5, "high": 10, "by_category": {}}
        assert engine.get_ci_exit_code(report, baseline=baseline) == 0

    def test_baseline_improvement_returns_0(self):
        """Fewer drifts than baseline → exit 0."""
        engine = DriftDetectionEngine()
        report = _report_with_counts(critical=1, high=2)
        baseline = {"total": 35, "critical": 5, "high": 10, "by_category": {}}
        assert engine.get_ci_exit_code(report, baseline=baseline) == 0

    def test_baseline_new_critical_returns_1(self):
        """New critical above baseline → exit 1."""
        engine = DriftDetectionEngine()
        report = _report_with_counts(critical=6, high=10)
        baseline = {"total": 15, "critical": 5, "high": 10, "by_category": {}}
        assert engine.get_ci_exit_code(report, baseline=baseline) == 1

    def test_baseline_new_high_returns_1(self):
        """New high above baseline → exit 1."""
        engine = DriftDetectionEngine()
        report = _report_with_counts(high=12)
        baseline = {"total": 10, "critical": 0, "high": 10, "by_category": {}}
        assert engine.get_ci_exit_code(report, baseline=baseline) == 1

    def test_baseline_new_medium_returns_2(self):
        """New medium-only above baseline → exit 2 (warning)."""
        engine = DriftDetectionEngine()
        report = _report_with_counts(medium=15)
        baseline = {"total": 10, "critical": 0, "high": 0, "by_category": {}}
        assert engine.get_ci_exit_code(report, baseline=baseline) == 2

    def test_baseline_exact_match_returns_0(self):
        """Exact same counts as baseline → exit 0."""
        engine = DriftDetectionEngine()
        report = _report_with_counts(critical=3, high=7, medium=5)
        baseline = {"total": 15, "critical": 3, "high": 7, "by_category": {}}
        assert engine.get_ci_exit_code(report, baseline=baseline) == 0


# ---------------------------------------------------------------------------
# Round-trip: create → load → compare
# ---------------------------------------------------------------------------


class TestBaselineRoundTrip:
    def test_create_write_load_compare(self, tmp_path):
        """Full round-trip: create baseline, write to disk, load, compare."""
        report = _report_with_counts(critical=5, high=10, medium=20)
        bl = create_baseline(report)

        path = tmp_path / "baseline.json"
        path.write_text(json.dumps(bl))

        loaded = load_baseline(str(path))
        assert loaded is not None

        # Same report → no regression
        delta = compare_with_baseline(report, loaded)
        assert delta["total"] == 0
        assert delta["critical"] == 0
        assert delta["high"] == 0

    def test_regression_after_baseline(self, tmp_path):
        """New drifts after baseline is created → detected as regression."""
        original = _report_with_counts(critical=2, high=5)
        bl = create_baseline(original)

        path = tmp_path / "baseline.json"
        path.write_text(json.dumps(bl))
        loaded = load_baseline(str(path))

        # New report with more drifts
        new_report = _report_with_counts(critical=4, high=8)
        delta = compare_with_baseline(new_report, loaded)
        assert delta["critical"] == 2
        assert delta["high"] == 3
        assert delta["total"] == 5
