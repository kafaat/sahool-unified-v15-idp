"""
SAHOOL Audit Trail Module
=========================
وحدة مسار التدقيق

Comprehensive audit trail management for the SAHOOL platform supporting:
- Action logging for compliance | تسجيل الإجراءات للامتثال
- Change tracking with automatic diff | تتبع التغييرات مع المقارنة التلقائية
- User activity reports | تقارير نشاط المستخدم
- Export for audits (JSON, CSV, Excel, XML) | التصدير للتدقيق
- Retention management with GlobalGAP support | إدارة الاحتفاظ مع دعم GlobalGAP

GlobalGAP Compliance:
- 5-year record retention (IFA v6 requirement)
- Field operation traceability
- Audit session tracking
- Non-conformance management

Example Usage:
    # Basic logging
    from shared.audit_trail import log_action, log_change, AuditActionType

    # Log a simple action
    entry = log_action(
        action=AuditActionType.CREATE,
        resource_type="field",
        resource_id="field-123",
        actor_id="user-456",
    )

    # Log with change tracking
    entry = log_change(
        action=AuditActionType.UPDATE,
        resource_type="field",
        resource_id="field-123",
        before={"name": "Old Name"},
        after={"name": "New Name"},
        actor_id="user-456",
    )

    # GlobalGAP event logging
    from shared.audit_trail import log_globalgap_event

    entry = log_globalgap_event(
        action=AuditActionType.FINDING_RECORDED,
        resource_type="control_point",
        resource_id="AF.1.1.1",
        ggn="4012345678901",
        audit_session_id="audit-2024-001",
    )

    # Generate reports
    from shared.audit_trail import (
        AuditTrailLogger,
        AuditReportGenerator,
        generate_globalgap_report,
    )

    logger = get_audit_logger("farm-001")
    entries = logger.get_entries()

    generator = AuditReportGenerator(entries, language="ar")
    report = generator.generate_globalgap_report(
        ggn="4012345678901",
        period_start=datetime(2024, 1, 1),
        period_end=datetime(2024, 12, 31),
    )

    # Export to Excel
    excel_data = generator.export_to_excel(report=report)

    # Retention management
    from shared.audit_trail import get_retention_manager, run_retention

    manager = get_retention_manager()
    expiring = manager.get_entries_expiring_soon(days=30)
    job = await manager.run_retention(dry_run=True)

Author: SAHOOL Platform Team
Version: 16.0.0
Updated: January 2026
"""

# Models | النماذج
# Logger | المسجل
from .logger import (
    AuditTrailLogger,
    compute_changes,
    get_audit_logger,
    # Convenience Functions
    log_action,
    log_change,
    log_globalgap_event,
    log_login,
)
from .models import (
    ACTION_LABELS,
    CATEGORY_LABELS,
    # Constants
    RETENTION_DAYS,
    SEVERITY_LABELS,
    ActorType,
    # Enums
    AuditActionType,
    AuditCategory,
    AuditEntry,
    AuditMetadata,
    AuditQueryFilter,
    AuditReport,
    AuditSeverity,
    ChangeType,
    ExportFormat,
    # Data Classes
    FieldChange,
    RetentionJob,
    RetentionPeriod,
    RetentionPolicy,
    UserActivitySummary,
    # Helper Functions
    get_action_label,
    get_category_label,
    get_severity_label,
)

# Reporter | مولد التقارير
from .reporter import (
    AuditReportGenerator,
    export_entries,
    # Convenience Functions
    generate_activity_report,
    generate_compliance_report,
    generate_globalgap_report,
)

# Retention | الاحتفاظ
from .retention import (
    RetentionManager,
    get_default_policies,
    get_entries_expiring_soon,
    get_expired_entries,
    get_retention_manager,
    get_retention_summary,
    # Convenience Functions
    run_retention,
)

__all__ = [
    # ─────────────────────────────────────────────────────────────────────────
    # Enums | التعدادات
    # ─────────────────────────────────────────────────────────────────────────
    "AuditActionType",
    "AuditCategory",
    "AuditSeverity",
    "ActorType",
    "ChangeType",
    "ExportFormat",
    "RetentionPeriod",
    # ─────────────────────────────────────────────────────────────────────────
    # Data Classes | فئات البيانات
    # ─────────────────────────────────────────────────────────────────────────
    "FieldChange",
    "AuditMetadata",
    "AuditEntry",
    "UserActivitySummary",
    "AuditReport",
    "RetentionPolicy",
    "RetentionJob",
    "AuditQueryFilter",
    # ─────────────────────────────────────────────────────────────────────────
    # Constants | الثوابت
    # ─────────────────────────────────────────────────────────────────────────
    "RETENTION_DAYS",
    "ACTION_LABELS",
    "CATEGORY_LABELS",
    "SEVERITY_LABELS",
    # ─────────────────────────────────────────────────────────────────────────
    # Helper Functions | دوال مساعدة
    # ─────────────────────────────────────────────────────────────────────────
    "get_action_label",
    "get_category_label",
    "get_severity_label",
    # ─────────────────────────────────────────────────────────────────────────
    # Logger Classes | فئات المسجل
    # ─────────────────────────────────────────────────────────────────────────
    "AuditTrailLogger",
    "compute_changes",
    "get_audit_logger",
    # ─────────────────────────────────────────────────────────────────────────
    # Logger Convenience Functions | دوال المسجل المساعدة
    # ─────────────────────────────────────────────────────────────────────────
    "log_action",
    "log_change",
    "log_login",
    "log_globalgap_event",
    # ─────────────────────────────────────────────────────────────────────────
    # Reporter Classes | فئات مولد التقارير
    # ─────────────────────────────────────────────────────────────────────────
    "AuditReportGenerator",
    # ─────────────────────────────────────────────────────────────────────────
    # Reporter Convenience Functions | دوال التقارير المساعدة
    # ─────────────────────────────────────────────────────────────────────────
    "generate_activity_report",
    "generate_compliance_report",
    "generate_globalgap_report",
    "export_entries",
    # ─────────────────────────────────────────────────────────────────────────
    # Retention Classes | فئات الاحتفاظ
    # ─────────────────────────────────────────────────────────────────────────
    "RetentionManager",
    "get_default_policies",
    "get_retention_manager",
    # ─────────────────────────────────────────────────────────────────────────
    # Retention Convenience Functions | دوال الاحتفاظ المساعدة
    # ─────────────────────────────────────────────────────────────────────────
    "run_retention",
    "get_expired_entries",
    "get_entries_expiring_soon",
    "get_retention_summary",
]

__version__ = "16.0.0"
