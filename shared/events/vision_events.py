"""
SAHOOL Vision Events
=====================
أحداث الرؤية الحاسوبية - أحداث اكتشاف YOLO26

YOLO26-based computer vision detection events for pest, disease, weed detection,
and plant counting in agricultural fields.

Event subjects follow pattern: sahool.vision.{event_type}
For tenant-scoped: sahool.tenant.{tenant_id}.vision.{event_type}

Usage:
    from shared.events.vision_events import (
        PestDetectedEvent,
        DiseaseDetectedEvent,
        VisionSubjects,
    )

    event = PestDetectedEvent(
        field_id=field_uuid,
        detection_id=detection_uuid,
        pest_class="fall_armyworm",
        pest_class_ar="دودة الحشد الخريفية",
        confidence=0.92,
        severity="high",
        ...
    )
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

# ─────────────────────────────────────────────────────────────────────────────
# Vision Subject Constants - ثوابت موضوعات الرؤية
# ─────────────────────────────────────────────────────────────────────────────


class VisionSubjects:
    """
    NATS subject constants for vision detection events.
    ثوابت موضوعات NATS لأحداث اكتشاف الرؤية الحاسوبية
    """

    # Detection events
    PEST_DETECTED = "sahool.vision.pest_detected"
    DISEASE_DETECTED = "sahool.vision.disease_detected"
    WEED_DETECTED = "sahool.vision.weed_detected"
    PLANT_COUNT_COMPLETED = "sahool.vision.plant_count_completed"
    CRITICAL_ALERT = "sahool.vision.critical_alert"

    # Processing events
    ANALYSIS_STARTED = "sahool.vision.analysis_started"
    ANALYSIS_COMPLETED = "sahool.vision.analysis_completed"
    ANALYSIS_FAILED = "sahool.vision.analysis_failed"

    # Model events
    MODEL_INFERENCE_COMPLETED = "sahool.vision.model_inference_completed"
    MODEL_UPDATED = "sahool.vision.model_updated"

    # Wildcards
    ALL = "sahool.vision.*"
    DETECTIONS_ALL = "sahool.vision.*.detected"

    @staticmethod
    def tenant_scoped(tenant_id: str, event_type: str) -> str:
        """
        Get tenant-scoped subject for vision events.

        Args:
            tenant_id: Tenant identifier
            event_type: Event type (e.g., "pest_detected")

        Returns:
            Tenant-scoped subject (e.g., "sahool.tenant.org_123.vision.pest_detected")
        """
        return f"sahool.tenant.{tenant_id}.vision.{event_type}"


# Convenience constants for direct import
SAHOOL_VISION_PEST_DETECTED = VisionSubjects.PEST_DETECTED
SAHOOL_VISION_DISEASE_DETECTED = VisionSubjects.DISEASE_DETECTED
SAHOOL_VISION_WEED_DETECTED = VisionSubjects.WEED_DETECTED
SAHOOL_VISION_PLANT_COUNT_COMPLETED = VisionSubjects.PLANT_COUNT_COMPLETED
SAHOOL_VISION_CRITICAL_ALERT = VisionSubjects.CRITICAL_ALERT
SAHOOL_VISION_ANALYSIS_STARTED = VisionSubjects.ANALYSIS_STARTED
SAHOOL_VISION_ANALYSIS_COMPLETED = VisionSubjects.ANALYSIS_COMPLETED
SAHOOL_VISION_ANALYSIS_FAILED = VisionSubjects.ANALYSIS_FAILED
SAHOOL_VISION_ALL = VisionSubjects.ALL


# ─────────────────────────────────────────────────────────────────────────────
# Enums - التعدادات
# ─────────────────────────────────────────────────────────────────────────────


class DetectionSeverity(StrEnum):
    """Severity levels for detections"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionSource(StrEnum):
    """Source of detection"""

    DRONE = "drone"
    MOBILE = "mobile"
    FIELD_CAMERA = "field_camera"
    SATELLITE = "satellite"
    EDGE_DEVICE = "edge_device"


class InfestationLevel(StrEnum):
    """Infestation/infection level"""

    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


# ─────────────────────────────────────────────────────────────────────────────
# Base Vision Event - النموذج الأساسي لأحداث الرؤية
# ─────────────────────────────────────────────────────────────────────────────


class BaseVisionEvent(BaseModel):
    """
    Base class for all vision detection events.
    النموذج الأساسي لجميع أحداث اكتشاف الرؤية
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event identifier")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Event timestamp")
    version: str = Field(default="1.0", description="Event schema version")
    source_service: str = Field(default="vision-ai-service", description="Service that emitted the event")
    correlation_id: str | None = Field(None, description="Correlation ID for tracing")

    @property
    def event_type(self) -> str:
        """Return the event type name (class name)"""
        return self.__class__.__name__

    model_config = ConfigDict(populate_by_name=True)


# ─────────────────────────────────────────────────────────────────────────────
# Bounding Box Model - نموذج مربع الإحاطة
# ─────────────────────────────────────────────────────────────────────────────


class DetectionBoundingBox(BaseModel):
    """
    Bounding box coordinates for detected objects (YOLO26 vision detections).
    إحداثيات مربع الإحاطة للكائنات المكتشفة (اكتشافات الرؤية YOLO26)
    """

    x_min: float = Field(..., ge=0, description="Left boundary (normalized 0-1 or pixels)")
    y_min: float = Field(..., ge=0, description="Top boundary")
    x_max: float = Field(..., ge=0, description="Right boundary")
    y_max: float = Field(..., ge=0, description="Bottom boundary")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence")

    # Optional pixel coordinates
    pixel_x: int | None = Field(None, ge=0, description="Pixel X coordinate")
    pixel_y: int | None = Field(None, ge=0, description="Pixel Y coordinate")
    width_px: int | None = Field(None, ge=0, description="Width in pixels")
    height_px: int | None = Field(None, ge=0, description="Height in pixels")


# Backward-compatible alias
BoundingBox = DetectionBoundingBox


class GeoLocation(BaseModel):
    """
    Geographic location for field-level detections.
    الموقع الجغرافي للاكتشافات على مستوى الحقل
    """

    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    altitude_m: float | None = Field(None, description="Altitude in meters")
    accuracy_m: float | None = Field(None, ge=0, description="GPS accuracy in meters")


# ─────────────────────────────────────────────────────────────────────────────
# Pest Detection Event - حدث اكتشاف الآفات
# ─────────────────────────────────────────────────────────────────────────────


class PestDetectedEvent(BaseVisionEvent):
    """
    Event emitted when a pest is detected via YOLO26 model.
    حدث يُطلق عند اكتشاف آفة عبر نموذج YOLO26
    """

    detection_id: UUID = Field(default_factory=uuid4, description="Unique detection identifier")
    field_id: UUID = Field(..., description="Field where pest was detected")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Pest classification
    pest_class: str = Field(..., description="Pest class/species name")
    pest_class_ar: str | None = Field(None, description="Arabic pest name")
    pest_family: str | None = Field(None, description="Pest family classification")
    scientific_name: str | None = Field(None, description="Scientific name")

    # Detection details
    confidence: float = Field(..., ge=0, le=1, description="Model confidence score")
    severity: str = Field(..., pattern="^(low|medium|high|critical)$", description="Severity level")
    infestation_level: str | None = Field(
        None,
        pattern="^(none|light|moderate|severe|critical)$",
        description="Infestation level",
    )

    # Location
    location: BoundingBox = Field(..., description="Bounding box coordinates")
    geo_location: GeoLocation | None = Field(None, description="GPS coordinates")
    zone_id: str | None = Field(None, description="Field zone identifier")

    # Image data
    image_url: str = Field(..., description="Source image URL")
    thumbnail_url: str | None = Field(None, description="Detection thumbnail URL")
    annotated_image_url: str | None = Field(None, description="Annotated image URL")

    # Detection metadata
    detection_source: str = Field(
        default="mobile",
        pattern="^(drone|mobile|field_camera|satellite|edge_device)$",
        description="Detection source",
    )
    model_version: str | None = Field(None, description="YOLO model version used")
    processing_time_ms: int | None = Field(None, ge=0, description="Processing time")

    # Crop context
    crop_type: str | None = Field(None, description="Affected crop type")
    crop_type_ar: str | None = Field(None, description="Arabic crop type")
    growth_stage: str | None = Field(None, description="Crop growth stage")

    # Count estimation
    estimated_count: int | None = Field(None, ge=0, description="Estimated pest count")
    affected_area_sqm: float | None = Field(None, ge=0, description="Affected area in m2")
    affected_area_percentage: float | None = Field(None, ge=0, le=100, description="Percentage of field affected")

    # Recommendations
    recommended_action: str | None = Field(None, description="Recommended action")
    recommended_action_ar: str | None = Field(None, description="Arabic recommendation")
    urgency_hours: int | None = Field(None, ge=0, description="Action urgency in hours")

    # Economic impact
    estimated_yield_loss_percentage: float | None = Field(
        None, ge=0, le=100, description="Estimated yield loss percentage"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Disease Detection Event - حدث اكتشاف الأمراض
# ─────────────────────────────────────────────────────────────────────────────


class VisionDiseaseDetectedEvent(BaseVisionEvent):
    """
    Event emitted when a plant disease is detected via YOLO26 model.
    حدث يُطلق عند اكتشاف مرض نباتي عبر نموذج YOLO26

    Note: Named VisionDiseaseDetectedEvent to distinguish from health.disease_detected
    """

    detection_id: UUID = Field(default_factory=uuid4, description="Unique detection identifier")
    field_id: UUID = Field(..., description="Field where disease was detected")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Disease classification
    disease_class: str = Field(..., description="Disease class/name")
    disease_class_ar: str | None = Field(None, description="Arabic disease name")
    disease_category: str | None = Field(
        None,
        pattern="^(fungal|bacterial|viral|physiological|nutrient_deficiency)$",
        description="Disease category",
    )
    pathogen_name: str | None = Field(None, description="Pathogen scientific name")

    # Detection details
    confidence: float = Field(..., ge=0, le=1, description="Model confidence score")
    severity: str = Field(..., pattern="^(low|medium|high|critical)$", description="Severity level")
    infection_stage: str | None = Field(
        None,
        pattern="^(early|developing|advanced|terminal)$",
        description="Infection stage",
    )

    # Location
    location: BoundingBox = Field(..., description="Bounding box coordinates")
    geo_location: GeoLocation | None = Field(None, description="GPS coordinates")
    zone_id: str | None = Field(None, description="Field zone identifier")

    # Image data
    image_url: str = Field(..., description="Source image URL")
    thumbnail_url: str | None = Field(None, description="Detection thumbnail URL")
    annotated_image_url: str | None = Field(None, description="Annotated image URL")

    # Detection metadata
    detection_source: str = Field(
        default="mobile",
        pattern="^(drone|mobile|field_camera|satellite|edge_device)$",
        description="Detection source",
    )
    model_version: str | None = Field(None, description="YOLO model version used")
    processing_time_ms: int | None = Field(None, ge=0, description="Processing time")

    # Crop context
    crop_type: str | None = Field(None, description="Affected crop type")
    crop_type_ar: str | None = Field(None, description="Arabic crop type")
    growth_stage: str | None = Field(None, description="Crop growth stage")
    plant_part_affected: str | None = Field(None, description="Plant part affected (leaf, stem, root, fruit)")

    # Spread estimation
    affected_plants_count: int | None = Field(None, ge=0, description="Number of affected plants")
    affected_area_sqm: float | None = Field(None, ge=0, description="Affected area in m2")
    affected_area_percentage: float | None = Field(None, ge=0, le=100, description="Percentage of field affected")
    spread_risk: str | None = Field(None, pattern="^(low|medium|high)$", description="Risk of spread")

    # Symptoms observed
    symptoms: list[str] = Field(default_factory=list, description="Observed symptoms")
    symptoms_ar: list[str] = Field(default_factory=list, description="Arabic symptoms list")

    # Recommendations
    treatment_recommendation: str | None = Field(None, description="Treatment recommendation")
    treatment_recommendation_ar: str | None = Field(None, description="Arabic treatment")
    preventive_measures: list[str] = Field(default_factory=list, description="Preventive measures")
    urgency_hours: int | None = Field(None, ge=0, description="Action urgency in hours")

    # Economic impact
    estimated_yield_loss_percentage: float | None = Field(
        None, ge=0, le=100, description="Estimated yield loss percentage"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Weed Detection Event - حدث اكتشاف الأعشاب الضارة
# ─────────────────────────────────────────────────────────────────────────────


class WeedDetectedEvent(BaseVisionEvent):
    """
    Event emitted when weeds are detected via YOLO26 model.
    حدث يُطلق عند اكتشاف أعشاب ضارة عبر نموذج YOLO26
    """

    detection_id: UUID = Field(default_factory=uuid4, description="Unique detection identifier")
    field_id: UUID = Field(..., description="Field where weeds were detected")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Weed classification
    weed_class: str = Field(..., description="Weed species/class name")
    weed_class_ar: str | None = Field(None, description="Arabic weed name")
    weed_type: str | None = Field(
        None,
        pattern="^(broadleaf|grass|sedge|parasitic)$",
        description="Weed type",
    )
    scientific_name: str | None = Field(None, description="Scientific name")

    # Detection details
    confidence: float = Field(..., ge=0, le=1, description="Model confidence score")
    severity: str = Field(..., pattern="^(low|medium|high|critical)$", description="Severity/density level")
    density: str | None = Field(None, pattern="^(sparse|moderate|dense|very_dense)$", description="Weed density")

    # Location
    location: BoundingBox = Field(..., description="Bounding box coordinates")
    geo_location: GeoLocation | None = Field(None, description="GPS coordinates")
    zone_id: str | None = Field(None, description="Field zone identifier")

    # Image data
    image_url: str = Field(..., description="Source image URL")
    thumbnail_url: str | None = Field(None, description="Detection thumbnail URL")
    annotated_image_url: str | None = Field(None, description="Annotated image URL")

    # Detection metadata
    detection_source: str = Field(
        default="drone",
        pattern="^(drone|mobile|field_camera|satellite|edge_device)$",
        description="Detection source",
    )
    model_version: str | None = Field(None, description="YOLO model version used")
    processing_time_ms: int | None = Field(None, ge=0, description="Processing time")

    # Crop context
    crop_type: str | None = Field(None, description="Main crop type in field")
    crop_type_ar: str | None = Field(None, description="Arabic crop type")
    growth_stage: str | None = Field(None, description="Crop growth stage")

    # Coverage estimation
    estimated_count: int | None = Field(None, ge=0, description="Estimated weed count")
    affected_area_sqm: float | None = Field(None, ge=0, description="Affected area in m2")
    affected_area_percentage: float | None = Field(None, ge=0, le=100, description="Percentage of field affected")
    coverage_map_url: str | None = Field(None, description="Weed coverage map URL")

    # Control recommendations
    control_method: str | None = Field(
        None,
        pattern="^(mechanical|chemical|biological|manual|integrated)$",
        description="Recommended control method",
    )
    herbicide_recommendation: str | None = Field(None, description="Recommended herbicide (if applicable)")
    herbicide_recommendation_ar: str | None = Field(None, description="Arabic herbicide recommendation")
    optimal_control_window: str | None = Field(None, description="Optimal time window for control")

    # Economic impact
    estimated_yield_loss_percentage: float | None = Field(
        None, ge=0, le=100, description="Estimated yield loss if untreated"
    )
    control_cost_estimate: float | None = Field(None, ge=0, description="Estimated control cost")
    currency: str = Field(default="SAR", description="Currency code")


# ─────────────────────────────────────────────────────────────────────────────
# Plant Count Event - حدث إحصاء النباتات
# ─────────────────────────────────────────────────────────────────────────────


class PlantCountCompletedEvent(BaseVisionEvent):
    """
    Event emitted when plant counting analysis is completed.
    حدث يُطلق عند اكتمال تحليل إحصاء النباتات
    """

    analysis_id: UUID = Field(default_factory=uuid4, description="Unique analysis identifier")
    field_id: UUID = Field(..., description="Analyzed field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Count results
    total_plant_count: int = Field(..., ge=0, description="Total plants counted")
    healthy_plant_count: int | None = Field(None, ge=0, description="Healthy plants")
    stressed_plant_count: int | None = Field(None, ge=0, description="Stressed plants")
    missing_plant_count: int | None = Field(None, ge=0, description="Missing/gap count")

    # Density metrics
    plants_per_sqm: float | None = Field(None, ge=0, description="Plant density per m2")
    plants_per_hectare: float | None = Field(None, ge=0, description="Plant density per hectare")
    expected_plants_per_hectare: float | None = Field(None, ge=0, description="Expected plants per hectare")
    emergence_rate: float | None = Field(None, ge=0, le=100, description="Emergence rate percentage")

    # Analysis metadata
    analyzed_area_sqm: float = Field(..., ge=0, description="Analyzed area in m2")
    analyzed_area_hectares: float | None = Field(None, ge=0, description="Analyzed area in ha")
    confidence: float = Field(..., ge=0, le=1, description="Overall confidence score")

    # Crop information
    crop_type: str = Field(..., description="Crop type being counted")
    crop_type_ar: str | None = Field(None, description="Arabic crop type")
    growth_stage: str | None = Field(None, description="Crop growth stage")
    variety: str | None = Field(None, description="Crop variety")

    # Detection metadata
    detection_source: str = Field(
        default="drone",
        pattern="^(drone|mobile|field_camera|satellite|edge_device)$",
        description="Detection source",
    )
    model_version: str | None = Field(None, description="YOLO model version used")
    processing_time_ms: int | None = Field(None, ge=0, description="Processing time")
    images_processed: int | None = Field(None, ge=0, description="Number of images processed")

    # Image data
    source_image_urls: list[str] = Field(default_factory=list, description="Source image URLs")
    heatmap_url: str | None = Field(None, description="Plant density heatmap URL")
    annotated_mosaic_url: str | None = Field(None, description="Annotated mosaic URL")

    # Gap analysis
    gap_locations: list[GeoLocation] = Field(default_factory=list, description="Locations of gaps/missing plants")
    gap_percentage: float | None = Field(None, ge=0, le=100, description="Percentage of gaps")

    # Uniformity metrics
    uniformity_score: float | None = Field(None, ge=0, le=1, description="Plant uniformity score")
    row_spacing_cm: float | None = Field(None, ge=0, description="Average row spacing")
    plant_spacing_cm: float | None = Field(None, ge=0, description="Average plant spacing")

    # Recommendations
    reseeding_recommended: bool = Field(default=False, description="Whether reseeding is recommended")
    reseeding_area_sqm: float | None = Field(None, ge=0, description="Area needing reseeding")
    recommendation: str | None = Field(None, description="Action recommendation")
    recommendation_ar: str | None = Field(None, description="Arabic recommendation")


# ─────────────────────────────────────────────────────────────────────────────
# Critical Alert Event - حدث تنبيه حرج
# ─────────────────────────────────────────────────────────────────────────────


class VisionCriticalAlertEvent(BaseVisionEvent):
    """
    Event emitted for critical vision-based alerts requiring immediate attention.
    حدث يُطلق للتنبيهات الحرجة المبنية على الرؤية التي تتطلب اهتمامًا فوريًا
    """

    alert_id: UUID = Field(default_factory=uuid4, description="Unique alert identifier")
    field_id: UUID = Field(..., description="Affected field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    # Alert classification
    alert_type: str = Field(
        ...,
        pattern="^(pest_outbreak|disease_outbreak|severe_infestation|crop_failure_risk)$",
        description="Alert type",
    )
    alert_title: str = Field(..., description="Alert title")
    alert_title_ar: str | None = Field(None, description="Arabic alert title")
    alert_message: str = Field(..., description="Detailed alert message")
    alert_message_ar: str | None = Field(None, description="Arabic alert message")

    # Severity
    severity: str = Field(
        default="critical",
        pattern="^(high|critical)$",
        description="Alert severity",
    )
    priority: int = Field(default=1, ge=1, le=5, description="Priority (1=highest)")

    # Related detections
    related_detection_ids: list[UUID] = Field(default_factory=list, description="Related detection event IDs")
    detection_count: int = Field(..., ge=1, description="Number of related detections")

    # Affected area
    affected_area_sqm: float | None = Field(None, ge=0, description="Total affected area")
    affected_area_percentage: float | None = Field(None, ge=0, le=100, description="Percentage of field affected")
    geo_location: GeoLocation | None = Field(None, description="Center of affected area")

    # Crop impact
    crop_type: str | None = Field(None, description="Affected crop type")
    crop_type_ar: str | None = Field(None, description="Arabic crop type")
    estimated_loss_percentage: float | None = Field(None, ge=0, le=100, description="Estimated crop loss percentage")
    estimated_loss_value: float | None = Field(None, ge=0, description="Estimated monetary loss")
    currency: str = Field(default="SAR", description="Currency code")

    # Response required
    response_deadline_hours: int = Field(..., ge=1, description="Hours to respond")
    recommended_actions: list[str] = Field(default_factory=list, description="Recommended immediate actions")
    recommended_actions_ar: list[str] = Field(default_factory=list, description="Arabic recommended actions")

    # Escalation
    auto_notify_agronomist: bool = Field(default=True, description="Auto-notify farm agronomist")
    escalation_level: int = Field(default=1, ge=1, le=3, description="Escalation level")

    # Evidence
    evidence_image_urls: list[str] = Field(default_factory=list, description="Evidence image URLs")
    report_url: str | None = Field(None, description="Detailed report URL")


# ─────────────────────────────────────────────────────────────────────────────
# Vision Analysis Events - أحداث تحليل الرؤية
# ─────────────────────────────────────────────────────────────────────────────


class VisionAnalysisStartedEvent(BaseVisionEvent):
    """
    Event emitted when vision analysis job starts.
    حدث يُطلق عند بدء مهمة تحليل الرؤية
    """

    analysis_id: UUID = Field(default_factory=uuid4, description="Analysis job identifier")
    field_id: UUID = Field(..., description="Target field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    analysis_type: str = Field(
        ...,
        pattern="^(pest_detection|disease_detection|weed_detection|plant_count|comprehensive)$",
        description="Type of analysis",
    )
    source_type: str = Field(
        ...,
        pattern="^(drone|mobile|field_camera|satellite|edge_device)$",
        description="Image source type",
    )
    images_to_process: int = Field(..., ge=1, description="Number of images to process")
    model_id: str | None = Field(None, description="Model identifier to use")
    requested_by: UUID | None = Field(None, description="User who requested analysis")


class VisionAnalysisCompletedEvent(BaseVisionEvent):
    """
    Event emitted when vision analysis job completes.
    حدث يُطلق عند اكتمال مهمة تحليل الرؤية
    """

    analysis_id: UUID = Field(..., description="Analysis job identifier")
    field_id: UUID = Field(..., description="Target field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    analysis_type: str = Field(
        ...,
        pattern="^(pest_detection|disease_detection|weed_detection|plant_count|comprehensive)$",
        description="Type of analysis",
    )
    status: str = Field(
        default="completed",
        pattern="^(completed|partial|completed_with_warnings)$",
        description="Completion status",
    )

    # Results summary
    images_processed: int = Field(..., ge=0, description="Images successfully processed")
    images_failed: int = Field(default=0, ge=0, description="Images that failed processing")
    total_detections: int = Field(default=0, ge=0, description="Total detections found")
    critical_detections: int = Field(default=0, ge=0, description="Critical severity detections")

    # Timing
    started_at: datetime = Field(..., description="Analysis start time")
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Completion time")
    processing_duration_ms: int = Field(..., ge=0, description="Total processing time")

    # Output
    report_url: str | None = Field(None, description="Analysis report URL")
    detection_summary: dict | None = Field(None, description="Summary of detections by type")


class VisionAnalysisFailedEvent(BaseVisionEvent):
    """
    Event emitted when vision analysis job fails.
    حدث يُطلق عند فشل مهمة تحليل الرؤية
    """

    analysis_id: UUID = Field(..., description="Analysis job identifier")
    field_id: UUID = Field(..., description="Target field identifier")
    tenant_id: UUID = Field(..., description="Tenant identifier")

    analysis_type: str = Field(..., description="Type of analysis attempted")
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    error_message_ar: str | None = Field(None, description="Arabic error message")

    # Partial results
    images_processed: int = Field(default=0, ge=0, description="Images processed before failure")
    images_failed: int = Field(default=0, ge=0, description="Images that failed")

    # Timing
    started_at: datetime = Field(..., description="Analysis start time")
    failed_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Failure time")

    # Retry info
    retry_count: int = Field(default=0, ge=0, description="Number of retries attempted")
    is_retriable: bool = Field(default=True, description="Whether job can be retried")


# ─────────────────────────────────────────────────────────────────────────────
# Exports
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # Subject constants
    "VisionSubjects",
    "SAHOOL_VISION_PEST_DETECTED",
    "SAHOOL_VISION_DISEASE_DETECTED",
    "SAHOOL_VISION_WEED_DETECTED",
    "SAHOOL_VISION_PLANT_COUNT_COMPLETED",
    "SAHOOL_VISION_CRITICAL_ALERT",
    "SAHOOL_VISION_ANALYSIS_STARTED",
    "SAHOOL_VISION_ANALYSIS_COMPLETED",
    "SAHOOL_VISION_ANALYSIS_FAILED",
    "SAHOOL_VISION_ALL",
    # Enums
    "DetectionSeverity",
    "DetectionSource",
    "InfestationLevel",
    # Models
    "BoundingBox",
    "GeoLocation",
    # Base event
    "BaseVisionEvent",
    # Detection events
    "PestDetectedEvent",
    "VisionDiseaseDetectedEvent",
    "WeedDetectedEvent",
    "PlantCountCompletedEvent",
    "VisionCriticalAlertEvent",
    # Analysis events
    "VisionAnalysisStartedEvent",
    "VisionAnalysisCompletedEvent",
    "VisionAnalysisFailedEvent",
]
