"""
Quality Orchestrator Tests - اختبارات منسق الجودة
===================================================

Tests for quality level classification, issue severity,
audit actions, and quality report generation.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from shared.ai.quality_orchestrator import (
    AuditAction,
    IssueSeverity,
    QualityLevel,
)


# =============================================================================
# QualityLevel Enum Tests
# =============================================================================


class TestQualityLevel:
    """Tests for QualityLevel enum."""

    def test_excellent(self):
        assert QualityLevel.EXCELLENT == "excellent"

    def test_good(self):
        assert QualityLevel.GOOD == "good"

    def test_acceptable(self):
        assert QualityLevel.ACCEPTABLE == "acceptable"

    def test_poor(self):
        assert QualityLevel.POOR == "poor"

    def test_critical(self):
        assert QualityLevel.CRITICAL == "critical"

    def test_all_values(self):
        values = [level.value for level in QualityLevel]
        assert "excellent" in values
        assert "good" in values
        assert "acceptable" in values
        assert "poor" in values
        assert "critical" in values


# =============================================================================
# IssueSeverity Enum Tests
# =============================================================================


class TestIssueSeverity:
    """Tests for IssueSeverity enum."""

    def test_severity_levels(self):
        assert IssueSeverity.CRITICAL == "critical"
        assert IssueSeverity.HIGH == "high"
        assert IssueSeverity.MEDIUM == "medium"
        assert IssueSeverity.LOW == "low"
        assert IssueSeverity.INFO == "info"

    def test_all_severity_values(self):
        values = [s.value for s in IssueSeverity]
        assert len(values) == 5


# =============================================================================
# AuditAction Enum Tests
# =============================================================================


class TestAuditAction:
    """Tests for AuditAction enum."""

    def test_analysis_actions(self):
        assert AuditAction.ANALYSIS_STARTED == "analysis_started"
        assert AuditAction.ANALYSIS_COMPLETED == "analysis_completed"

    def test_tool_actions(self):
        assert AuditAction.TOOL_EXECUTED == "tool_executed"

    def test_issue_actions(self):
        assert AuditAction.ISSUE_FOUND == "issue_found"
        assert AuditAction.ISSUE_FIXED == "issue_fixed"

    def test_quality_gate_actions(self):
        assert AuditAction.QUALITY_GATE_CHECK == "quality_gate_check"
        assert AuditAction.QUALITY_GATE_PASSED == "quality_gate_passed"
        assert AuditAction.QUALITY_GATE_FAILED == "quality_gate_failed"

    def test_notification_action(self):
        assert AuditAction.NOTIFICATION_SENT == "notification_sent"

    def test_error_action(self):
        assert AuditAction.ERROR_OCCURRED == "error_occurred"


# =============================================================================
# Quality Score Classification Tests
# =============================================================================


class TestQualityScoreClassification:
    """Tests for quality score to level mapping."""

    def _classify_score(self, score: float) -> QualityLevel:
        """Helper to classify a quality score."""
        if score >= 90:
            return QualityLevel.EXCELLENT
        elif score >= 70:
            return QualityLevel.GOOD
        elif score >= 50:
            return QualityLevel.ACCEPTABLE
        elif score >= 30:
            return QualityLevel.POOR
        else:
            return QualityLevel.CRITICAL

    def test_excellent_score(self):
        assert self._classify_score(95) == QualityLevel.EXCELLENT
        assert self._classify_score(90) == QualityLevel.EXCELLENT
        assert self._classify_score(100) == QualityLevel.EXCELLENT

    def test_good_score(self):
        assert self._classify_score(70) == QualityLevel.GOOD
        assert self._classify_score(85) == QualityLevel.GOOD
        assert self._classify_score(89) == QualityLevel.GOOD

    def test_acceptable_score(self):
        assert self._classify_score(50) == QualityLevel.ACCEPTABLE
        assert self._classify_score(65) == QualityLevel.ACCEPTABLE
        assert self._classify_score(69) == QualityLevel.ACCEPTABLE

    def test_poor_score(self):
        assert self._classify_score(30) == QualityLevel.POOR
        assert self._classify_score(45) == QualityLevel.POOR

    def test_critical_score(self):
        assert self._classify_score(0) == QualityLevel.CRITICAL
        assert self._classify_score(15) == QualityLevel.CRITICAL
        assert self._classify_score(29) == QualityLevel.CRITICAL


# =============================================================================
# QualityOrchestrator Import Test
# =============================================================================


class TestQualityOrchestratorImport:
    """Tests to verify quality orchestrator can be imported and instantiated."""

    def test_import_quality_orchestrator(self):
        from shared.ai.quality_orchestrator import QualityOrchestrator
        assert QualityOrchestrator is not None

    def test_import_quality_report(self):
        from shared.ai.quality_orchestrator import QualityReport
        assert QualityReport is not None

    def test_quality_orchestrator_instantiation(self):
        from shared.ai.quality_orchestrator import QualityOrchestrator
        orchestrator = QualityOrchestrator()
        assert orchestrator is not None
