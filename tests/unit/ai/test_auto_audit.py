"""
Tests for Auto Audit Module
============================
اختبارات وحدة التدقيق التلقائي

Comprehensive tests for audit logging, reporting, and tracking.

Author: SAHOOL Platform Team
Created: January 2026
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from shared.ai.auto_fix.auto_audit import (
    AuditAction,
    AuditLogEntry,
    AuditSeverity,
    AuditSummary,
    AutoAudit,
    create_audit,
)

# ═══════════════════════════════════════════════════════════════════════════
# Test AuditLogEntry
# ═══════════════════════════════════════════════════════════════════════════


class TestAuditLogEntry:
    """Tests for AuditLogEntry dataclass."""

    def test_create_entry(self):
        """Test creating an audit log entry."""
        entry = AuditLogEntry(
            id="test-123",
            timestamp=datetime.now(),
            action=AuditAction.DIAGNOSE,
            severity=AuditSeverity.INFO,
            description="Diagnosed 5 files",
            description_ar="تم تشخيص 5 ملفات",
            user_id="system",
            tenant_id="sahool",
        )

        assert entry.id == "test-123"
        assert entry.action == AuditAction.DIAGNOSE
        assert entry.severity == AuditSeverity.INFO
        assert entry.description_ar == "تم تشخيص 5 ملفات"

    def test_entry_to_dict(self):
        """Test converting entry to dictionary."""
        entry = AuditLogEntry(
            id="test-456",
            timestamp=datetime(2026, 1, 21, 10, 30, 0),
            action=AuditAction.FIX_APPLY,
            severity=AuditSeverity.WARNING,
            description="Applied fix",
            description_ar="تم تطبيق الإصلاح",
            component="fixer",
            file_path="/test.py",
            metadata={"fix_type": "ruff"},
        )

        data = entry.to_dict()

        assert data["id"] == "test-456"
        assert data["action"] == "fix_apply"
        assert data["severity"] == "warning"
        assert data["component"] == "fixer"
        assert data["file_path"] == "/test.py"
        assert data["metadata"]["fix_type"] == "ruff"

    def test_entry_to_json(self):
        """Test converting entry to JSON."""
        entry = AuditLogEntry(
            id="test-json",
            timestamp=datetime(2026, 1, 21, 10, 30, 0),
            action=AuditAction.HEALTH_CHECK,
            severity=AuditSeverity.INFO,
            description="Health check passed",
            description_ar="فحص الصحة ناجح",
        )

        json_str = entry.to_json()
        parsed = json.loads(json_str)

        assert parsed["id"] == "test-json"
        assert parsed["action"] == "health_check"
        assert "فحص الصحة ناجح" in json_str


# ═══════════════════════════════════════════════════════════════════════════
# Test AuditSummary
# ═══════════════════════════════════════════════════════════════════════════


class TestAuditSummary:
    """Tests for AuditSummary dataclass."""

    def test_summary_defaults(self):
        """Test summary with default values."""
        summary = AuditSummary()

        assert summary.total_entries == 0
        assert summary.files_modified == 0
        assert summary.fixes_applied == 0
        assert summary.errors_encountered == 0

    def test_summary_duration(self):
        """Test summary duration calculation."""
        summary = AuditSummary(
            start_time=datetime(2026, 1, 21, 10, 0, 0),
            end_time=datetime(2026, 1, 21, 10, 0, 30),
        )

        assert summary.duration_seconds == 30.0

    def test_summary_to_dict(self):
        """Test summary to dictionary conversion."""
        summary = AuditSummary(
            total_entries=10,
            by_action={"diagnose": 5, "fix_apply": 5},
            by_severity={"info": 8, "warning": 2},
            files_modified=3,
            fixes_applied=5,
            errors_encountered=0,
            start_time=datetime(2026, 1, 21, 10, 0, 0),
            end_time=datetime(2026, 1, 21, 10, 1, 0),
        )

        data = summary.to_dict()

        assert data["total_entries"] == 10
        assert data["files_modified"] == 3
        assert data["fixes_applied"] == 5
        assert data["duration_seconds"] == 60.0
        assert "إجمالي: 10" in data["summary_ar"]


# ═══════════════════════════════════════════════════════════════════════════
# Test AutoAudit
# ═══════════════════════════════════════════════════════════════════════════


class TestAutoAudit:
    """Tests for AutoAudit class."""

    @pytest.fixture
    def temp_audit_dir(self):
        """Create a temporary directory for audit logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_create_audit_instance(self, temp_audit_dir):
        """Test creating an audit instance."""
        audit = AutoAudit(
            audit_dir=temp_audit_dir,
            enabled=True,
            tenant_id="test-tenant",
        )

        assert audit.enabled is True
        assert audit.tenant_id == "test-tenant"
        assert Path(temp_audit_dir).exists()

    def test_log_basic_entry(self, temp_audit_dir):
        """Test logging a basic audit entry."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        entry = audit.log(
            action=AuditAction.DIAGNOSE,
            description="Test diagnosis",
            description_ar="تشخيص تجريبي",
            severity=AuditSeverity.INFO,
        )

        assert entry.action == AuditAction.DIAGNOSE
        assert entry.description == "Test diagnosis"
        assert entry.description_ar == "تشخيص تجريبي"
        assert len(audit._entries) == 1

    def test_log_diagnose(self, temp_audit_dir):
        """Test logging diagnostic operation."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        entry = audit.log_diagnose(
            paths=["apps/", "shared/"],
            tools=["ruff", "mypy"],
            total_issues=15,
            fixable_issues=10,
        )

        assert entry.action == AuditAction.DIAGNOSE
        assert "15" in entry.description
        assert entry.metadata["total_issues"] == 15
        assert entry.metadata["fixable_issues"] == 10

    def test_log_fix(self, temp_audit_dir):
        """Test logging fix operation."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        entry = audit.log_fix(
            file_path="/test.py",
            fix_type="ruff",
            old_content="x= 1",
            new_content="x = 1",
            success=True,
        )

        assert entry.action == AuditAction.FIX_APPLY
        assert entry.file_path == "/test.py"
        assert entry.severity == AuditSeverity.INFO
        assert entry.metadata["success"] is True

    def test_log_fix_failure(self, temp_audit_dir):
        """Test logging failed fix operation."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        entry = audit.log_fix(
            file_path="/test.py",
            fix_type="ruff",
            success=False,
        )

        assert entry.severity == AuditSeverity.ERROR
        assert entry.metadata["success"] is False

    def test_log_health_check(self, temp_audit_dir):
        """Test logging health check."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        entry = audit.log_health_check(
            component="postgresql",
            status="healthy",
            latency_ms=15.5,
            details={"version": "16.0"},
        )

        assert entry.action == AuditAction.HEALTH_CHECK
        assert entry.component == "postgresql"
        assert entry.metadata["latency_ms"] == 15.5

    def test_log_security_scan(self, temp_audit_dir):
        """Test logging security scan."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        entry = audit.log_security_scan(
            paths=["apps/"],
            vulnerabilities_found=5,
            high_severity=1,
            medium_severity=2,
            low_severity=2,
        )

        assert entry.action == AuditAction.SECURITY_SCAN
        assert entry.severity == AuditSeverity.CRITICAL
        assert entry.metadata["high"] == 1

    def test_log_file_change(self, temp_audit_dir):
        """Test logging file changes."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        entry = audit.log_file_change(
            file_path="/test.py",
            action=AuditAction.FILE_MODIFIED,
            old_content="old",
            new_content="new",
        )

        assert entry.action == AuditAction.FILE_MODIFIED
        assert "Modified" in entry.description
        assert "تم تعديل" in entry.description_ar

    def test_get_entries_filtered(self, temp_audit_dir):
        """Test filtering audit entries."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        # Log various entries
        audit.log(
            action=AuditAction.DIAGNOSE,
            description="Diagnose 1",
            description_ar="تشخيص 1",
            severity=AuditSeverity.INFO,
        )
        audit.log(
            action=AuditAction.FIX_APPLY,
            description="Fix 1",
            description_ar="إصلاح 1",
            severity=AuditSeverity.WARNING,
        )
        audit.log(
            action=AuditAction.DIAGNOSE,
            description="Diagnose 2",
            description_ar="تشخيص 2",
            severity=AuditSeverity.INFO,
        )

        # Filter by action
        diagnose_entries = audit.get_entries(action=AuditAction.DIAGNOSE)
        assert len(diagnose_entries) == 2

        # Filter by severity
        warning_entries = audit.get_entries(severity=AuditSeverity.WARNING)
        assert len(warning_entries) == 1

    def test_get_summary(self, temp_audit_dir):
        """Test getting audit summary."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        # Log some entries
        audit.log_diagnose(["apps/"], ["ruff"], 5, 3)
        audit.log_fix("/test.py", "ruff", success=True)
        audit.log_fix("/test2.py", "ruff", success=True)
        audit.log_file_change("/test.py", AuditAction.FILE_MODIFIED)

        summary = audit.get_summary()

        assert summary.total_entries == 4
        assert summary.fixes_applied == 2
        assert summary.files_modified == 1

    def test_export_report_json(self, temp_audit_dir):
        """Test exporting report as JSON."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        audit.log_diagnose(["apps/"], ["ruff"], 5, 3)

        output_path = Path(temp_audit_dir) / "report.json"
        result = audit.export_report(output_path, format="json")

        assert result.exists()

        with open(result, encoding="utf-8") as f:
            data = json.load(f)

        assert "session_id" in data
        assert "summary" in data
        assert "entries" in data

    def test_export_report_markdown(self, temp_audit_dir):
        """Test exporting report as Markdown."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        audit.log_diagnose(["apps/"], ["ruff"], 5, 3)
        audit.log_fix("/test.py", "ruff", success=True)

        output_path = Path(temp_audit_dir) / "report.md"
        result = audit.export_report(output_path, format="markdown")

        assert result.exists()

        with open(result, encoding="utf-8") as f:
            content = f.read()

        assert "# Audit Report" in content
        assert "تقرير التدقيق" in content

    def test_clear_entries(self, temp_audit_dir):
        """Test clearing audit entries."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=True)

        audit.log_diagnose(["apps/"], ["ruff"], 5, 3)
        audit.log_diagnose(["shared/"], ["mypy"], 3, 1)

        assert len(audit._entries) == 2

        audit.clear()

        assert len(audit._entries) == 0

    def test_disabled_audit(self, temp_audit_dir):
        """Test audit with disabled logging."""
        audit = AutoAudit(audit_dir=temp_audit_dir, enabled=False)

        entry = audit.log(
            action=AuditAction.DIAGNOSE,
            description="Test",
            description_ar="اختبار",
        )

        # Entry is still created but not persisted
        assert entry is not None
        assert len(audit._entries) == 1


# ═══════════════════════════════════════════════════════════════════════════
# Test Convenience Functions
# ═══════════════════════════════════════════════════════════════════════════


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_create_audit(self):
        """Test create_audit function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = create_audit(
                enabled=True,
                audit_dir=tmpdir,
                tenant_id="test",
            )

            assert audit.enabled is True
            assert audit.tenant_id == "test"


# ═══════════════════════════════════════════════════════════════════════════
# Test Action and Severity Enums
# ═══════════════════════════════════════════════════════════════════════════


class TestEnums:
    """Tests for AuditAction and AuditSeverity enums."""

    def test_audit_actions(self):
        """Test all audit action values."""
        assert AuditAction.DIAGNOSE.value == "diagnose"
        assert AuditAction.FIX_APPLY.value == "fix_apply"
        assert AuditAction.FIX_ROLLBACK.value == "fix_rollback"
        assert AuditAction.CONFIG_CHANGE.value == "config_change"
        assert AuditAction.FILE_MODIFIED.value == "file_modified"
        assert AuditAction.FILE_CREATED.value == "file_created"
        assert AuditAction.FILE_DELETED.value == "file_deleted"
        assert AuditAction.HEALTH_CHECK.value == "health_check"
        assert AuditAction.DEPENDENCY_UPDATE.value == "dependency_update"
        assert AuditAction.SECURITY_SCAN.value == "security_scan"

    def test_audit_severities(self):
        """Test all audit severity values."""
        assert AuditSeverity.INFO.value == "info"
        assert AuditSeverity.WARNING.value == "warning"
        assert AuditSeverity.ERROR.value == "error"
        assert AuditSeverity.CRITICAL.value == "critical"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
