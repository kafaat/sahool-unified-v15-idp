"""
Comprehensive Unit Tests for SAHOOL Audit Trail Module
=======================================================

Tests cover:
1. Audit entry models and serialization
2. Logger functionality (actions, changes, logins, field operations)
3. Report generation
4. Retention policies
5. GlobalGAP compliance
6. Hash chain tamper detection
7. Change detection and tracking

Author: SAHOOL Test Suite
Updated: January 2026
"""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest

from shared.audit_trail import (
    RETENTION_DAYS,
    ActorType,
    # Models
    AuditActionType,
    AuditCategory,
    AuditEntry,
    AuditMetadata,
    AuditQueryFilter,
    AuditReportGenerator,
    AuditSeverity,
    # Logger
    AuditTrailLogger,
    ChangeType,
    FieldChange,
    RetentionJob,
    RetentionPeriod,
    RetentionPolicy,
    UserActivitySummary,
    compute_changes,
    # Reporter
    generate_activity_report,
    # Label helpers
    get_action_label,
    get_category_label,
    # Retention
    get_default_policies,
    get_severity_label,
    log_action,
    log_change,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def audit_logger():
    """Create a test audit logger with in-memory storage."""
    logger = AuditTrailLogger(
        tenant_id="test-tenant",
        storage_path=None,  # In-memory only
        max_buffer_size=100,
        enable_hash_chain=True,
    )
    yield logger
    logger.clear()


@pytest.fixture
def sample_entries():
    """Create sample audit entries for testing."""
    entries = []

    # Login entry
    login_entry = AuditEntry(
        tenant_id="test-tenant",
        actor_id="user-001",
        actor_type=ActorType.USER,
        actor_name="Ahmed Ibrahim",
        actor_name_ar="أحمد إبراهيم",
        action=AuditActionType.LOGIN,
        category=AuditCategory.SECURITY,
        severity=AuditSeverity.INFO,
        resource_type="user",
        resource_id="user-001",
        success=True,
    )
    entries.append(login_entry)

    # Create field entry with changes
    create_entry = AuditEntry(
        tenant_id="test-tenant",
        actor_id="user-001",
        actor_type=ActorType.USER,
        action=AuditActionType.CREATE,
        category=AuditCategory.DATA,
        severity=AuditSeverity.INFO,
        resource_type="field",
        resource_id="field-001",
        resource_name="North Field",
        resource_name_ar="الحقل الشمالي",
        changes=[
            FieldChange(
                field_name="name",
                field_name_ar="الاسم",
                old_value=None,
                new_value="North Field",
                change_type=ChangeType.ADDED,
            ),
            FieldChange(
                field_name="area_hectares",
                field_name_ar="المساحة بالهـ",
                old_value=None,
                new_value=8.5,
                change_type=ChangeType.ADDED,
            ),
        ],
        after_state={"name": "North Field", "area_hectares": 8.5},
        success=True,
    )
    entries.append(create_entry)

    # Update field entry
    update_entry = AuditEntry(
        tenant_id="test-tenant",
        actor_id="user-001",
        actor_type=ActorType.USER,
        action=AuditActionType.UPDATE,
        category=AuditCategory.DATA,
        severity=AuditSeverity.INFO,
        resource_type="field",
        resource_id="field-001",
        changes=[
            FieldChange(
                field_name="area_hectares",
                field_name_ar="المساحة بالهـ",
                old_value=8.5,
                new_value=9.2,
                change_type=ChangeType.MODIFIED,
            ),
        ],
        before_state={"area_hectares": 8.5},
        after_state={"area_hectares": 9.2},
        success=True,
    )
    entries.append(update_entry)

    # Irrigation field operation
    irrigation_entry = AuditEntry(
        tenant_id="test-tenant",
        actor_id="user-002",
        actor_type=ActorType.USER,
        actor_name="Fatima Hassan",
        actor_name_ar="فاطمة حسن",
        action=AuditActionType.IRRIGATION,
        category=AuditCategory.FIELD_OPS,
        severity=AuditSeverity.INFO,
        resource_type="field",
        resource_id="field-001",
        action_description="Irrigation applied",
        action_description_ar="تم تطبيق الري",
        after_state={"amount_mm": 25.0, "duration_hours": 2.0},
        success=True,
    )
    entries.append(irrigation_entry)

    # Failed operation
    failed_entry = AuditEntry(
        tenant_id="test-tenant",
        actor_id="user-001",
        actor_type=ActorType.USER,
        action=AuditActionType.DELETE,
        category=AuditCategory.DATA,
        severity=AuditSeverity.ERROR,
        resource_type="field",
        resource_id="field-999",
        success=False,
        error_code="NOT_FOUND",
        error_message="Field not found",
        error_message_ar="الحقل غير موجود",
    )
    entries.append(failed_entry)

    # GlobalGAP event
    globalgap_entry = AuditEntry(
        tenant_id="test-tenant",
        actor_id="auditor-001",
        actor_type=ActorType.AUDITOR,
        action=AuditActionType.AUDIT_STARTED,
        category=AuditCategory.GLOBALGAP,
        severity=AuditSeverity.INFO,
        resource_type="audit_session",
        resource_id="session-001",
        metadata=AuditMetadata(
            ggn="4012345678901",
            audit_session_id="session-001",
            control_point_id="AF.1.1.1",
        ),
        retention_period=RetentionPeriod.GLOBALGAP,
        success=True,
    )
    entries.append(globalgap_entry)

    return entries


# ─────────────────────────────────────────────────────────────────────────────
# 1. Audit Entry Models Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAuditEntryModels:
    """Test audit entry models and data structures."""

    def test_field_change_creation(self):
        """Test FieldChange model creation."""
        change = FieldChange(
            field_name="irrigation_amount",
            field_name_ar="كمية الري",
            old_value=20.0,
            new_value=25.0,
            change_type=ChangeType.MODIFIED,
        )

        assert change.field_name == "irrigation_amount"
        assert change.field_name_ar == "كمية الري"
        assert change.old_value == 20.0
        assert change.new_value == 25.0
        assert change.change_type == ChangeType.MODIFIED

    def test_field_change_serialization(self):
        """Test FieldChange serialization to dict."""
        change = FieldChange(
            field_name="crop_type",
            old_value=None,
            new_value="wheat",
            change_type=ChangeType.ADDED,
        )

        data = change.to_dict()
        assert data["field_name"] == "crop_type"
        assert data["old_value"] is None
        assert data["new_value"] == "wheat"
        assert data["change_type"] == "added"

    def test_audit_metadata_creation(self):
        """Test AuditMetadata model creation."""
        metadata = AuditMetadata(
            correlation_id="corr-001",
            trace_id="trace-001",
            ip_address="192.168.1.100",
            user_agent="Mobile App v1.0",
            ggn="4012345678901",
            tags=["critical", "compliance"],
            custom={"farm_region": "North Valley"},
        )

        assert metadata.correlation_id == "corr-001"
        assert metadata.trace_id == "trace-001"
        assert metadata.ip_address == "192.168.1.100"
        assert metadata.ggn == "4012345678901"
        assert len(metadata.tags) == 2
        assert metadata.custom["farm_region"] == "North Valley"

    def test_audit_entry_creation(self):
        """Test AuditEntry model creation."""
        entry = AuditEntry(
            tenant_id="farm-001",
            actor_id="user-001",
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
            category=AuditCategory.DATA,
        )

        assert entry.tenant_id == "farm-001"
        assert entry.actor_id == "user-001"
        assert entry.action == AuditActionType.CREATE
        assert entry.resource_type == "field"
        assert entry.success is True
        assert entry.retention_period == RetentionPeriod.GLOBALGAP

    def test_audit_entry_expiration_calculation(self):
        """Test automatic expiration date calculation."""
        now = datetime.now(UTC)
        entry = AuditEntry(
            tenant_id="farm-001",
            timestamp=now,
            retention_period=RetentionPeriod.GLOBALGAP,
            action=AuditActionType.CREATE,
            resource_type="test",
            resource_id="123",
        )

        assert entry.expires_at is not None
        expected_expiry = now + timedelta(days=RETENTION_DAYS[RetentionPeriod.GLOBALGAP])
        assert (entry.expires_at - expected_expiry).total_seconds() < 1

    def test_audit_entry_hash_chain(self):
        """Test entry hash calculation and chain."""
        entry = AuditEntry(
            tenant_id="farm-001",
            actor_id="user-001",
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
        )

        assert entry.entry_hash is not None
        assert len(entry.entry_hash) == 64  # SHA-256 hex digest length
        assert entry.prev_hash is None  # First entry has no previous hash

    def test_audit_entry_hash_chain_linkage(self):
        """Test hash chain linkage between entries."""
        entry1 = AuditEntry(
            id="entry-001",
            tenant_id="farm-001",
            actor_id="user-001",
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
        )

        entry2 = AuditEntry(
            id="entry-002",
            tenant_id="farm-001",
            actor_id="user-001",
            action=AuditActionType.UPDATE,
            resource_type="field",
            resource_id="field-001",
            prev_hash=entry1.entry_hash,
        )

        assert entry2.prev_hash == entry1.entry_hash
        assert entry2.entry_hash != entry1.entry_hash

    def test_audit_entry_serialization(self):
        """Test AuditEntry serialization to dict and JSON."""
        entry = AuditEntry(
            tenant_id="farm-001",
            actor_id="user-001",
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
            changes=[
                FieldChange(
                    field_name="name",
                    old_value=None,
                    new_value="North Field",
                    change_type=ChangeType.ADDED,
                )
            ],
        )

        # Test to_dict
        data = entry.to_dict()
        assert data["id"] == entry.id
        assert data["tenant_id"] == "farm-001"
        assert data["action"] == "create"
        assert len(data["changes"]) == 1
        assert data["changes"][0]["field_name"] == "name"

        # Test to_json
        json_str = entry.to_json()
        parsed = json.loads(json_str)
        assert parsed["id"] == entry.id
        assert parsed["action"] == "create"

    def test_audit_entry_deserialization(self):
        """Test AuditEntry deserialization from dict."""
        original = AuditEntry(
            tenant_id="farm-001",
            actor_id="user-001",
            action=AuditActionType.UPDATE,
            resource_type="field",
            resource_id="field-001",
            category=AuditCategory.DATA,
            severity=AuditSeverity.WARNING,
            changes=[
                FieldChange(
                    field_name="area",
                    old_value=8.0,
                    new_value=9.0,
                    change_type=ChangeType.MODIFIED,
                )
            ],
        )

        data = original.to_dict()
        restored = AuditEntry.from_dict(data)

        assert restored.id == original.id
        assert restored.tenant_id == original.tenant_id
        assert restored.action == original.action
        assert restored.category == original.category
        assert len(restored.changes) == 1
        assert restored.changes[0].field_name == "area"

    def test_retention_policy_creation(self):
        """Test RetentionPolicy model."""
        policy = RetentionPolicy(
            name="GlobalGAP Compliance",
            name_ar="امتثال GlobalGAP",
            tenant_id="farm-001",
            category=AuditCategory.GLOBALGAP,
            retention_period=RetentionPeriod.GLOBALGAP,
            retention_days=1825,
            archive_before_delete=True,
        )

        assert policy.name == "GlobalGAP Compliance"
        assert policy.retention_days == 1825
        assert policy.archive_before_delete is True
        assert policy.is_active is True

    def test_retention_job_creation(self):
        """Test RetentionJob model."""
        job = RetentionJob(
            policy_id="policy-001",
            started_at=datetime.now(UTC),
            status="running",
        )

        assert job.policy_id == "policy-001"
        assert job.status == "running"
        assert job.entries_processed == 0

    def test_user_activity_summary_creation(self):
        """Test UserActivitySummary model."""
        summary = UserActivitySummary(
            user_id="user-001",
            user_name="Ahmed Ibrahim",
            user_name_ar="أحمد إبراهيم",
            tenant_id="farm-001",
            total_actions=25,
            successful_actions=24,
            failed_actions=1,
        )

        assert summary.user_id == "user-001"
        assert summary.total_actions == 25
        assert summary.successful_actions == 24


# ─────────────────────────────────────────────────────────────────────────────
# 2. Logger Functionality Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestAuditTrailLogger:
    """Test AuditTrailLogger functionality."""

    def test_logger_initialization(self, audit_logger):
        """Test logger initialization."""
        assert audit_logger.tenant_id == "test-tenant"
        assert audit_logger.enable_hash_chain is True
        assert audit_logger.default_retention == RetentionPeriod.GLOBALGAP

    def test_log_simple_action(self, audit_logger):
        """Test logging a simple action."""
        entry = audit_logger.log_action(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
            actor_id="user-001",
            actor_name="Ahmed",
        )

        assert entry.action == AuditActionType.CREATE
        assert entry.resource_type == "field"
        assert entry.resource_id == "field-001"
        assert entry.actor_id == "user-001"
        assert entry.success is True
        assert entry.id is not None

    def test_log_failed_action(self, audit_logger):
        """Test logging a failed action."""
        entry = audit_logger.log_action(
            action=AuditActionType.DELETE,
            resource_type="field",
            resource_id="field-999",
            success=False,
            error_code="NOT_FOUND",
            error_message="Field not found",
        )

        assert entry.success is False
        assert entry.error_code == "NOT_FOUND"
        assert entry.error_message == "Field not found"

    def test_log_change_create(self, audit_logger):
        """Test logging a create action with changes."""
        before = None
        after = {"name": "North Field", "area": 8.5}

        entry = audit_logger.log_change(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
            before=before,
            after=after,
            actor_id="user-001",
        )

        assert len(entry.changes) == 2
        assert entry.changes[0].change_type == ChangeType.ADDED
        assert entry.changes[0].old_value is None
        assert entry.changes[0].new_value in [8.5, "North Field"]

    def test_log_change_update(self, audit_logger):
        """Test logging an update action with changes."""
        before = {"name": "North Field", "area": 8.5}
        after = {"name": "North Field", "area": 9.2}

        entry = audit_logger.log_change(
            action=AuditActionType.UPDATE,
            resource_type="field",
            resource_id="field-001",
            before=before,
            after=after,
            actor_id="user-001",
        )

        # Only area changed
        assert len(entry.changes) == 1
        assert entry.changes[0].field_name == "area"
        assert entry.changes[0].old_value == 8.5
        assert entry.changes[0].new_value == 9.2
        assert entry.changes[0].change_type == ChangeType.MODIFIED

    def test_log_change_delete(self, audit_logger):
        """Test logging a delete action with changes."""
        before = {"name": "North Field", "area": 8.5}
        after = None

        entry = audit_logger.log_change(
            action=AuditActionType.DELETE,
            resource_type="field",
            resource_id="field-001",
            before=before,
            after=after,
            actor_id="user-001",
        )

        assert all(c.change_type == ChangeType.DELETED for c in entry.changes)
        assert len(entry.changes) == 2

    def test_log_login_success(self, audit_logger):
        """Test logging a successful login."""
        entry = audit_logger.log_login(
            user_id="user-001",
            success=True,
            user_name="Ahmed",
            ip_address="192.168.1.100",
            user_agent="Mobile App v1.0",
        )

        assert entry.action == AuditActionType.LOGIN
        assert entry.success is True
        assert entry.category == AuditCategory.SECURITY
        assert entry.severity == AuditSeverity.INFO
        assert entry.metadata.ip_address == "192.168.1.100"

    def test_log_login_failure(self, audit_logger):
        """Test logging a failed login."""
        entry = audit_logger.log_login(
            user_id="user-001",
            success=False,
            error_message="Invalid credentials",
        )

        assert entry.action == AuditActionType.LOGIN_FAILED
        assert entry.success is False
        assert entry.severity == AuditSeverity.WARNING

    def test_log_logout(self, audit_logger):
        """Test logging a logout."""
        entry = audit_logger.log_logout(
            user_id="user-001",
            user_name="Ahmed",
        )

        assert entry.action == AuditActionType.LOGOUT
        assert entry.success is True

    def test_log_globalgap_event(self, audit_logger):
        """Test logging a GlobalGAP compliance event."""
        entry = audit_logger.log_globalgap_event(
            action=AuditActionType.AUDIT_STARTED,
            resource_type="audit_session",
            resource_id="session-001",
            ggn="4012345678901",
            audit_session_id="session-001",
            control_point_id="AF.1.1.1",
            actor_id="auditor-001",
        )

        assert entry.action == AuditActionType.AUDIT_STARTED
        assert entry.category == AuditCategory.GLOBALGAP
        assert entry.retention_period == RetentionPeriod.GLOBALGAP
        assert entry.metadata.ggn == "4012345678901"
        assert entry.metadata.control_point_id == "AF.1.1.1"

    def test_log_field_operation_irrigation(self, audit_logger):
        """Test logging field operations."""
        entry = audit_logger.log_field_operation(
            operation_type=AuditActionType.IRRIGATION,
            field_id="field-001",
            field_name="North Field",
            actor_id="user-002",
            details={"amount_mm": 25.0, "duration_hours": 2.0},
        )

        assert entry.action == AuditActionType.IRRIGATION
        assert entry.category == AuditCategory.FIELD_OPS
        assert entry.after_state["amount_mm"] == 25.0

    def test_automatic_category_inference(self, audit_logger):
        """Test automatic category inference from action type."""
        # Security action
        security_entry = audit_logger.log_action(
            action=AuditActionType.PASSWORD_CHANGE,
            resource_type="user",
            resource_id="user-001",
        )
        assert security_entry.category == AuditCategory.SECURITY

        # Field ops action
        field_entry = audit_logger.log_action(
            action=AuditActionType.FERTILIZER_APPLICATION,
            resource_type="field",
            resource_id="field-001",
        )
        assert field_entry.category == AuditCategory.FIELD_OPS

        # Compliance action
        compliance_entry = audit_logger.log_action(
            action=AuditActionType.NC_RAISED,
            resource_type="issue",
            resource_id="nc-001",
        )
        assert compliance_entry.category == AuditCategory.COMPLIANCE

    def test_buffer_and_metrics(self, audit_logger):
        """Test buffer management and metrics tracking."""
        # Log multiple entries
        audit_logger.log_action(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
        )
        audit_logger.log_action(
            action=AuditActionType.UPDATE,
            resource_type="field",
            resource_id="field-001",
        )
        audit_logger.log_action(
            action=AuditActionType.LOGIN,
            resource_type="user",
            resource_id="user-001",
        )

        summary = audit_logger.get_summary()
        assert summary["total_entries"] == 3
        assert "create" in summary["entries_by_action"]
        assert summary["entries_by_action"]["create"] == 1
        assert "data" in summary["entries_by_category"]
        assert "security" in summary["entries_by_category"]

    def test_hash_chain_verification(self, audit_logger):
        """Test hash chain verification."""
        audit_logger.log_action(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
        )
        audit_logger.log_action(
            action=AuditActionType.UPDATE,
            resource_type="field",
            resource_id="field-001",
        )

        is_valid, invalid_ids = audit_logger.verify_hash_chain()
        assert is_valid is True
        assert len(invalid_ids) == 0

    def test_history_retrieval(self, audit_logger):
        """Test retrieving history for a resource."""
        # Log multiple actions on same resource
        audit_logger.log_action(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
        )
        audit_logger.log_action(
            action=AuditActionType.UPDATE,
            resource_type="field",
            resource_id="field-001",
        )
        audit_logger.log_action(
            action=AuditActionType.UPDATE,
            resource_type="field",
            resource_id="field-001",
        )

        # Log action on different resource
        audit_logger.log_action(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-002",
        )

        history = audit_logger.get_history(
            resource_type="field",
            resource_id="field-001",
        )
        assert len(history) == 3

    def test_user_activity_retrieval(self, audit_logger):
        """Test retrieving user activity."""
        # Log actions for user 1
        audit_logger.log_action(
            action=AuditActionType.LOGIN,
            resource_type="user",
            resource_id="user-001",
            actor_id="user-001",
        )
        audit_logger.log_action(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
            actor_id="user-001",
        )

        # Log action for user 2
        audit_logger.log_action(
            action=AuditActionType.LOGIN,
            resource_type="user",
            resource_id="user-002",
            actor_id="user-002",
        )

        activity = audit_logger.get_user_activity("user-001")
        assert len(activity) == 2
        assert all(e.actor_id == "user-001" for e in activity)

    def test_query_filtering(self, audit_logger):
        """Test audit entry filtering."""
        # Log various entries
        audit_logger.log_action(
            action=AuditActionType.LOGIN,
            resource_type="user",
            resource_id="user-001",
            actor_id="user-001",
        )
        audit_logger.log_action(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
            actor_id="user-001",
            category=AuditCategory.DATA,
            severity=AuditSeverity.INFO,
        )
        audit_logger.log_action(
            action=AuditActionType.DELETE,
            resource_type="field",
            resource_id="field-999",
            success=False,
        )

        # Filter by action
        filter_ = AuditQueryFilter(action=AuditActionType.LOGIN)
        results = audit_logger.get_entries(filter_)
        assert len(results) == 1
        assert results[0].action == AuditActionType.LOGIN

        # Filter by success
        filter_ = AuditQueryFilter(success=False)
        results = audit_logger.get_entries(filter_)
        assert len(results) == 1
        assert results[0].success is False


# ─────────────────────────────────────────────────────────────────────────────
# 3. Change Detection Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestChangeDetection:
    """Test change detection functionality."""

    def test_compute_changes_create(self):
        """Test change detection for create operations."""
        after = {"name": "North Field", "area": 8.5}
        changes = compute_changes(before=None, after=after)

        assert len(changes) == 2
        assert all(c.change_type == ChangeType.ADDED for c in changes)
        assert all(c.old_value is None for c in changes)

    def test_compute_changes_delete(self):
        """Test change detection for delete operations."""
        before = {"name": "North Field", "area": 8.5}
        changes = compute_changes(before=before, after=None)

        assert len(changes) == 2
        assert all(c.change_type == ChangeType.DELETED for c in changes)
        assert all(c.new_value is None for c in changes)

    def test_compute_changes_update(self):
        """Test change detection for update operations."""
        before = {"name": "North Field", "area": 8.5, "crop": "wheat"}
        after = {"name": "North Field", "area": 9.2, "crop": "wheat"}

        changes = compute_changes(before=before, after=after)

        # Only area changed
        assert len(changes) == 1
        assert changes[0].field_name == "area"
        assert changes[0].old_value == 8.5
        assert changes[0].new_value == 9.2
        assert changes[0].change_type == ChangeType.MODIFIED

    def test_compute_changes_exclude_fields(self):
        """Test excluding fields from change detection."""
        before = {"name": "North Field", "updated_at": "2024-01-01"}
        after = {"name": "Updated Field", "updated_at": "2024-01-02"}

        # Exclude updated_at (already done by default)
        changes = compute_changes(before=before, after=after)

        assert len(changes) == 1
        assert changes[0].field_name == "name"

    def test_compute_changes_with_labels(self):
        """Test change detection with Arabic labels."""
        before = {"name": "North Field"}
        after = {"name": "New Name"}

        labels_ar = {"name": "الاسم"}
        changes = compute_changes(
            before=before,
            after=after,
            field_labels_ar=labels_ar,
        )

        assert len(changes) == 1
        assert changes[0].field_name_ar == "الاسم"

    def test_compute_changes_field_added(self):
        """Test detecting fields added during update."""
        before = {"name": "Field"}
        after = {"name": "Field", "area": 8.5}

        changes = compute_changes(before=before, after=after)

        added_changes = [c for c in changes if c.change_type == ChangeType.ADDED]
        assert len(added_changes) == 1
        assert added_changes[0].field_name == "area"

    def test_compute_changes_field_removed(self):
        """Test detecting fields removed during update."""
        before = {"name": "Field", "area": 8.5}
        after = {"name": "Field"}

        changes = compute_changes(before=before, after=after)

        deleted_changes = [c for c in changes if c.change_type == ChangeType.DELETED]
        assert len(deleted_changes) == 1
        assert deleted_changes[0].field_name == "area"


# ─────────────────────────────────────────────────────────────────────────────
# 4. Report Generation Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestReportGeneration:
    """Test audit report generation."""

    def test_report_initialization(self, sample_entries):
        """Test report generator initialization."""
        generator = AuditReportGenerator(
            entries=sample_entries,
            tenant_id="test-tenant",
            language="en",
        )

        assert generator.tenant_id == "test-tenant"
        assert generator.language == "en"
        assert len(generator.entries) == len(sample_entries)

    def test_user_activity_summary(self, sample_entries):
        """Test user activity summary generation."""
        generator = AuditReportGenerator(
            entries=sample_entries,
            tenant_id="test-tenant",
        )

        summary = generator.generate_user_activity_summary(
            user_id="user-001",
        )

        assert summary.user_id == "user-001"
        assert summary.total_actions > 0
        assert summary.successful_actions > 0

    def test_user_activity_summary_with_period(self, sample_entries):
        """Test user activity summary with time period."""
        now = datetime.now(UTC)
        start = now - timedelta(days=1)
        end = now + timedelta(days=1)

        generator = AuditReportGenerator(entries=sample_entries)
        summary = generator.generate_user_activity_summary(
            user_id="user-001",
            period_start=start,
            period_end=end,
        )

        assert summary.period_start == start
        assert summary.period_end == end

    def test_activity_report_generation(self, sample_entries):
        """Test activity report generation."""
        generator = AuditReportGenerator(
            entries=sample_entries,
            tenant_id="test-tenant",
        )

        report = generator.generate_activity_report(
            period_start=datetime.now(UTC) - timedelta(days=1),
            period_end=datetime.now(UTC) + timedelta(days=1),
        )

        assert report.report_type == "activity"
        assert report.total_entries > 0
        assert len(report.user_summaries) > 0

    def test_compliance_report_generation(self, sample_entries):
        """Test compliance report generation."""
        generator = AuditReportGenerator(
            entries=sample_entries,
            tenant_id="test-tenant",
        )

        report = generator.generate_compliance_report()

        assert report.report_type == "compliance"
        assert report.total_entries > 0

    def test_globalgap_report_generation(self, sample_entries):
        """Test GlobalGAP report generation."""
        generator = AuditReportGenerator(
            entries=sample_entries,
            tenant_id="test-tenant",
        )

        report = generator.generate_globalgap_report(
            ggn="4012345678901",
            period_start=datetime.now(UTC) - timedelta(days=30),
            period_end=datetime.now(UTC),
        )

        assert report.report_type == "globalgap"
        assert report.ggn == "4012345678901"

    def test_report_statistics(self, sample_entries):
        """Test report statistics generation."""
        generator = AuditReportGenerator(entries=sample_entries)
        report = generator.generate_activity_report()

        # Check statistics structure
        assert "entries_by_category" in report.to_dict()
        assert "entries_by_severity" in report.to_dict()
        assert "entries_by_action" in report.to_dict()

    def test_export_to_json(self, sample_entries):
        """Test export to JSON format."""
        generator = AuditReportGenerator(entries=sample_entries)
        json_data = generator.export_to_json(sample_entries)

        # Export returns string or bytes
        if isinstance(json_data, bytes):
            parsed = json.loads(json_data)
        else:
            parsed = json.loads(json_data)
        assert isinstance(parsed, dict)
        assert "entries" in parsed or isinstance(parsed, list)

    def test_export_to_csv(self, sample_entries):
        """Test export to CSV format."""
        generator = AuditReportGenerator(entries=sample_entries)
        csv_data = generator.export_to_csv(sample_entries)

        # Export returns string or bytes
        if isinstance(csv_data, bytes):
            csv_str = csv_data.decode()
        else:
            csv_str = csv_data
        lines = csv_str.split("\n")
        assert len(lines) > 1  # At least header and one row


# ─────────────────────────────────────────────────────────────────────────────
# 5. Retention Policy Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestRetentionPolicies:
    """Test retention policy management."""

    def test_default_policies(self):
        """Test getting default retention policies."""
        policies = get_default_policies()

        assert len(policies) >= 7
        assert any(p.category == AuditCategory.GLOBALGAP for p in policies)
        assert any(p.category == AuditCategory.FIELD_OPS for p in policies)
        assert any(p.category == AuditCategory.SECURITY for p in policies)

    def test_globalgap_policy(self):
        """Test GlobalGAP retention policy."""
        policies = get_default_policies()
        ggap_policy = next(p for p in policies if p.category == AuditCategory.GLOBALGAP)

        assert ggap_policy.retention_period == RetentionPeriod.GLOBALGAP
        assert ggap_policy.retention_days == 1825
        assert ggap_policy.archive_before_delete is True

    def test_field_ops_policy(self):
        """Test field operations retention policy."""
        policies = get_default_policies()
        ops_policy = next(p for p in policies if p.category == AuditCategory.FIELD_OPS)

        assert ops_policy.retention_period == RetentionPeriod.GLOBALGAP
        assert ops_policy.retention_days == 1825

    def test_security_policy(self):
        """Test security retention policy."""
        policies = get_default_policies()
        sec_policy = next(p for p in policies if p.category == AuditCategory.SECURITY)

        assert sec_policy.retention_period == RetentionPeriod.LONG
        assert sec_policy.retention_days == 1095

    def test_custom_retention_policy(self):
        """Test creating custom retention policy."""
        policy = RetentionPolicy(
            name="Custom Policy",
            name_ar="سياسة مخصصة",
            tenant_id="farm-001",
            category=AuditCategory.DATA,
            retention_period=RetentionPeriod.MEDIUM,
            retention_days=365,
        )

        assert policy.name == "Custom Policy"
        assert policy.tenant_id == "farm-001"
        assert policy.is_active is True

    def test_retention_job_creation(self):
        """Test retention job creation and tracking."""
        job = RetentionJob(
            policy_id="policy-001",
            status="running",
        )

        assert job.policy_id == "policy-001"
        assert job.status == "running"
        assert job.entries_processed == 0

    def test_retention_job_completion(self):
        """Test retention job completion."""
        job = RetentionJob(
            policy_id="policy-001",
            status="running",
        )

        job.status = "completed"
        job.completed_at = datetime.now(UTC)
        job.entries_processed = 100
        job.entries_deleted = 50
        job.entries_archived = 50

        assert job.status == "completed"
        assert job.entries_processed == 100
        assert job.entries_deleted + job.entries_archived == 100


# ─────────────────────────────────────────────────────────────────────────────
# 6. GlobalGAP Compliance Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestGlobalGAPCompliance:
    """Test GlobalGAP compliance features."""

    def test_globalgap_metadata(self):
        """Test GlobalGAP metadata in audit entries."""
        metadata = AuditMetadata(
            ggn="4012345678901",
            audit_session_id="audit-2024-001",
            control_point_id="AF.1.1.1",
        )

        assert metadata.ggn == "4012345678901"
        assert metadata.audit_session_id == "audit-2024-001"
        assert metadata.control_point_id == "AF.1.1.1"

    def test_globalgap_retention_period(self):
        """Test GlobalGAP 5-year retention period."""
        entry = AuditEntry(
            tenant_id="farm-001",
            retention_period=RetentionPeriod.GLOBALGAP,
            action=AuditActionType.CROP_PLANTING,
            resource_type="field",
            resource_id="field-001",
        )

        assert entry.retention_period == RetentionPeriod.GLOBALGAP
        assert RETENTION_DAYS[entry.retention_period] == 1825

    def test_field_operation_logging(self, audit_logger):
        """Test field operation logging for GlobalGAP."""
        entry = audit_logger.log_field_operation(
            operation_type=AuditActionType.CROP_PLANTING,
            field_id="field-001",
            field_name="North Field",
            ggn="4012345678901",
            details={"crop": "wheat", "variety": "Sakha 95"},
        )

        assert entry.retention_period == RetentionPeriod.GLOBALGAP
        assert entry.category == AuditCategory.FIELD_OPS
        assert entry.metadata.ggn == "4012345678901"

    def test_globalgap_audit_event(self, audit_logger):
        """Test GlobalGAP audit event logging."""
        entry = audit_logger.log_globalgap_event(
            action=AuditActionType.FINDING_RECORDED,
            resource_type="finding",
            resource_id="find-001",
            ggn="4012345678901",
            audit_session_id="audit-2024-001",
            control_point_id="AF.1.1.1",
        )

        assert entry.category == AuditCategory.GLOBALGAP
        assert entry.retention_period == RetentionPeriod.GLOBALGAP

    def test_compliance_traceability(self, audit_logger):
        """Test traceability for compliance requirements."""
        # Log multiple operations on a field
        audit_logger.log_field_operation(
            operation_type=AuditActionType.CROP_PLANTING,
            field_id="field-001",
            details={"variety": "Sakha 95"},
            ggn="4012345678901",
        )

        audit_logger.log_field_operation(
            operation_type=AuditActionType.IRRIGATION,
            field_id="field-001",
            details={"amount_mm": 25},
            ggn="4012345678901",
        )

        audit_logger.log_field_operation(
            operation_type=AuditActionType.FERTILIZER_APPLICATION,
            field_id="field-001",
            details={"product": "Urea 46%"},
            ggn="4012345678901",
        )

        # Retrieve full history
        history = audit_logger.get_history(
            resource_type="field",
            resource_id="field-001",
        )

        assert len(history) >= 3
        assert all(e.metadata.ggn == "4012345678901" for e in history)


# ─────────────────────────────────────────────────────────────────────────────
# 7. Label and Localization Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestLabelsAndLocalization:
    """Test bilingual labels and localization."""

    def test_action_label_english(self):
        """Test action label in English."""
        label = get_action_label(AuditActionType.CREATE, language="en")
        assert label == "Create"

    def test_action_label_arabic(self):
        """Test action label in Arabic."""
        label = get_action_label(AuditActionType.CREATE, language="ar")
        assert label == "إنشاء"

    def test_category_label_english(self):
        """Test category label in English."""
        label = get_category_label(AuditCategory.GLOBALGAP, language="en")
        assert label == "GlobalGAP"

    def test_category_label_arabic(self):
        """Test category label in Arabic."""
        label = get_category_label(AuditCategory.GLOBALGAP, language="ar")
        assert label == "GlobalGAP"

    def test_severity_label_english(self):
        """Test severity label in English."""
        label = get_severity_label(AuditSeverity.CRITICAL, language="en")
        assert label == "Critical"

    def test_severity_label_arabic(self):
        """Test severity label in Arabic."""
        label = get_severity_label(AuditSeverity.CRITICAL, language="ar")
        assert label == "حرج"

    def test_bilingual_entry(self):
        """Test bilingual audit entry."""
        entry = AuditEntry(
            action=AuditActionType.IRRIGATION,
            resource_type="field",
            resource_id="field-001",
            action_description="Irrigation applied",
            action_description_ar="تم تطبيق الري",
            resource_name="North Field",
            resource_name_ar="الحقل الشمالي",
        )

        assert entry.action_description == "Irrigation applied"
        assert entry.action_description_ar == "تم تطبيق الري"
        assert entry.resource_name_ar == "الحقل الشمالي"


# ─────────────────────────────────────────────────────────────────────────────
# 8. Integration Tests
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.unit
class TestIntegration:
    """Integration tests combining multiple components."""

    def test_end_to_end_workflow(self, audit_logger):
        """Test complete audit trail workflow."""
        # 1. User logs in
        audit_logger.log_login(
            user_id="user-001",
            success=True,
            user_name="Ahmed",
        )

        # 2. Create a field
        create_entry = audit_logger.log_change(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
            before=None,
            after={"name": "North Field", "area": 8.5},
            actor_id="user-001",
        )

        # 3. Apply irrigation
        audit_logger.log_field_operation(
            operation_type=AuditActionType.IRRIGATION,
            field_id="field-001",
            actor_id="user-001",
            details={"amount_mm": 25},
        )

        # 4. User logs out
        audit_logger.log_logout(user_id="user-001")

        # Verify audit trail
        history = audit_logger.get_history("field", "field-001")
        assert len(history) >= 1
        assert history[0].action == AuditActionType.IRRIGATION

    def test_compliance_audit(self, audit_logger):
        """Test compliance audit scenario."""
        # Simulate GlobalGAP audit
        audit_logger.log_globalgap_event(
            action=AuditActionType.AUDIT_STARTED,
            resource_type="audit",
            resource_id="audit-001",
            ggn="4012345678901",
            audit_session_id="session-001",
            actor_id="auditor-001",
        )

        # Log field operations during audit
        for i in range(3):
            audit_logger.log_field_operation(
                operation_type=AuditActionType.CROP_PLANTING,
                field_id=f"field-{i:03d}",
                ggn="4012345678901",
            )

        # Complete audit
        audit_logger.log_globalgap_event(
            action=AuditActionType.AUDIT_COMPLETED,
            resource_type="audit",
            resource_id="audit-001",
            ggn="4012345678901",
            audit_session_id="session-001",
            actor_id="auditor-001",
        )

        # Generate report
        entries = audit_logger.get_entries()
        generator = AuditReportGenerator(entries)
        report = generator.generate_globalgap_report(
            ggn="4012345678901",
        )

        assert report.ggn == "4012345678901"
        assert report.total_entries >= 5

    def test_error_tracking(self, audit_logger):
        """Test error and failure tracking."""
        # Successful operation
        audit_logger.log_action(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
            success=True,
        )

        # Failed operation
        audit_logger.log_action(
            action=AuditActionType.DELETE,
            resource_type="field",
            resource_id="field-999",
            success=False,
            error_code="NOT_FOUND",
            error_message="Field does not exist",
        )

        # Query failed operations
        filter_ = AuditQueryFilter(success=False)
        failed = audit_logger.get_entries(filter_)

        assert len(failed) == 1
        assert failed[0].error_code == "NOT_FOUND"


# ═══════════════════════════════════════════════════════════════════════════
# A-05: HMAC Signing Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestHMACSigning:
    """Tests for HMAC-based audit log signing (A-05)."""

    def test_hmac_signing_with_secret(self, monkeypatch):
        """When AUDIT_HMAC_SECRET is set, hash uses HMAC-SHA256."""
        monkeypatch.setenv("AUDIT_HMAC_SECRET", "test-secret-32-chars-minimum!!")

        entry = AuditEntry(
            tenant_id="farm-001",
            actor_id="user-001",
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
        )

        assert entry.entry_hash is not None
        assert len(entry.entry_hash) == 64

    def test_different_secrets_produce_different_hashes(self, monkeypatch):
        """Different secrets must produce different hashes for identical data."""
        fixed_id = "test-entry-001"
        ts = datetime(2026, 1, 1, tzinfo=UTC)

        monkeypatch.setenv("AUDIT_HMAC_SECRET", "secret-A")
        entry_a = AuditEntry(
            id=fixed_id,
            tenant_id="farm-001",
            actor_id="user-001",
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
            timestamp=ts,
        )

        monkeypatch.setenv("AUDIT_HMAC_SECRET", "secret-B")
        # Force recalculation with new secret
        entry_b = AuditEntry(
            id=fixed_id,
            tenant_id="farm-001",
            actor_id="user-001",
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
            timestamp=ts,
        )

        assert entry_a.entry_hash != entry_b.entry_hash

    def test_tampered_entry_fails_verification(self, monkeypatch):
        """Modifying entry data must break hash verification."""
        monkeypatch.setenv("AUDIT_HMAC_SECRET", "test-secret-for-tamper-check")

        entry = AuditEntry(
            tenant_id="farm-001",
            actor_id="user-001",
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
        )
        original_hash = entry.entry_hash

        # Tamper with the data
        entry.actor_id = "attacker-001"

        # Hash should no longer match
        assert entry._calculate_hash() != original_hash

    def test_fallback_to_sha256_without_secret(self, monkeypatch):
        """Without AUDIT_HMAC_SECRET, falls back to plain SHA-256."""
        monkeypatch.delenv("AUDIT_HMAC_SECRET", raising=False)

        entry = AuditEntry(
            tenant_id="farm-001",
            actor_id="user-001",
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-001",
        )

        assert entry.entry_hash is not None
        assert len(entry.entry_hash) == 64


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
