# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Pydantic schemas for Edge Orchestrator Service.

Defines data models for edge devices, jobs, and synchronization.

مخططات Pydantic لخدمة تنسيق الحافة.
تحدد نماذج البيانات لأجهزة الحافة والمهام والمزامنة.
"""

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

# =============================================================================
# Enums | التعدادات
# =============================================================================


class DeviceType(StrEnum):
    """Edge device types | أنواع أجهزة الحافة."""

    JETSON_ORIN_NANO = "jetson_orin_nano"  # NVIDIA Jetson Orin Nano
    JETSON_ORIN_NX = "jetson_orin_nx"  # NVIDIA Jetson Orin NX
    JETSON_AGX_ORIN = "jetson_agx_orin"  # NVIDIA Jetson AGX Orin
    RASPBERRY_PI_5 = "raspberry_pi_5"  # Raspberry Pi 5 with AI HAT
    GENERIC_EDGE = "generic_edge"  # Generic edge device


class DeviceStatus(StrEnum):
    """Device operational status | حالة تشغيل الجهاز."""

    ONLINE = "online"  # Device is connected and operational | متصل وعامل
    OFFLINE = "offline"  # Device is not responding | غير متصل
    IDLE = "idle"  # Device is connected but idle | متصل وخامل
    BUSY = "busy"  # Device is processing a job | يعالج مهمة
    SYNCING = "syncing"  # Device is syncing data | يزامن البيانات
    DEPLOYING = "deploying"  # Model deployment in progress | نشر النموذج جاري
    ERROR = "error"  # Device encountered an error | حدث خطأ
    MAINTENANCE = "maintenance"  # Device under maintenance | تحت الصيانة


class JobType(StrEnum):
    """Edge job types | أنواع مهام الحافة."""

    INFERENCE = "inference"  # Run AI inference | تشغيل الاستدلال
    MODEL_DEPLOY = "model_deploy"  # Deploy new model | نشر نموذج جديد
    DATA_SYNC = "data_sync"  # Sync data to cloud | مزامنة البيانات
    FIRMWARE_UPDATE = "firmware_update"  # Update device firmware | تحديث البرامج الثابتة
    DIAGNOSTIC = "diagnostic"  # Run diagnostic tests | تشغيل اختبارات تشخيصية
    CALIBRATION = "calibration"  # Calibrate sensors | معايرة المستشعرات
    CAPTURE = "capture"  # Capture images/data | التقاط صور/بيانات


class JobStatus(StrEnum):
    """Job execution status | حالة تنفيذ المهمة."""

    PENDING = "pending"  # Job is queued | في الانتظار
    SCHEDULED = "scheduled"  # Job is scheduled | مجدولة
    RUNNING = "running"  # Job is executing | قيد التنفيذ
    COMPLETED = "completed"  # Job finished successfully | اكتملت بنجاح
    FAILED = "failed"  # Job failed | فشلت
    CANCELLED = "cancelled"  # Job was cancelled | ألغيت
    TIMEOUT = "timeout"  # Job timed out | انتهت المهلة


class JobPriority(StrEnum):
    """Job priority levels | مستويات أولوية المهمة."""

    LOW = "low"  # Low priority | أولوية منخفضة
    NORMAL = "normal"  # Normal priority | أولوية عادية
    HIGH = "high"  # High priority | أولوية عالية
    CRITICAL = "critical"  # Critical priority | أولوية حرجة


class SyncDirection(StrEnum):
    """Data sync direction | اتجاه مزامنة البيانات."""

    UPLOAD = "upload"  # Device to cloud | من الجهاز إلى السحابة
    DOWNLOAD = "download"  # Cloud to device | من السحابة إلى الجهاز
    BIDIRECTIONAL = "bidirectional"  # Both directions | ثنائي الاتجاه


class ModelFormat(StrEnum):
    """AI model format | تنسيق نموذج الذكاء الاصطناعي."""

    TENSORRT = "tensorrt"  # NVIDIA TensorRT optimized
    ONNX = "onnx"  # ONNX format
    PYTORCH = "pytorch"  # PyTorch model
    TFLITE = "tflite"  # TensorFlow Lite


# =============================================================================
# Base Schemas | المخططات الأساسية
# =============================================================================


class BilingualMixin(BaseModel):
    """Mixin for bilingual name/description fields."""

    name: str = Field(..., min_length=1, max_length=255)
    name_ar: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    description_ar: str | None = Field(default=None, max_length=1000)


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Device Schemas | مخططات الجهاز
# =============================================================================


class DeviceCapabilities(BaseModel):
    """Device hardware capabilities | قدرات أجهزة الجهاز."""

    model_config = ConfigDict(extra="allow")

    gpu_memory_gb: float = Field(default=8.0, description="GPU memory in GB")
    cpu_cores: int = Field(default=6, description="Number of CPU cores")
    ram_gb: float = Field(default=8.0, description="RAM in GB")
    storage_gb: float = Field(default=64.0, description="Storage in GB")
    has_nvme: bool = Field(default=False, description="Has NVMe storage")
    max_power_watts: int = Field(default=15, description="Max power consumption")
    supported_models: list[str] = Field(
        default=["yolo26-s", "yolo26-n"],
        description="Supported AI models",
    )
    camera_interfaces: list[str] = Field(
        default=["csi", "usb"],
        description="Camera interfaces available",
    )


class DeviceMetrics(BaseModel):
    """Real-time device metrics | مقاييس الجهاز في الوقت الفعلي."""

    model_config = ConfigDict(extra="allow")

    cpu_usage_percent: float = Field(default=0.0, ge=0, le=100)
    gpu_usage_percent: float = Field(default=0.0, ge=0, le=100)
    memory_usage_percent: float = Field(default=0.0, ge=0, le=100)
    disk_usage_percent: float = Field(default=0.0, ge=0, le=100)
    temperature_celsius: float = Field(default=0.0)
    power_usage_watts: float = Field(default=0.0, ge=0)
    network_latency_ms: float = Field(default=0.0, ge=0)
    uptime_seconds: int = Field(default=0, ge=0)
    inference_fps: float = Field(default=0.0, ge=0)
    last_heartbeat: datetime | None = None


class GeoLocation(BaseModel):
    """Geographic location | الموقع الجغرافي."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude_m: float | None = Field(default=None, description="Altitude in meters")
    accuracy_m: float | None = Field(default=None, description="Accuracy in meters")


class EdgeDeviceBase(BilingualMixin):
    """Base schema for edge device | المخطط الأساسي لجهاز الحافة."""

    device_type: DeviceType = Field(
        default=DeviceType.JETSON_ORIN_NANO,
        description="Device type | نوع الجهاز",
    )
    farm_id: UUID = Field(..., description="Associated farm ID | معرف المزرعة")
    field_id: UUID | None = Field(
        default=None,
        description="Associated field ID | معرف الحقل",
    )
    location: GeoLocation | None = Field(
        default=None,
        description="Device location | موقع الجهاز",
    )
    ip_address: str | None = Field(default=None, description="Device IP address")
    mac_address: str | None = Field(default=None, description="Device MAC address")
    serial_number: str | None = Field(default=None, description="Device serial number")
    firmware_version: str | None = Field(default=None, description="Firmware version")
    installed_model: str | None = Field(
        default=None,
        description="Currently installed AI model",
    )
    installed_model_version: str | None = Field(
        default=None,
        description="Version of installed model",
    )
    tags: list[str] = Field(default=[], description="Device tags | علامات الجهاز")
    metadata: dict[str, Any] = Field(
        default={},
        description="Additional metadata | بيانات وصفية إضافية",
    )


class EdgeDeviceCreate(EdgeDeviceBase):
    """Schema for creating a new edge device | مخطط إنشاء جهاز حافة جديد."""

    @field_validator("mac_address")
    @classmethod
    def validate_mac_address(cls, v: str | None) -> str | None:
        """Validate MAC address format."""
        if v is None:
            return v
        # Normalize MAC address
        v = v.upper().replace("-", ":").strip()
        parts = v.split(":")
        if len(parts) != 6:
            raise ValueError("Invalid MAC address format. Expected XX:XX:XX:XX:XX:XX")
        for part in parts:
            if len(part) != 2:
                raise ValueError("Invalid MAC address format")
            try:
                int(part, 16)
            except ValueError:
                raise ValueError("Invalid MAC address format - must be hexadecimal")
        return v


class EdgeDeviceUpdate(BaseModel):
    """Schema for updating an edge device | مخطط تحديث جهاز الحافة."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    field_id: UUID | None = None
    location: GeoLocation | None = None
    ip_address: str | None = None
    firmware_version: str | None = None
    installed_model: str | None = None
    installed_model_version: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None
    status: DeviceStatus | None = None


class EdgeDevice(EdgeDeviceBase, TimestampMixin):
    """Complete edge device schema | مخطط جهاز الحافة الكامل."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Device unique ID | المعرف الفريد للجهاز")
    tenant_id: UUID = Field(..., description="Tenant ID | معرف المستأجر")
    status: DeviceStatus = Field(
        default=DeviceStatus.OFFLINE,
        description="Current status | الحالة الحالية",
    )
    capabilities: DeviceCapabilities = Field(default_factory=DeviceCapabilities)
    metrics: DeviceMetrics = Field(default_factory=DeviceMetrics)
    last_seen: datetime | None = Field(
        default=None,
        description="Last seen timestamp | آخر ظهور",
    )
    is_active: bool = Field(default=True, description="Is device active | هل الجهاز نشط")
    total_inference_count: int = Field(
        default=0,
        description="Total inferences run | إجمالي الاستدلالات",
    )
    total_sync_bytes: int = Field(
        default=0,
        description="Total bytes synced | إجمالي البايتات المزامنة",
    )


class EdgeDeviceList(BaseModel):
    """Paginated list of edge devices | قائمة أجهزة الحافة مرقمة."""

    items: list[EdgeDevice]
    total: int = Field(..., description="Total count | العدد الإجمالي")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    pages: int = Field(default=1, ge=1)


# =============================================================================
# Job Schemas | مخططات المهمة
# =============================================================================


class JobConfig(BaseModel):
    """Job configuration parameters | معلمات تكوين المهمة."""

    model_config = ConfigDict(extra="allow")

    model_name: str | None = Field(default=None, description="AI model to use")
    confidence_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Detection confidence threshold",
    )
    max_detections: int = Field(default=100, ge=1, le=1000)
    input_source: str | None = Field(
        default=None,
        description="Input source (camera, file path)",
    )
    output_format: str = Field(default="json", description="Output format")
    save_images: bool = Field(default=False, description="Save annotated images")
    batch_size: int = Field(default=1, ge=1, le=32)
    timeout_seconds: int = Field(default=300, ge=1, le=3600)


class EdgeJobBase(BaseModel):
    """Base schema for edge job | المخطط الأساسي لمهمة الحافة."""

    job_type: JobType = Field(..., description="Type of job | نوع المهمة")
    device_id: UUID = Field(..., description="Target device ID | معرف الجهاز المستهدف")
    priority: JobPriority = Field(
        default=JobPriority.NORMAL,
        description="Job priority | أولوية المهمة",
    )
    config: JobConfig = Field(
        default_factory=JobConfig,
        description="Job configuration | تكوين المهمة",
    )
    scheduled_at: datetime | None = Field(
        default=None,
        description="Scheduled execution time | وقت التنفيذ المجدول",
    )
    metadata: dict[str, Any] = Field(default={}, description="Additional metadata")


class EdgeJobCreate(EdgeJobBase):
    """Schema for creating a new job | مخطط إنشاء مهمة جديدة."""

    pass


class JobResult(BaseModel):
    """Job execution result | نتيجة تنفيذ المهمة."""

    model_config = ConfigDict(extra="allow")

    success: bool = Field(..., description="Whether job succeeded")
    message: str | None = Field(default=None, description="Result message")
    message_ar: str | None = Field(default=None, description="Result message in Arabic")
    output_data: dict[str, Any] = Field(default={}, description="Job output data")
    error_code: str | None = Field(default=None, description="Error code if failed")
    execution_time_ms: int | None = Field(default=None, description="Execution time in ms")
    detections_count: int | None = Field(default=None, description="Number of detections")
    artifacts: list[str] = Field(default=[], description="Generated artifact paths")


class EdgeJob(EdgeJobBase, TimestampMixin):
    """Complete edge job schema | مخطط مهمة الحافة الكامل."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Job unique ID | المعرف الفريد للمهمة")
    tenant_id: UUID = Field(..., description="Tenant ID | معرف المستأجر")
    status: JobStatus = Field(
        default=JobStatus.PENDING,
        description="Current status | الحالة الحالية",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When job started | وقت بدء المهمة",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When job completed | وقت اكتمال المهمة",
    )
    result: JobResult | None = Field(
        default=None,
        description="Job result | نتيجة المهمة",
    )
    retry_count: int = Field(default=0, description="Number of retries")
    max_retries: int = Field(default=3, description="Maximum retries allowed")
    progress_percent: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Progress percentage | نسبة التقدم",
    )


class EdgeJobList(BaseModel):
    """Paginated list of jobs | قائمة المهام مرقمة."""

    items: list[EdgeJob]
    total: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    pages: int = Field(default=1, ge=1)


# =============================================================================
# Sync Schemas | مخططات المزامنة
# =============================================================================


class SyncDataItem(BaseModel):
    """Single data item for synchronization | عنصر بيانات واحد للمزامنة."""

    model_config = ConfigDict(extra="allow")

    item_type: str = Field(..., description="Type of data item")
    item_id: str = Field(..., description="Unique identifier")
    data: dict[str, Any] = Field(..., description="Item data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checksum: str | None = Field(default=None, description="Data checksum for validation")


class SyncRequest(BaseModel):
    """Request to sync data from/to device | طلب مزامنة البيانات من/إلى الجهاز."""

    device_id: UUID = Field(..., description="Device to sync | الجهاز للمزامنة")
    direction: SyncDirection = Field(
        default=SyncDirection.UPLOAD,
        description="Sync direction | اتجاه المزامنة",
    )
    data_types: list[str] = Field(
        default=["inference_results", "sensor_data", "images"],
        description="Types of data to sync | أنواع البيانات للمزامنة",
    )
    since: datetime | None = Field(
        default=None,
        description="Sync data since this timestamp | مزامنة البيانات منذ",
    )
    items: list[SyncDataItem] = Field(
        default=[],
        description="Data items to sync | عناصر البيانات للمزامنة",
    )
    force: bool = Field(
        default=False,
        description="Force sync even if no changes | فرض المزامنة",
    )


class SyncProgress(BaseModel):
    """Sync operation progress | تقدم عملية المزامنة."""

    total_items: int = Field(default=0, description="Total items to sync")
    synced_items: int = Field(default=0, description="Items synced so far")
    failed_items: int = Field(default=0, description="Items that failed to sync")
    bytes_transferred: int = Field(default=0, description="Bytes transferred")
    percent_complete: float = Field(default=0.0, ge=0, le=100)
    estimated_time_remaining_seconds: int | None = Field(default=None)


class SyncResponse(BaseModel):
    """Response from sync operation | استجابة عملية المزامنة."""

    sync_id: UUID = Field(..., description="Sync operation ID | معرف عملية المزامنة")
    device_id: UUID
    status: str = Field(..., description="Sync status")
    direction: SyncDirection
    progress: SyncProgress = Field(default_factory=SyncProgress)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_message: str | None = None
    error_message_ar: str | None = None


# =============================================================================
# Deploy Schemas | مخططات النشر
# =============================================================================


class DeployRequest(BaseModel):
    """Request to deploy model to device | طلب نشر النموذج على الجهاز."""

    device_id: UUID = Field(..., description="Target device | الجهاز المستهدف")
    model_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Model to deploy | النموذج للنشر",
    )
    model_version: str = Field(
        default="latest",
        description="Model version | إصدار النموذج",
    )
    model_format: ModelFormat = Field(
        default=ModelFormat.TENSORRT,
        description="Model format | تنسيق النموذج",
    )
    force_update: bool = Field(
        default=False,
        description="Force update even if same version | فرض التحديث",
    )
    config_overrides: dict[str, Any] = Field(
        default={},
        description="Configuration overrides for deployment",
    )
    validate_after_deploy: bool = Field(
        default=True,
        description="Run validation after deployment",
    )


class DeployProgress(BaseModel):
    """Model deployment progress | تقدم نشر النموذج."""

    stage: str = Field(
        default="initializing",
        description="Current deployment stage",
    )
    stage_ar: str | None = Field(default=None, description="Stage in Arabic")
    percent_complete: float = Field(default=0.0, ge=0, le=100)
    bytes_transferred: int = Field(default=0)
    total_bytes: int = Field(default=0)
    estimated_time_remaining_seconds: int | None = None


class DeployResponse(BaseModel):
    """Response from deploy operation | استجابة عملية النشر."""

    deploy_id: UUID = Field(..., description="Deployment ID | معرف النشر")
    device_id: UUID
    model_name: str
    model_version: str
    status: str = Field(..., description="Deployment status")
    progress: DeployProgress = Field(default_factory=DeployProgress)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    validation_result: dict[str, Any] | None = Field(
        default=None,
        description="Post-deployment validation result",
    )
    error_message: str | None = None
    error_message_ar: str | None = None


# =============================================================================
# WebSocket Schemas | مخططات WebSocket
# =============================================================================


class WSMessageType(StrEnum):
    """WebSocket message types | أنواع رسائل WebSocket."""

    HEARTBEAT = "heartbeat"  # Device heartbeat | نبض القلب
    METRICS = "metrics"  # Device metrics update | تحديث المقاييس
    JOB_STATUS = "job_status"  # Job status update | تحديث حالة المهمة
    ALERT = "alert"  # Alert notification | إشعار تنبيه
    DETECTION = "detection"  # Real-time detection result | نتيجة كشف فوري
    SYNC_PROGRESS = "sync_progress"  # Sync progress update | تحديث تقدم المزامنة
    DEPLOY_PROGRESS = "deploy_progress"  # Deploy progress | تقدم النشر
    ERROR = "error"  # Error message | رسالة خطأ


class WSMessage(BaseModel):
    """WebSocket message format | تنسيق رسالة WebSocket."""

    type: WSMessageType
    device_id: UUID | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: dict[str, Any] = Field(default={})


class DetectionResult(BaseModel):
    """Real-time detection result | نتيجة الكشف في الوقت الفعلي."""

    model_config = ConfigDict(extra="allow")

    class_name: str = Field(..., description="Detected class name")
    class_name_ar: str | None = Field(default=None, description="Class name in Arabic")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    bbox: list[float] = Field(
        default=[],
        description="Bounding box [x1, y1, x2, y2]",
    )
    segmentation: list[list[float]] | None = Field(
        default=None,
        description="Segmentation polygon",
    )
    metadata: dict[str, Any] = Field(default={})


class InferenceResult(BaseModel):
    """Complete inference result | نتيجة الاستدلال الكاملة."""

    job_id: UUID | None = None
    device_id: UUID
    model_name: str
    model_version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    inference_time_ms: float = Field(..., ge=0)
    detections: list[DetectionResult] = Field(default=[])
    image_path: str | None = None
    field_id: UUID | None = None
    location: GeoLocation | None = None
    metadata: dict[str, Any] = Field(default={})


# =============================================================================
# Health Check Schemas | مخططات فحص الصحة
# =============================================================================


class HealthStatus(BaseModel):
    """Health check response | استجابة فحص الصحة."""

    status: str = Field(default="ok", description="Service status")
    service: str = Field(
        default="edge-orchestrator-service",
        description="Service name",
    )
    version: str = Field(default="16.0.0", description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReadinessStatus(BaseModel):
    """Readiness check response | استجابة فحص الجاهزية."""

    status: str = Field(default="ok")
    database: bool = Field(default=False, description="Database connection status")
    nats: bool = Field(default=False, description="NATS connection status")
    redis: bool = Field(default=False, description="Redis connection status")
    active_devices: int = Field(default=0, description="Number of active devices")
    active_jobs: int = Field(default=0, description="Number of active jobs")
