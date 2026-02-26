"""
Tests for SAHOOL Contract Validation Framework
=================================================
"""

import pytest

from shared.stability.contracts import (
    ContractValidator,
    ContractReport,
    ContractSeverity,
    ContractType,
)


class TestEventEnvelopeValidation:
    """Tests for event envelope contract validation."""

    def test_valid_event_envelope(self):
        event_data = {
            "event_id": "evt-123",
            "timestamp": "2026-01-20T10:00:00Z",
            "version": "1.0",
            "source_service": "field-management",
            "event_type": "field.created",
            "correlation_id": "corr-456",
            "causation_id": "cause-789",
            "tenant_id_header": "tenant-001",
            "trace_id": "abc123",
            "span_id": "def456",
        }
        validator = ContractValidator()
        report = validator.validate_event_envelope(event_data)

        assert report.checks_passed >= 5  # All required fields
        assert not report.has_breaking

    def test_missing_required_fields(self):
        event_data = {
            "event_id": "evt-123",
            # Missing: timestamp, version, source_service, event_type
        }
        validator = ContractValidator()
        report = validator.validate_event_envelope(event_data)

        assert report.has_breaking
        assert report.breaking_count >= 3  # Missing 4 required fields

    def test_wrong_type_field(self):
        event_data = {
            "event_id": 123,  # Should be str
            "timestamp": "2026-01-20T10:00:00Z",
            "version": "1.0",
            "source_service": "test",
            "event_type": "test.event",
        }
        validator = ContractValidator()
        report = validator.validate_event_envelope(event_data)

        type_violations = [
            v for v in report.violations
            if "type" in v.message.lower() and v.severity == ContractSeverity.BREAKING
        ]
        assert len(type_violations) > 0

    def test_missing_optional_fields_are_info(self):
        event_data = {
            "event_id": "evt-123",
            "timestamp": "2026-01-20T10:00:00Z",
            "version": "1.0",
            "source_service": "test",
            "event_type": "test.event",
            # No correlation_id, trace_id, etc.
        }
        validator = ContractValidator()
        report = validator.validate_event_envelope(event_data)

        info_violations = [v for v in report.violations if v.severity == ContractSeverity.INFO]
        assert len(info_violations) > 0  # Missing optional fields

    def test_empty_event_data(self):
        validator = ContractValidator()
        report = validator.validate_event_envelope({})

        assert report.has_breaking
        assert report.breaking_count == 5  # All 5 required fields missing


class TestMigrationBackwardCompat:
    """Tests for migration backward compatibility checking."""

    def test_safe_addition(self):
        """Adding new optional field is safe."""
        old_schema = {
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        }
        new_schema = {
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["name"],
        }
        validator = ContractValidator()
        report = validator.validate_migration_backward_compat(old_schema, new_schema)

        assert not report.has_breaking

    def test_removing_required_field_is_breaking(self):
        """Removing a required field is breaking."""
        old_schema = {
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["name", "email"],
        }
        new_schema = {
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        }
        validator = ContractValidator()
        report = validator.validate_migration_backward_compat(old_schema, new_schema)

        assert report.has_breaking
        breaking = [v for v in report.violations if v.severity == ContractSeverity.BREAKING]
        assert any("email" in v.location for v in breaking)

    def test_changing_type_is_breaking(self):
        """Changing a field type is breaking."""
        old_schema = {
            "properties": {
                "age": {"type": "integer"},
            },
        }
        new_schema = {
            "properties": {
                "age": {"type": "string"},
            },
        }
        validator = ContractValidator()
        report = validator.validate_migration_backward_compat(old_schema, new_schema)

        assert report.has_breaking
        type_violations = [v for v in report.violations if "type changed" in v.message.lower()]
        assert len(type_violations) > 0

    def test_new_required_without_default_is_breaking(self):
        """Adding new required field without default is breaking."""
        old_schema = {
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        }
        new_schema = {
            "properties": {
                "name": {"type": "string"},
                "status": {"type": "string"},
            },
            "required": ["name", "status"],
        }
        validator = ContractValidator()
        report = validator.validate_migration_backward_compat(old_schema, new_schema)

        assert report.has_breaking

    def test_new_required_with_default_is_ok(self):
        """Adding new required field with default is acceptable."""
        old_schema = {
            "properties": {
                "name": {"type": "string"},
            },
            "required": ["name"],
        }
        new_schema = {
            "properties": {
                "name": {"type": "string"},
                "status": {"type": "string", "default": "active"},
            },
            "required": ["name", "status"],
        }
        validator = ContractValidator()
        report = validator.validate_migration_backward_compat(old_schema, new_schema)

        assert not report.has_breaking


class TestContractReport:
    """Tests for ContractReport."""

    def test_clean_report(self):
        report = ContractReport(checks_run=5, checks_passed=5)
        assert report.is_clean
        assert not report.has_breaking

    def test_summary_format(self):
        report = ContractReport(checks_run=10, checks_passed=8)
        summary = report.summary()

        assert summary["checks_run"] == 10
        assert summary["checks_passed"] == 8
        assert isinstance(summary["violations"], list)
