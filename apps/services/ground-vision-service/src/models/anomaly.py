"""
Anomaly Detection Models - نماذج كشف الشذوذ
Based on: Qin et al. (2026) - Unusual event detection in agricultural monitoring
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class AnomalyType(StrEnum):
    """Types of anomalies that can be detected - أنواع الشذوذ"""

    # Biological threats
    PEST_INFESTATION = "pest_infestation"  # إصابة آفات
    DISEASE_OUTBREAK = "disease_outbreak"  # تفشي مرض
    WEED_GROWTH = "weed_growth"  # نمو أعشاب ضارة
    WILDLIFE_DAMAGE = "wildlife_damage"  # ضرر من الحيوانات البرية

    # Environmental stress
    WATER_STRESS = "water_stress"  # إجهاد مائي
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"  # نقص عناصر غذائية
    HEAT_STRESS = "heat_stress"  # إجهاد حراري
    COLD_DAMAGE = "cold_damage"  # ضرر برد
    FLOOD_DAMAGE = "flood_damage"  # ضرر فيضان
    WIND_DAMAGE = "wind_damage"  # ضرر رياح
    SALINITY_STRESS = "salinity_stress"  # إجهاد ملوحة

    # Infrastructure issues
    IRRIGATION_FAILURE = "irrigation_failure"  # عطل نظام الري
    EQUIPMENT_MALFUNCTION = "equipment_malfunction"  # عطل معدات

    # Security/Unauthorized
    UNAUTHORIZED_ACTIVITY = "unauthorized_activity"  # نشاط غير مصرح
    TRESPASSING = "trespassing"  # تعدي
    THEFT = "theft"  # سرقة
    VANDALISM = "vandalism"  # تخريب

    # Fire/Safety
    FIRE_DETECTED = "fire_detected"  # حريق مكتشف
    SMOKE_DETECTED = "smoke_detected"  # دخان مكتشف

    # Other
    CROP_LODGING = "crop_lodging"  # رقاد المحصول
    UNEVEN_GROWTH = "uneven_growth"  # نمو غير متساوي
    FIELD_BOUNDARY_ENCROACHMENT = "boundary_encroachment"  # تعدي على حدود الحقل
    UNKNOWN = "unknown"  # غير معروف


ANOMALY_TYPE_AR = {
    AnomalyType.PEST_INFESTATION: "إصابة آفات",
    AnomalyType.DISEASE_OUTBREAK: "تفشي مرض",
    AnomalyType.WEED_GROWTH: "نمو أعشاب ضارة",
    AnomalyType.WILDLIFE_DAMAGE: "ضرر من الحيوانات البرية",
    AnomalyType.WATER_STRESS: "إجهاد مائي",
    AnomalyType.NUTRIENT_DEFICIENCY: "نقص عناصر غذائية",
    AnomalyType.HEAT_STRESS: "إجهاد حراري",
    AnomalyType.COLD_DAMAGE: "ضرر برد",
    AnomalyType.FLOOD_DAMAGE: "ضرر فيضان",
    AnomalyType.WIND_DAMAGE: "ضرر رياح",
    AnomalyType.SALINITY_STRESS: "إجهاد ملوحة",
    AnomalyType.IRRIGATION_FAILURE: "عطل نظام الري",
    AnomalyType.EQUIPMENT_MALFUNCTION: "عطل معدات",
    AnomalyType.UNAUTHORIZED_ACTIVITY: "نشاط غير مصرح",
    AnomalyType.TRESPASSING: "تعدي",
    AnomalyType.THEFT: "سرقة",
    AnomalyType.VANDALISM: "تخريب",
    AnomalyType.FIRE_DETECTED: "حريق مكتشف",
    AnomalyType.SMOKE_DETECTED: "دخان مكتشف",
    AnomalyType.CROP_LODGING: "رقاد المحصول",
    AnomalyType.UNEVEN_GROWTH: "نمو غير متساوي",
    AnomalyType.FIELD_BOUNDARY_ENCROACHMENT: "تعدي على حدود الحقل",
    AnomalyType.UNKNOWN: "غير معروف",
}


class AnomalySeverity(StrEnum):
    """Severity levels for anomalies - مستويات خطورة الشذوذ"""

    CRITICAL = "critical"  # حرج - استجابة فورية (< 6 ساعات)
    HIGH = "high"  # عالي - استجابة خلال 24 ساعة
    MEDIUM = "medium"  # متوسط - استجابة خلال أسبوع
    LOW = "low"  # منخفض - للمتابعة


SEVERITY_AR = {
    AnomalySeverity.CRITICAL: "حرج",
    AnomalySeverity.HIGH: "عالي",
    AnomalySeverity.MEDIUM: "متوسط",
    AnomalySeverity.LOW: "منخفض",
}

# Response time guidelines (hours)
SEVERITY_RESPONSE_TIME = {
    AnomalySeverity.CRITICAL: 6,  # < 6 hours
    AnomalySeverity.HIGH: 24,  # < 24 hours
    AnomalySeverity.MEDIUM: 168,  # < 1 week
    AnomalySeverity.LOW: 336,  # < 2 weeks
}


class AnomalyLocation(BaseModel):
    """Geographic location of detected anomaly"""

    # Geographic coordinates
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)

    # Optional bounding box for area anomalies
    bbox_coords: list[dict] | None = Field(default=None, description="List of {lat, lon} for anomaly boundary")

    # Affected area
    affected_area_hectares: float | None = Field(default=None, ge=0, description="Estimated affected area in hectares")
    affected_area_percent: float | None = Field(default=None, ge=0, le=100, description="Percentage of field affected")


class AnomalyDetection(BaseModel):
    """
    Detected anomaly in a field - شذوذ مكتشف في الحقل
    """

    anomaly_id: str = Field(..., description="Unique anomaly identifier")
    field_id: str = Field(..., description="Field where anomaly was detected")
    camera_id: str = Field(..., description="Camera that detected the anomaly")

    # Anomaly classification
    anomaly_type: AnomalyType
    anomaly_type_ar: str = Field(default="", description="Anomaly type in Arabic")
    sub_type: str | None = Field(default=None, description="More specific classification (e.g., pest species)")

    # Severity
    severity: AnomalySeverity
    severity_ar: str = Field(default="", description="Severity in Arabic")
    response_deadline_hours: int = Field(default=168, description="Recommended response time in hours")

    # Confidence
    confidence: float = Field(..., ge=0.0, le=1.0)

    # Description (bilingual)
    description: str = Field(..., description="Description in English")
    description_ar: str = Field(..., description="الوصف بالعربية")

    # Location
    location: AnomalyLocation

    # Evidence
    source_frame_id: str = Field(..., description="Frame where first detected")
    source_frame_url: str | None = None
    additional_frames: list[str] = Field(default_factory=list, description="Additional supporting frame IDs")

    # Detection details
    detection_method: str = Field(default="mllm", description="Method: mllm, cv_model, change_detection")
    model_version: str | None = None

    # Timestamps
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    first_observed_at: datetime | None = Field(
        default=None, description="When anomaly was first observed (may differ from detected_at)"
    )

    # Progression tracking
    is_recurring: bool = Field(default=False, description="Whether this anomaly has occurred before")
    previous_occurrence_id: str | None = None
    progression_status: str = Field(default="new", description="new, spreading, stable, improving, resolved")

    # Multi-tenancy
    tenant_id: str

    # Resolution tracking
    status: str = Field(default="open", description="open, acknowledged, investigating, resolved, false_positive")
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    resolution_notes: str | None = None
    resolution_notes_ar: str | None = None

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-fill Arabic translations and response deadline
        if not self.anomaly_type_ar:
            self.anomaly_type_ar = ANOMALY_TYPE_AR.get(self.anomaly_type, "غير معروف")
        if not self.severity_ar:
            self.severity_ar = SEVERITY_AR.get(self.severity, "غير معروف")
        if self.response_deadline_hours == 168:  # Default value
            self.response_deadline_hours = SEVERITY_RESPONSE_TIME.get(self.severity, 168)

    class Config:
        json_schema_extra = {
            "example": {
                "anomaly_id": "anomaly_001",
                "field_id": "field_001",
                "camera_id": "cam_tower_001",
                "anomaly_type": "water_stress",
                "anomaly_type_ar": "إجهاد مائي",
                "severity": "high",
                "severity_ar": "عالي",
                "confidence": 0.87,
                "description": "Water stress detected in northwest section",
                "description_ar": "تم اكتشاف إجهاد مائي في القسم الشمالي الغربي",
                "tenant_id": "sahool",
            }
        }


class AnomalyAlert(BaseModel):
    """Alert generated from anomaly detection"""

    alert_id: str
    anomaly_id: str
    field_id: str

    # Alert content
    title: str
    title_ar: str
    message: str
    message_ar: str

    # Severity indicator
    severity: AnomalySeverity
    priority_score: int = Field(..., ge=1, le=100, description="Higher = more urgent")

    # Recommended actions
    recommended_actions: list[str] = Field(default_factory=list)
    recommended_actions_ar: list[str] = Field(default_factory=list)

    # Links
    anomaly_details_url: str | None = None
    frame_url: str | None = None

    # Distribution
    notify_roles: list[str] = Field(
        default_factory=lambda: ["field_manager"],
        description="Roles to notify: field_manager, agronomist, owner",
    )
    notification_channels: list[str] = Field(
        default_factory=lambda: ["push", "sms"], description="Channels: push, sms, email, whatsapp"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None

    # Status
    delivered: bool = Field(default=False)
    read: bool = Field(default=False)
    actioned: bool = Field(default=False)

    # Multi-tenancy
    tenant_id: str


class AnomalySummary(BaseModel):
    """Summary of anomalies for a field or time period"""

    field_id: str
    period_start: datetime
    period_end: datetime

    total_anomalies: int
    anomalies_by_type: dict[str, int]
    anomalies_by_severity: dict[str, int]

    # Current open anomalies
    open_anomalies: int
    critical_open: int
    high_open: int

    # Resolution stats
    resolved_this_period: int
    average_resolution_time_hours: float | None = None

    # Trends
    trend: str = Field(default="stable", description="increasing, decreasing, stable")
    comparison_to_previous: float | None = Field(default=None, description="Percentage change from previous period")
