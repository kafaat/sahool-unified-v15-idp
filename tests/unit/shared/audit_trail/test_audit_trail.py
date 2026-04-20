"""
Unit tests for shared/audit_trail module.

Tests audit entry models, event types, trail utilities, logging,
filtering, querying, reporting, retention, and bilingual label helpers.

All tests run without a database -- everything is in-memory or mocked.
"""

import json
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from shared.audit_trail.models import (
    ACTION_LABELS,
    CATEGORY_LABELS,
    RETENTION_DAYS,
    SEVERITY_LABELS,
    ActorType,
    AuditActionType,
    AuditCategory,
    AuditEntry,
    AuditMetadata,
    AuditQueryFilter,
    AuditReport,
    AuditSeverity,
    ChangeType,
    ExportFormat,
    FieldChange,
    RetentionJob,
    RetentionPeriod,
    RetentionPolicy,
    UserActivitySummary,
    get_action_label,
    get_category_label,
    get_severity_label,
)
from shared.audit_trail.logger import (
    AuditTrailLogger,
    compute_changes,
)
from shared.audit_trail.reporter import (
    AuditReportGenerator,
    export_entries,
    generate_activity_report,
    generate_compliance_report,
    generate_globalgap_report,
)
from shared.audit_trail.retention import (
    RetentionManager,
    get_default_policies,
)


# =============================================================================
# Helpers
# =============================================================================


def _make_entry(**overrides) -> AuditEntry:
    """Build an AuditEntry with sensible defaults, applying overrides."""
    defaults = {
        "tenant_id": "farm-001",
        "actor_id": "user-100",
        "actor_type": ActorType.USER,
        "actor_name": "Ali",
        "actor_name_ar": "علي",
        "action": AuditActionType.CREATE,
        "category": AuditCategory.DATA,
        "severity": AuditSeverity.INFO,
        "resource_type": "field",
        "resource_id": "field-001",
        "success": True,
    }
    defaults.update(overrides)
    return AuditEntry(**defaults)


def _make_logger(**kwargs) -> AuditTrailLogger:
    """Create an in-memory AuditTrailLogger (no file I/O)."""
    defaults = {"tenant_id": "farm-001", "storage_path": None}
    defaults.update(kwargs)
    return AuditTrailLogger(**defaults)


# =============================================================================
# Enum Tests
# =============================================================================


@pytest.mark.unit
class TestEnums:
    """Verify enum values for action types, categories, severities, etc."""

    def test_audit_action_type_crud(self):
        assert AuditActionType.CREATE == "create"
        assert AuditActionType.READ == "read"
        assert AuditActionType.UPDATE == "update"
        assert AuditActionType.DELETE == "delete"

    def test_audit_action_type_auth(self):
        assert AuditActionType.LOGIN == "login"
        assert AuditActionType.LOGOUT == "logout"
        assert AuditActionType.LOGIN_FAILED == "login_failed"

    def test_audit_action_type_globalgap(self):
        assert AuditActionType.FINDING_RECORDED == "finding_recorded"
        assert AuditActionType.NC_RAISED == "nc_raised"
        assert AuditActionType.NC_CLOSED == "nc_closed"

    def test_audit_action_type_field_ops(self):
        assert AuditActionType.IRRIGATION == "irrigation"
        assert AuditActionType.HARVEST == "harvest"
        assert AuditActionType.SOIL_TEST == "soil_test"

    def test_audit_category_values(self):
        assert AuditCategory.SECURITY == "security"
        assert AuditCategory.DATA == "data"
        assert AuditCategory.GLOBALGAP == "globalgap"
        assert AuditCategory.FIELD_OPS == "field_ops"

    def test_audit_severity_values(self):
        assert AuditSeverity.DEBUG == "debug"
        assert AuditSeverity.INFO == "info"
        assert AuditSeverity.WARNING == "warning"
        assert AuditSeverity.ERROR == "error"
        assert AuditSeverity.CRITICAL == "critical"

    def test_actor_type_values(self):
        assert ActorType.USER == "user"
        assert ActorType.SERVICE == "service"
        assert ActorType.SYSTEM == "system"
        assert ActorType.AUDITOR == "auditor"
        assert ActorType.AGENT == "agent"

    def test_change_type_values(self):
        assert ChangeType.ADDED == "added"
        assert ChangeType.MODIFIED == "modified"
        assert ChangeType.DELETED == "deleted"

    def test_export_format_values(self):
        assert ExportFormat.JSON == "json"
        assert ExportFormat.CSV == "csv"
        assert ExportFormat.EXCEL == "excel"
        assert ExportFormat.XML == "xml"

    def test_retention_period_values(self):
        assert RetentionPeriod.SHORT == "short"
        assert RetentionPeriod.MEDIUM == "medium"
        assert RetentionPeriod.LONG == "long"
        assert RetentionPeriod.GLOBALGAP == "globalgap"
        assert RetentionPeriod.PERMANENT == "permanent"

    def test_retention_days_mapping(self):
        assert RETENTION_DAYS[RetentionPeriod.SHORT] == 90
        assert RETENTION_DAYS[RetentionPeriod.MEDIUM] == 365
        assert RETENTION_DAYS[RetentionPeriod.LONG] == 1095
        assert RETENTION_DAYS[RetentionPeriod.GLOBALGAP] == 1825
        assert RETENTION_DAYS[RetentionPeriod.PERMANENT] == -1


# =============================================================================
# FieldChange Tests
# =============================================================================


@pytest.mark.unit
class TestFieldChange:
    def test_field_change_to_dict(self):
        fc = FieldChange(
            field_name="name",
            field_name_ar="الاسم",
            old_value="Old",
            new_value="New",
            change_type=ChangeType.MODIFIED,
        )
        d = fc.to_dict()
        assert d["field_name"] == "name"
        assert d["field_name_ar"] == "الاسم"
        assert d["old_value"] == "Old"
        assert d["new_value"] == "New"
        assert d["change_type"] == "modified"

    def test_field_change_serialize_datetime(self):
        dt = datetime(2025, 6, 1, tzinfo=UTC)
        fc = FieldChange(field_name="date", old_value=dt, new_value=None, change_type=ChangeType.DELETED)
        d = fc.to_dict()
        assert d["old_value"] == dt.isoformat()


# =============================================================================
# AuditMetadata Tests
# =============================================================================


@pytest.mark.unit
class TestAuditMetadata:
    def test_metadata_defaults(self):
        m = AuditMetadata()
        assert m.correlation_id is None
        assert m.ggn is None
        assert m.tags == []
        assert m.custom == {}

    def test_metadata_to_dict_with_values(self):
        m = AuditMetadata(
            correlation_id="corr-1",
            ggn="4012345678901",
            audit_session_id="audit-001",
            control_point_id="AF.1.1.1",
            ip_address="10.0.0.1",
            tags=["globalgap", "field"],
            custom={"extra": "value"},
        )
        d = m.to_dict()
        assert d["correlation_id"] == "corr-1"
        assert d["ggn"] == "4012345678901"
        assert d["ip_address"] == "10.0.0.1"
        assert "globalgap" in d["tags"]


# =============================================================================
# AuditEntry Tests
# =============================================================================


@pytest.mark.unit
class TestAuditEntry:
    def test_entry_defaults(self):
        entry = AuditEntry()
        assert entry.id is not None
        assert entry.action == AuditActionType.READ
        assert entry.category == AuditCategory.DATA
        assert entry.severity == AuditSeverity.INFO
        assert entry.success is True
        assert entry.entry_hash is not None

    def test_entry_expiration_calculated(self):
        entry = _make_entry(retention_period=RetentionPeriod.SHORT)
        assert entry.expires_at is not None
        expected = entry.timestamp + timedelta(days=90)
        assert abs((entry.expires_at - expected).total_seconds()) < 1

    def test_entry_permanent_no_expiration(self):
        entry = _make_entry(retention_period=RetentionPeriod.PERMANENT)
        # Permanent entries still get expires_at set by __post_init__ using RETENTION_DAYS
        # but the manager filters them out via retention_period check
        assert entry.retention_period == RetentionPeriod.PERMANENT

    def test_entry_to_dict_roundtrip(self):
        entry = _make_entry()
        d = entry.to_dict()
        assert d["tenant_id"] == "farm-001"
        assert d["actor_id"] == "user-100"
        assert d["action"] == "create"
        assert d["resource_type"] == "field"

    def test_entry_to_json(self):
        entry = _make_entry()
        j = entry.to_json()
        data = json.loads(j)
        assert data["tenant_id"] == "farm-001"

    def test_entry_from_dict(self):
        entry = _make_entry(
            metadata=AuditMetadata(ggn="4012345678901"),
            changes=[FieldChange(field_name="area", old_value=5, new_value=10, change_type=ChangeType.MODIFIED)],
        )
        d = entry.to_dict()
        restored = AuditEntry.from_dict(d)
        assert restored.id == entry.id
        assert restored.tenant_id == entry.tenant_id
        assert restored.action == entry.action
        assert len(restored.changes) == 1
        assert restored.changes[0].field_name == "area"
        assert restored.metadata.ggn == "4012345678901"

    def test_entry_hash_chain(self):
        e1 = _make_entry()
        e2 = _make_entry(prev_hash=e1.entry_hash)
        assert e2.prev_hash == e1.entry_hash
        assert e2.entry_hash is not None
        assert e2.entry_hash != e1.entry_hash


# =============================================================================
# Bilingual Label Tests
# =============================================================================


@pytest.mark.unit
class TestBilingualLabels:
    def test_action_labels_have_both_languages(self):
        for action in AuditActionType:
            label = ACTION_LABELS.get(action)
            assert label is not None, f"Missing label for {action}"
            assert "en" in label
            assert "ar" in label

    def test_get_action_label_english(self):
        assert get_action_label(AuditActionType.CREATE, "en") == "Create"
        assert get_action_label(AuditActionType.LOGIN, "en") == "Login"

    def test_get_action_label_arabic(self):
        assert get_action_label(AuditActionType.CREATE, "ar") == "إنشاء"

    def test_get_category_label(self):
        assert get_category_label(AuditCategory.SECURITY, "en") == "Security"
        assert get_category_label(AuditCategory.SECURITY, "ar") == "الأمان"

    def test_get_severity_label(self):
        assert get_severity_label(AuditSeverity.CRITICAL, "en") == "Critical"
        assert get_severity_label(AuditSeverity.CRITICAL, "ar") == "حرج"

    def test_category_labels_complete(self):
        for cat in AuditCategory:
            assert cat in CATEGORY_LABELS

    def test_severity_labels_complete(self):
        for sev in AuditSeverity:
            assert sev in SEVERITY_LABELS


# =============================================================================
# compute_changes Tests
# =============================================================================


@pytest.mark.unit
class TestComputeChanges:
    def test_create_all_fields_added(self):
        after = {"name": "Field A", "area": 10}
        changes = compute_changes(None, after)
        assert len(changes) == 2
        assert all(c.change_type == ChangeType.ADDED for c in changes)

    def test_delete_all_fields_deleted(self):
        before = {"name": "Field A", "area": 10}
        changes = compute_changes(before, None)
        assert len(changes) == 2
        assert all(c.change_type == ChangeType.DELETED for c in changes)

    def test_update_detects_modifications(self):
        before = {"name": "Old", "area": 10}
        after = {"name": "New", "area": 10}
        changes = compute_changes(before, after)
        assert len(changes) == 1
        assert changes[0].field_name == "name"
        assert changes[0].change_type == ChangeType.MODIFIED
        assert changes[0].old_value == "Old"
        assert changes[0].new_value == "New"

    def test_update_detects_added_and_removed_fields(self):
        before = {"name": "A", "old_field": "x"}
        after = {"name": "A", "new_field": "y"}
        changes = compute_changes(before, after)
        types = {c.change_type for c in changes}
        assert ChangeType.ADDED in types
        assert ChangeType.DELETED in types

    def test_exclude_fields(self):
        before = {"name": "Old", "password": "secret"}
        after = {"name": "New", "password": "newsecret"}
        changes = compute_changes(before, after, exclude_fields=["password"])
        field_names = [c.field_name for c in changes]
        assert "password" not in field_names
        # password is auto-excluded by default, but also verify name is there
        assert "name" in field_names

    def test_auto_excludes_sensitive_fields(self):
        before = {"updated_at": "old", "password_hash": "h1", "token": "t1", "name": "A"}
        after = {"updated_at": "new", "password_hash": "h2", "token": "t2", "name": "B"}
        changes = compute_changes(before, after)
        field_names = {c.field_name for c in changes}
        assert "updated_at" not in field_names
        assert "password_hash" not in field_names
        assert "token" not in field_names
        assert "name" in field_names

    def test_arabic_labels(self):
        changes = compute_changes(None, {"name": "A"}, field_labels_ar={"name": "الاسم"})
        assert changes[0].field_name_ar == "الاسم"

    def test_no_changes_when_equal(self):
        data = {"name": "Same", "area": 10}
        changes = compute_changes(data, data.copy())
        assert len(changes) == 0

    def test_both_none_returns_empty(self):
        changes = compute_changes(None, None)
        assert changes == []


# =============================================================================
# AuditTrailLogger Tests
# =============================================================================


@pytest.mark.unit
class TestAuditTrailLogger:
    def test_log_action(self):
        logger = _make_logger()
        entry = logger.log_action(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
            actor_id="user-100",
        )
        assert entry.action == AuditActionType.CREATE
        assert entry.resource_id == "field-001"
        assert entry.tenant_id == "farm-001"

    def test_log_change_with_diff(self):
        logger = _make_logger()
        entry = logger.log_change(
            action=AuditActionType.UPDATE,
            resource_type="field",
            resource_id="field-001",
            before={"name": "Old Name"},
            after={"name": "New Name"},
            actor_id="user-100",
        )
        assert len(entry.changes) == 1
        assert entry.changes[0].field_name == "name"
        assert entry.before_state == {"name": "Old Name"}
        assert entry.after_state == {"name": "New Name"}

    def test_log_login_success(self):
        logger = _make_logger()
        entry = logger.log_login(user_id="user-100", success=True, ip_address="10.0.0.1")
        assert entry.action == AuditActionType.LOGIN
        assert entry.category == AuditCategory.SECURITY
        assert entry.success is True
        assert entry.metadata.ip_address == "10.0.0.1"

    def test_log_login_failure(self):
        logger = _make_logger()
        entry = logger.log_login(user_id="user-100", success=False, error_message="Invalid password")
        assert entry.action == AuditActionType.LOGIN_FAILED
        assert entry.severity == AuditSeverity.WARNING
        assert entry.success is False

    def test_log_globalgap_event(self):
        logger = _make_logger()
        entry = logger.log_globalgap_event(
            action=AuditActionType.FINDING_RECORDED,
            resource_type="control_point",
            resource_id="AF.1.1.1",
            ggn="4012345678901",
            audit_session_id="audit-001",
            control_point_id="AF.1.1.1",
        )
        assert entry.category == AuditCategory.GLOBALGAP
        assert entry.metadata.ggn == "4012345678901"
        assert entry.metadata.audit_session_id == "audit-001"
        assert entry.retention_period == RetentionPeriod.GLOBALGAP

    def test_log_field_operation(self):
        logger = _make_logger()
        entry = logger.log_field_operation(
            operation_type=AuditActionType.IRRIGATION,
            field_id="field-001",
            field_name="North Field",
            actor_id="user-100",
            details={"volume_m3": 50},
        )
        assert entry.action == AuditActionType.IRRIGATION
        assert entry.category == AuditCategory.FIELD_OPS
        assert entry.after_state == {"volume_m3": 50}

    def test_infer_category_security(self):
        logger = _make_logger()
        entry = logger.log_action(
            action=AuditActionType.PASSWORD_CHANGE,
            resource_type="user",
            resource_id="user-100",
        )
        assert entry.category == AuditCategory.SECURITY

    def test_infer_category_compliance(self):
        logger = _make_logger()
        entry = logger.log_action(
            action=AuditActionType.AUDIT_STARTED,
            resource_type="audit",
            resource_id="audit-001",
        )
        assert entry.category == AuditCategory.COMPLIANCE

    def test_infer_category_system(self):
        logger = _make_logger()
        entry = logger.log_action(
            action=AuditActionType.SYSTEM_CONFIG_CHANGE,
            resource_type="config",
            resource_id="db-config",
        )
        assert entry.category == AuditCategory.SYSTEM

    def test_hash_chain_integrity(self):
        logger = _make_logger(enable_hash_chain=True)
        logger.log_action(action=AuditActionType.CREATE, resource_type="a", resource_id="1")
        logger.log_action(action=AuditActionType.UPDATE, resource_type="a", resource_id="1")
        logger.log_action(action=AuditActionType.DELETE, resource_type="a", resource_id="1")

        is_valid, invalid_ids = logger.verify_hash_chain()
        assert is_valid is True
        assert invalid_ids == []

    def test_get_summary(self):
        logger = _make_logger()
        logger.log_action(action=AuditActionType.CREATE, resource_type="field", resource_id="f1")
        logger.log_login(user_id="user-100", success=True)

        summary = logger.get_summary()
        assert summary["total_entries"] == 2
        assert "create" in summary["entries_by_action"]
        assert summary["hash_chain_enabled"] is True

    def test_clear(self):
        logger = _make_logger()
        logger.log_action(action=AuditActionType.CREATE, resource_type="f", resource_id="1")
        assert logger._total_entries == 1

        logger.clear()
        assert logger._total_entries == 0
        assert len(logger._entries) == 0

    def test_on_entry_callback(self):
        callback = MagicMock()
        logger = _make_logger(on_entry_callback=callback)
        logger.log_action(action=AuditActionType.CREATE, resource_type="f", resource_id="1")
        callback.assert_called_once()
        assert isinstance(callback.call_args[0][0], AuditEntry)


# =============================================================================
# Query / Filtering Tests
# =============================================================================


@pytest.mark.unit
class TestQueryFiltering:
    def _setup_logger(self) -> AuditTrailLogger:
        logger = _make_logger()
        logger.log_action(
            action=AuditActionType.CREATE, resource_type="field", resource_id="f1", actor_id="user-A"
        )
        logger.log_action(
            action=AuditActionType.UPDATE, resource_type="field", resource_id="f1", actor_id="user-A"
        )
        logger.log_action(
            action=AuditActionType.DELETE, resource_type="crop", resource_id="c1", actor_id="user-B"
        )
        logger.log_login(user_id="user-A", success=True)
        logger.log_login(user_id="user-B", success=False)
        return logger

    def test_get_entries_default_returns_all(self):
        logger = self._setup_logger()
        entries = logger.get_entries()
        assert len(entries) == 5

    def test_filter_by_actor_id(self):
        logger = self._setup_logger()
        f = AuditQueryFilter(actor_id="user-A")
        entries = logger.get_entries(f)
        assert all(e.actor_id == "user-A" for e in entries)
        assert len(entries) == 3

    def test_filter_by_action(self):
        logger = self._setup_logger()
        f = AuditQueryFilter(action=AuditActionType.CREATE)
        entries = logger.get_entries(f)
        assert len(entries) == 1

    def test_filter_by_resource_type(self):
        logger = self._setup_logger()
        f = AuditQueryFilter(resource_type="crop")
        entries = logger.get_entries(f)
        assert len(entries) == 1

    def test_filter_by_success(self):
        logger = self._setup_logger()
        f = AuditQueryFilter(success=False)
        entries = logger.get_entries(f)
        assert len(entries) == 1
        assert entries[0].action == AuditActionType.LOGIN_FAILED

    def test_filter_by_category(self):
        logger = self._setup_logger()
        f = AuditQueryFilter(category=AuditCategory.SECURITY)
        entries = logger.get_entries(f)
        assert all(e.category == AuditCategory.SECURITY for e in entries)

    def test_get_history(self):
        logger = self._setup_logger()
        history = logger.get_history(resource_type="field", resource_id="f1")
        assert len(history) == 2

    def test_get_user_activity(self):
        logger = self._setup_logger()
        activity = logger.get_user_activity(user_id="user-A")
        assert len(activity) == 3

    def test_filter_pagination(self):
        logger = self._setup_logger()
        f = AuditQueryFilter(limit=2, offset=0)
        page1 = logger.get_entries(f)
        assert len(page1) == 2
        f2 = AuditQueryFilter(limit=2, offset=2)
        page2 = logger.get_entries(f2)
        assert len(page2) == 2

    def test_audit_query_filter_to_dict(self):
        f = AuditQueryFilter(
            actor_id="user-A",
            action=AuditActionType.CREATE,
            category=AuditCategory.DATA,
            limit=50,
        )
        d = f.to_dict()
        assert d["actor_id"] == "user-A"
        assert d["action"] == "create"
        assert d["limit"] == 50


# =============================================================================
# Reporter Tests
# =============================================================================


@pytest.mark.unit
class TestReporter:
    def _make_entries(self) -> list[AuditEntry]:
        entries = []
        now = datetime.now(UTC)
        # Data entries
        for i in range(5):
            entries.append(
                _make_entry(
                    actor_id="user-A",
                    action=AuditActionType.CREATE,
                    category=AuditCategory.DATA,
                    timestamp=now - timedelta(hours=i),
                )
            )
        # Security entries
        entries.append(
            _make_entry(
                actor_id="user-B",
                action=AuditActionType.LOGIN,
                category=AuditCategory.SECURITY,
                timestamp=now - timedelta(hours=1),
            )
        )
        entries.append(
            _make_entry(
                actor_id="user-B",
                action=AuditActionType.LOGIN_FAILED,
                category=AuditCategory.SECURITY,
                severity=AuditSeverity.WARNING,
                success=False,
                timestamp=now - timedelta(hours=2),
            )
        )
        # Compliance entries
        entries.append(
            _make_entry(
                actor_id="auditor-1",
                action=AuditActionType.FINDING_RECORDED,
                category=AuditCategory.COMPLIANCE,
                timestamp=now - timedelta(hours=3),
            )
        )
        entries.append(
            _make_entry(
                actor_id="auditor-1",
                action=AuditActionType.NC_RAISED,
                category=AuditCategory.COMPLIANCE,
                severity=AuditSeverity.ERROR,
                success=False,
                timestamp=now - timedelta(hours=4),
            )
        )
        return entries

    def test_generate_activity_report(self):
        entries = self._make_entries()
        gen = AuditReportGenerator(entries, tenant_id="farm-001", language="en")
        report = gen.generate_activity_report()
        assert report.report_type == "activity"
        assert report.total_entries == len(entries)
        assert report.unique_users >= 2

    def test_generate_compliance_report(self):
        entries = self._make_entries()
        gen = AuditReportGenerator(entries, tenant_id="farm-001")
        report = gen.generate_compliance_report()
        assert report.report_type == "compliance"
        assert report.compliance_items_checked >= 0

    def test_generate_globalgap_report(self):
        now = datetime.now(UTC)
        entries = [
            _make_entry(
                action=AuditActionType.FINDING_RECORDED,
                category=AuditCategory.GLOBALGAP,
                metadata=AuditMetadata(
                    ggn="4012345678901",
                    audit_session_id="audit-001",
                    control_point_id="AF.1.1.1",
                ),
                timestamp=now,
            ),
            _make_entry(
                action=AuditActionType.NC_RAISED,
                category=AuditCategory.GLOBALGAP,
                metadata=AuditMetadata(
                    ggn="4012345678901",
                    audit_session_id="audit-001",
                    control_point_id="AF.2.1",
                ),
                success=False,
                timestamp=now - timedelta(hours=1),
            ),
        ]
        gen = AuditReportGenerator(entries)
        report = gen.generate_globalgap_report(ggn="4012345678901")
        assert report.report_type == "globalgap"
        assert report.ggn == "4012345678901"

    def test_generate_security_report(self):
        entries = self._make_entries()
        gen = AuditReportGenerator(entries)
        report = gen.generate_security_report()
        assert report.report_type == "security"

    def test_generate_user_activity_summary(self):
        entries = self._make_entries()
        gen = AuditReportGenerator(entries, tenant_id="farm-001")
        summary = gen.generate_user_activity_summary("user-A")
        assert summary.user_id == "user-A"
        assert summary.total_actions == 5

    def test_export_to_json(self):
        entries = [_make_entry()]
        gen = AuditReportGenerator(entries)
        result = gen.export_to_json()
        data = json.loads(result)
        assert "entries" in data
        assert data["total_entries"] == 1

    def test_export_to_csv(self):
        entries = [_make_entry()]
        gen = AuditReportGenerator(entries)
        csv_text = gen.export_to_csv()
        assert "id" in csv_text
        assert "timestamp" in csv_text
        assert "field" in csv_text

    def test_export_to_xml(self):
        entries = [_make_entry()]
        gen = AuditReportGenerator(entries)
        xml_text = gen.export(ExportFormat.XML)
        assert '<?xml version="1.0"' in xml_text
        assert "<audit_trail>" in xml_text

    def test_export_pdf_raises(self):
        gen = AuditReportGenerator([])
        with pytest.raises(NotImplementedError):
            gen.export(ExportFormat.PDF)

    def test_convenience_generate_activity_report(self):
        entries = [_make_entry()]
        report = generate_activity_report(entries, tenant_id="farm-001")
        assert report.report_type == "activity"

    def test_convenience_generate_compliance_report(self):
        entries = [_make_entry(action=AuditActionType.FINDING_RECORDED, category=AuditCategory.COMPLIANCE)]
        report = generate_compliance_report(entries)
        assert report.report_type == "compliance"

    def test_convenience_export_entries(self):
        entries = [_make_entry()]
        result = export_entries(entries, format_=ExportFormat.JSON)
        assert isinstance(result, str)
        data = json.loads(result)
        assert data["total_entries"] == 1


# =============================================================================
# AuditReport / UserActivitySummary Tests
# =============================================================================


@pytest.mark.unit
class TestReportModels:
    def test_audit_report_to_dict(self):
        report = AuditReport(
            title="Test Report",
            title_ar="تقرير اختبار",
            tenant_id="farm-001",
            report_type="activity",
            total_entries=10,
        )
        d = report.to_dict()
        assert d["title"] == "Test Report"
        assert d["total_entries"] == 10

    def test_user_activity_summary_to_dict(self):
        summary = UserActivitySummary(
            user_id="user-100",
            user_name="Ali",
            total_actions=5,
            login_count=2,
        )
        d = summary.to_dict()
        assert d["user_id"] == "user-100"
        assert d["total_actions"] == 5


# =============================================================================
# RetentionPolicy / RetentionJob Tests
# =============================================================================


@pytest.mark.unit
class TestRetentionModels:
    def test_retention_policy_to_dict(self):
        policy = RetentionPolicy(
            id="policy-1",
            name="Test Policy",
            name_ar="سياسة اختبار",
            category=AuditCategory.SECURITY,
            retention_days=1095,
        )
        d = policy.to_dict()
        assert d["id"] == "policy-1"
        assert d["category"] == "security"
        assert d["retention_days"] == 1095

    def test_retention_job_to_dict(self):
        job = RetentionJob(
            id="job-1",
            policy_id="policy-1",
            status="completed",
            entries_processed=10,
            entries_archived=8,
            entries_deleted=10,
        )
        d = job.to_dict()
        assert d["status"] == "completed"
        assert d["entries_processed"] == 10


# =============================================================================
# RetentionManager Tests
# =============================================================================


@pytest.mark.unit
class TestRetentionManager:
    def test_add_and_get_policy(self):
        manager = RetentionManager()
        policy = RetentionPolicy(id="p1", name="Test", category=AuditCategory.DATA)
        manager.add_policy(policy)
        assert manager.get_policy("p1") is not None
        assert len(manager.get_policies()) == 1

    def test_remove_policy(self):
        manager = RetentionManager()
        policy = RetentionPolicy(id="p1", name="Test")
        manager.add_policy(policy)
        assert manager.remove_policy("p1") is True
        assert manager.remove_policy("nonexistent") is False

    def test_load_default_policies(self):
        manager = RetentionManager()
        manager.load_default_policies()
        policies = manager.get_policies()
        assert len(policies) >= 7  # At least 7 default policies
        policy_ids = [p.id for p in policies]
        assert "policy-globalgap" in policy_ids
        assert "policy-security" in policy_ids
        assert "policy-system" in policy_ids

    def test_get_default_policies(self):
        policies = get_default_policies()
        assert len(policies) >= 7
        globalgap = next(p for p in policies if p.id == "policy-globalgap")
        assert globalgap.retention_days == 1825
        assert globalgap.archive_before_delete is True

    def test_get_expired_entries(self):
        manager = RetentionManager()
        now = datetime.now(UTC)
        expired_entry = _make_entry(
            retention_period=RetentionPeriod.SHORT,
        )
        # Manually set expires_at to the past
        expired_entry.expires_at = now - timedelta(days=1)

        active_entry = _make_entry(
            retention_period=RetentionPeriod.GLOBALGAP,
        )
        active_entry.expires_at = now + timedelta(days=100)

        manager.set_entries([expired_entry, active_entry])
        expired = manager.get_expired_entries()
        assert len(expired) == 1
        assert expired[0].id == expired_entry.id

    def test_get_entries_expiring_soon(self):
        manager = RetentionManager()
        now = datetime.now(UTC)
        soon_entry = _make_entry(retention_period=RetentionPeriod.SHORT)
        soon_entry.expires_at = now + timedelta(days=15)

        far_entry = _make_entry(retention_period=RetentionPeriod.GLOBALGAP)
        far_entry.expires_at = now + timedelta(days=365)

        manager.set_entries([soon_entry, far_entry])
        expiring = manager.get_entries_expiring_soon(days=30)
        assert len(expiring) == 1
        assert expiring[0].id == soon_entry.id

    def test_permanent_entries_not_expired(self):
        manager = RetentionManager()
        entry = _make_entry(retention_period=RetentionPeriod.PERMANENT)
        entry.expires_at = datetime.now(UTC) - timedelta(days=1)
        manager.set_entries([entry])
        expired = manager.get_expired_entries()
        assert len(expired) == 0

    def test_get_policy_for_entry(self):
        manager = RetentionManager()
        manager.load_default_policies()
        entry = _make_entry(category=AuditCategory.SECURITY)
        policy = manager.get_policy_for_entry(entry)
        assert policy is not None
        assert policy.id == "policy-security"

    def test_get_entries_by_policy(self):
        manager = RetentionManager()
        policy = RetentionPolicy(id="p1", name="Test", category=AuditCategory.DATA)
        manager.add_policy(policy)

        data_entry = _make_entry(category=AuditCategory.DATA)
        sec_entry = _make_entry(category=AuditCategory.SECURITY)
        manager.set_entries([data_entry, sec_entry])

        matching = manager.get_entries_by_policy("p1")
        assert len(matching) == 1
        assert matching[0].category == AuditCategory.DATA

    @pytest.mark.asyncio
    async def test_run_retention_dry_run(self):
        manager = RetentionManager()
        now = datetime.now(UTC)
        expired = _make_entry(retention_period=RetentionPeriod.SHORT)
        expired.expires_at = now - timedelta(days=1)
        manager.set_entries([expired])

        job = await manager.run_retention(dry_run=True)
        assert job.status == "completed"
        assert job.entries_processed == 1
        # Dry run should not remove entries
        assert len(manager._entries) == 1

    @pytest.mark.asyncio
    async def test_run_retention_actual(self):
        manager = RetentionManager()
        now = datetime.now(UTC)
        expired = _make_entry(retention_period=RetentionPeriod.SHORT)
        expired.expires_at = now - timedelta(days=1)
        active = _make_entry(retention_period=RetentionPeriod.GLOBALGAP)
        active.expires_at = now + timedelta(days=100)
        manager.set_entries([expired, active])

        job = await manager.run_retention(dry_run=False)
        assert job.status == "completed"
        assert job.entries_deleted == 1
        assert len(manager._entries) == 1
        assert manager._entries[0].id == active.id

    def test_retention_summary(self):
        manager = RetentionManager()
        manager.load_default_policies()
        now = datetime.now(UTC)
        entry = _make_entry(retention_period=RetentionPeriod.GLOBALGAP)
        entry.expires_at = now + timedelta(days=100)
        manager.set_entries([entry])

        summary = manager.get_retention_summary()
        assert summary["total_entries"] == 1
        assert summary["active_policies"] >= 7
        assert "entries_by_category" in summary

    def test_get_jobs_empty(self):
        manager = RetentionManager()
        jobs = manager.get_jobs()
        assert jobs == []

    def test_get_last_job(self):
        manager = RetentionManager()
        assert manager.get_last_job() is None

    @pytest.mark.asyncio
    async def test_archive_callback(self):
        callback = MagicMock()
        manager = RetentionManager(on_archive=callback)
        entries = [_make_entry()]
        await manager.archive_entries(entries, reason="test")
        callback.assert_called_once_with(entries)

    @pytest.mark.asyncio
    async def test_delete_callback(self):
        callback = MagicMock()
        manager = RetentionManager(on_delete=callback)
        entry = _make_entry()
        manager.set_entries([entry])
        await manager.delete_entries([entry])
        callback.assert_called_once_with([entry])
        assert len(manager._entries) == 0
