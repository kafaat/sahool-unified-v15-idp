"""
SAHOOL Audit Trail Data Models
==============================
نماذج بيانات مسار التدقيق

Comprehensive data models for audit trail management supporting GlobalGAP
compliance requirements, change tracking, and bilingual content.

Features:
    - Action logging for compliance | تسجيل الإجراءات للامتثال
    - Change tracking with diff | تتبع التغييرات مع المقارنة
    - User activity tracking | تتبع نشاط المستخدم
    - Export formats for audits | صيغ التصدير للتدقيق
    - Retention policy management | إدارة سياسة الاحتفاظ

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any
from uuid import uuid4

# ─────────────────────────────────────────────────────────────────────────────
# Enums | التعدادات
# ─────────────────────────────────────────────────────────────────────────────


class AuditActionType(StrEnum):
    """
    Types of auditable actions.
    أنواع الإجراءات القابلة للتدقيق
    """

    # CRUD Operations
    CREATE = "create"  # إنشاء
    READ = "read"  # قراءة
    UPDATE = "update"  # تحديث
    DELETE = "delete"  # حذف

    # Authentication
    LOGIN = "login"  # تسجيل الدخول
    LOGOUT = "logout"  # تسجيل الخروج
    LOGIN_FAILED = "login_failed"  # فشل تسجيل الدخول
    PASSWORD_CHANGE = "password_change"  # تغيير كلمة المرور
    PASSWORD_RESET = "password_reset"  # إعادة تعيين كلمة المرور
    TWOFA_ENABLED = "twofa_enabled"  # تفعيل المصادقة الثنائية
    TWOFA_DISABLED = "twofa_disabled"  # تعطيل المصادقة الثنائية

    # Authorization
    PERMISSION_GRANTED = "permission_granted"  # منح الصلاحية
    PERMISSION_REVOKED = "permission_revoked"  # إلغاء الصلاحية
    ROLE_ASSIGNED = "role_assigned"  # تعيين الدور
    ROLE_REMOVED = "role_removed"  # إزالة الدور

    # Data Operations
    EXPORT = "export"  # تصدير
    IMPORT = "import"  # استيراد
    ARCHIVE = "archive"  # أرشفة
    RESTORE = "restore"  # استعادة
    PURGE = "purge"  # حذف نهائي

    # GlobalGAP Compliance
    AUDIT_STARTED = "audit_started"  # بدء التدقيق
    AUDIT_COMPLETED = "audit_completed"  # اكتمال التدقيق
    FINDING_RECORDED = "finding_recorded"  # تسجيل الملاحظة
    NC_RAISED = "nc_raised"  # رفع عدم المطابقة
    NC_CLOSED = "nc_closed"  # إغلاق عدم المطابقة
    CORRECTIVE_ACTION = "corrective_action"  # إجراء تصحيحي
    CERTIFICATE_ISSUED = "certificate_issued"  # إصدار الشهادة
    CERTIFICATE_SUSPENDED = "certificate_suspended"  # تعليق الشهادة

    # Field Operations
    FIELD_OPERATION = "field_operation"  # عملية الحقل
    IRRIGATION = "irrigation"  # ري
    FERTILIZER_APPLICATION = "fertilizer_application"  # تطبيق السماد
    PESTICIDE_APPLICATION = "pesticide_application"  # تطبيق المبيد
    HARVEST = "harvest"  # حصاد
    SOIL_TEST = "soil_test"  # اختبار التربة
    CROP_PLANTING = "crop_planting"  # زراعة المحصول

    # System Events
    SYSTEM_CONFIG_CHANGE = "system_config_change"  # تغيير تكوين النظام
    SCHEDULED_TASK = "scheduled_task"  # مهمة مجدولة
    INTEGRATION_SYNC = "integration_sync"  # مزامنة التكامل


class AuditCategory(StrEnum):
    """
    Audit event categories for classification.
    فئات أحداث التدقيق للتصنيف
    """

    SECURITY = "security"  # الأمان
    DATA = "data"  # البيانات
    CONFIG = "config"  # التكوين
    ACCESS = "access"  # الوصول
    ADMIN = "admin"  # الإدارة
    COMPLIANCE = "compliance"  # الامتثال
    FIELD_OPS = "field_ops"  # عمليات الحقل
    FINANCIAL = "financial"  # المالية
    SYSTEM = "system"  # النظام
    GLOBALGAP = "globalgap"  # GlobalGAP


class AuditSeverity(StrEnum):
    """
    Audit event severity levels.
    مستويات خطورة حدث التدقيق
    """

    DEBUG = "debug"  # تصحيح
    INFO = "info"  # معلومات
    WARNING = "warning"  # تحذير
    ERROR = "error"  # خطأ
    CRITICAL = "critical"  # حرج


class ActorType(StrEnum):
    """
    Types of actors that can perform auditable actions.
    أنواع الفاعلين الذين يمكنهم تنفيذ إجراءات قابلة للتدقيق
    """

    USER = "user"  # مستخدم
    SERVICE = "service"  # خدمة
    SYSTEM = "system"  # نظام
    API_KEY = "api_key"  # مفتاح API
    ADMIN = "admin"  # مسؤول
    AUDITOR = "auditor"  # مدقق
    AGENT = "agent"  # وكيل ذكاء اصطناعي


class ChangeType(StrEnum):
    """
    Types of field-level changes.
    أنواع التغييرات على مستوى الحقل
    """

    ADDED = "added"  # مضاف
    MODIFIED = "modified"  # معدل
    DELETED = "deleted"  # محذوف


class ExportFormat(StrEnum):
    """
    Supported export formats for audit data.
    صيغ التصدير المدعومة لبيانات التدقيق
    """

    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF = "pdf"
    XML = "xml"


class RetentionPeriod(StrEnum):
    """
    Standard retention periods for audit data.
    فترات الاحتفاظ القياسية لبيانات التدقيق
    """

    SHORT = "short"  # 90 days | 90 يوم
    MEDIUM = "medium"  # 1 year | سنة واحدة
    LONG = "long"  # 3 years | 3 سنوات
    GLOBALGAP = "globalgap"  # 5 years (GlobalGAP requirement) | 5 سنوات
    PERMANENT = "permanent"  # Never delete | لا يحذف أبداً


# Retention period in days
RETENTION_DAYS = {
    RetentionPeriod.SHORT: 90,
    RetentionPeriod.MEDIUM: 365,
    RetentionPeriod.LONG: 1095,  # 3 years
    RetentionPeriod.GLOBALGAP: 1825,  # 5 years (GlobalGAP requirement)
    RetentionPeriod.PERMANENT: -1,  # Never delete
}


# ─────────────────────────────────────────────────────────────────────────────
# Data Classes | فئات البيانات
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class FieldChange:
    """
    Represents a change to a single field.
    يمثل تغيير في حقل واحد
    """

    field_name: str
    field_name_ar: str | None = None
    old_value: Any = None
    new_value: Any = None
    change_type: ChangeType = ChangeType.MODIFIED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "field_name": self.field_name,
            "field_name_ar": self.field_name_ar,
            "old_value": self._serialize_value(self.old_value),
            "new_value": self._serialize_value(self.new_value),
            "change_type": self.change_type.value,
        }

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Serialize value for storage."""
        if isinstance(value, datetime):
            return value.isoformat()
        if hasattr(value, "to_dict"):
            return value.to_dict()
        return value


@dataclass
class AuditMetadata:
    """
    Additional metadata for audit entries.
    بيانات وصفية إضافية لإدخالات التدقيق
    """

    correlation_id: str | None = None
    causation_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    session_id: str | None = None
    request_id: str | None = None

    # Network context
    ip_address: str | None = None
    user_agent: str | None = None
    geo_location: str | None = None

    # GlobalGAP specific
    ggn: str | None = None  # GlobalGAP Number
    audit_session_id: str | None = None
    control_point_id: str | None = None

    # Additional context
    tags: list[str] = field(default_factory=list)
    custom: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "geo_location": self.geo_location,
            "ggn": self.ggn,
            "audit_session_id": self.audit_session_id,
            "control_point_id": self.control_point_id,
            "tags": self.tags,
            "custom": self.custom,
        }


@dataclass
class AuditEntry:
    """
    A single audit log entry.
    إدخال سجل تدقيق واحد

    This is the core data structure for audit trail. Each entry represents
    a single auditable action with full context for compliance requirements.
    """

    # Identity
    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Actor information
    actor_id: str | None = None
    actor_type: ActorType = ActorType.SYSTEM
    actor_name: str | None = None
    actor_name_ar: str | None = None

    # Action information
    action: AuditActionType = AuditActionType.READ
    action_description: str | None = None
    action_description_ar: str | None = None

    # Classification
    category: AuditCategory = AuditCategory.DATA
    severity: AuditSeverity = AuditSeverity.INFO

    # Resource information
    resource_type: str = ""
    resource_id: str = ""
    resource_name: str | None = None
    resource_name_ar: str | None = None

    # Change tracking
    changes: list[FieldChange] = field(default_factory=list)
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None

    # Result
    success: bool = True
    error_code: str | None = None
    error_message: str | None = None
    error_message_ar: str | None = None

    # Metadata
    metadata: AuditMetadata = field(default_factory=AuditMetadata)

    # Hash chain for tamper detection
    prev_hash: str | None = None
    entry_hash: str | None = None

    # Retention
    retention_period: RetentionPeriod = RetentionPeriod.GLOBALGAP
    expires_at: datetime | None = None

    def __post_init__(self):
        """Calculate expiration and hash after initialization."""
        # Calculate expiration date based on retention period
        if self.retention_period != RetentionPeriod.PERMANENT:
            days = RETENTION_DAYS.get(self.retention_period, 1825)
            self.expires_at = self.timestamp + timedelta(days=days)

        # Calculate entry hash
        if not self.entry_hash:
            self.entry_hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calculate SHA-256 hash for tamper detection."""
        hash_data = {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "timestamp": self.timestamp.isoformat(),
            "actor_id": self.actor_id,
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "prev_hash": self.prev_hash,
        }
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage/serialization."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "timestamp": self.timestamp.isoformat(),
            "actor_id": self.actor_id,
            "actor_type": self.actor_type.value,
            "actor_name": self.actor_name,
            "actor_name_ar": self.actor_name_ar,
            "action": self.action.value,
            "action_description": self.action_description,
            "action_description_ar": self.action_description_ar,
            "category": self.category.value,
            "severity": self.severity.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "resource_name": self.resource_name,
            "resource_name_ar": self.resource_name_ar,
            "changes": [c.to_dict() for c in self.changes],
            "before_state": self.before_state,
            "after_state": self.after_state,
            "success": self.success,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "error_message_ar": self.error_message_ar,
            "metadata": self.metadata.to_dict(),
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
            "retention_period": self.retention_period.value,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AuditEntry:
        """Create AuditEntry from dictionary."""
        # Parse changes
        changes = []
        for change_data in data.get("changes", []):
            changes.append(
                FieldChange(
                    field_name=change_data["field_name"],
                    field_name_ar=change_data.get("field_name_ar"),
                    old_value=change_data.get("old_value"),
                    new_value=change_data.get("new_value"),
                    change_type=ChangeType(change_data.get("change_type", "modified")),
                )
            )

        # Parse metadata
        metadata_data = data.get("metadata", {})
        metadata = AuditMetadata(
            correlation_id=metadata_data.get("correlation_id"),
            causation_id=metadata_data.get("causation_id"),
            trace_id=metadata_data.get("trace_id"),
            span_id=metadata_data.get("span_id"),
            session_id=metadata_data.get("session_id"),
            request_id=metadata_data.get("request_id"),
            ip_address=metadata_data.get("ip_address"),
            user_agent=metadata_data.get("user_agent"),
            geo_location=metadata_data.get("geo_location"),
            ggn=metadata_data.get("ggn"),
            audit_session_id=metadata_data.get("audit_session_id"),
            control_point_id=metadata_data.get("control_point_id"),
            tags=metadata_data.get("tags", []),
            custom=metadata_data.get("custom", {}),
        )

        return cls(
            id=data["id"],
            tenant_id=data["tenant_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            actor_id=data.get("actor_id"),
            actor_type=ActorType(data.get("actor_type", "system")),
            actor_name=data.get("actor_name"),
            actor_name_ar=data.get("actor_name_ar"),
            action=AuditActionType(data["action"]),
            action_description=data.get("action_description"),
            action_description_ar=data.get("action_description_ar"),
            category=AuditCategory(data.get("category", "data")),
            severity=AuditSeverity(data.get("severity", "info")),
            resource_type=data["resource_type"],
            resource_id=data["resource_id"],
            resource_name=data.get("resource_name"),
            resource_name_ar=data.get("resource_name_ar"),
            changes=changes,
            before_state=data.get("before_state"),
            after_state=data.get("after_state"),
            success=data.get("success", True),
            error_code=data.get("error_code"),
            error_message=data.get("error_message"),
            error_message_ar=data.get("error_message_ar"),
            metadata=metadata,
            prev_hash=data.get("prev_hash"),
            entry_hash=data.get("entry_hash"),
            retention_period=RetentionPeriod(data.get("retention_period", "globalgap")),
            expires_at=(datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None),
        )


@dataclass
class UserActivitySummary:
    """
    Summary of user activity for reporting.
    ملخص نشاط المستخدم للتقارير
    """

    user_id: str
    user_name: str | None = None
    user_name_ar: str | None = None
    tenant_id: str = ""

    # Period
    period_start: datetime = field(default_factory=lambda: datetime.now(UTC))
    period_end: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Statistics
    total_actions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0

    # Breakdown by action type
    actions_by_type: dict[str, int] = field(default_factory=dict)
    actions_by_category: dict[str, int] = field(default_factory=dict)
    actions_by_resource: dict[str, int] = field(default_factory=dict)

    # Security events
    login_count: int = 0
    failed_login_count: int = 0
    password_changes: int = 0
    permission_changes: int = 0

    # Access patterns
    unique_resources_accessed: int = 0
    most_accessed_resources: list[tuple[str, int]] = field(default_factory=list)
    access_times: list[datetime] = field(default_factory=list)

    # Risk indicators
    unusual_activity_flags: list[str] = field(default_factory=list)
    high_severity_events: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_name_ar": self.user_name_ar,
            "tenant_id": self.tenant_id,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_actions": self.total_actions,
            "successful_actions": self.successful_actions,
            "failed_actions": self.failed_actions,
            "actions_by_type": self.actions_by_type,
            "actions_by_category": self.actions_by_category,
            "actions_by_resource": self.actions_by_resource,
            "login_count": self.login_count,
            "failed_login_count": self.failed_login_count,
            "password_changes": self.password_changes,
            "permission_changes": self.permission_changes,
            "unique_resources_accessed": self.unique_resources_accessed,
            "most_accessed_resources": self.most_accessed_resources,
            "access_times": [t.isoformat() for t in self.access_times],
            "unusual_activity_flags": self.unusual_activity_flags,
            "high_severity_events": self.high_severity_events,
        }


@dataclass
class AuditReport:
    """
    Audit report for compliance and analysis.
    تقرير التدقيق للامتثال والتحليل
    """

    # Report identification
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    title_ar: str = ""
    description: str | None = None
    description_ar: str | None = None

    # Scope
    tenant_id: str = ""
    report_type: str = "compliance"  # compliance, activity, security, globalgap
    period_start: datetime = field(default_factory=lambda: datetime.now(UTC))
    period_end: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Generation info
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    generated_by: str | None = None

    # Statistics
    total_entries: int = 0
    entries_by_category: dict[str, int] = field(default_factory=dict)
    entries_by_severity: dict[str, int] = field(default_factory=dict)
    entries_by_action: dict[str, int] = field(default_factory=dict)

    # User activity
    unique_users: int = 0
    user_summaries: list[UserActivitySummary] = field(default_factory=list)

    # Compliance specific
    compliance_score: float | None = None
    compliance_items_checked: int = 0
    compliance_items_passed: int = 0
    non_conformances: list[dict[str, Any]] = field(default_factory=list)

    # GlobalGAP specific
    ggn: str | None = None
    audit_session_id: str | None = None
    checklist_completion: float | None = None
    major_musts_compliant: int = 0
    minor_musts_compliant: int = 0

    # Security
    security_incidents: int = 0
    high_risk_events: list[dict[str, Any]] = field(default_factory=list)

    # Data
    sample_entries: list[AuditEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "title_ar": self.title_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "tenant_id": self.tenant_id,
            "report_type": self.report_type,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "generated_at": self.generated_at.isoformat(),
            "generated_by": self.generated_by,
            "total_entries": self.total_entries,
            "entries_by_category": self.entries_by_category,
            "entries_by_severity": self.entries_by_severity,
            "entries_by_action": self.entries_by_action,
            "unique_users": self.unique_users,
            "user_summaries": [s.to_dict() for s in self.user_summaries],
            "compliance_score": self.compliance_score,
            "compliance_items_checked": self.compliance_items_checked,
            "compliance_items_passed": self.compliance_items_passed,
            "non_conformances": self.non_conformances,
            "ggn": self.ggn,
            "audit_session_id": self.audit_session_id,
            "checklist_completion": self.checklist_completion,
            "major_musts_compliant": self.major_musts_compliant,
            "minor_musts_compliant": self.minor_musts_compliant,
            "security_incidents": self.security_incidents,
            "high_risk_events": self.high_risk_events,
            "sample_entries": [e.to_dict() for e in self.sample_entries],
        }


@dataclass
class RetentionPolicy:
    """
    Data retention policy configuration.
    تكوين سياسة الاحتفاظ بالبيانات
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    name_ar: str = ""
    description: str | None = None
    description_ar: str | None = None

    # Scope
    tenant_id: str | None = None  # None = global policy
    category: AuditCategory | None = None  # None = all categories
    resource_type: str | None = None  # None = all resources

    # Retention settings
    retention_period: RetentionPeriod = RetentionPeriod.GLOBALGAP
    retention_days: int = 1825  # 5 years for GlobalGAP

    # Actions on expiration
    archive_before_delete: bool = True
    archive_location: str | None = None  # S3 bucket, etc.
    notify_before_delete_days: int = 30

    # Status
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "tenant_id": self.tenant_id,
            "category": self.category.value if self.category else None,
            "resource_type": self.resource_type,
            "retention_period": self.retention_period.value,
            "retention_days": self.retention_days,
            "archive_before_delete": self.archive_before_delete,
            "archive_location": self.archive_location,
            "notify_before_delete_days": self.notify_before_delete_days,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
        }


@dataclass
class RetentionJob:
    """
    Retention job execution record.
    سجل تنفيذ مهمة الاحتفاظ
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    policy_id: str = ""

    # Execution info
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    status: str = "running"  # running, completed, failed

    # Results
    entries_processed: int = 0
    entries_archived: int = 0
    entries_deleted: int = 0
    entries_failed: int = 0

    # Errors
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "policy_id": self.policy_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "entries_processed": self.entries_processed,
            "entries_archived": self.entries_archived,
            "entries_deleted": self.entries_deleted,
            "entries_failed": self.entries_failed,
            "errors": self.errors,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Query Models | نماذج الاستعلام
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class AuditQueryFilter:
    """
    Filter options for querying audit entries.
    خيارات التصفية للاستعلام عن إدخالات التدقيق
    """

    tenant_id: str | None = None
    actor_id: str | None = None
    actor_type: ActorType | None = None
    action: AuditActionType | None = None
    actions: list[AuditActionType] | None = None
    category: AuditCategory | None = None
    categories: list[AuditCategory] | None = None
    severity: AuditSeverity | None = None
    min_severity: AuditSeverity | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    success: bool | None = None

    # Time range
    start_date: datetime | None = None
    end_date: datetime | None = None

    # GlobalGAP specific
    ggn: str | None = None
    audit_session_id: str | None = None
    control_point_id: str | None = None

    # Metadata
    correlation_id: str | None = None
    tags: list[str] | None = None

    # Pagination
    limit: int = 100
    offset: int = 0
    order_by: str = "timestamp"
    order_direction: str = "desc"  # asc or desc

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tenant_id": self.tenant_id,
            "actor_id": self.actor_id,
            "actor_type": self.actor_type.value if self.actor_type else None,
            "action": self.action.value if self.action else None,
            "actions": [a.value for a in self.actions] if self.actions else None,
            "category": self.category.value if self.category else None,
            "categories": [c.value for c in self.categories] if self.categories else None,
            "severity": self.severity.value if self.severity else None,
            "min_severity": self.min_severity.value if self.min_severity else None,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "success": self.success,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "ggn": self.ggn,
            "audit_session_id": self.audit_session_id,
            "control_point_id": self.control_point_id,
            "correlation_id": self.correlation_id,
            "tags": self.tags,
            "limit": self.limit,
            "offset": self.offset,
            "order_by": self.order_by,
            "order_direction": self.order_direction,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Bilingual Labels | تسميات ثنائية اللغة
# ─────────────────────────────────────────────────────────────────────────────


ACTION_LABELS = {
    AuditActionType.CREATE: {"en": "Create", "ar": "إنشاء"},
    AuditActionType.READ: {"en": "Read", "ar": "قراءة"},
    AuditActionType.UPDATE: {"en": "Update", "ar": "تحديث"},
    AuditActionType.DELETE: {"en": "Delete", "ar": "حذف"},
    AuditActionType.LOGIN: {"en": "Login", "ar": "تسجيل الدخول"},
    AuditActionType.LOGOUT: {"en": "Logout", "ar": "تسجيل الخروج"},
    AuditActionType.LOGIN_FAILED: {"en": "Login Failed", "ar": "فشل تسجيل الدخول"},
    AuditActionType.PASSWORD_CHANGE: {"en": "Password Change", "ar": "تغيير كلمة المرور"},
    AuditActionType.PASSWORD_RESET: {"en": "Password Reset", "ar": "إعادة تعيين كلمة المرور"},
    AuditActionType.TWOFA_ENABLED: {"en": "2FA Enabled", "ar": "تفعيل المصادقة الثنائية"},
    AuditActionType.TWOFA_DISABLED: {"en": "2FA Disabled", "ar": "تعطيل المصادقة الثنائية"},
    AuditActionType.PERMISSION_GRANTED: {"en": "Permission Granted", "ar": "منح الصلاحية"},
    AuditActionType.PERMISSION_REVOKED: {"en": "Permission Revoked", "ar": "إلغاء الصلاحية"},
    AuditActionType.ROLE_ASSIGNED: {"en": "Role Assigned", "ar": "تعيين الدور"},
    AuditActionType.ROLE_REMOVED: {"en": "Role Removed", "ar": "إزالة الدور"},
    AuditActionType.EXPORT: {"en": "Export", "ar": "تصدير"},
    AuditActionType.IMPORT: {"en": "Import", "ar": "استيراد"},
    AuditActionType.ARCHIVE: {"en": "Archive", "ar": "أرشفة"},
    AuditActionType.RESTORE: {"en": "Restore", "ar": "استعادة"},
    AuditActionType.PURGE: {"en": "Purge", "ar": "حذف نهائي"},
    AuditActionType.AUDIT_STARTED: {"en": "Audit Started", "ar": "بدء التدقيق"},
    AuditActionType.AUDIT_COMPLETED: {"en": "Audit Completed", "ar": "اكتمال التدقيق"},
    AuditActionType.FINDING_RECORDED: {"en": "Finding Recorded", "ar": "تسجيل الملاحظة"},
    AuditActionType.NC_RAISED: {"en": "Non-Conformance Raised", "ar": "رفع عدم المطابقة"},
    AuditActionType.NC_CLOSED: {"en": "Non-Conformance Closed", "ar": "إغلاق عدم المطابقة"},
    AuditActionType.CORRECTIVE_ACTION: {"en": "Corrective Action", "ar": "إجراء تصحيحي"},
    AuditActionType.CERTIFICATE_ISSUED: {"en": "Certificate Issued", "ar": "إصدار الشهادة"},
    AuditActionType.CERTIFICATE_SUSPENDED: {"en": "Certificate Suspended", "ar": "تعليق الشهادة"},
    AuditActionType.FIELD_OPERATION: {"en": "Field Operation", "ar": "عملية الحقل"},
    AuditActionType.IRRIGATION: {"en": "Irrigation", "ar": "ري"},
    AuditActionType.FERTILIZER_APPLICATION: {"en": "Fertilizer Application", "ar": "تطبيق السماد"},
    AuditActionType.PESTICIDE_APPLICATION: {"en": "Pesticide Application", "ar": "تطبيق المبيد"},
    AuditActionType.HARVEST: {"en": "Harvest", "ar": "حصاد"},
    AuditActionType.SOIL_TEST: {"en": "Soil Test", "ar": "اختبار التربة"},
    AuditActionType.CROP_PLANTING: {"en": "Crop Planting", "ar": "زراعة المحصول"},
    AuditActionType.SYSTEM_CONFIG_CHANGE: {
        "en": "System Config Change",
        "ar": "تغيير تكوين النظام",
    },
    AuditActionType.SCHEDULED_TASK: {"en": "Scheduled Task", "ar": "مهمة مجدولة"},
    AuditActionType.INTEGRATION_SYNC: {"en": "Integration Sync", "ar": "مزامنة التكامل"},
}

CATEGORY_LABELS = {
    AuditCategory.SECURITY: {"en": "Security", "ar": "الأمان"},
    AuditCategory.DATA: {"en": "Data", "ar": "البيانات"},
    AuditCategory.CONFIG: {"en": "Configuration", "ar": "التكوين"},
    AuditCategory.ACCESS: {"en": "Access", "ar": "الوصول"},
    AuditCategory.ADMIN: {"en": "Administration", "ar": "الإدارة"},
    AuditCategory.COMPLIANCE: {"en": "Compliance", "ar": "الامتثال"},
    AuditCategory.FIELD_OPS: {"en": "Field Operations", "ar": "عمليات الحقل"},
    AuditCategory.FINANCIAL: {"en": "Financial", "ar": "المالية"},
    AuditCategory.SYSTEM: {"en": "System", "ar": "النظام"},
    AuditCategory.GLOBALGAP: {"en": "GlobalGAP", "ar": "GlobalGAP"},
}

SEVERITY_LABELS = {
    AuditSeverity.DEBUG: {"en": "Debug", "ar": "تصحيح"},
    AuditSeverity.INFO: {"en": "Information", "ar": "معلومات"},
    AuditSeverity.WARNING: {"en": "Warning", "ar": "تحذير"},
    AuditSeverity.ERROR: {"en": "Error", "ar": "خطأ"},
    AuditSeverity.CRITICAL: {"en": "Critical", "ar": "حرج"},
}


def get_action_label(action: AuditActionType, language: str = "en") -> str:
    """Get localized label for action type."""
    labels = ACTION_LABELS.get(action, {"en": action.value, "ar": action.value})
    return labels.get(language, labels["en"])


def get_category_label(category: AuditCategory, language: str = "en") -> str:
    """Get localized label for category."""
    labels = CATEGORY_LABELS.get(category, {"en": category.value, "ar": category.value})
    return labels.get(language, labels["en"])


def get_severity_label(severity: AuditSeverity, language: str = "en") -> str:
    """Get localized label for severity."""
    labels = SEVERITY_LABELS.get(severity, {"en": severity.value, "ar": severity.value})
    return labels.get(language, labels["en"])
