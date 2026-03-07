"""
Batch Operations Models
=======================
نماذج عمليات الدفعات

Data models for batch operations including field operations,
harvest data entry, equipment assignments, and alert management.

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


class BatchOperationType(StrEnum):
    """Types of batch operations."""

    IRRIGATION = "irrigation"  # ري متعدد الحقول
    SPRAYING = "spraying"  # رش متعدد الحقول
    FERTILIZATION = "fertilization"  # تسميد متعدد الحقول
    HARVEST = "harvest"  # حصاد جماعي
    EQUIPMENT_ASSIGN = "equipment_assign"  # تخصيص المعدات
    ALERT_ACK = "alert_ack"  # إقرار التنبيهات


class BatchStatus(StrEnum):
    """Status of a batch operation."""

    PENDING = "pending"  # في الانتظار
    QUEUED = "queued"  # في قائمة الانتظار
    IN_PROGRESS = "in_progress"  # قيد التنفيذ
    PAUSED = "paused"  # متوقف مؤقتاً
    COMPLETED = "completed"  # مكتمل
    PARTIALLY_COMPLETED = "partially_completed"  # مكتمل جزئياً
    FAILED = "failed"  # فشل
    CANCELLED = "cancelled"  # ملغى
    ROLLED_BACK = "rolled_back"  # تم التراجع


class BatchPriority(StrEnum):
    """Priority levels for batch operations."""

    LOW = "low"  # منخفض
    MEDIUM = "medium"  # متوسط
    HIGH = "high"  # عالي
    URGENT = "urgent"  # عاجل


class ItemStatus(StrEnum):
    """Status of an individual item in a batch."""

    PENDING = "pending"  # في الانتظار
    IN_PROGRESS = "in_progress"  # قيد التنفيذ
    COMPLETED = "completed"  # مكتمل
    FAILED = "failed"  # فشل
    SKIPPED = "skipped"  # تم تخطيه
    ROLLED_BACK = "rolled_back"  # تم التراجع


class RollbackStrategy(StrEnum):
    """Strategy for handling rollbacks."""

    NONE = "none"  # لا تراجع
    ON_FIRST_ERROR = "on_first_error"  # عند أول خطأ
    ON_THRESHOLD = "on_threshold"  # عند تجاوز الحد
    MANUAL = "manual"  # يدوي


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


# Standard messages
BATCH_MESSAGES = {
    "started": BilingualMessage(en="Batch operation started", ar="بدأت عملية الدفعة"),
    "completed": BilingualMessage(en="Batch operation completed successfully", ar="اكتملت عملية الدفعة بنجاح"),
    "partially_completed": BilingualMessage(en="Batch operation partially completed", ar="اكتملت عملية الدفعة جزئياً"),
    "failed": BilingualMessage(en="Batch operation failed", ar="فشلت عملية الدفعة"),
    "cancelled": BilingualMessage(en="Batch operation cancelled", ar="تم إلغاء عملية الدفعة"),
    "rolled_back": BilingualMessage(en="Batch operation rolled back", ar="تم التراجع عن عملية الدفعة"),
    "paused": BilingualMessage(en="Batch operation paused", ar="تم إيقاف عملية الدفعة مؤقتاً"),
    "resumed": BilingualMessage(en="Batch operation resumed", ar="تم استئناف عملية الدفعة"),
    "item_completed": BilingualMessage(en="Item processed successfully", ar="تمت معالجة العنصر بنجاح"),
    "item_failed": BilingualMessage(en="Item processing failed", ar="فشلت معالجة العنصر"),
    "rollback_started": BilingualMessage(en="Rollback started", ar="بدأ التراجع"),
    "rollback_completed": BilingualMessage(en="Rollback completed", ar="اكتمل التراجع"),
}


# ─────────────────────────────────────────────────────────────────────────────
# Field Operation Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class IrrigationParams:
    """Parameters for irrigation operations."""

    water_amount_mm: float  # كمية المياه بالملم
    duration_minutes: int | None = None  # مدة الري بالدقائق
    method: str = "drip"  # طريقة الري
    notes: str | None = None
    notes_ar: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "water_amount_mm": self.water_amount_mm,
            "duration_minutes": self.duration_minutes,
            "method": self.method,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }


@dataclass
class SprayingParams:
    """Parameters for spraying operations."""

    product_name: str  # اسم المنتج
    product_name_ar: str | None = None
    product_type: str = "pesticide"  # نوع المنتج (pesticide/herbicide/fungicide)
    concentration: float | None = None  # التركيز
    volume_per_hectare: float | None = None  # الحجم لكل هكتار
    safety_interval_days: int = 0  # فترة الأمان بالأيام
    notes: str | None = None
    notes_ar: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "product_name": self.product_name,
            "product_name_ar": self.product_name_ar,
            "product_type": self.product_type,
            "concentration": self.concentration,
            "volume_per_hectare": self.volume_per_hectare,
            "safety_interval_days": self.safety_interval_days,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }


@dataclass
class FertilizationParams:
    """Parameters for fertilization operations."""

    fertilizer_name: str  # اسم السماد
    fertilizer_name_ar: str | None = None
    fertilizer_type: str = "granular"  # نوع السماد
    rate_kg_per_hectare: float = 0.0  # معدل التسميد
    nitrogen_percent: float | None = None
    phosphorus_percent: float | None = None
    potassium_percent: float | None = None
    application_method: str = "broadcast"
    notes: str | None = None
    notes_ar: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "fertilizer_name": self.fertilizer_name,
            "fertilizer_name_ar": self.fertilizer_name_ar,
            "fertilizer_type": self.fertilizer_type,
            "rate_kg_per_hectare": self.rate_kg_per_hectare,
            "nitrogen_percent": self.nitrogen_percent,
            "phosphorus_percent": self.phosphorus_percent,
            "potassium_percent": self.potassium_percent,
            "application_method": self.application_method,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
        }


@dataclass
class FieldOperationItem:
    """A single field operation in a batch."""

    id: str = field(default_factory=lambda: str(uuid4()))
    field_id: str = ""
    field_name: str = ""
    field_name_ar: str | None = None
    area_hectares: float = 0.0
    status: ItemStatus = ItemStatus.PENDING
    error_message: str | None = None
    error_message_ar: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result_data: dict[str, Any] = field(default_factory=dict)
    rollback_data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "field_id": self.field_id,
            "field_name": self.field_name,
            "field_name_ar": self.field_name_ar,
            "area_hectares": self.area_hectares,
            "status": self.status.value,
            "error_message": self.error_message,
            "error_message_ar": self.error_message_ar,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result_data": self.result_data,
            "rollback_data": self.rollback_data,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Harvest Data Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class HarvestEntry:
    """A single harvest data entry."""

    id: str = field(default_factory=lambda: str(uuid4()))
    field_id: str = ""
    field_name: str = ""
    field_name_ar: str | None = None
    crop_type: str = ""
    crop_type_ar: str | None = None
    harvest_date: datetime | None = None
    yield_kg: float = 0.0
    yield_per_hectare: float | None = None
    quality_grade: str | None = None
    moisture_percent: float | None = None
    storage_location: str | None = None
    notes: str | None = None
    notes_ar: str | None = None
    status: ItemStatus = ItemStatus.PENDING
    error_message: str | None = None
    error_message_ar: str | None = None
    created_record_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "field_id": self.field_id,
            "field_name": self.field_name,
            "field_name_ar": self.field_name_ar,
            "crop_type": self.crop_type,
            "crop_type_ar": self.crop_type_ar,
            "harvest_date": self.harvest_date.isoformat() if self.harvest_date else None,
            "yield_kg": self.yield_kg,
            "yield_per_hectare": self.yield_per_hectare,
            "quality_grade": self.quality_grade,
            "moisture_percent": self.moisture_percent,
            "storage_location": self.storage_location,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
            "status": self.status.value,
            "error_message": self.error_message,
            "error_message_ar": self.error_message_ar,
            "created_record_id": self.created_record_id,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Equipment Assignment Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class EquipmentAssignment:
    """A single equipment task assignment."""

    id: str = field(default_factory=lambda: str(uuid4()))
    equipment_id: str = ""
    equipment_name: str = ""
    equipment_name_ar: str | None = None
    task_id: str = ""
    task_description: str = ""
    task_description_ar: str | None = None
    assigned_to_user_id: str | None = None
    assigned_to_name: str | None = None
    field_id: str | None = None
    field_name: str | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    status: ItemStatus = ItemStatus.PENDING
    error_message: str | None = None
    error_message_ar: str | None = None
    created_assignment_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "equipment_name": self.equipment_name,
            "equipment_name_ar": self.equipment_name_ar,
            "task_id": self.task_id,
            "task_description": self.task_description,
            "task_description_ar": self.task_description_ar,
            "assigned_to_user_id": self.assigned_to_user_id,
            "assigned_to_name": self.assigned_to_name,
            "field_id": self.field_id,
            "field_name": self.field_name,
            "scheduled_start": self.scheduled_start.isoformat() if self.scheduled_start else None,
            "scheduled_end": self.scheduled_end.isoformat() if self.scheduled_end else None,
            "status": self.status.value,
            "error_message": self.error_message,
            "error_message_ar": self.error_message_ar,
            "created_assignment_id": self.created_assignment_id,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Alert Acknowledgment Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class AlertAcknowledgment:
    """A single alert acknowledgment."""

    id: str = field(default_factory=lambda: str(uuid4()))
    alert_id: str = ""
    alert_title: str = ""
    alert_title_ar: str | None = None
    alert_type: str = ""
    severity: str = ""
    acknowledged_by_user_id: str | None = None
    acknowledged_by_name: str | None = None
    acknowledgment_note: str | None = None
    acknowledgment_note_ar: str | None = None
    action_taken: str | None = None
    action_taken_ar: str | None = None
    status: ItemStatus = ItemStatus.PENDING
    error_message: str | None = None
    error_message_ar: str | None = None
    acknowledged_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "alert_title": self.alert_title,
            "alert_title_ar": self.alert_title_ar,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "acknowledged_by_user_id": self.acknowledged_by_user_id,
            "acknowledged_by_name": self.acknowledged_by_name,
            "acknowledgment_note": self.acknowledgment_note,
            "acknowledgment_note_ar": self.acknowledgment_note_ar,
            "action_taken": self.action_taken,
            "action_taken_ar": self.action_taken_ar,
            "status": self.status.value,
            "error_message": self.error_message,
            "error_message_ar": self.error_message_ar,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Batch Operation Models
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class BatchProgress:
    """Progress tracking for a batch operation."""

    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    current_item_index: int = 0
    current_item_id: str | None = None
    percent_complete: float = 0.0
    estimated_remaining_seconds: float | None = None
    items_per_second: float | None = None

    def update(self, total: int, completed: int, failed: int, skipped: int = 0):
        """Update progress metrics."""
        self.total_items = total
        self.completed_items = completed
        self.failed_items = failed
        self.skipped_items = skipped
        self.current_item_index = completed + failed + skipped
        if total > 0:
            self.percent_complete = ((completed + failed + skipped) / total) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "failed_items": self.failed_items,
            "skipped_items": self.skipped_items,
            "current_item_index": self.current_item_index,
            "current_item_id": self.current_item_id,
            "percent_complete": round(self.percent_complete, 2),
            "estimated_remaining_seconds": self.estimated_remaining_seconds,
            "items_per_second": self.items_per_second,
        }


@dataclass
class BatchConfig:
    """Configuration for a batch operation."""

    max_concurrent: int = 5  # الحد الأقصى للعمليات المتزامنة
    timeout_per_item_seconds: float = 60.0  # مهلة كل عنصر
    retry_failed_items: bool = True  # إعادة محاولة العناصر الفاشلة
    max_retries: int = 3  # الحد الأقصى لمحاولات الإعادة
    retry_delay_seconds: float = 1.0  # تأخير بين المحاولات
    stop_on_error: bool = False  # التوقف عند أول خطأ
    rollback_on_failure: bool = False  # التراجع عند الفشل
    rollback_strategy: RollbackStrategy = RollbackStrategy.NONE
    failure_threshold_percent: float = 50.0  # حد فشل النسبة المئوية
    continue_on_partial_success: bool = True  # المتابعة عند النجاح الجزئي
    dry_run: bool = False  # وضع المحاكاة

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_concurrent": self.max_concurrent,
            "timeout_per_item_seconds": self.timeout_per_item_seconds,
            "retry_failed_items": self.retry_failed_items,
            "max_retries": self.max_retries,
            "retry_delay_seconds": self.retry_delay_seconds,
            "stop_on_error": self.stop_on_error,
            "rollback_on_failure": self.rollback_on_failure,
            "rollback_strategy": self.rollback_strategy.value,
            "failure_threshold_percent": self.failure_threshold_percent,
            "continue_on_partial_success": self.continue_on_partial_success,
            "dry_run": self.dry_run,
        }


@dataclass
class BatchOperation:
    """A batch operation containing multiple items."""

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: str = ""
    operation_type: BatchOperationType = BatchOperationType.IRRIGATION
    name: str = ""
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    status: BatchStatus = BatchStatus.PENDING
    priority: BatchPriority = BatchPriority.MEDIUM
    config: BatchConfig = field(default_factory=BatchConfig)
    progress: BatchProgress = field(default_factory=BatchProgress)

    # Operation-specific parameters
    irrigation_params: IrrigationParams | None = None
    spraying_params: SprayingParams | None = None
    fertilization_params: FertilizationParams | None = None

    # Items (one of these will be populated based on operation_type)
    field_items: list[FieldOperationItem] = field(default_factory=list)
    harvest_entries: list[HarvestEntry] = field(default_factory=list)
    equipment_assignments: list[EquipmentAssignment] = field(default_factory=list)
    alert_acknowledgments: list[AlertAcknowledgment] = field(default_factory=list)

    # Metadata
    created_by_user_id: str | None = None
    created_by_name: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    error_message: str | None = None
    error_message_ar: str | None = None

    # Audit
    audit_log: list[dict[str, Any]] = field(default_factory=list)

    def get_items(self) -> list[Any]:
        """Get the items list based on operation type."""
        if self.operation_type in [
            BatchOperationType.IRRIGATION,
            BatchOperationType.SPRAYING,
            BatchOperationType.FERTILIZATION,
        ]:
            return self.field_items
        elif self.operation_type == BatchOperationType.HARVEST:
            return self.harvest_entries
        elif self.operation_type == BatchOperationType.EQUIPMENT_ASSIGN:
            return self.equipment_assignments
        elif self.operation_type == BatchOperationType.ALERT_ACK:
            return self.alert_acknowledgments
        return []

    def get_item_count(self) -> int:
        """Get total number of items."""
        return len(self.get_items())

    def get_completed_count(self) -> int:
        """Get number of completed items."""
        return sum(1 for item in self.get_items() if item.status == ItemStatus.COMPLETED)

    def get_failed_count(self) -> int:
        """Get number of failed items."""
        return sum(1 for item in self.get_items() if item.status == ItemStatus.FAILED)

    def add_audit_entry(
        self,
        action: str,
        details: dict[str, Any] | None = None,
        user_id: str | None = None,
    ):
        """Add an audit log entry."""
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "action": action,
            "details": details or {},
            "user_id": user_id,
        }
        self.audit_log.append(entry)

    def to_dict(self, include_items: bool = True) -> dict[str, Any]:
        """Convert to dictionary."""
        data = {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "operation_type": self.operation_type.value,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "status": self.status.value,
            "priority": self.priority.value,
            "config": self.config.to_dict(),
            "progress": self.progress.to_dict(),
            "created_by_user_id": self.created_by_user_id,
            "created_by_name": self.created_by_name,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "error_message": self.error_message,
            "error_message_ar": self.error_message_ar,
            "audit_log": self.audit_log,
        }

        # Add operation-specific params
        if self.irrigation_params:
            data["irrigation_params"] = self.irrigation_params.to_dict()
        if self.spraying_params:
            data["spraying_params"] = self.spraying_params.to_dict()
        if self.fertilization_params:
            data["fertilization_params"] = self.fertilization_params.to_dict()

        # Add items if requested
        if include_items:
            data["field_items"] = [item.to_dict() for item in self.field_items]
            data["harvest_entries"] = [entry.to_dict() for entry in self.harvest_entries]
            data["equipment_assignments"] = [a.to_dict() for a in self.equipment_assignments]
            data["alert_acknowledgments"] = [a.to_dict() for a in self.alert_acknowledgments]
            data["item_count"] = self.get_item_count()
            data["completed_count"] = self.get_completed_count()
            data["failed_count"] = self.get_failed_count()

        return data


@dataclass
class BatchResult:
    """Result of a batch operation execution."""

    batch_id: str
    status: BatchStatus
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    duration_seconds: float = 0.0
    errors: list[dict[str, Any]] = field(default_factory=list)
    rollback_performed: bool = False
    rollback_successful: bool | None = None
    message: BilingualMessage | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "batch_id": self.batch_id,
            "status": self.status.value,
            "total_items": self.total_items,
            "completed_items": self.completed_items,
            "failed_items": self.failed_items,
            "skipped_items": self.skipped_items,
            "duration_seconds": round(self.duration_seconds, 2),
            "success_rate": round((self.completed_items / self.total_items * 100) if self.total_items > 0 else 0, 2),
            "errors": self.errors,
            "rollback_performed": self.rollback_performed,
            "rollback_successful": self.rollback_successful,
            "message": self.message.to_dict() if self.message else None,
        }
