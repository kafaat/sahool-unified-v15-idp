"""
Field Operation Detection Models - نماذج كشف العمليات الزراعية
Based on: Qin et al. (2026) - YOLO-based operation detection
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class OperationType(StrEnum):
    """Agricultural operation types - أنواع العمليات الزراعية"""

    HARVEST = "harvest"  # حصاد
    TILLAGE = "tillage"  # حراثة
    IRRIGATION = "irrigation"  # ري
    PLANTING = "planting"  # زراعة
    SPRAYING = "spraying"  # رش (مبيدات/أسمدة)
    FERTILIZING = "fertilizing"  # تسميد
    WEEDING = "weeding"  # إزالة الأعشاب
    MULCHING = "mulching"  # تغطية التربة
    PRUNING = "pruning"  # تقليم
    TRANSPORT = "transport"  # نقل
    UNKNOWN = "unknown"  # غير معروف


OPERATION_TYPE_AR = {
    OperationType.HARVEST: "حصاد",
    OperationType.TILLAGE: "حراثة",
    OperationType.IRRIGATION: "ري",
    OperationType.PLANTING: "زراعة",
    OperationType.SPRAYING: "رش",
    OperationType.FERTILIZING: "تسميد",
    OperationType.WEEDING: "إزالة الأعشاب",
    OperationType.MULCHING: "تغطية التربة",
    OperationType.PRUNING: "تقليم",
    OperationType.TRANSPORT: "نقل",
    OperationType.UNKNOWN: "غير معروف",
}


class DetectionConfidence(StrEnum):
    """Detection confidence levels"""

    HIGH = "high"  # > 0.85
    MEDIUM = "medium"  # 0.60 - 0.85
    LOW = "low"  # < 0.60


class EquipmentType(StrEnum):
    """Agricultural equipment types - أنواع المعدات الزراعية"""

    COMBINE_HARVESTER = "combine_harvester"  # حاصدة درس
    TRACTOR = "tractor"  # جرار
    PLOW = "plow"  # محراث
    SPRAYER = "sprayer"  # رشاشة
    SEEDER = "seeder"  # بذارة
    IRRIGATION_PIVOT = "irrigation_pivot"  # محور الري
    IRRIGATION_DRIP = "irrigation_drip"  # ري بالتنقيط
    TRUCK = "truck"  # شاحنة
    WORKER = "worker"  # عامل
    UNKNOWN = "unknown"  # غير معروف


EQUIPMENT_TYPE_AR = {
    EquipmentType.COMBINE_HARVESTER: "حاصدة درس",
    EquipmentType.TRACTOR: "جرار",
    EquipmentType.PLOW: "محراث",
    EquipmentType.SPRAYER: "رشاشة",
    EquipmentType.SEEDER: "بذارة",
    EquipmentType.IRRIGATION_PIVOT: "محور الري",
    EquipmentType.IRRIGATION_DRIP: "ري بالتنقيط",
    EquipmentType.TRUCK: "شاحنة",
    EquipmentType.WORKER: "عامل",
    EquipmentType.UNKNOWN: "غير معروف",
}


class BoundingBox(BaseModel):
    """Geo-referenced bounding box"""

    # Image coordinates
    x_min: int
    y_min: int
    x_max: int
    y_max: int

    # Geographic coordinates (corners)
    geo_coords: list[dict] | None = Field(default=None, description="List of {lat, lon} for bounding box corners")


class FieldOperationDetection(BaseModel):
    """
    Detected agricultural operation - عملية زراعية مكتشفة
    """

    detection_id: str = Field(..., description="Unique detection identifier")
    field_id: str = Field(..., description="Field where operation was detected")
    camera_id: str = Field(..., description="Camera that captured the detection")

    # Operation details
    operation_type: OperationType
    operation_type_ar: str = Field(default="", description="Operation type in Arabic")
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_level: DetectionConfidence

    # Equipment
    equipment_type: EquipmentType | None = None
    equipment_type_ar: str | None = None
    equipment_count: int = Field(default=1)

    # Location
    bounding_box: BoundingBox
    center_lat: float | None = None
    center_lon: float | None = None
    affected_area_hectares: float | None = None

    # Source
    source_frame_id: str = Field(..., description="ID of source video frame")
    source_frame_url: str | None = None

    # Timestamps
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    operation_started_at: datetime | None = None
    operation_ended_at: datetime | None = None

    # Multi-tenancy
    tenant_id: str

    # Verification
    verified: bool = Field(default=False)
    verified_by: str | None = None
    verified_at: datetime | None = None

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-fill Arabic translations
        if not self.operation_type_ar:
            self.operation_type_ar = OPERATION_TYPE_AR.get(self.operation_type, "غير معروف")
        if self.equipment_type and not self.equipment_type_ar:
            self.equipment_type_ar = EQUIPMENT_TYPE_AR.get(self.equipment_type, "غير معروف")

    class Config:
        json_schema_extra = {
            "example": {
                "detection_id": "det_001",
                "field_id": "field_001",
                "camera_id": "cam_tower_001",
                "operation_type": "harvest",
                "operation_type_ar": "حصاد",
                "confidence": 0.92,
                "confidence_level": "high",
                "equipment_type": "combine_harvester",
                "equipment_type_ar": "حاصدة درس",
                "tenant_id": "sahool",
            }
        }


class DetectionSummary(BaseModel):
    """Summary of detections for a field or time period"""

    field_id: str
    period_start: datetime
    period_end: datetime
    total_detections: int
    operations_by_type: dict[str, int]
    confidence_distribution: dict[str, int]
    equipment_used: list[str]
