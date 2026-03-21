"""
SAHOOL Audit Trail Logger
=========================
مسجل مسار التدقيق

Centralized audit logging with support for:
- Action logging for compliance
- Change tracking with automatic diff
- Hash chain for tamper detection
- Async batch writing
- Multiple storage backends

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import structlog

from .models import (
    ActorType,
    AuditActionType,
    AuditCategory,
    AuditEntry,
    AuditMetadata,
    AuditQueryFilter,
    AuditSeverity,
    ChangeType,
    FieldChange,
    RetentionPeriod,
)

logger = structlog.get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Change Detection | كشف التغييرات
# ─────────────────────────────────────────────────────────────────────────────


def compute_changes(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    exclude_fields: list[str] | None = None,
    field_labels_ar: dict[str, str] | None = None,
) -> list[FieldChange]:
    """
    Compute field-level changes between two states.
    حساب التغييرات على مستوى الحقل بين حالتين

    Args:
        before: State before the change (None for creates)
        after: State after the change (None for deletes)
        exclude_fields: Fields to exclude from change tracking
        field_labels_ar: Arabic labels for field names

    Returns:
        List of FieldChange objects
    """
    exclude = set(exclude_fields or [])
    exclude.update(["updated_at", "created_at", "password", "password_hash", "token"])
    labels_ar = field_labels_ar or {}

    changes: list[FieldChange] = []

    if before is None and after is not None:
        # Create - all fields are new
        for key, value in after.items():
            if key not in exclude:
                changes.append(
                    FieldChange(
                        field_name=key,
                        field_name_ar=labels_ar.get(key),
                        old_value=None,
                        new_value=value,
                        change_type=ChangeType.ADDED,
                    )
                )
    elif before is not None and after is None:
        # Delete - all fields are removed
        for key, value in before.items():
            if key not in exclude:
                changes.append(
                    FieldChange(
                        field_name=key,
                        field_name_ar=labels_ar.get(key),
                        old_value=value,
                        new_value=None,
                        change_type=ChangeType.DELETED,
                    )
                )
    elif before is not None and after is not None:
        # Update - compare fields
        all_keys = set(before.keys()) | set(after.keys())
        for key in all_keys:
            if key in exclude:
                continue

            old_val = before.get(key)
            new_val = after.get(key)

            if key not in before:
                changes.append(
                    FieldChange(
                        field_name=key,
                        field_name_ar=labels_ar.get(key),
                        old_value=None,
                        new_value=new_val,
                        change_type=ChangeType.ADDED,
                    )
                )
            elif key not in after:
                changes.append(
                    FieldChange(
                        field_name=key,
                        field_name_ar=labels_ar.get(key),
                        old_value=old_val,
                        new_value=None,
                        change_type=ChangeType.DELETED,
                    )
                )
            elif old_val != new_val:
                changes.append(
                    FieldChange(
                        field_name=key,
                        field_name_ar=labels_ar.get(key),
                        old_value=old_val,
                        new_value=new_val,
                        change_type=ChangeType.MODIFIED,
                    )
                )

    return changes


# ─────────────────────────────────────────────────────────────────────────────
# Audit Logger | مسجل التدقيق
# ─────────────────────────────────────────────────────────────────────────────


class AuditTrailLogger:
    """
    Centralized audit trail logger.
    مسجل مسار التدقيق المركزي

    Provides comprehensive audit logging with:
    - Action logging for compliance | تسجيل الإجراءات للامتثال
    - Automatic change detection | كشف التغييرات التلقائي
    - Hash chain for tamper detection | سلسلة التجزئة لكشف التلاعب
    - Async batch writing | الكتابة الدفعية غير المتزامنة
    - Multiple storage backends | خلفيات تخزين متعددة

    Example:
        logger = AuditTrailLogger(tenant_id="farm-001")

        # Log a simple action
        entry = logger.log_action(
            action=AuditActionType.CREATE,
            resource_type="field",
            resource_id="field-123",
            actor_id="user-456",
        )

        # Log with change tracking
        entry = logger.log_change(
            action=AuditActionType.UPDATE,
            resource_type="field",
            resource_id="field-123",
            before={"name": "Old Name"},
            after={"name": "New Name"},
            actor_id="user-456",
        )

        # Get audit history
        history = logger.get_history(resource_type="field", resource_id="field-123")
    """

    def __init__(
        self,
        tenant_id: str,
        storage_path: str | None = None,
        max_buffer_size: int = 100,
        flush_interval_seconds: float = 30.0,
        enable_hash_chain: bool = True,
        default_retention: RetentionPeriod = RetentionPeriod.GLOBALGAP,
        on_entry_callback: Callable[[AuditEntry], None] | None = None,
        exclude_fields: list[str] | None = None,
    ):
        """
        Initialize AuditTrailLogger.

        Args:
            tenant_id: Tenant identifier | معرف المستأجر
            storage_path: Path for file-based storage | مسار التخزين
            max_buffer_size: Max entries before auto-flush | الحد الأقصى للمخزن المؤقت
            flush_interval_seconds: Auto-flush interval | فترة التفريغ التلقائي
            enable_hash_chain: Enable hash chain for tamper detection | تفعيل سلسلة التجزئة
            default_retention: Default retention period | فترة الاحتفاظ الافتراضية
            on_entry_callback: Callback for each entry | رد الاتصال لكل إدخال
            exclude_fields: Fields to exclude from change tracking | الحقول المستبعدة
        """
        self.tenant_id = tenant_id
        self.storage_path = storage_path
        self.max_buffer_size = max_buffer_size
        self.flush_interval_seconds = flush_interval_seconds
        self.enable_hash_chain = enable_hash_chain
        self.default_retention = default_retention
        self.on_entry_callback = on_entry_callback
        self.exclude_fields = exclude_fields or []

        # Internal state
        self._buffer: list[AuditEntry] = []
        self._entries: list[AuditEntry] = []
        self._lock = asyncio.Lock()
        self._last_hash: str | None = None

        # Metrics
        self._total_entries = 0
        self._entries_by_category: dict[str, int] = {}
        self._entries_by_action: dict[str, int] = {}
        self._entries_by_severity: dict[str, int] = {}

        # Ensure storage directory exists
        if storage_path:
            Path(storage_path).mkdir(parents=True, exist_ok=True)

        logger.info(
            "audit_logger_initialized",
            tenant_id=tenant_id,
            storage_path=storage_path,
            enable_hash_chain=enable_hash_chain,
        )

    def _create_entry(
        self,
        action: AuditActionType,
        resource_type: str,
        resource_id: str,
        actor_id: str | None = None,
        actor_type: ActorType = ActorType.USER,
        actor_name: str | None = None,
        actor_name_ar: str | None = None,
        category: AuditCategory | None = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        action_description: str | None = None,
        action_description_ar: str | None = None,
        resource_name: str | None = None,
        resource_name_ar: str | None = None,
        changes: list[FieldChange] | None = None,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
        success: bool = True,
        error_code: str | None = None,
        error_message: str | None = None,
        error_message_ar: str | None = None,
        metadata: AuditMetadata | None = None,
        retention_period: RetentionPeriod | None = None,
    ) -> AuditEntry:
        """Create a new audit entry with hash chain."""
        # Auto-determine category if not provided
        if category is None:
            category = self._infer_category(action)

        # Create entry
        entry = AuditEntry(
            id=str(uuid4()),
            tenant_id=self.tenant_id,
            timestamp=datetime.now(UTC),
            actor_id=actor_id,
            actor_type=actor_type,
            actor_name=actor_name,
            actor_name_ar=actor_name_ar,
            action=action,
            action_description=action_description,
            action_description_ar=action_description_ar,
            category=category,
            severity=severity,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            resource_name_ar=resource_name_ar,
            changes=changes or [],
            before_state=before_state,
            after_state=after_state,
            success=success,
            error_code=error_code,
            error_message=error_message,
            error_message_ar=error_message_ar,
            metadata=metadata or AuditMetadata(),
            retention_period=retention_period or self.default_retention,
            prev_hash=self._last_hash if self.enable_hash_chain else None,
        )

        # Update hash chain
        if self.enable_hash_chain:
            self._last_hash = entry.entry_hash

        # Update metrics
        self._total_entries += 1
        cat_key = category.value
        self._entries_by_category[cat_key] = self._entries_by_category.get(cat_key, 0) + 1
        action_key = action.value
        self._entries_by_action[action_key] = self._entries_by_action.get(action_key, 0) + 1
        sev_key = severity.value
        self._entries_by_severity[sev_key] = self._entries_by_severity.get(sev_key, 0) + 1

        # Add to buffer and storage
        self._buffer.append(entry)
        self._entries.append(entry)

        # Trigger callback if set
        if self.on_entry_callback:
            try:
                self.on_entry_callback(entry)
            except Exception as e:
                logger.error("audit_callback_error", error=str(e))

        # Auto-flush if buffer is full
        if len(self._buffer) >= self.max_buffer_size:
            asyncio.create_task(self.flush())

        # Log entry
        logger.info(
            "audit_entry_created",
            entry_id=entry.id,
            action=action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_id=actor_id,
        )

        return entry

    def _infer_category(self, action: AuditActionType) -> AuditCategory:
        """Infer category from action type."""
        security_actions = {
            AuditActionType.LOGIN,
            AuditActionType.LOGOUT,
            AuditActionType.LOGIN_FAILED,
            AuditActionType.PASSWORD_CHANGE,
            AuditActionType.PASSWORD_RESET,
            AuditActionType.TWOFA_ENABLED,
            AuditActionType.TWOFA_DISABLED,
            AuditActionType.PERMISSION_GRANTED,
            AuditActionType.PERMISSION_REVOKED,
            AuditActionType.ROLE_ASSIGNED,
            AuditActionType.ROLE_REMOVED,
        }

        compliance_actions = {
            AuditActionType.AUDIT_STARTED,
            AuditActionType.AUDIT_COMPLETED,
            AuditActionType.FINDING_RECORDED,
            AuditActionType.NC_RAISED,
            AuditActionType.NC_CLOSED,
            AuditActionType.CORRECTIVE_ACTION,
            AuditActionType.CERTIFICATE_ISSUED,
            AuditActionType.CERTIFICATE_SUSPENDED,
        }

        field_ops_actions = {
            AuditActionType.FIELD_OPERATION,
            AuditActionType.IRRIGATION,
            AuditActionType.FERTILIZER_APPLICATION,
            AuditActionType.PESTICIDE_APPLICATION,
            AuditActionType.HARVEST,
            AuditActionType.SOIL_TEST,
            AuditActionType.CROP_PLANTING,
        }

        system_actions = {
            AuditActionType.SYSTEM_CONFIG_CHANGE,
            AuditActionType.SCHEDULED_TASK,
            AuditActionType.INTEGRATION_SYNC,
        }

        data_actions = {
            AuditActionType.CREATE,
            AuditActionType.READ,
            AuditActionType.UPDATE,
            AuditActionType.DELETE,
            AuditActionType.EXPORT,
            AuditActionType.IMPORT,
            AuditActionType.ARCHIVE,
            AuditActionType.RESTORE,
            AuditActionType.PURGE,
        }

        if action in security_actions:
            return AuditCategory.SECURITY
        if action in compliance_actions:
            return AuditCategory.COMPLIANCE
        if action in field_ops_actions:
            return AuditCategory.FIELD_OPS
        if action in system_actions:
            return AuditCategory.SYSTEM
        if action in data_actions:
            return AuditCategory.DATA

        return AuditCategory.DATA

    # ─────────────────────────────────────────────────────────────────────────
    # Public Logging Methods | طرق التسجيل العامة
    # ─────────────────────────────────────────────────────────────────────────

    def log_action(
        self,
        action: AuditActionType,
        resource_type: str,
        resource_id: str,
        actor_id: str | None = None,
        actor_type: ActorType = ActorType.USER,
        actor_name: str | None = None,
        actor_name_ar: str | None = None,
        category: AuditCategory | None = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        action_description: str | None = None,
        action_description_ar: str | None = None,
        resource_name: str | None = None,
        resource_name_ar: str | None = None,
        success: bool = True,
        error_code: str | None = None,
        error_message: str | None = None,
        error_message_ar: str | None = None,
        metadata: AuditMetadata | None = None,
        retention_period: RetentionPeriod | None = None,
    ) -> AuditEntry:
        """
        Log a simple action without change tracking.
        تسجيل إجراء بسيط بدون تتبع التغييرات

        Args:
            action: Action type | نوع الإجراء
            resource_type: Type of resource | نوع المورد
            resource_id: Resource identifier | معرف المورد
            actor_id: Actor identifier | معرف الفاعل
            actor_type: Type of actor | نوع الفاعل
            actor_name: Actor name (English) | اسم الفاعل
            actor_name_ar: Actor name (Arabic) | اسم الفاعل بالعربية
            category: Event category | فئة الحدث
            severity: Event severity | خطورة الحدث
            action_description: Description (English) | الوصف
            action_description_ar: Description (Arabic) | الوصف بالعربية
            resource_name: Resource name (English) | اسم المورد
            resource_name_ar: Resource name (Arabic) | اسم المورد بالعربية
            success: Whether action succeeded | نجاح الإجراء
            error_code: Error code if failed | رمز الخطأ
            error_message: Error message (English) | رسالة الخطأ
            error_message_ar: Error message (Arabic) | رسالة الخطأ بالعربية
            metadata: Additional metadata | بيانات وصفية إضافية
            retention_period: Retention period | فترة الاحتفاظ

        Returns:
            Created AuditEntry
        """
        return self._create_entry(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_id=actor_id,
            actor_type=actor_type,
            actor_name=actor_name,
            actor_name_ar=actor_name_ar,
            category=category,
            severity=severity,
            action_description=action_description,
            action_description_ar=action_description_ar,
            resource_name=resource_name,
            resource_name_ar=resource_name_ar,
            success=success,
            error_code=error_code,
            error_message=error_message,
            error_message_ar=error_message_ar,
            metadata=metadata,
            retention_period=retention_period,
        )

    def log_change(
        self,
        action: AuditActionType,
        resource_type: str,
        resource_id: str,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        actor_id: str | None = None,
        actor_type: ActorType = ActorType.USER,
        actor_name: str | None = None,
        actor_name_ar: str | None = None,
        category: AuditCategory | None = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        action_description: str | None = None,
        action_description_ar: str | None = None,
        resource_name: str | None = None,
        resource_name_ar: str | None = None,
        exclude_fields: list[str] | None = None,
        field_labels_ar: dict[str, str] | None = None,
        success: bool = True,
        error_code: str | None = None,
        error_message: str | None = None,
        error_message_ar: str | None = None,
        metadata: AuditMetadata | None = None,
        retention_period: RetentionPeriod | None = None,
    ) -> AuditEntry:
        """
        Log an action with automatic change tracking.
        تسجيل إجراء مع تتبع التغييرات التلقائي

        Args:
            action: Action type | نوع الإجراء
            resource_type: Type of resource | نوع المورد
            resource_id: Resource identifier | معرف المورد
            before: State before change | الحالة قبل التغيير
            after: State after change | الحالة بعد التغيير
            actor_id: Actor identifier | معرف الفاعل
            actor_type: Type of actor | نوع الفاعل
            actor_name: Actor name (English) | اسم الفاعل
            actor_name_ar: Actor name (Arabic) | اسم الفاعل بالعربية
            category: Event category | فئة الحدث
            severity: Event severity | خطورة الحدث
            action_description: Description (English) | الوصف
            action_description_ar: Description (Arabic) | الوصف بالعربية
            resource_name: Resource name (English) | اسم المورد
            resource_name_ar: Resource name (Arabic) | اسم المورد بالعربية
            exclude_fields: Fields to exclude | الحقول المستبعدة
            field_labels_ar: Arabic labels for fields | التسميات العربية
            success: Whether action succeeded | نجاح الإجراء
            error_code: Error code if failed | رمز الخطأ
            error_message: Error message (English) | رسالة الخطأ
            error_message_ar: Error message (Arabic) | رسالة الخطأ بالعربية
            metadata: Additional metadata | بيانات وصفية إضافية
            retention_period: Retention period | فترة الاحتفاظ

        Returns:
            Created AuditEntry
        """
        # Compute changes
        all_exclude = list(set(self.exclude_fields + (exclude_fields or [])))
        changes = compute_changes(before, after, all_exclude, field_labels_ar)

        return self._create_entry(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_id=actor_id,
            actor_type=actor_type,
            actor_name=actor_name,
            actor_name_ar=actor_name_ar,
            category=category,
            severity=severity,
            action_description=action_description,
            action_description_ar=action_description_ar,
            resource_name=resource_name,
            resource_name_ar=resource_name_ar,
            changes=changes,
            before_state=before,
            after_state=after,
            success=success,
            error_code=error_code,
            error_message=error_message,
            error_message_ar=error_message_ar,
            metadata=metadata,
            retention_period=retention_period,
        )

    def log_login(
        self,
        user_id: str,
        success: bool = True,
        user_name: str | None = None,
        user_name_ar: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        error_message: str | None = None,
        error_message_ar: str | None = None,
    ) -> AuditEntry:
        """
        Log a login attempt.
        تسجيل محاولة تسجيل الدخول
        """
        metadata = AuditMetadata(ip_address=ip_address, user_agent=user_agent)

        action = AuditActionType.LOGIN if success else AuditActionType.LOGIN_FAILED
        severity = AuditSeverity.INFO if success else AuditSeverity.WARNING

        desc_en = "Successful login" if success else "Failed login attempt"
        desc_ar = "تسجيل دخول ناجح" if success else "محاولة تسجيل دخول فاشلة"

        return self.log_action(
            action=action,
            resource_type="user",
            resource_id=user_id,
            actor_id=user_id,
            actor_type=ActorType.USER,
            actor_name=user_name,
            actor_name_ar=user_name_ar,
            category=AuditCategory.SECURITY,
            severity=severity,
            action_description=desc_en,
            action_description_ar=desc_ar,
            success=success,
            error_message=error_message,
            error_message_ar=error_message_ar,
            metadata=metadata,
        )

    def log_logout(
        self,
        user_id: str,
        user_name: str | None = None,
        user_name_ar: str | None = None,
    ) -> AuditEntry:
        """
        Log a logout.
        تسجيل الخروج
        """
        return self.log_action(
            action=AuditActionType.LOGOUT,
            resource_type="user",
            resource_id=user_id,
            actor_id=user_id,
            actor_type=ActorType.USER,
            actor_name=user_name,
            actor_name_ar=user_name_ar,
            category=AuditCategory.SECURITY,
            severity=AuditSeverity.INFO,
            action_description="User logged out",
            action_description_ar="تسجيل خروج المستخدم",
        )

    def log_globalgap_event(
        self,
        action: AuditActionType,
        resource_type: str,
        resource_id: str,
        ggn: str,
        audit_session_id: str | None = None,
        control_point_id: str | None = None,
        actor_id: str | None = None,
        actor_name: str | None = None,
        actor_name_ar: str | None = None,
        action_description: str | None = None,
        action_description_ar: str | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        success: bool = True,
    ) -> AuditEntry:
        """
        Log a GlobalGAP compliance event.
        تسجيل حدث امتثال GlobalGAP
        """
        metadata = AuditMetadata(
            ggn=ggn,
            audit_session_id=audit_session_id,
            control_point_id=control_point_id,
        )

        # Compute changes if before/after provided
        changes = []
        if before is not None or after is not None:
            changes = compute_changes(before, after)

        return self._create_entry(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            actor_id=actor_id,
            actor_type=ActorType.AUDITOR if actor_id else ActorType.SYSTEM,
            actor_name=actor_name,
            actor_name_ar=actor_name_ar,
            category=AuditCategory.GLOBALGAP,
            severity=AuditSeverity.INFO,
            action_description=action_description,
            action_description_ar=action_description_ar,
            changes=changes,
            before_state=before,
            after_state=after,
            success=success,
            metadata=metadata,
            retention_period=RetentionPeriod.GLOBALGAP,  # 5 years
        )

    def log_field_operation(
        self,
        operation_type: AuditActionType,
        field_id: str,
        field_name: str | None = None,
        field_name_ar: str | None = None,
        actor_id: str | None = None,
        actor_name: str | None = None,
        actor_name_ar: str | None = None,
        details: dict[str, Any] | None = None,
        ggn: str | None = None,
    ) -> AuditEntry:
        """
        Log a field operation (irrigation, fertilizer, pesticide, harvest).
        تسجيل عملية الحقل (ري، سماد، مبيد، حصاد)
        """
        metadata = AuditMetadata(ggn=ggn) if ggn else AuditMetadata()

        # Generate description
        op_descriptions = {
            AuditActionType.IRRIGATION: ("Irrigation applied", "تم تطبيق الري"),
            AuditActionType.FERTILIZER_APPLICATION: ("Fertilizer applied", "تم تطبيق السماد"),
            AuditActionType.PESTICIDE_APPLICATION: ("Pesticide applied", "تم تطبيق المبيد"),
            AuditActionType.HARVEST: ("Harvest completed", "تم الحصاد"),
            AuditActionType.SOIL_TEST: ("Soil test conducted", "تم إجراء اختبار التربة"),
            AuditActionType.CROP_PLANTING: ("Crop planted", "تمت زراعة المحصول"),
        }
        desc_en, desc_ar = op_descriptions.get(operation_type, ("Field operation", "عملية الحقل"))

        return self._create_entry(
            action=operation_type,
            resource_type="field",
            resource_id=field_id,
            resource_name=field_name,
            resource_name_ar=field_name_ar,
            actor_id=actor_id,
            actor_type=ActorType.USER if actor_id else ActorType.SYSTEM,
            actor_name=actor_name,
            actor_name_ar=actor_name_ar,
            category=AuditCategory.FIELD_OPS,
            severity=AuditSeverity.INFO,
            action_description=desc_en,
            action_description_ar=desc_ar,
            after_state=details,
            metadata=metadata,
            retention_period=RetentionPeriod.GLOBALGAP,  # Required for GlobalGAP
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Query Methods | طرق الاستعلام
    # ─────────────────────────────────────────────────────────────────────────

    def get_entries(
        self,
        filter_: AuditQueryFilter | None = None,
    ) -> list[AuditEntry]:
        """
        Get filtered audit entries.
        الحصول على إدخالات التدقيق المفلترة
        """
        entries = self._entries

        if filter_ is None:
            return entries[-100:]  # Default to last 100

        # Apply filters
        if filter_.tenant_id:
            entries = [e for e in entries if e.tenant_id == filter_.tenant_id]
        if filter_.actor_id:
            entries = [e for e in entries if e.actor_id == filter_.actor_id]
        if filter_.actor_type:
            entries = [e for e in entries if e.actor_type == filter_.actor_type]
        if filter_.action:
            entries = [e for e in entries if e.action == filter_.action]
        if filter_.actions:
            entries = [e for e in entries if e.action in filter_.actions]
        if filter_.category:
            entries = [e for e in entries if e.category == filter_.category]
        if filter_.categories:
            entries = [e for e in entries if e.category in filter_.categories]
        if filter_.severity:
            entries = [e for e in entries if e.severity == filter_.severity]
        if filter_.resource_type:
            entries = [e for e in entries if e.resource_type == filter_.resource_type]
        if filter_.resource_id:
            entries = [e for e in entries if e.resource_id == filter_.resource_id]
        if filter_.success is not None:
            entries = [e for e in entries if e.success == filter_.success]
        if filter_.start_date:
            entries = [e for e in entries if e.timestamp >= filter_.start_date]
        if filter_.end_date:
            entries = [e for e in entries if e.timestamp <= filter_.end_date]
        if filter_.ggn:
            entries = [e for e in entries if e.metadata.ggn == filter_.ggn]
        if filter_.audit_session_id:
            entries = [e for e in entries if e.metadata.audit_session_id == filter_.audit_session_id]
        if filter_.control_point_id:
            entries = [e for e in entries if e.metadata.control_point_id == filter_.control_point_id]
        if filter_.correlation_id:
            entries = [e for e in entries if e.metadata.correlation_id == filter_.correlation_id]
        if filter_.tags:
            entries = [e for e in entries if any(tag in e.metadata.tags for tag in filter_.tags)]

        # Sort
        reverse = filter_.order_direction == "desc"
        if filter_.order_by == "timestamp":
            entries = sorted(entries, key=lambda e: e.timestamp, reverse=reverse)

        # Pagination
        start = filter_.offset
        end = start + filter_.limit
        return entries[start:end]

    def get_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 50,
    ) -> list[AuditEntry]:
        """
        Get audit history for a specific resource.
        الحصول على سجل التدقيق لمورد محدد
        """
        filter_ = AuditQueryFilter(
            resource_type=resource_type,
            resource_id=resource_id,
            limit=limit,
            order_direction="desc",
        )
        return self.get_entries(filter_)

    def get_user_activity(
        self,
        user_id: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditEntry]:
        """
        Get activity for a specific user.
        الحصول على نشاط مستخدم محدد
        """
        filter_ = AuditQueryFilter(
            actor_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            order_direction="desc",
        )
        return self.get_entries(filter_)

    # ─────────────────────────────────────────────────────────────────────────
    # Storage Methods | طرق التخزين
    # ─────────────────────────────────────────────────────────────────────────

    async def flush(self) -> int:
        """
        Flush buffered entries to storage.
        تفريغ الإدخالات المؤقتة إلى التخزين

        Returns:
            Number of entries flushed
        """
        async with self._lock:
            if not self._buffer:
                return 0

            entries_to_flush = self._buffer.copy()
            self._buffer.clear()

        # Write to file if storage path configured
        if self.storage_path:
            filename = f"audit_trail_{datetime.now(UTC).strftime('%Y%m%d')}.jsonl"
            filepath = os.path.join(self.storage_path, filename)

            with open(filepath, "a", encoding="utf-8") as f:
                for entry in entries_to_flush:
                    f.write(entry.to_json() + "\n")

        logger.info("audit_entries_flushed", count=len(entries_to_flush))
        return len(entries_to_flush)

    def get_summary(self) -> dict[str, Any]:
        """
        Get audit summary statistics.
        الحصول على ملخص إحصائيات التدقيق
        """
        return {
            "tenant_id": self.tenant_id,
            "total_entries": self._total_entries,
            "entries_by_category": self._entries_by_category.copy(),
            "entries_by_action": self._entries_by_action.copy(),
            "entries_by_severity": self._entries_by_severity.copy(),
            "buffer_size": len(self._buffer),
            "hash_chain_enabled": self.enable_hash_chain,
            "last_hash": self._last_hash,
        }

    def verify_hash_chain(self) -> tuple[bool, list[str]]:
        """
        Verify the integrity of the hash chain.
        التحقق من سلامة سلسلة التجزئة

        Returns:
            Tuple of (is_valid, list of invalid entry IDs)
        """
        if not self.enable_hash_chain:
            return True, []

        invalid_entries: list[str] = []
        prev_hash: str | None = None

        for entry in self._entries:
            # Check prev_hash matches
            if entry.prev_hash != prev_hash:
                invalid_entries.append(entry.id)

            # Recalculate hash using the entry's own hash_version
            expected_hash = entry._calculate_hash(version=entry.hash_version)
            if entry.entry_hash != expected_hash:
                invalid_entries.append(entry.id)

            prev_hash = entry.entry_hash

        return len(invalid_entries) == 0, invalid_entries

    def clear(self) -> None:
        """Clear all entries and reset metrics."""
        self._buffer.clear()
        self._entries.clear()
        self._total_entries = 0
        self._entries_by_category.clear()
        self._entries_by_action.clear()
        self._entries_by_severity.clear()
        self._last_hash = None


# ─────────────────────────────────────────────────────────────────────────────
# Global Logger Instance | نسخة المسجل العالمية
# ─────────────────────────────────────────────────────────────────────────────

_global_logger: AuditTrailLogger | None = None


def get_audit_logger(tenant_id: str = "sahool") -> AuditTrailLogger:
    """
    Get or create the global audit logger.
    الحصول على أو إنشاء مسجل التدقيق العالمي
    """
    global _global_logger
    if _global_logger is None or _global_logger.tenant_id != tenant_id:
        # Default to /var/lib/sahool in production, /tmp for development only
        default_path = (
            "/var/lib/sahool/audit_trail" if os.getenv("ENVIRONMENT") == "production" else "/tmp/sahool_audit_trail"
        )  # nosec B108
        storage_path = os.getenv("AUDIT_TRAIL_STORAGE_PATH", default_path)
        _global_logger = AuditTrailLogger(tenant_id=tenant_id, storage_path=storage_path)
    return _global_logger


# ─────────────────────────────────────────────────────────────────────────────
# Convenience Functions | دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────


def log_action(
    action: AuditActionType,
    resource_type: str,
    resource_id: str,
    actor_id: str | None = None,
    tenant_id: str = "sahool",
    **kwargs,
) -> AuditEntry:
    """
    Convenience function to log an action.
    دالة مساعدة لتسجيل إجراء
    """
    logger = get_audit_logger(tenant_id)
    return logger.log_action(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        actor_id=actor_id,
        **kwargs,
    )


def log_change(
    action: AuditActionType,
    resource_type: str,
    resource_id: str,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    actor_id: str | None = None,
    tenant_id: str = "sahool",
    **kwargs,
) -> AuditEntry:
    """
    Convenience function to log a change.
    دالة مساعدة لتسجيل تغيير
    """
    logger = get_audit_logger(tenant_id)
    return logger.log_change(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        before=before,
        after=after,
        actor_id=actor_id,
        **kwargs,
    )


def log_login(
    user_id: str,
    success: bool = True,
    tenant_id: str = "sahool",
    **kwargs,
) -> AuditEntry:
    """
    Convenience function to log a login.
    دالة مساعدة لتسجيل الدخول
    """
    logger = get_audit_logger(tenant_id)
    return logger.log_login(user_id=user_id, success=success, **kwargs)


def log_globalgap_event(
    action: AuditActionType,
    resource_type: str,
    resource_id: str,
    ggn: str,
    tenant_id: str = "sahool",
    **kwargs,
) -> AuditEntry:
    """
    Convenience function to log a GlobalGAP event.
    دالة مساعدة لتسجيل حدث GlobalGAP
    """
    logger = get_audit_logger(tenant_id)
    return logger.log_globalgap_event(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ggn=ggn,
        **kwargs,
    )
