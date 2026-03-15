"""
SAHOOL Edge Events
===================
أحداث أجهزة الحافة - أحداث الأجهزة الطرفية والمعالجة المحلية

Edge device events for offline-first processing, device management,
job execution, data synchronization, and model deployment.

Event subjects follow pattern: sahool.edge.{event_type}
For tenant-scoped: sahool.tenant.{tenant_id}.edge.{event_type}

Usage:
    from shared.events.edge_events import (
        DeviceOnlineEvent,
        JobCompletedEvent,
        EdgeSubjects,
    )

    event = DeviceOnlineEvent(
        device_id=device_uuid,
        tenant_id=tenant_uuid,
        device_type="edge_gateway",
        firmware_version="2.1.0",
        ...
    )
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

# ─────────────────────────────────────────────────────────────────────────────
# Edge Subject Constants - ثوابت موضوعات أجهزة الحافة
# ─────────────────────────────────────────────────────────────────────────────


class EdgeSubjects:
    """
    NATS subject constants for edge device events.
    ثوابت موضوعات NATS لأحداث أجهزة الحافة
    """

    # Device status events
    DEVICE_ONLINE = "sahool.edge.device_online"
    DEVICE_OFFLINE = "sahool.edge.device_offline"
    DEVICE_REGISTERED = "sahool.edge.device_registered"
    DEVICE_DEREGISTERED = "sahool.edge.device_deregistered"
    DEVICE_HEALTH_UPDATE = "sahool.edge.device_health_update"
    DEVICE_ERROR = "sahool.edge.device_error"

    # Job events
    JOB_QUEUED = "sahool.edge.job_queued"
    JOB_STARTED = "sahool.edge.job_started"
    JOB_PROGRESS = "sahool.edge.job_progress"
    JOB_COMPLETED = "sahool.edge.job_completed"
    JOB_FAILED = "sahool.edge.job_failed"
    JOB_CANCELLED = "sahool.edge.job_cancelled"

    # Sync events
    SYNC_STARTED = "sahool.edge.sync_started"
    SYNC_PROGRESS = "sahool.edge.sync_progress"
    SYNC_COMPLETED = "sahool.edge.sync_completed"
    SYNC_FAILED = "sahool.edge.sync_failed"
    SYNC_CONFLICT = "sahool.edge.sync_conflict"

    # Model deployment events
    MODEL_DEPLOYED = "sahool.edge.model_deployed"
    MODEL_DEPLOYMENT_STARTED = "sahool.edge.model_deployment_started"
    MODEL_DEPLOYMENT_FAILED = "sahool.edge.model_deployment_failed"
    MODEL_UPDATED = "sahool.edge.model_updated"
    MODEL_ROLLBACK = "sahool.edge.model_rollback"

    # Firmware events
    FIRMWARE_UPDATE_AVAILABLE = "sahool.edge.firmware_update_available"
    FIRMWARE_UPDATE_STARTED = "sahool.edge.firmware_update_started"
    FIRMWARE_UPDATE_COMPLETED = "sahool.edge.firmware_update_completed"
    FIRMWARE_UPDATE_FAILED = "sahool.edge.firmware_update_failed"

    # Data events
    DATA_COLLECTED = "sahool.edge.data_collected"
    DATA_UPLOADED = "sahool.edge.data_uploaded"
    DATA_QUEUE_FULL = "sahool.edge.data_queue_full"

    # Wildcards
    # Note: NATS '*' matches a full token, not a prefix.
    # Edge subjects use underscores (e.g., device_online) so prefix-based
    # filtering is not possible. Use ALL to subscribe to all edge events.
    ALL = "sahool.edge.*"

    @staticmethod
    def tenant_scoped(tenant_id: str, event_type: str) -> str:
        """
        Get tenant-scoped subject for edge events.

        Args:
            tenant_id: Tenant identifier
            event_type: Event type (e.g., "device_online")

        Returns:
            Tenant-scoped subject (e.g., "sahool.tenant.org_123.edge.device_online")
        """
        return f"sahool.tenant.{tenant_id}.edge.{event_type}"

    @staticmethod
    def device_scoped(device_id: str, event_type: str) -> str:
        """
        Get device-scoped subject for device-specific events.

        Args:
            device_id: Device identifier
            event_type: Event type

        Returns:
            Device-scoped subject (e.g., "sahool.edge.device.dev_123.job_completed")
        """
        return f"sahool.edge.device.{device_id}.{event_type}"


# Convenience constants for direct import
SAHOOL_EDGE_DEVICE_ONLINE = EdgeSubjects.DEVICE_ONLINE
SAHOOL_EDGE_DEVICE_OFFLINE = EdgeSubjects.DEVICE_OFFLINE
SAHOOL_EDGE_DEVICE_REGISTERED = EdgeSubjects.DEVICE_REGISTERED
SAHOOL_EDGE_DEVICE_HEALTH_UPDATE = EdgeSubjects.DEVICE_HEALTH_UPDATE
SAHOOL_EDGE_DEVICE_ERROR = EdgeSubjects.DEVICE_ERROR
SAHOOL_EDGE_JOB_QUEUED = EdgeSubjects.JOB_QUEUED
SAHOOL_EDGE_JOB_STARTED = EdgeSubjects.JOB_STARTED
SAHOOL_EDGE_JOB_PROGRESS = EdgeSubjects.JOB_PROGRESS
SAHOOL_EDGE_JOB_COMPLETED = EdgeSubjects.JOB_COMPLETED
SAHOOL_EDGE_JOB_FAILED = EdgeSubjects.JOB_FAILED
SAHOOL_EDGE_SYNC_STARTED = EdgeSubjects.SYNC_STARTED
SAHOOL_EDGE_SYNC_COMPLETED = EdgeSubjects.SYNC_COMPLETED
SAHOOL_EDGE_SYNC_FAILED = EdgeSubjects.SYNC_FAILED
SAHOOL_EDGE_SYNC_CONFLICT = EdgeSubjects.SYNC_CONFLICT
SAHOOL_EDGE_MODEL_DEPLOYED = EdgeSubjects.MODEL_DEPLOYED
SAHOOL_EDGE_MODEL_DEPLOYMENT_STARTED = EdgeSubjects.MODEL_DEPLOYMENT_STARTED
SAHOOL_EDGE_MODEL_DEPLOYMENT_FAILED = EdgeSubjects.MODEL_DEPLOYMENT_FAILED
SAHOOL_EDGE_FIRMWARE_UPDATE_AVAILABLE = EdgeSubjects.FIRMWARE_UPDATE_AVAILABLE
SAHOOL_EDGE_DATA_COLLECTED = EdgeSubjects.DATA_COLLECTED
SAHOOL_EDGE_ALL = EdgeSubjects.ALL


# ─────────────────────────────────────────────────────────────────────────────
# Enums - التعدادات
# ─────────────────────────────────────────────────────────────────────────────


class DeviceType(StrEnum):
    """Edge device types"""

    EDGE_GATEWAY = "edge_gateway"
    FIELD_CAMERA = "field_camera"
    SENSOR_HUB = "sensor_hub"
    WEATHER_STATION = "weather_station"
    IRRIGATION_CONTROLLER = "irrigation_controller"
    DRONE_STATION = "drone_station"
    MOBILE_DEVICE = "mobile_device"


class DeviceStatus(StrEnum):
    """Device status states"""

    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UPDATING = "updating"
    INITIALIZING = "initializing"


class ConnectionType(StrEnum):
    """Network connection types"""

    WIFI = "wifi"
    CELLULAR_4G = "cellular_4g"
    CELLULAR_5G = "cellular_5g"
    ETHERNET = "ethernet"
    LORA = "lora"
    SATELLITE = "satellite"
    OFFLINE = "offline"


class JobType(StrEnum):
    """Edge job types"""

    INFERENCE = "inference"
    DATA_COLLECTION = "data_collection"
    SYNC = "sync"
    CALIBRATION = "calibration"
    DIAGNOSTICS = "diagnostics"
    FIRMWARE_UPDATE = "firmware_update"
    MODEL_UPDATE = "model_update"
    MAINTENANCE = "maintenance"


class JobStatus(StrEnum):
    """Job execution status"""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class SyncDirection(StrEnum):
    """Data synchronization direction"""

    UPLOAD = "upload"
    DOWNLOAD = "download"
    BIDIRECTIONAL = "bidirectional"


class SyncStatus(StrEnum):
    """Synchronization status"""

    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    COMPLETED_WITH_CONFLICTS = "completed_with_conflicts"
    FAILED = "failed"


class ModelType(StrEnum):
    """AI model types for edge deployment"""

    YOLO_PEST = "yolo_pest"
    YOLO_DISEASE = "yolo_disease"
    YOLO_WEED = "yolo_weed"
    YOLO_PLANT_COUNT = "yolo_plant_count"
    SEGMENTATION = "segmentation"
    CLASSIFICATION = "classification"
    ANOMALY_DETECTION = "anomaly_detection"


# ─────────────────────────────────────────────────────────────────────────────
# Base Edge Event - النموذج الأساسي لأحداث أجهزة الحافة
# ─────────────────────────────────────────────────────────────────────────────


class BaseEdgeEvent(BaseModel):
    """
    Base class for all edge device events.
    النموذج الأساسي لجميع أحداث أجهزة الحافة
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Event timestamp")
    version: str = Field(default="1.0", description="Event schema version")
    source_service: str = Field(default="edge-orchestrator", description="Service that emitted the event")
    correlation_id: str | None = Field(None, description="Correlation ID for tracing")

    @property
    def event_type(self) -> str:
        """Return the event type name (class name)"""
        return self.__class__.__name__

    model_config = ConfigDict(populate_by_name=True)


# ─────────────────────────────────────────────────────────────────────────────
# Supporting Models - النماذج الداعمة
# ─────────────────────────────────────────────────────────────────────────────


class DeviceCapabilities(BaseModel):
    """
    Device hardware and software capabilities.
    قدرات الجهاز من الأجهزة والبرمجيات
    """

    has_gpu: bool = Field(default=False, description="Has GPU for inference")
    gpu_type: str | None = Field(None, description="GPU type if available")
    has_camera: bool = Field(default=False, description="Has integrated camera")
    has_gps: bool = Field(default=True, description="Has GPS capability")
    storage_gb: float | None = Field(None, ge=0, description="Storage capacity in GB")
    ram_gb: float | None = Field(None, ge=0, description="RAM in GB")
    supported_models: list[str] = Field(default_factory=list, description="Supported AI model types")
    max_inference_fps: float | None = Field(None, ge=0, description="Maximum inference FPS")


class DeviceHealth(BaseModel):
    """
    Device health metrics.
    مقاييس صحة الجهاز
    """

    cpu_usage_percent: float = Field(..., ge=0, le=100, description="CPU usage")
    memory_usage_percent: float = Field(..., ge=0, le=100, description="Memory usage")
    storage_usage_percent: float = Field(..., ge=0, le=100, description="Storage usage")
    temperature_celsius: float | None = Field(None, description="Device temperature")
    battery_percent: float | None = Field(None, ge=0, le=100, description="Battery level if applicable")
    uptime_seconds: int = Field(..., ge=0, description="Device uptime")
    last_reboot: datetime | None = Field(None, description="Last reboot time")


class NetworkStatus(BaseModel):
    """
    Network connectivity status.
    حالة الاتصال بالشبكة
    """

    connection_type: str = Field(
        ...,
        pattern="^(wifi|cellular_4g|cellular_5g|ethernet|lora|satellite|offline)$",
        description="Connection type",
    )
    is_connected: bool = Field(..., description="Currently connected")
    signal_strength_dbm: int | None = Field(None, description="Signal strength in dBm")
    signal_quality_percent: float | None = Field(None, ge=0, le=100, description="Signal quality")
    bandwidth_mbps: float | None = Field(None, ge=0, description="Available bandwidth")
    latency_ms: int | None = Field(None, ge=0, description="Network latency")
    ip_address: str | None = Field(None, description="Current IP address")


class SyncStatistics(BaseModel):
    """
    Data synchronization statistics.
    إحصائيات مزامنة البيانات
    """

    records_uploaded: int = Field(default=0, ge=0, description="Records uploaded")
    records_downloaded: int = Field(default=0, ge=0, description="Records downloaded")
    bytes_uploaded: int = Field(default=0, ge=0, description="Bytes uploaded")
    bytes_downloaded: int = Field(default=0, ge=0, description="Bytes downloaded")
    conflicts_detected: int = Field(default=0, ge=0, description="Conflicts detected")
    conflicts_resolved: int = Field(default=0, ge=0, description="Conflicts auto-resolved")


class JobResult(BaseModel):
    """
    Job execution result.
    نتيجة تنفيذ المهمة
    """

    outputs_count: int = Field(default=0, ge=0, description="Number of outputs")
    detections_count: int | None = Field(None, ge=0, description="Detections if inference")
    files_generated: list[str] = Field(default_factory=list, description="Generated file paths")
    metrics: dict | None = Field(None, description="Job-specific metrics")


# ─────────────────────────────────────────────────────────────────────────────
# Device Status Events - أحداث حالة الأجهزة
# ─────────────────────────────────────────────────────────────────────────────


class DeviceOnlineEvent(BaseEdgeEvent):
    """
    Event emitted when an edge device comes online.
    حدث يُطلق عند اتصال جهاز حافة بالشبكة
    """

    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    farm_id: UUID | None = Field(None, description="Associated farm identifier")
    field_id: UUID | None = Field(None, description="Associated field identifier")

    # Device identification
    device_type: str = Field(
        ...,
        pattern="^(edge_gateway|field_camera|sensor_hub|weather_station|irrigation_controller|drone_station|mobile_device)$",
        description="Device type",
    )
    device_name: str = Field(..., description="Device friendly name")
    device_name_ar: str | None = Field(None, description="Arabic device name")
    serial_number: str | None = Field(None, description="Hardware serial number")

    # Version information
    firmware_version: str = Field(..., description="Current firmware version")
    software_version: str | None = Field(None, description="Application software version")
    os_version: str | None = Field(None, description="Operating system version")

    # Location
    location_lat: float | None = Field(None, ge=-90, le=90, description="Device latitude")
    location_lon: float | None = Field(None, ge=-180, le=180, description="Device longitude")

    # Capabilities
    capabilities: DeviceCapabilities | None = Field(None, description="Device capabilities")

    # Network status
    network_status: NetworkStatus = Field(..., description="Network connectivity status")

    # Health metrics
    health: DeviceHealth | None = Field(None, description="Device health metrics")

    # State
    was_graceful_shutdown: bool = Field(default=True, description="Previous shutdown was graceful")
    offline_duration_seconds: int | None = Field(None, ge=0, description="Duration device was offline")

    # Pending work
    pending_sync_count: int = Field(default=0, ge=0, description="Pending sync records")
    pending_jobs_count: int = Field(default=0, ge=0, description="Pending jobs")


class DeviceOfflineEvent(BaseEdgeEvent):
    """
    Event emitted when an edge device goes offline.
    حدث يُطلق عند انقطاع اتصال جهاز الحافة
    """

    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Device identification
    device_type: str = Field(..., description="Device type")
    device_name: str = Field(..., description="Device friendly name")

    # Offline reason
    reason: str = Field(
        ...,
        pattern="^(graceful_shutdown|connection_lost|timeout|error|maintenance|unknown)$",
        description="Offline reason",
    )
    last_seen_at: datetime = Field(..., description="Last seen timestamp")
    last_heartbeat_at: datetime | None = Field(None, description="Last heartbeat time")

    # Last known state
    last_known_health: DeviceHealth | None = Field(None, description="Last health metrics")
    last_known_network: NetworkStatus | None = Field(None, description="Last network status")

    # Impact assessment
    active_jobs_interrupted: int = Field(default=0, ge=0, description="Jobs interrupted by offline")
    pending_data_at_risk: bool = Field(default=False, description="Unsynchronized data at risk")

    # Error details if applicable
    error_code: str | None = Field(None, description="Error code if applicable")
    error_message: str | None = Field(None, description="Error message")


class DeviceRegisteredEvent(BaseEdgeEvent):
    """
    Event emitted when a new edge device is registered.
    حدث يُطلق عند تسجيل جهاز حافة جديد
    """

    device_id: UUID = Field(default_factory=uuid4, description="Assigned device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    farm_id: UUID | None = Field(None, description="Associated farm")
    field_id: UUID | None = Field(None, description="Associated field")

    # Device identification
    device_type: str = Field(..., description="Device type")
    device_name: str = Field(..., description="Device friendly name")
    device_name_ar: str | None = Field(None, description="Arabic device name")
    serial_number: str = Field(..., description="Hardware serial number")
    manufacturer: str | None = Field(None, description="Device manufacturer")
    model: str | None = Field(None, description="Device model")

    # Versions
    firmware_version: str = Field(..., description="Initial firmware version")

    # Capabilities
    capabilities: DeviceCapabilities = Field(..., description="Device capabilities")

    # Registration details
    registered_by: UUID | None = Field(None, description="User who registered device")
    registration_method: str = Field(
        default="manual",
        pattern="^(manual|auto_discovery|qr_code|api)$",
        description="Registration method",
    )

    # Assigned configuration
    assigned_models: list[str] = Field(default_factory=list, description="AI models to deploy")
    sync_interval_seconds: int = Field(default=300, ge=60, description="Data sync interval")


class DeviceHealthUpdateEvent(BaseEdgeEvent):
    """
    Event emitted periodically with device health metrics.
    حدث يُطلق دوريًا مع مقاييس صحة الجهاز
    """

    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Health metrics
    health: DeviceHealth = Field(..., description="Device health metrics")
    network_status: NetworkStatus = Field(..., description="Network status")

    # Status assessment
    status: str = Field(
        ...,
        pattern="^(healthy|degraded|warning|critical)$",
        description="Overall status assessment",
    )
    issues: list[str] = Field(default_factory=list, description="Current issues detected")

    # Resource trends
    cpu_trend: str | None = Field(None, pattern="^(stable|increasing|decreasing)$", description="CPU usage trend")
    memory_trend: str | None = Field(None, pattern="^(stable|increasing|decreasing)$", description="Memory usage trend")
    storage_trend: str | None = Field(
        None, pattern="^(stable|increasing|decreasing)$", description="Storage usage trend"
    )


class DeviceErrorEvent(BaseEdgeEvent):
    """
    Event emitted when a device encounters an error.
    حدث يُطلق عند مواجهة الجهاز لخطأ
    """

    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Error details
    error_code: str = Field(..., description="Error code")
    error_type: str = Field(
        ...,
        pattern="^(hardware|software|network|storage|sensor|inference|unknown)$",
        description="Error type",
    )
    severity: str = Field(..., pattern="^(warning|error|critical)$", description="Error severity")
    error_message: str = Field(..., description="Error message")
    error_message_ar: str | None = Field(None, description="Arabic error message")

    # Context
    component: str | None = Field(None, description="Component that errored")
    job_id: UUID | None = Field(None, description="Related job ID if applicable")

    # Recovery
    is_recoverable: bool = Field(default=True, description="Error is recoverable")
    auto_recovery_attempted: bool = Field(default=False, description="Auto-recovery was attempted")
    recovery_action_required: str | None = Field(None, description="Required recovery action")
    recovery_action_required_ar: str | None = Field(None, description="Arabic recovery action")


# ─────────────────────────────────────────────────────────────────────────────
# Job Events - أحداث المهام
# ─────────────────────────────────────────────────────────────────────────────


class JobQueuedEvent(BaseEdgeEvent):
    """
    Event emitted when a job is queued for edge execution.
    حدث يُطلق عند وضع مهمة في قائمة الانتظار للتنفيذ
    """

    job_id: UUID = Field(default_factory=uuid4, description="Job identifier")
    device_id: UUID = Field(..., description="Target device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    field_id: UUID | None = Field(None, description="Target field if applicable")

    # Job specification
    job_type: str = Field(
        ...,
        pattern="^(inference|data_collection|sync|calibration|diagnostics|firmware_update|model_update|maintenance)$",
        description="Job type",
    )
    job_name: str = Field(..., description="Job name")
    job_name_ar: str | None = Field(None, description="Arabic job name")
    priority: int = Field(default=5, ge=1, le=10, description="Priority (1=highest)")

    # Parameters
    parameters: dict | None = Field(None, description="Job parameters")
    timeout_seconds: int | None = Field(None, ge=0, description="Job timeout")

    # Scheduling
    scheduled_at: datetime | None = Field(None, description="Scheduled execution time")
    queued_by: UUID | None = Field(None, description="User who queued the job")
    queue_position: int | None = Field(None, ge=1, description="Position in queue")


class JobStartedEvent(BaseEdgeEvent):
    """
    Event emitted when a job starts executing on edge device.
    حدث يُطلق عند بدء تنفيذ مهمة على جهاز الحافة
    """

    job_id: UUID = Field(..., description="Job identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Job info
    job_type: str = Field(..., description="Job type")
    job_name: str = Field(..., description="Job name")

    # Execution context
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Start time")
    estimated_duration_seconds: int | None = Field(None, ge=0, description="Estimated duration")
    queue_wait_seconds: int | None = Field(None, ge=0, description="Time spent in queue")

    # Resources allocated
    gpu_allocated: bool = Field(default=False, description="GPU allocated for job")
    model_loaded: str | None = Field(None, description="AI model loaded if applicable")


class JobProgressEvent(BaseEdgeEvent):
    """
    Event emitted to report job progress.
    حدث يُطلق للإبلاغ عن تقدم المهمة
    """

    job_id: UUID = Field(..., description="Job identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Progress
    progress_percent: float = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: str | None = Field(None, description="Current step description")
    current_step_ar: str | None = Field(None, description="Arabic step description")

    # Stats
    items_processed: int = Field(default=0, ge=0, description="Items processed")
    items_total: int | None = Field(None, ge=0, description="Total items")

    # Timing
    elapsed_seconds: int = Field(..., ge=0, description="Elapsed time")
    estimated_remaining_seconds: int | None = Field(None, ge=0, description="Estimated remaining time")


class JobCompletedEvent(BaseEdgeEvent):
    """
    Event emitted when a job completes successfully.
    حدث يُطلق عند اكتمال مهمة بنجاح
    """

    job_id: UUID = Field(..., description="Job identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    field_id: UUID | None = Field(None, description="Target field if applicable")

    # Job info
    job_type: str = Field(..., description="Job type")
    job_name: str = Field(..., description="Job name")

    # Timing
    started_at: datetime = Field(..., description="Start time")
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Completion time")
    duration_seconds: int = Field(..., ge=0, description="Total duration")

    # Results
    result: JobResult = Field(..., description="Job result")
    status: str = Field(default="completed", description="Completion status")

    # Resource usage
    cpu_usage_avg_percent: float | None = Field(None, ge=0, le=100, description="Average CPU usage")
    memory_usage_max_percent: float | None = Field(None, ge=0, le=100, description="Peak memory usage")
    gpu_usage_avg_percent: float | None = Field(None, ge=0, le=100, description="Average GPU usage")

    # Output
    output_files: list[str] = Field(default_factory=list, description="Output file paths")
    output_data_bytes: int | None = Field(None, ge=0, description="Output data size")


class JobFailedEvent(BaseEdgeEvent):
    """
    Event emitted when a job fails.
    حدث يُطلق عند فشل مهمة
    """

    job_id: UUID = Field(..., description="Job identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Job info
    job_type: str = Field(..., description="Job type")
    job_name: str = Field(..., description="Job name")

    # Failure details
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    error_message_ar: str | None = Field(None, description="Arabic error message")
    failed_at_step: str | None = Field(None, description="Step where failure occurred")

    # Timing
    started_at: datetime = Field(..., description="Start time")
    failed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Failure time")
    duration_seconds: int = Field(..., ge=0, description="Duration before failure")

    # Partial results
    partial_results: JobResult | None = Field(None, description="Partial results if any")

    # Recovery
    retry_count: int = Field(default=0, ge=0, description="Retry attempts made")
    is_retriable: bool = Field(default=True, description="Can be retried")
    next_retry_at: datetime | None = Field(None, description="Next retry time if scheduled")


class JobCancelledEvent(BaseEdgeEvent):
    """
    Event emitted when a job is cancelled.
    حدث يُطلق عند إلغاء مهمة
    """

    job_id: UUID = Field(..., description="Job identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Cancellation details
    cancelled_by: UUID | None = Field(None, description="User who cancelled")
    cancellation_reason: str | None = Field(None, description="Cancellation reason")
    cancellation_reason_ar: str | None = Field(None, description="Arabic reason")
    was_running: bool = Field(default=False, description="Was running when cancelled")

    # Partial results
    progress_at_cancellation: float | None = Field(None, ge=0, le=100, description="Progress when cancelled")
    partial_results: JobResult | None = Field(None, description="Partial results if any")


# ─────────────────────────────────────────────────────────────────────────────
# Sync Events - أحداث المزامنة
# ─────────────────────────────────────────────────────────────────────────────


class SyncStartedEvent(BaseEdgeEvent):
    """
    Event emitted when data synchronization starts.
    حدث يُطلق عند بدء مزامنة البيانات
    """

    sync_id: UUID = Field(default_factory=uuid4, description="Sync session identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Sync configuration
    sync_direction: str = Field(
        ...,
        pattern="^(upload|download|bidirectional)$",
        description="Sync direction",
    )
    sync_type: str = Field(
        default="incremental",
        pattern="^(full|incremental|selective)$",
        description="Sync type",
    )

    # Scope
    data_types: list[str] = Field(default_factory=list, description="Data types to sync")
    records_to_sync: int | None = Field(None, ge=0, description="Records to sync")
    bytes_to_sync: int | None = Field(None, ge=0, description="Bytes to sync")

    # Trigger
    trigger: str = Field(
        default="scheduled",
        pattern="^(scheduled|manual|auto|connectivity_restored)$",
        description="Sync trigger",
    )


class SyncProgressEvent(BaseEdgeEvent):
    """
    Event emitted to report synchronization progress.
    حدث يُطلق للإبلاغ عن تقدم المزامنة
    """

    sync_id: UUID = Field(..., description="Sync session identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Progress
    progress_percent: float = Field(..., ge=0, le=100, description="Progress percentage")
    current_phase: str = Field(..., description="Current sync phase")

    # Statistics
    statistics: SyncStatistics = Field(..., description="Current sync statistics")

    # Timing
    elapsed_seconds: int = Field(..., ge=0, description="Elapsed time")
    estimated_remaining_seconds: int | None = Field(None, ge=0, description="Estimated remaining")


class SyncCompletedEvent(BaseEdgeEvent):
    """
    Event emitted when data synchronization completes.
    حدث يُطلق عند اكتمال مزامنة البيانات
    """

    sync_id: UUID = Field(..., description="Sync session identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Result
    status: str = Field(
        ...,
        pattern="^(completed|completed_with_conflicts|partial)$",
        description="Completion status",
    )

    # Statistics
    statistics: SyncStatistics = Field(..., description="Final sync statistics")

    # Timing
    started_at: datetime = Field(..., description="Sync start time")
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Completion time")
    duration_seconds: int = Field(..., ge=0, description="Total duration")

    # Transfer details
    average_speed_kbps: float | None = Field(None, ge=0, description="Average transfer speed")

    # Next sync
    next_scheduled_sync: datetime | None = Field(None, description="Next scheduled sync")


class SyncFailedEvent(BaseEdgeEvent):
    """
    Event emitted when data synchronization fails.
    حدث يُطلق عند فشل مزامنة البيانات
    """

    sync_id: UUID = Field(..., description="Sync session identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Failure details
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    error_message_ar: str | None = Field(None, description="Arabic error message")
    failed_at_phase: str | None = Field(None, description="Phase where failure occurred")

    # Partial progress
    statistics: SyncStatistics | None = Field(None, description="Statistics before failure")

    # Recovery
    is_retriable: bool = Field(default=True, description="Can be retried")
    next_retry_at: datetime | None = Field(None, description="Next retry time")
    data_at_risk: bool = Field(default=False, description="Unsynced data at risk")


class SyncConflictEvent(BaseEdgeEvent):
    """
    Event emitted when a sync conflict is detected.
    حدث يُطلق عند اكتشاف تعارض في المزامنة
    """

    conflict_id: UUID = Field(default_factory=uuid4, description="Conflict identifier")
    sync_id: UUID = Field(..., description="Sync session identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Conflict details
    entity_type: str = Field(..., description="Type of entity in conflict")
    entity_id: str = Field(..., description="Entity identifier")
    conflict_type: str = Field(
        ...,
        pattern="^(update_update|update_delete|delete_update|create_create)$",
        description="Conflict type",
    )

    # Versions
    local_version: int = Field(..., ge=0, description="Local version number")
    remote_version: int = Field(..., ge=0, description="Remote version number")
    local_modified_at: datetime = Field(..., description="Local modification time")
    remote_modified_at: datetime = Field(..., description="Remote modification time")

    # Resolution
    resolution_strategy: str = Field(
        default="manual",
        pattern="^(local_wins|remote_wins|merge|manual)$",
        description="Resolution strategy",
    )
    auto_resolved: bool = Field(default=False, description="Was auto-resolved")
    resolved_at: datetime | None = Field(None, description="Resolution time")
    resolved_by: UUID | None = Field(None, description="User who resolved")


# ─────────────────────────────────────────────────────────────────────────────
# Model Deployment Events - أحداث نشر النماذج
# ─────────────────────────────────────────────────────────────────────────────


class ModelDeploymentStartedEvent(BaseEdgeEvent):
    """
    Event emitted when model deployment to edge device starts.
    حدث يُطلق عند بدء نشر نموذج على جهاز الحافة
    """

    deployment_id: UUID = Field(default_factory=uuid4, description="Deployment identifier")
    device_id: UUID = Field(..., description="Target device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Model information
    model_id: str = Field(..., description="Model identifier")
    model_type: str = Field(
        ...,
        pattern="^(yolo_pest|yolo_disease|yolo_weed|yolo_plant_count|segmentation|classification|anomaly_detection)$",
        description="Model type",
    )
    model_version: str = Field(..., description="Model version")
    model_size_mb: float = Field(..., ge=0, description="Model size in MB")

    # Deployment configuration
    deployment_type: str = Field(
        default="update",
        pattern="^(initial|update|rollback)$",
        description="Deployment type",
    )
    replacing_version: str | None = Field(None, description="Version being replaced")

    # Initiated by
    initiated_by: UUID | None = Field(None, description="User who initiated deployment")


class ModelDeployedEvent(BaseEdgeEvent):
    """
    Event emitted when a model is successfully deployed to edge device.
    حدث يُطلق عند نشر نموذج بنجاح على جهاز الحافة
    """

    deployment_id: UUID = Field(..., description="Deployment identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Model information
    model_id: str = Field(..., description="Model identifier")
    model_type: str = Field(..., description="Model type")
    model_version: str = Field(..., description="Deployed model version")
    previous_version: str | None = Field(None, description="Previous model version")

    # Deployment details
    deployment_type: str = Field(..., description="Deployment type")
    started_at: datetime = Field(..., description="Deployment start time")
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Completion time")
    duration_seconds: int = Field(..., ge=0, description="Deployment duration")

    # Validation
    validation_passed: bool = Field(default=True, description="Model validation passed")
    inference_test_passed: bool = Field(default=True, description="Inference test passed")
    test_inference_time_ms: int | None = Field(None, ge=0, description="Test inference time")

    # Storage
    model_path: str = Field(..., description="Model file path on device")
    storage_used_mb: float = Field(..., ge=0, description="Storage used")


class ModelDeploymentFailedEvent(BaseEdgeEvent):
    """
    Event emitted when model deployment fails.
    حدث يُطلق عند فشل نشر النموذج
    """

    deployment_id: UUID = Field(..., description="Deployment identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Model information
    model_id: str = Field(..., description="Model identifier")
    model_type: str = Field(..., description="Model type")
    model_version: str = Field(..., description="Attempted model version")

    # Failure details
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    error_message_ar: str | None = Field(None, description="Arabic error message")
    failed_at_step: str = Field(
        ...,
        pattern="^(download|extraction|validation|installation|inference_test)$",
        description="Step where failure occurred",
    )

    # Rollback
    rollback_triggered: bool = Field(default=False, description="Rollback was triggered")
    rollback_version: str | None = Field(None, description="Version rolled back to")

    # Recovery
    is_retriable: bool = Field(default=True, description="Can be retried")


class ModelRollbackEvent(BaseEdgeEvent):
    """
    Event emitted when a model is rolled back to a previous version.
    حدث يُطلق عند التراجع عن نموذج إلى إصدار سابق
    """

    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Model information
    model_id: str = Field(..., description="Model identifier")
    model_type: str = Field(..., description="Model type")
    rolled_back_from: str = Field(..., description="Version rolled back from")
    rolled_back_to: str = Field(..., description="Version rolled back to")

    # Rollback details
    rollback_reason: str = Field(..., description="Reason for rollback")
    rollback_reason_ar: str | None = Field(None, description="Arabic reason")
    triggered_by: str = Field(
        ...,
        pattern="^(automatic|manual|deployment_failure|performance_degradation)$",
        description="Rollback trigger",
    )
    triggered_by_user: UUID | None = Field(None, description="User if manual rollback")

    # Status
    rollback_successful: bool = Field(default=True, description="Rollback succeeded")


# ─────────────────────────────────────────────────────────────────────────────
# Data Collection Events - أحداث جمع البيانات
# ─────────────────────────────────────────────────────────────────────────────


class DataCollectedEvent(BaseEdgeEvent):
    """
    Event emitted when data is collected on edge device.
    حدث يُطلق عند جمع البيانات على جهاز الحافة
    """

    collection_id: UUID = Field(default_factory=uuid4, description="Collection identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")
    field_id: UUID | None = Field(None, description="Field identifier if applicable")

    # Data type
    data_type: str = Field(
        ...,
        pattern="^(image|sensor_reading|weather|video|audio|inference_result)$",
        description="Type of data collected",
    )

    # Collection details
    records_count: int = Field(..., ge=1, description="Number of records")
    data_size_bytes: int = Field(..., ge=0, description="Data size in bytes")
    collection_duration_seconds: int | None = Field(None, ge=0, description="Collection duration")

    # Storage
    stored_locally: bool = Field(default=True, description="Stored on device")
    local_path: str | None = Field(None, description="Local storage path")
    pending_upload: bool = Field(default=True, description="Pending upload to cloud")

    # Quality
    quality_score: float | None = Field(None, ge=0, le=1, description="Data quality score")


class DataUploadedEvent(BaseEdgeEvent):
    """
    Event emitted when collected data is uploaded to cloud.
    حدث يُطلق عند رفع البيانات المجمعة إلى السحابة
    """

    upload_id: UUID = Field(default_factory=uuid4, description="Upload identifier")
    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Upload details
    collection_ids: list[UUID] = Field(..., description="Collection IDs uploaded")
    records_uploaded: int = Field(..., ge=0, description="Records uploaded")
    bytes_uploaded: int = Field(..., ge=0, description="Bytes uploaded")

    # Timing
    upload_duration_seconds: int = Field(..., ge=0, description="Upload duration")
    average_speed_kbps: float | None = Field(None, ge=0, description="Upload speed")

    # Status
    upload_successful: bool = Field(default=True, description="Upload successful")
    local_data_deleted: bool = Field(default=False, description="Local data deleted after upload")


# ─────────────────────────────────────────────────────────────────────────────
# Firmware Update Events - أحداث تحديث البرنامج الثابت
# ─────────────────────────────────────────────────────────────────────────────


class FirmwareUpdateAvailableEvent(BaseEdgeEvent):
    """
    Event emitted when a firmware update is available.
    حدث يُطلق عند توفر تحديث للبرنامج الثابت
    """

    device_id: UUID = Field(..., description="Target device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Version information
    current_version: str = Field(..., description="Current firmware version")
    available_version: str = Field(..., description="Available firmware version")

    # Update details
    update_size_mb: float = Field(..., ge=0, description="Update size in MB")
    release_notes: str | None = Field(None, description="Release notes")
    release_notes_ar: str | None = Field(None, description="Arabic release notes")
    is_critical: bool = Field(default=False, description="Is critical security update")
    is_mandatory: bool = Field(default=False, description="Update is mandatory")

    # Compatibility
    requires_reboot: bool = Field(default=True, description="Requires device reboot")
    estimated_downtime_minutes: int = Field(..., ge=0, description="Estimated downtime")


class FirmwareUpdateCompletedEvent(BaseEdgeEvent):
    """
    Event emitted when firmware update completes.
    حدث يُطلق عند اكتمال تحديث البرنامج الثابت
    """

    device_id: UUID = Field(..., description="Device identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Version information
    previous_version: str = Field(..., description="Previous firmware version")
    new_version: str = Field(..., description="New firmware version")

    # Update details
    started_at: datetime = Field(..., description="Update start time")
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Completion time")
    duration_seconds: int = Field(..., ge=0, description="Update duration")
    reboot_count: int = Field(default=1, ge=0, description="Number of reboots")

    # Validation
    post_update_check_passed: bool = Field(default=True, description="Post-update checks passed")


# ─────────────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # Subject constants
    "EdgeSubjects",
    "SAHOOL_EDGE_DEVICE_ONLINE",
    "SAHOOL_EDGE_DEVICE_OFFLINE",
    "SAHOOL_EDGE_DEVICE_REGISTERED",
    "SAHOOL_EDGE_DEVICE_HEALTH_UPDATE",
    "SAHOOL_EDGE_DEVICE_ERROR",
    "SAHOOL_EDGE_JOB_QUEUED",
    "SAHOOL_EDGE_JOB_STARTED",
    "SAHOOL_EDGE_JOB_PROGRESS",
    "SAHOOL_EDGE_JOB_COMPLETED",
    "SAHOOL_EDGE_JOB_FAILED",
    "SAHOOL_EDGE_SYNC_STARTED",
    "SAHOOL_EDGE_SYNC_COMPLETED",
    "SAHOOL_EDGE_SYNC_FAILED",
    "SAHOOL_EDGE_SYNC_CONFLICT",
    "SAHOOL_EDGE_MODEL_DEPLOYED",
    "SAHOOL_EDGE_MODEL_DEPLOYMENT_STARTED",
    "SAHOOL_EDGE_MODEL_DEPLOYMENT_FAILED",
    "SAHOOL_EDGE_FIRMWARE_UPDATE_AVAILABLE",
    "SAHOOL_EDGE_DATA_COLLECTED",
    "SAHOOL_EDGE_ALL",
    # Enums
    "DeviceType",
    "DeviceStatus",
    "ConnectionType",
    "JobType",
    "JobStatus",
    "SyncDirection",
    "SyncStatus",
    "ModelType",
    # Supporting models
    "DeviceCapabilities",
    "DeviceHealth",
    "NetworkStatus",
    "SyncStatistics",
    "JobResult",
    # Base event
    "BaseEdgeEvent",
    # Device status events
    "DeviceOnlineEvent",
    "DeviceOfflineEvent",
    "DeviceRegisteredEvent",
    "DeviceHealthUpdateEvent",
    "DeviceErrorEvent",
    # Job events
    "JobQueuedEvent",
    "JobStartedEvent",
    "JobProgressEvent",
    "JobCompletedEvent",
    "JobFailedEvent",
    "JobCancelledEvent",
    # Sync events
    "SyncStartedEvent",
    "SyncProgressEvent",
    "SyncCompletedEvent",
    "SyncFailedEvent",
    "SyncConflictEvent",
    # Model deployment events
    "ModelDeploymentStartedEvent",
    "ModelDeployedEvent",
    "ModelDeploymentFailedEvent",
    "ModelRollbackEvent",
    # Data events
    "DataCollectedEvent",
    "DataUploadedEvent",
    # Firmware events
    "FirmwareUpdateAvailableEvent",
    "FirmwareUpdateCompletedEvent",
]
