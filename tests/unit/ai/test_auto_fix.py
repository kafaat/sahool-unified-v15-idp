"""
Tests for Auto-Fix Module
=========================
اختبارات وحدة الإصلاح التلقائي

Comprehensive tests for code diagnostics, fixing, and audit integration.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
import os
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.ai.auto_fix import (
    AuditEntry,
    AutoFixEngine,
    CodeDiagnostics,
    CodeFix,
    CodeFixer,
    CodeLocation,
    Diagnostic,
    DiagnosticCategory,
    DiagnosticError,
    DiagnosticReport,
    DiagnosticSeverity,
    FixConfidence,
    FixPlan,
    FixResult,
    FixStrategy,
    ToolType,
)

# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_diagnostic() -> Diagnostic:
    """Create a sample diagnostic for testing."""
    return Diagnostic(
        id=str(uuid.uuid4()),
        message="Unused import 'os'",
        message_ar="استيراد غير مستخدم 'os'",
        severity=DiagnosticSeverity.WARNING,
        category=DiagnosticCategory.IMPORT,
        location=CodeLocation(
            file_path="/tmp/test.py",
            line_start=1,
            line_end=1,
            column_start=1,
            column_end=10,
        ),
        rule_id="F401",
        tool=ToolType.RUFF,
        suggestion="Remove the unused import",
    )


@pytest.fixture
def sample_report(sample_diagnostic: Diagnostic) -> DiagnosticReport:
    """Create a sample diagnostic report."""
    return DiagnosticReport(
        id=str(uuid.uuid4()),
        target="/tmp/test.py",
        diagnostics=[sample_diagnostic],
        tools_used=[ToolType.RUFF],
        scan_duration_ms=150.5,
    )


@pytest.fixture
def sample_fix(sample_diagnostic: Diagnostic) -> CodeFix:
    """Create a sample code fix."""
    return CodeFix(
        id=str(uuid.uuid4()),
        diagnostic_id=sample_diagnostic.id,
        description="Remove unused import",
        description_ar="إزالة الاستيراد غير المستخدم",
        original_code="import os\n",
        fixed_code="",
        strategy=FixStrategy.SAFE,
        confidence=FixConfidence.HIGH,
        is_safe=True,
    )


@pytest.fixture
def temp_python_file():
    """Create a temporary Python file for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8",
    ) as f:
        f.write("""import os
import sys  # unused

def hello():
    print("Hello")

x= 1  # missing space
""")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


# ═══════════════════════════════════════════════════════════════════════════
# Test Models
# ═══════════════════════════════════════════════════════════════════════════


class TestDiagnosticModels:
    """Tests for diagnostic data models."""

    def test_code_location_str(self):
        """Test CodeLocation string representation."""
        loc = CodeLocation(
            file_path="/test/file.py",
            line_start=10,
            line_end=15,
            column_start=5,
        )
        assert str(loc) == "/test/file.py:10:5-15"

    def test_diagnostic_to_dict(self, sample_diagnostic: Diagnostic):
        """Test Diagnostic to dictionary conversion."""
        data = sample_diagnostic.to_dict()

        assert data["message"] == "Unused import 'os'"
        assert data["message_ar"] == "استيراد غير مستخدم 'os'"
        assert data["severity"] == "warning"
        assert data["category"] == "import"
        assert data["rule_id"] == "F401"
        assert data["tool"] == "ruff"

    def test_diagnostic_report_totals(self, sample_diagnostic: Diagnostic):
        """Test DiagnosticReport total calculations."""
        # Create multiple diagnostics with different severities
        error_diag = Diagnostic(
            id=str(uuid.uuid4()),
            message="Syntax error",
            message_ar="خطأ في بناء الجملة",
            severity=DiagnosticSeverity.ERROR,
            category=DiagnosticCategory.SYNTAX,
            location=CodeLocation(file_path="/test.py", line_start=1),
        )

        info_diag = Diagnostic(
            id=str(uuid.uuid4()),
            message="Info message",
            message_ar="رسالة معلومات",
            severity=DiagnosticSeverity.INFO,
            category=DiagnosticCategory.STYLE,
            location=CodeLocation(file_path="/test.py", line_start=2),
        )

        report = DiagnosticReport(
            id=str(uuid.uuid4()),
            target="/test.py",
            diagnostics=[sample_diagnostic, error_diag, info_diag],
        )

        assert report.total_errors == 1
        assert report.total_warnings == 1
        assert report.total_info == 1
        assert report.has_errors is True
        assert report.has_issues is True

    def test_code_fix_to_dict(self, sample_fix: CodeFix):
        """Test CodeFix to dictionary conversion."""
        data = sample_fix.to_dict()

        assert data["description"] == "Remove unused import"
        assert data["description_ar"] == "إزالة الاستيراد غير المستخدم"
        assert data["strategy"] == "safe"
        assert data["confidence"] == "high"
        assert data["is_safe"] is True

    def test_fix_plan_statistics(self, sample_fix: CodeFix):
        """Test FixPlan statistics calculation."""
        unsafe_fix = CodeFix(
            id=str(uuid.uuid4()),
            diagnostic_id="test",
            description="Unsafe fix",
            description_ar="إصلاح غير آمن",
            original_code="x",
            fixed_code="y",
            strategy=FixStrategy.COMPREHENSIVE,
            confidence=FixConfidence.LOW,
            is_safe=False,
            requires_review=True,
        )

        plan = FixPlan(
            id=str(uuid.uuid4()),
            diagnostic_report_id="report-1",
            fixes=[sample_fix, unsafe_fix],
            strategy=FixStrategy.SAFE,
        )

        assert plan.total_fixes == 2
        assert plan.safe_fixes == 1
        assert plan.review_required == 1

    def test_audit_entry_to_dict(self):
        """Test AuditEntry to dictionary conversion."""
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            action="fix_applied",
            actor="system",
            target="/test.py",
            details={"fix_id": "123", "rule_id": "F401"},
            severity=DiagnosticSeverity.WARNING,
            success=True,
        )

        data = entry.to_dict()

        assert data["action"] == "fix_applied"
        assert data["actor"] == "system"
        assert data["severity"] == "warning"
        assert data["success"] is True


# ═══════════════════════════════════════════════════════════════════════════
# Test Diagnostics
# ═══════════════════════════════════════════════════════════════════════════


class TestCodeDiagnostics:
    """Tests for CodeDiagnostics class."""

    @pytest.mark.asyncio
    async def test_diagnose_nonexistent_file(self):
        """Test diagnosing a non-existent file raises error."""
        diagnostics = CodeDiagnostics()

        with pytest.raises(DiagnosticError) as exc_info:
            await diagnostics.diagnose_file("/nonexistent/file.py")

        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_diagnose_nonexistent_directory(self):
        """Test diagnosing a non-existent directory raises error."""
        diagnostics = CodeDiagnostics()

        with pytest.raises(DiagnosticError) as exc_info:
            await diagnostics.diagnose_directory("/nonexistent/dir")

        assert "not found" in str(exc_info.value).lower()

    def test_get_file_tools_python(self):
        """Test tool detection for Python files."""
        diagnostics = CodeDiagnostics()
        tools = diagnostics._get_file_tools("test.py")

        assert ToolType.RUFF in tools
        assert ToolType.MYPY in tools
        assert ToolType.BANDIT in tools

    def test_get_file_tools_typescript(self):
        """Test tool detection for TypeScript files."""
        diagnostics = CodeDiagnostics()
        tools = diagnostics._get_file_tools("test.ts")

        assert ToolType.ESLINT in tools

    def test_get_file_tools_dart(self):
        """Test tool detection for Dart files."""
        diagnostics = CodeDiagnostics()
        tools = diagnostics._get_file_tools("test.dart")

        assert ToolType.DART_ANALYZE in tools

    def test_format_report_markdown(self, sample_report: DiagnosticReport):
        """Test markdown report formatting."""
        diagnostics = CodeDiagnostics()
        md = diagnostics.format_report_markdown(sample_report)

        assert "# Code Diagnostic Report" in md
        assert "تقرير تشخيص الكود" in md
        assert "F401" in md
        assert sample_report.target in md

    def test_format_report_markdown_no_arabic(self, sample_report: DiagnosticReport):
        """Test markdown report without Arabic."""
        diagnostics = CodeDiagnostics()
        md = diagnostics.format_report_markdown(sample_report, include_arabic=False)

        assert "الرسالة" not in md


# ═══════════════════════════════════════════════════════════════════════════
# Test Fixers
# ═══════════════════════════════════════════════════════════════════════════


class TestCodeFixer:
    """Tests for CodeFixer class."""

    @pytest.mark.asyncio
    async def test_apply_fix_to_missing_file(self, sample_fix: CodeFix):
        """Test applying fix to non-existent file."""
        fixer = CodeFixer(dry_run=True)
        result = await fixer.apply_fix_to_file(sample_fix, "/nonexistent.py")

        assert result.success is False
        assert "not found" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_dry_run_no_changes(self, sample_fix: CodeFix, temp_python_file: str):
        """Test dry run doesn't modify files."""
        # Read original content
        with open(temp_python_file, encoding="utf-8") as f:
            original = f.read()

        fixer = CodeFixer(dry_run=True)
        result = await fixer.apply_fix_to_file(sample_fix, temp_python_file)

        # Verify file unchanged
        with open(temp_python_file, encoding="utf-8") as f:
            after = f.read()

        assert original == after
        assert result.success is True

    @pytest.mark.asyncio
    async def test_rollback_unavailable(self):
        """Test rollback when not available."""
        fixer = CodeFixer()
        result = FixResult(
            fix_id="test",
            success=True,
            applied_at=datetime.utcnow(),
            file_path="/test.py",
            rollback_available=False,
        )

        success = await fixer.rollback_fix(result)
        assert success is False


# ═══════════════════════════════════════════════════════════════════════════
# Test Engine
# ═══════════════════════════════════════════════════════════════════════════


class TestAutoFixEngine:
    """Tests for AutoFixEngine class."""

    @pytest.mark.asyncio
    async def test_diagnose_logs_audit(self, temp_python_file: str):
        """Test that diagnose operation creates audit entries."""
        audit_entries: list[AuditEntry] = []
        engine = AutoFixEngine(
            dry_run=True,
            audit_callback=lambda e: audit_entries.append(e),
        )

        # Mock the diagnostics to avoid actual tool execution
        with patch.object(
            engine.diagnostics,
            "diagnose_file",
            new_callable=AsyncMock,
        ) as mock_diagnose:
            mock_diagnose.return_value = DiagnosticReport(
                id="test",
                target=temp_python_file,
                diagnostics=[],
            )

            await engine.diagnose(temp_python_file)

        # Check audit entries
        assert len(audit_entries) >= 2
        actions = [e.action for e in audit_entries]
        assert "diagnose_started" in actions
        assert "diagnose_completed" in actions

    @pytest.mark.asyncio
    async def test_generate_fix_plan(self, sample_report: DiagnosticReport):
        """Test fix plan generation."""
        engine = AutoFixEngine(dry_run=True)

        # Mock fix generation
        with patch.object(
            engine.fixer,
            "generate_fix",
            new_callable=AsyncMock,
        ) as mock_fix:
            mock_fix.return_value = CodeFix(
                id="fix-1",
                diagnostic_id=sample_report.diagnostics[0].id,
                description="Test fix",
                description_ar="إصلاح تجريبي",
                original_code="x",
                fixed_code="y",
                strategy=FixStrategy.SAFE,
                confidence=FixConfidence.HIGH,
                is_safe=True,
            )

            plan = await engine.generate_fix_plan(sample_report)

        assert plan.total_fixes == 1
        assert plan.strategy == FixStrategy.SAFE

    def test_get_audit_log(self):
        """Test audit log retrieval."""
        engine = AutoFixEngine(dry_run=True)

        # Manually add audit entries
        engine._log_audit(
            action="test_action_1",
            target="/test1.py",
            details={"key": "value"},
        )
        engine._log_audit(
            action="test_action_2",
            target="/test2.py",
            details={},
        )

        # Get all logs
        all_logs = engine.get_audit_log()
        assert len(all_logs) == 2

        # Filter by action
        filtered = engine.get_audit_log(action_filter="test_action_1")
        assert len(filtered) == 1
        assert filtered[0].action == "test_action_1"

    def test_export_audit_log_json(self):
        """Test JSON audit log export."""
        engine = AutoFixEngine(dry_run=True)

        engine._log_audit(
            action="test",
            target="/test.py",
            details={"foo": "bar"},
        )

        json_export = engine.export_audit_log(format="json")

        assert '"action": "test"' in json_export
        assert '"target": "/test.py"' in json_export

    def test_export_audit_log_markdown(self):
        """Test markdown audit log export."""
        engine = AutoFixEngine(dry_run=True)

        engine._log_audit(
            action="test_action",
            target="/test.py",
            details={},
        )

        md_export = engine.export_audit_log(format="markdown")

        assert "# Auto-Fix Audit Log" in md_export
        assert "سجل التدقيق" in md_export
        assert "test_action" in md_export

    def test_generate_report(
        self,
        sample_report: DiagnosticReport,
    ):
        """Test comprehensive report generation."""
        engine = AutoFixEngine(dry_run=True)

        results = [
            FixResult(
                fix_id="fix-1",
                success=True,
                applied_at=datetime.utcnow(),
                file_path="/test.py",
            ),
            FixResult(
                fix_id="fix-2",
                success=False,
                applied_at=datetime.utcnow(),
                file_path="/test2.py",
                error_message="Test error",
            ),
        ]

        report = engine.generate_report(sample_report, results)

        assert "# Auto-Fix Report" in report
        assert "تقرير الإصلاح التلقائي" in report
        assert "Fixes Applied" in report
        assert "✅ Success" in report
        assert "❌ Failed" in report

    @pytest.mark.asyncio
    async def test_get_available_tools(self):
        """Test tool availability checking."""
        engine = AutoFixEngine()

        # Mock tool checks
        with patch.object(
            engine.diagnostics,
            "check_tool_available",
            new_callable=AsyncMock,
        ) as mock_check:
            mock_check.side_effect = lambda tool: tool == ToolType.RUFF

            tools = await engine.get_available_tools()

        assert "ruff" in tools
        assert tools["ruff"] is True


# ═══════════════════════════════════════════════════════════════════════════
# Test Quick Functions
# ═══════════════════════════════════════════════════════════════════════════


class TestQuickFunctions:
    """Tests for quick diagnostic/fix functions."""

    @pytest.mark.asyncio
    async def test_quick_diagnose(self, temp_python_file: str):
        """Test quick_diagnose function."""
        from shared.ai.auto_fix import quick_diagnose

        # Mock the engine's diagnose method
        with patch(
            "shared.ai.auto_fix.engine.AutoFixEngine.diagnose",
            new_callable=AsyncMock,
        ) as mock_diagnose:
            mock_diagnose.return_value = DiagnosticReport(
                id="test",
                target=temp_python_file,
                diagnostics=[],
            )

            report = await quick_diagnose(temp_python_file)

        assert report is not None

    @pytest.mark.asyncio
    async def test_quick_fix(self, temp_python_file: str):
        """Test quick_fix function."""
        from shared.ai.auto_fix import quick_fix

        # Mock the engine's diagnose_and_fix method
        with patch(
            "shared.ai.auto_fix.engine.AutoFixEngine.diagnose_and_fix",
            new_callable=AsyncMock,
        ) as mock_fix:
            mock_fix.return_value = (
                DiagnosticReport(id="test", target=temp_python_file, diagnostics=[]),
                [],
            )

            report, results = await quick_fix(temp_python_file)

        assert report is not None
        assert results is not None


# ═══════════════════════════════════════════════════════════════════════════
# Test Arabic Support
# ═══════════════════════════════════════════════════════════════════════════


class TestArabicSupport:
    """Tests for Arabic language support."""

    def test_diagnostic_arabic_message(self):
        """Test diagnostic with Arabic message."""
        diag = Diagnostic(
            id="test",
            message="Unused import",
            message_ar="استيراد غير مستخدم",
            severity=DiagnosticSeverity.WARNING,
            category=DiagnosticCategory.IMPORT,
            location=CodeLocation(file_path="/test.py", line_start=1),
        )

        assert diag.message_ar == "استيراد غير مستخدم"

        data = diag.to_dict()
        assert data["message_ar"] == "استيراد غير مستخدم"

    def test_fix_plan_arabic_impact(self):
        """Test FixPlan with Arabic impact description."""
        plan = FixPlan(
            id="test",
            diagnostic_report_id="report",
            fixes=[],
            strategy=FixStrategy.SAFE,
            estimated_impact="Will fix 5 issues",
            estimated_impact_ar="سيتم إصلاح 5 مشاكل",
        )

        assert plan.estimated_impact_ar == "سيتم إصلاح 5 مشاكل"

        data = plan.to_dict()
        assert data["estimated_impact_ar"] == "سيتم إصلاح 5 مشاكل"


# ═══════════════════════════════════════════════════════════════════════════
# Test Integration
# ═══════════════════════════════════════════════════════════════════════════


class TestIntegration:
    """Integration tests for the full auto-fix workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_dry_run(self, temp_python_file: str):
        """Test complete diagnose -> plan -> fix workflow in dry-run mode."""
        engine = AutoFixEngine(dry_run=True)

        # Read original content
        with open(temp_python_file, encoding="utf-8") as f:
            original_content = f.read()

        # Mock diagnose to return a report
        with patch.object(
            engine.diagnostics,
            "diagnose_file",
            new_callable=AsyncMock,
        ) as mock_diagnose:
            mock_report = DiagnosticReport(
                id="report-1",
                target=temp_python_file,
                diagnostics=[
                    Diagnostic(
                        id="diag-1",
                        message="Unused import 'sys'",
                        message_ar="استيراد غير مستخدم 'sys'",
                        severity=DiagnosticSeverity.WARNING,
                        category=DiagnosticCategory.IMPORT,
                        location=CodeLocation(
                            file_path=temp_python_file,
                            line_start=2,
                        ),
                        rule_id="F401",
                        tool=ToolType.RUFF,
                    ),
                ],
                tools_used=[ToolType.RUFF],
            )
            mock_diagnose.return_value = mock_report

            # Step 1: Diagnose
            report = await engine.diagnose(temp_python_file)

        assert len(report.diagnostics) == 1

        # Step 2: Generate fix plan
        with patch.object(
            engine.fixer,
            "generate_fix",
            new_callable=AsyncMock,
        ) as mock_fix:
            mock_fix.return_value = CodeFix(
                id="fix-1",
                diagnostic_id="diag-1",
                description="Remove unused import",
                description_ar="إزالة الاستيراد غير المستخدم",
                original_code="import sys  # unused\n",
                fixed_code="",
                strategy=FixStrategy.SAFE,
                confidence=FixConfidence.HIGH,
                is_safe=True,
            )

            plan = await engine.generate_fix_plan(report)

        assert plan.total_fixes == 1

        # Step 3: Apply fixes (dry run)
        results = await engine.apply_fix_plan(plan, report)
        assert results is not None  # Verify apply returns results

        # Verify file unchanged (dry run)
        with open(temp_python_file, encoding="utf-8") as f:
            after_content = f.read()

        assert original_content == after_content

        # Verify audit trail
        audit_log = engine.get_audit_log()
        assert len(audit_log) >= 4  # diagnose start/end + plan start/end + apply start/end


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
