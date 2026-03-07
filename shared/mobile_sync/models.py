"""
Mobile Offline Sync Models
==========================
نماذج المزامنة للأجهزة المحمولة بدون اتصال

Data models for mobile offline synchronization including sync items,
conflicts, sync status, and delta operations.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class SyncStatus(StrEnum):
    """Status of a sync item or operation."""

    PENDING = "pending"  # في الانتظار - Waiting to sync
    QUEUED = "queued"  # في قائمة الانتظار - Added to sync queue
    SYNCING = "syncing"  # جاري المزامنة - Currently syncing
    SYNCED = "synced"  # تمت المزامنة - Successfully synced
    CONFLICT = "conflict"  # تعارض - Has conflict needing resolution
    FAILED = "failed"  # فشل - Sync failed
    CANCELLED = "cancelled"  # ملغى - Sync cancelled
    DEFERRED = "deferred"  # مؤجل - Deferred for later


class SyncPriority(StrEnum):
    """Priority levels for sync operations."""

    CRITICAL = "critical"  # حرج - Must sync immediately (e.g., alerts)
    HIGH = "high"  # عالي - Important data (e.g., field readings)
    MEDIUM = "medium"  # متوسط - Normal priority
    LOW = "low"  # منخفض - Can wait (e.g., historical data)
    BACKGROUND = "background"  # خلفية - Sync when idle


class SyncDirection(StrEnum):
    """Direction of sync operation."""

    UPLOAD = "upload"  # رفع - Local to server
    DOWNLOAD = "download"  # تنزيل - Server to local
    BIDIRECTIONAL = "bidirectional"  # ثنائي الاتجاه - Both ways


class SyncOperationType(StrEnum):
    """Type of sync operation."""

    CREATE = "create"  # إنشاء - New record
    UPDATE = "update"  # تحديث - Modified record
    DELETE = "delete"  # حذف - Deleted record
    PARTIAL_UPDATE = "partial_update"  # تحديث جزئي - Partial field update


class ConflictType(StrEnum):
    """Types of sync conflicts."""

    UPDATE_UPDATE = "update_update"  # تعارض تحديث - Both sides updated
    UPDATE_DELETE = "update_delete"  # تعارض تحديث/حذف - One updated, one deleted
    DELETE_UPDATE = "delete_update"  # تعارض حذف/تحديث - One deleted, one updated
    CREATE_CREATE = "create_create"  # تعارض إنشاء - Duplicate creation
    SCHEMA_MISMATCH = "schema_mismatch"  # تعارض مخطط - Schema version mismatch


class ConflictResolutionStrategy(StrEnum):
    """Strategies for resolving conflicts."""

    LAST_WRITE_WINS = "last_write_wins"  # الكتابة الأخيرة تفوز
    SERVER_WINS = "server_wins"  # الخادم يفوز
    CLIENT_WINS = "client_wins"  # العميل يفوز
    MANUAL_MERGE = "manual_merge"  # دمج يدوي
    FIELD_LEVEL_MERGE = "field_level_merge"  # دمج على مستوى الحقل
    CUSTOM = "custom"  # مخصص


class EntityType(StrEnum):
    """Types of entities that can be synced."""

    FIELD = "field"  # حقل
    CROP = "crop"  # محصول
    IRRIGATION = "irrigation"  # ري
    SPRAY = "spray"  # رش
    HARVEST = "harvest"  # حصاد
    OBSERVATION = "observation"  # ملاحظة
    TASK = "task"  # مهمة
    ALERT = "alert"  # تنبيه
    EQUIPMENT = "equipment"  # معدات
    SENSOR_READING = "sensor_reading"  # قراءة مستشعر
    WEATHER = "weather"  # طقس
    USER_PREFERENCE = "user_preference"  # تفضيل مستخدم


# ─────────────────────────────────────────────────────────────────────────────
# Bilingual Messages
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class BilingualMessage:
    """A message with English and Arabic content."""

    en: str
    ar: str

    def get(self, language: str = "en") -> str:
        """Get message in specified language."""
        return self.ar if language == "ar" else self.en

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary."""
        return {"en": self.en, "ar": self.ar}


# Standard sync messages
SYNC_MESSAGES = {
    "sync_started": BilingualMessage(en="Synchronization started", ar="بدأت المزامنة"),
    "sync_completed": BilingualMessage(en="Synchronization completed successfully", ar="اكتملت المزامنة بنجاح"),
    "sync_failed": BilingualMessage(en="Synchronization failed", ar="فشلت المزامنة"),
    "sync_partial": BilingualMessage(en="Synchronization partially completed", ar="اكتملت المزامنة جزئياً"),
    "conflict_detected": BilingualMessage(
        en="Conflict detected, manual resolution required", ar="تم اكتشاف تعارض، يلزم حل يدوي"
    ),
    "conflict_resolved": BilingualMessage(en="Conflict resolved successfully", ar="تم حل التعارض بنجاح"),
    "network_unavailable": BilingualMessage(
        en="Network unavailable, changes saved locally",
        ar="الشبكة غير متاحة، تم حفظ التغييرات محلياً",
    ),
    "queued_for_sync": BilingualMessage(
        en="Changes queued for synchronization", ar="التغييرات في قائمة انتظار المزامنة"
    ),
    "upload_completed": BilingualMessage(en="Upload completed", ar="اكتمل الرفع"),
    "download_completed": BilingualMessage(en="Download completed", ar="اكتمل التنزيل"),
    "delta_sync_available": BilingualMessage(en="Incremental sync available", ar="المزامنة التزايدية متاحة"),
    "full_sync_required": BilingualMessage(en="Full sync required", ar="يلزم مزامنة كاملة"),
}

# Error messages
SYNC_ERRORS = {
    "network_error": BilingualMessage(en="Network error occurred during sync", ar="حدث خطأ في الشبكة أثناء المزامنة"),
    "server_error": BilingualMessage(en="Server error occurred", ar="حدث خطأ في الخادم"),
    "timeout_error": BilingualMessage(en="Sync operation timed out", ar="انتهت مهلة عملية المزامنة"),
    "validation_error": BilingualMessage(en="Data validation failed", ar="فشل التحقق من صحة البيانات"),
    "authentication_error": BilingualMessage(
        en="Authentication failed, please login again",
        ar="فشلت المصادقة، يرجى تسجيل الدخول مرة أخرى",
    ),
    "quota_exceeded": BilingualMessage(en="Sync quota exceeded", ar="تم تجاوز حصة المزامنة"),
    "version_mismatch": BilingualMessage(en="Data version mismatch", ar="عدم تطابق إصدار البيانات"),
    "conflict_unresolved": BilingualMessage(en="Unresolved conflict exists", ar="يوجد تعارض لم يُحل"),
    "storage_full": BilingualMessage(en="Local storage is full", ar="التخزين المحلي ممتلئ"),
    "invalid_entity": BilingualMessage(en="Invalid entity for sync", ar="كيان غير صالح للمزامنة"),
}


# ─────────────────────────────────────────────────────────────────────────────
# Core Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class SyncMetadata:
    """Metadata for a sync operation."""

    version: int = 1  # إصدار البيانات
    schema_version: str = "1.0.0"  # إصدار المخطط
    checksum: str | None = None  # مجموع التحقق
    size_bytes: int = 0  # الحجم بالبايت
    compressed: bool = False  # مضغوط
    encrypted: bool = False  # مشفر
    last_sync_at: datetime | None = None  # آخر مزامنة
    server_version: int | None = None  # إصدار الخادم
    local_version: int | None = None  # إصدار محلي
    ancestor_version: int | None = None  # إصدار الجد المشترك

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "schema_version": self.schema_version,
            "checksum": self.checksum,
            "size_bytes": self.size_bytes,
            "compressed": self.compressed,
            "encrypted": self.encrypted,
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "server_version": self.server_version,
            "local_version": self.local_version,
            "ancestor_version": self.ancestor_version,
        }


@dataclass
class SyncItem:
    """A single item to be synchronized."""

    id: str = field(default_factory=lambda: str(uuid4()))
    entity_id: str = ""  # معرف الكيان
    entity_type: EntityType = EntityType.FIELD
    operation: SyncOperationType = SyncOperationType.UPDATE
    status: SyncStatus = SyncStatus.PENDING
    priority: SyncPriority = SyncPriority.MEDIUM
    direction: SyncDirection = SyncDirection.UPLOAD

    # Data payloads
    local_data: dict[str, Any] = field(default_factory=dict)
    server_data: dict[str, Any] | None = None
    merged_data: dict[str, Any] | None = None
    delta_data: dict[str, Any] | None = None  # Only changed fields

    # Metadata
    metadata: SyncMetadata = field(default_factory=SyncMetadata)
    tenant_id: str = ""
    user_id: str = ""
    device_id: str = ""

    # Timestamps
    local_modified_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    server_modified_at: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    queued_at: datetime | None = None
    synced_at: datetime | None = None

    # Retry handling
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: datetime | None = None
    last_error: str | None = None
    last_error_ar: str | None = None

    # Conflict tracking
    conflict_id: str | None = None
    has_conflict: bool = False

    def is_expired(self, max_age_hours: int = 72) -> bool:
        """Check if sync item is too old."""
        if not self.created_at:
            return False
        age = (datetime.now(UTC) - self.created_at).total_seconds() / 3600
        return age > max_age_hours

    def can_retry(self) -> bool:
        """Check if item can be retried."""
        return self.retry_count < self.max_retries

    def increment_retry(self, error: str, error_ar: str | None = None):
        """Increment retry count and set error."""
        self.retry_count += 1
        self.last_error = error
        self.last_error_ar = error_ar
        # Exponential backoff: 1, 2, 4, 8... minutes
        backoff_seconds = 60 * (2 ** (self.retry_count - 1))
        from datetime import timedelta

        self.next_retry_at = datetime.now(UTC) + timedelta(seconds=backoff_seconds)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "operation": self.operation.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "direction": self.direction.value,
            "local_data": self.local_data,
            "server_data": self.server_data,
            "merged_data": self.merged_data,
            "delta_data": self.delta_data,
            "metadata": self.metadata.to_dict(),
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "local_modified_at": self.local_modified_at.isoformat(),
            "server_modified_at": self.server_modified_at.isoformat() if self.server_modified_at else None,
            "created_at": self.created_at.isoformat(),
            "queued_at": self.queued_at.isoformat() if self.queued_at else None,
            "synced_at": self.synced_at.isoformat() if self.synced_at else None,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "next_retry_at": self.next_retry_at.isoformat() if self.next_retry_at else None,
            "last_error": self.last_error,
            "last_error_ar": self.last_error_ar,
            "conflict_id": self.conflict_id,
            "has_conflict": self.has_conflict,
        }


@dataclass
class SyncConflict:
    """A sync conflict that needs resolution."""

    id: str = field(default_factory=lambda: str(uuid4()))
    sync_item_id: str = ""
    entity_id: str = ""
    entity_type: EntityType = EntityType.FIELD
    conflict_type: ConflictType = ConflictType.UPDATE_UPDATE

    # Conflicting versions
    local_data: dict[str, Any] = field(default_factory=dict)
    server_data: dict[str, Any] = field(default_factory=dict)
    base_data: dict[str, Any] | None = None  # Common ancestor

    # Conflict details
    conflicting_fields: list[str] = field(default_factory=list)
    local_modified_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    server_modified_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    local_modified_by: str | None = None
    server_modified_by: str | None = None

    # Resolution
    resolution_strategy: ConflictResolutionStrategy | None = None
    resolved_data: dict[str, Any] | None = None
    resolved_at: datetime | None = None
    resolved_by: str | None = None
    resolution_note: str | None = None
    resolution_note_ar: str | None = None

    # Metadata
    tenant_id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    auto_resolvable: bool = False

    def get_field_conflicts(self) -> list[dict[str, Any]]:
        """Get detailed information about each conflicting field."""
        conflicts = []
        for field_name in self.conflicting_fields:
            conflict_info = {
                "field": field_name,
                "local_value": self.local_data.get(field_name),
                "server_value": self.server_data.get(field_name),
                "base_value": self.base_data.get(field_name) if self.base_data else None,
            }
            conflicts.append(conflict_info)
        return conflicts

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "sync_item_id": self.sync_item_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "conflict_type": self.conflict_type.value,
            "local_data": self.local_data,
            "server_data": self.server_data,
            "base_data": self.base_data,
            "conflicting_fields": self.conflicting_fields,
            "local_modified_at": self.local_modified_at.isoformat(),
            "server_modified_at": self.server_modified_at.isoformat(),
            "local_modified_by": self.local_modified_by,
            "server_modified_by": self.server_modified_by,
            "resolution_strategy": self.resolution_strategy.value if self.resolution_strategy else None,
            "resolved_data": self.resolved_data,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolution_note": self.resolution_note,
            "resolution_note_ar": self.resolution_note_ar,
            "tenant_id": self.tenant_id,
            "created_at": self.created_at.isoformat(),
            "auto_resolvable": self.auto_resolvable,
            "field_conflicts": self.get_field_conflicts(),
        }


@dataclass
class SyncProgress:
    """Progress tracking for sync operations."""

    total_items: int = 0
    pending_items: int = 0
    syncing_items: int = 0
    synced_items: int = 0
    failed_items: int = 0
    conflict_items: int = 0

    upload_count: int = 0
    download_count: int = 0

    bytes_uploaded: int = 0
    bytes_downloaded: int = 0
    total_bytes: int = 0

    started_at: datetime | None = None
    estimated_completion: datetime | None = None
    current_entity_type: EntityType | None = None
    current_entity_id: str | None = None

    @property
    def percent_complete(self) -> float:
        """Calculate completion percentage."""
        if self.total_items == 0:
            return 0.0
        completed = self.synced_items + self.failed_items + self.conflict_items
        return (completed / self.total_items) * 100

    @property
    def is_complete(self) -> bool:
        """Check if sync is complete."""
        return self.pending_items == 0 and self.syncing_items == 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_items": self.total_items,
            "pending_items": self.pending_items,
            "syncing_items": self.syncing_items,
            "synced_items": self.synced_items,
            "failed_items": self.failed_items,
            "conflict_items": self.conflict_items,
            "upload_count": self.upload_count,
            "download_count": self.download_count,
            "bytes_uploaded": self.bytes_uploaded,
            "bytes_downloaded": self.bytes_downloaded,
            "total_bytes": self.total_bytes,
            "percent_complete": round(self.percent_complete, 2),
            "is_complete": self.is_complete,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "current_entity_type": self.current_entity_type.value if self.current_entity_type else None,
            "current_entity_id": self.current_entity_id,
        }


@dataclass
class SyncSession:
    """A sync session containing multiple sync operations."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    user_id: str = ""
    device_id: str = ""

    status: SyncStatus = SyncStatus.PENDING
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    progress: SyncProgress = field(default_factory=SyncProgress)

    # Configuration
    priority_threshold: SyncPriority = SyncPriority.LOW  # Sync items >= this priority
    entity_types: list[EntityType] = field(default_factory=list)  # Empty = all types
    batch_size: int = 50
    timeout_seconds: int = 300

    # Timestamps
    started_at: datetime | None = None
    completed_at: datetime | None = None
    last_activity_at: datetime | None = None

    # Results
    items_processed: int = 0
    conflicts_detected: int = 0
    conflicts_resolved: int = 0
    errors: list[dict[str, Any]] = field(default_factory=list)

    # Metadata
    sync_token: str | None = None  # For incremental sync
    server_timestamp: datetime | None = None
    client_timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_error(self, error: str, error_ar: str | None = None, entity_id: str | None = None):
        """Add an error to the session."""
        self.errors.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "error": error,
                "error_ar": error_ar,
                "entity_id": entity_id,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "status": self.status.value,
            "direction": self.direction.value,
            "progress": self.progress.to_dict(),
            "priority_threshold": self.priority_threshold.value,
            "entity_types": [et.value for et in self.entity_types],
            "batch_size": self.batch_size,
            "timeout_seconds": self.timeout_seconds,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "items_processed": self.items_processed,
            "conflicts_detected": self.conflicts_detected,
            "conflicts_resolved": self.conflicts_resolved,
            "errors": self.errors,
            "sync_token": self.sync_token,
            "server_timestamp": self.server_timestamp.isoformat() if self.server_timestamp else None,
            "client_timestamp": self.client_timestamp.isoformat(),
        }


@dataclass
class DeltaChange:
    """Represents a single field change in a delta sync."""

    field_path: str  # مسار الحقل (e.g., "irrigation.amount")
    old_value: Any = None  # القيمة القديمة
    new_value: Any = None  # القيمة الجديدة
    operation: str = "set"  # set, unset, increment, append
    changed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "field_path": self.field_path,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "operation": self.operation,
            "changed_at": self.changed_at.isoformat(),
        }


@dataclass
class DeltaPacket:
    """A packet containing delta changes for efficient sync."""

    id: str = field(default_factory=lambda: str(uuid4()))
    entity_id: str = ""
    entity_type: EntityType = EntityType.FIELD
    base_version: int = 0  # Version this delta is based on
    target_version: int = 0  # Version after applying delta

    changes: list[DeltaChange] = field(default_factory=list)

    # Size info
    full_size_bytes: int = 0  # Size of full record
    delta_size_bytes: int = 0  # Size of delta only
    compression_ratio: float = 0.0  # Savings ratio

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    checksum: str | None = None

    @property
    def savings_percent(self) -> float:
        """Calculate bandwidth savings percentage."""
        if self.full_size_bytes == 0:
            return 0.0
        return ((self.full_size_bytes - self.delta_size_bytes) / self.full_size_bytes) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type.value,
            "base_version": self.base_version,
            "target_version": self.target_version,
            "changes": [c.to_dict() for c in self.changes],
            "full_size_bytes": self.full_size_bytes,
            "delta_size_bytes": self.delta_size_bytes,
            "compression_ratio": round(self.compression_ratio, 4),
            "savings_percent": round(self.savings_percent, 2),
            "created_at": self.created_at.isoformat(),
            "checksum": self.checksum,
        }


@dataclass
class SyncResult:
    """Result of a sync operation."""

    session_id: str
    status: SyncStatus
    message: BilingualMessage | None = None

    # Counts
    total_items: int = 0
    synced_items: int = 0
    failed_items: int = 0
    conflict_items: int = 0
    skipped_items: int = 0

    # Performance
    duration_seconds: float = 0.0
    bytes_transferred: int = 0
    delta_savings_bytes: int = 0

    # Conflicts
    conflicts: list[SyncConflict] = field(default_factory=list)

    # Errors
    errors: list[dict[str, Any]] = field(default_factory=list)

    # Next sync info
    next_sync_token: str | None = None
    full_sync_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "message": self.message.to_dict() if self.message else None,
            "total_items": self.total_items,
            "synced_items": self.synced_items,
            "failed_items": self.failed_items,
            "conflict_items": self.conflict_items,
            "skipped_items": self.skipped_items,
            "success_rate": round((self.synced_items / self.total_items * 100) if self.total_items > 0 else 0, 2),
            "duration_seconds": round(self.duration_seconds, 2),
            "bytes_transferred": self.bytes_transferred,
            "delta_savings_bytes": self.delta_savings_bytes,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "errors": self.errors,
            "next_sync_token": self.next_sync_token,
            "full_sync_required": self.full_sync_required,
        }
