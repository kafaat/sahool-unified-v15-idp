"""
Tests for shared/ai/auto_fix/models.py
========================================

Tests cover:
- All enums: DiagnosticSeverity, DiagnosticCategory, FixStrategy,
  FixConfidence, ToolType
- Dataclass models: CodeLocation, Diagnostic, CodeFix, FixResult,
  DiagnosticReport, FixPlan, AuditEntry
- to_dict() conversions
- __post_init__ calculations
- Properties: has_errors, has_issues
"""

import pytest
from datetime import UTC, datetime

from shared.ai.auto_fix.models import (
    AuditEntry,
    CodeFix,
    CodeLocation,
    Diagnostic,
    DiagnosticCategory,
    DiagnosticReport,
    DiagnosticSeverity,
    FixConfidence,
    FixPlan,
    FixResult,
    FixStrategy,
    ToolType,
)


# ─────────────────────────────────────────────────────────────────────────────
# Enum Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestDiagnosticSeverity:
    def test_all_values(self):
        assert DiagnosticSeverity.ERROR.value == "error"
        assert DiagnosticSeverity.WARNING.value == "warning"
        assert DiagnosticSeverity.INFO.value == "info"
        assert DiagnosticSeverity.HINT.value == "hint"

    def test_member_count(self):
        assert len(DiagnosticSeverity) == 4


class TestDiagnosticCategory:
    def test_all_values(self):
        assert DiagnosticCategory.SYNTAX.value == "syntax"
        assert DiagnosticCategory.TYPE.value == "type"
        assert DiagnosticCategory.SECURITY.value == "security"
        assert DiagnosticCategory.PERFORMANCE.value == "performance"
        assert DiagnosticCategory.STYLE.value == "style"
        assert DiagnosticCategory.BEST_PRACTICE.value == "best_practice"
        assert DiagnosticCategory.DEPRECATION.value == "deprecation"
        assert DiagnosticCategory.LOGIC.value == "logic"
        assert DiagnosticCategory.IMPORT.value == "import"
        assert DiagnosticCategory.NAMING.value == "naming"

    def test_member_count(self):
        assert len(DiagnosticCategory) == 10


class TestFixStrategy:
    def test_all_values(self):
        assert FixStrategy.MINIMAL.value == "minimal"
        assert FixStrategy.SAFE.value == "safe"
        assert FixStrategy.COMPREHENSIVE.value == "comprehensive"
        assert FixStrategy.REFACTOR.value == "refactor"

    def test_member_count(self):
        assert len(FixStrategy) == 4


class TestFixConfidence:
    def test_all_values(self):
        assert FixConfidence.HIGH.value == "high"
        assert FixConfidence.MEDIUM.value == "medium"
        assert FixConfidence.LOW.value == "low"

    def test_member_count(self):
        assert len(FixConfidence) == 3


class TestToolType:
    def test_all_values(self):
        # Layer 1: Code Quality & Static Analysis
        assert ToolType.RUFF.value == "ruff"
        assert ToolType.ESLINT.value == "eslint"
        assert ToolType.BIOME.value == "biome"
        assert ToolType.OXLINT.value == "oxlint"
        assert ToolType.PYLINT.value == "pylint"
        # Layer 2: Type Checking
        assert ToolType.MYPY.value == "mypy"
        assert ToolType.PYRIGHT.value == "pyright"
        assert ToolType.TYPESCRIPT.value == "typescript"
        # Layer 3: Security SAST
        assert ToolType.BANDIT.value == "bandit"
        assert ToolType.SEMGREP.value == "semgrep"
        assert ToolType.CODEQL.value == "codeql"
        assert ToolType.TRIVY.value == "trivy"
        # Layer 4: Dependency & Supply Chain
        assert ToolType.NPM_AUDIT.value == "npm_audit"
        assert ToolType.PIP_AUDIT.value == "pip_audit"
        # Layer 5: Architecture & Dependencies
        assert ToolType.KNIP.value == "knip"
        assert ToolType.MADGE.value == "madge"
        assert ToolType.DEPCHECK.value == "depcheck"
        assert ToolType.VULTURE.value == "vulture"
        assert ToolType.RADON.value == "radon"
        # Layer 6: Mobile
        assert ToolType.DART_ANALYZE.value == "dart_analyze"
        # Layer 7: Container & Infrastructure
        assert ToolType.HADOLINT.value == "hadolint"
        assert ToolType.DETECT_SECRETS.value == "detect_secrets"

    def test_member_count(self):
        assert len(ToolType) == 22


# ─────────────────────────────────────────────────────────────────────────────
# CodeLocation Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestCodeLocation:
    def test_basic_creation(self):
        loc = CodeLocation(file_path="app.py", line_start=10)
        assert loc.file_path == "app.py"
        assert loc.line_start == 10
        assert loc.line_end is None
        assert loc.column_start is None
        assert loc.column_end is None

    def test_str_simple(self):
        loc = CodeLocation(file_path="app.py", line_start=10)
        assert str(loc) == "app.py:10"

    def test_str_with_column(self):
        loc = CodeLocation(file_path="app.py", line_start=10, column_start=5)
        assert str(loc) == "app.py:10:5"

    def test_str_with_line_range(self):
        loc = CodeLocation(file_path="app.py", line_start=10, line_end=15)
        assert str(loc) == "app.py:10-15"

    def test_str_with_column_and_range(self):
        loc = CodeLocation(file_path="app.py", line_start=10, line_end=15, column_start=3)
        assert str(loc) == "app.py:10:3-15"

    def test_str_same_line_start_end(self):
        loc = CodeLocation(file_path="app.py", line_start=10, line_end=10)
        # When line_end == line_start, no range shown
        assert str(loc) == "app.py:10"


# ─────────────────────────────────────────────────────────────────────────────
# Diagnostic Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestDiagnostic:
    def _make_diagnostic(self, **kwargs):
        defaults = {
            "id": "d1",
            "message": "Unused import",
            "message_ar": "استيراد غير مستخدم",
            "severity": DiagnosticSeverity.WARNING,
            "category": DiagnosticCategory.IMPORT,
            "location": CodeLocation(file_path="app.py", line_start=1),
        }
        defaults.update(kwargs)
        return Diagnostic(**defaults)

    def test_basic_creation(self):
        diag = self._make_diagnostic()
        assert diag.id == "d1"
        assert diag.message == "Unused import"
        assert diag.message_ar == "استيراد غير مستخدم"
        assert diag.severity == DiagnosticSeverity.WARNING
        assert diag.category == DiagnosticCategory.IMPORT
        assert diag.rule_id is None
        assert diag.tool is None
        assert diag.suggestion is None
        assert diag.related_diagnostics == []

    def test_to_dict(self):
        diag = self._make_diagnostic(
            rule_id="F401",
            tool=ToolType.RUFF,
            suggestion="Remove import",
            suggestion_ar="أزل الاستيراد",
        )
        d = diag.to_dict()
        assert d["id"] == "d1"
        assert d["message"] == "Unused import"
        assert d["message_ar"] == "استيراد غير مستخدم"
        assert d["severity"] == "warning"
        assert d["category"] == "import"
        assert d["location"]["file_path"] == "app.py"
        assert d["location"]["line_start"] == 1
        assert d["rule_id"] == "F401"
        assert d["tool"] == "ruff"
        assert d["suggestion"] == "Remove import"
        assert "created_at" in d

    def test_to_dict_no_tool(self):
        diag = self._make_diagnostic()
        d = diag.to_dict()
        assert d["tool"] is None


# ─────────────────────────────────────────────────────────────────────────────
# CodeFix Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestCodeFix:
    def _make_fix(self, **kwargs):
        defaults = {
            "id": "f1",
            "diagnostic_id": "d1",
            "description": "Remove unused import",
            "description_ar": "إزالة الاستيراد غير المستخدم",
            "original_code": "import os",
            "fixed_code": "",
            "strategy": FixStrategy.SAFE,
            "confidence": FixConfidence.HIGH,
        }
        defaults.update(kwargs)
        return CodeFix(**defaults)

    def test_basic_creation(self):
        fix = self._make_fix()
        assert fix.id == "f1"
        assert fix.diagnostic_id == "d1"
        assert fix.is_safe is True
        assert fix.requires_review is False
        assert fix.breaking_change is False
        assert fix.test_required is False
        assert fix.related_fixes == []

    def test_to_dict(self):
        fix = self._make_fix()
        d = fix.to_dict()
        assert d["id"] == "f1"
        assert d["strategy"] == "safe"
        assert d["confidence"] == "high"
        assert d["is_safe"] is True
        assert "created_at" in d

    def test_unsafe_fix(self):
        fix = self._make_fix(
            is_safe=False,
            requires_review=True,
            breaking_change=True,
            test_required=True,
        )
        assert fix.is_safe is False
        assert fix.requires_review is True
        assert fix.breaking_change is True
        assert fix.test_required is True


# ─────────────────────────────────────────────────────────────────────────────
# FixResult Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestFixResult:
    def test_success(self):
        result = FixResult(
            fix_id="f1",
            success=True,
            applied_at=datetime.now(UTC),
            file_path="app.py",
            verification_passed=True,
        )
        assert result.success is True
        assert result.error_message is None
        assert result.rollback_available is True
        assert result.backup_path is None

    def test_failure(self):
        result = FixResult(
            fix_id="f1",
            success=False,
            applied_at=datetime.now(UTC),
            file_path="app.py",
            error_message="Permission denied",
        )
        assert result.success is False
        assert result.error_message == "Permission denied"

    def test_to_dict(self):
        result = FixResult(
            fix_id="f1",
            success=True,
            applied_at=datetime.now(UTC),
            file_path="app.py",
            backup_path="/tmp/backup.py",
        )
        d = result.to_dict()
        assert d["fix_id"] == "f1"
        assert d["success"] is True
        assert d["file_path"] == "app.py"
        assert d["backup_path"] == "/tmp/backup.py"
        assert d["rollback_available"] is True


# ─────────────────────────────────────────────────────────────────────────────
# DiagnosticReport Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestDiagnosticReport:
    def _make_diagnostics(self):
        loc = CodeLocation(file_path="app.py", line_start=1)
        return [
            Diagnostic(
                id="d1", message="err", message_ar="خطأ",
                severity=DiagnosticSeverity.ERROR,
                category=DiagnosticCategory.SYNTAX, location=loc,
            ),
            Diagnostic(
                id="d2", message="warn", message_ar="تحذير",
                severity=DiagnosticSeverity.WARNING,
                category=DiagnosticCategory.STYLE, location=loc,
            ),
            Diagnostic(
                id="d3", message="info", message_ar="معلومات",
                severity=DiagnosticSeverity.INFO,
                category=DiagnosticCategory.BEST_PRACTICE, location=loc,
            ),
            Diagnostic(
                id="d4", message="hint", message_ar="تلميح",
                severity=DiagnosticSeverity.HINT,
                category=DiagnosticCategory.NAMING, location=loc,
            ),
        ]

    def test_post_init_calculates_totals(self):
        diagnostics = self._make_diagnostics()
        report = DiagnosticReport(id="r1", target="app.py", diagnostics=diagnostics)
        assert report.total_errors == 1
        assert report.total_warnings == 1
        assert report.total_info == 1
        assert report.total_hints == 1

    def test_has_errors(self):
        diagnostics = self._make_diagnostics()
        report = DiagnosticReport(id="r1", target="app.py", diagnostics=diagnostics)
        assert report.has_errors is True

    def test_has_issues(self):
        diagnostics = self._make_diagnostics()
        report = DiagnosticReport(id="r1", target="app.py", diagnostics=diagnostics)
        assert report.has_issues is True

    def test_empty_report(self):
        report = DiagnosticReport(id="r1", target="app.py", diagnostics=[])
        assert report.has_errors is False
        assert report.has_issues is False
        assert report.total_errors == 0

    def test_to_dict(self):
        diagnostics = self._make_diagnostics()
        report = DiagnosticReport(
            id="r1",
            target="app.py",
            diagnostics=diagnostics,
            tools_used=[ToolType.RUFF, ToolType.MYPY],
            scan_duration_ms=123.5,
        )
        d = report.to_dict()
        assert d["id"] == "r1"
        assert d["target"] == "app.py"
        assert len(d["diagnostics"]) == 4
        assert d["summary"]["total_errors"] == 1
        assert d["summary"]["total_warnings"] == 1
        assert d["summary"]["total_issues"] == 4
        assert d["tools_used"] == ["ruff", "mypy"]
        assert d["scan_duration_ms"] == 123.5


# ─────────────────────────────────────────────────────────────────────────────
# FixPlan Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestFixPlan:
    def _make_fixes(self):
        return [
            CodeFix(
                id="f1", diagnostic_id="d1", description="Fix 1",
                description_ar="إصلاح 1", original_code="a", fixed_code="b",
                strategy=FixStrategy.SAFE, confidence=FixConfidence.HIGH,
                is_safe=True, requires_review=False,
            ),
            CodeFix(
                id="f2", diagnostic_id="d2", description="Fix 2",
                description_ar="إصلاح 2", original_code="c", fixed_code="d",
                strategy=FixStrategy.COMPREHENSIVE, confidence=FixConfidence.MEDIUM,
                is_safe=False, requires_review=True,
            ),
        ]

    def test_post_init_calculates_stats(self):
        fixes = self._make_fixes()
        plan = FixPlan(
            id="p1",
            diagnostic_report_id="r1",
            fixes=fixes,
            strategy=FixStrategy.SAFE,
        )
        assert plan.total_fixes == 2
        assert plan.safe_fixes == 1
        assert plan.review_required == 1

    def test_empty_plan(self):
        plan = FixPlan(
            id="p1",
            diagnostic_report_id="r1",
            fixes=[],
            strategy=FixStrategy.MINIMAL,
        )
        assert plan.total_fixes == 0
        assert plan.safe_fixes == 0
        assert plan.review_required == 0

    def test_to_dict(self):
        fixes = self._make_fixes()
        plan = FixPlan(
            id="p1",
            diagnostic_report_id="r1",
            fixes=fixes,
            strategy=FixStrategy.SAFE,
            estimated_impact="Minor",
            estimated_impact_ar="بسيط",
        )
        d = plan.to_dict()
        assert d["id"] == "p1"
        assert d["strategy"] == "safe"
        assert d["summary"]["total_fixes"] == 2
        assert d["summary"]["safe_fixes"] == 1
        assert d["summary"]["review_required"] == 1
        assert d["estimated_impact"] == "Minor"
        assert len(d["fixes"]) == 2


# ─────────────────────────────────────────────────────────────────────────────
# AuditEntry Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestAuditEntry:
    def test_creation(self):
        entry = AuditEntry(
            id="a1",
            action="fix_applied",
            actor="system",
            target="app.py",
            details={"fixes_count": 5},
        )
        assert entry.id == "a1"
        assert entry.action == "fix_applied"
        assert entry.actor == "system"
        assert entry.target == "app.py"
        assert entry.severity is None
        assert entry.success is True
        assert entry.error is None

    def test_to_dict(self):
        entry = AuditEntry(
            id="a1",
            action="diagnose",
            actor="user-123",
            target="shared/",
            details={"issues": 10},
            severity=DiagnosticSeverity.WARNING,
            success=True,
        )
        d = entry.to_dict()
        assert d["id"] == "a1"
        assert d["action"] == "diagnose"
        assert d["actor"] == "user-123"
        assert d["severity"] == "warning"
        assert d["success"] is True
        assert "timestamp" in d

    def test_to_dict_no_severity(self):
        entry = AuditEntry(
            id="a1",
            action="fix_applied",
            actor="system",
            target="app.py",
            details={},
        )
        d = entry.to_dict()
        assert d["severity"] is None

    def test_failed_entry(self):
        entry = AuditEntry(
            id="a1",
            action="fix_applied",
            actor="system",
            target="app.py",
            details={},
            success=False,
            error="File not found",
        )
        d = entry.to_dict()
        assert d["success"] is False
        assert d["error"] == "File not found"
