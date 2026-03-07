"""
Crop Timeline Models - نماذج الخط الزمني للمحاصيل
Based on: Qin et al. (2026) - MLLM-based crop timeline analysis
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class GrowthStage(StrEnum):
    """Crop growth stages - مراحل نمو المحصول"""

    # General stages
    FALLOW = "fallow"  # أرض بور
    PREPARED = "prepared"  # مُعَدَّة للزراعة
    PLANTING = "planting"  # زراعة
    GERMINATION = "germination"  # إنبات
    EMERGENCE = "emergence"  # بزوغ
    SEEDLING = "seedling"  # شتلة
    VEGETATIVE = "vegetative"  # نمو خضري
    TILLERING = "tillering"  # تفريع (للحبوب)
    JOINTING = "jointing"  # عقد السيقان
    BOOTING = "booting"  # انتفاخ السنبلة
    HEADING = "heading"  # إسبال
    FLOWERING = "flowering"  # إزهار
    GRAIN_FILL = "grain_fill"  # امتلاء الحبوب
    MATURITY = "maturity"  # نضج
    HARVEST_READY = "harvest_ready"  # جاهز للحصاد
    HARVESTED = "harvested"  # محصود
    POST_HARVEST = "post_harvest"  # ما بعد الحصاد
    UNKNOWN = "unknown"  # غير معروف


GROWTH_STAGE_AR = {
    GrowthStage.FALLOW: "أرض بور",
    GrowthStage.PREPARED: "معدة للزراعة",
    GrowthStage.PLANTING: "زراعة",
    GrowthStage.GERMINATION: "إنبات",
    GrowthStage.EMERGENCE: "بزوغ",
    GrowthStage.SEEDLING: "شتلة",
    GrowthStage.VEGETATIVE: "نمو خضري",
    GrowthStage.TILLERING: "تفريع",
    GrowthStage.JOINTING: "عقد السيقان",
    GrowthStage.BOOTING: "انتفاخ السنبلة",
    GrowthStage.HEADING: "إسبال",
    GrowthStage.FLOWERING: "إزهار",
    GrowthStage.GRAIN_FILL: "امتلاء الحبوب",
    GrowthStage.MATURITY: "نضج",
    GrowthStage.HARVEST_READY: "جاهز للحصاد",
    GrowthStage.HARVESTED: "محصود",
    GrowthStage.POST_HARVEST: "ما بعد الحصاد",
    GrowthStage.UNKNOWN: "غير معروف",
}


class CropType(StrEnum):
    """Crop types supported - أنواع المحاصيل المدعومة"""

    WHEAT = "wheat"  # قمح
    BARLEY = "barley"  # شعير
    RICE = "rice"  # أرز
    CORN = "corn"  # ذرة
    SORGHUM = "sorghum"  # ذرة رفيعة
    ALFALFA = "alfalfa"  # برسيم
    DATE_PALM = "date_palm"  # نخيل
    CITRUS = "citrus"  # حمضيات
    OLIVE = "olive"  # زيتون
    TOMATO = "tomato"  # طماطم
    CUCUMBER = "cucumber"  # خيار
    POTATO = "potato"  # بطاطا
    ONION = "onion"  # بصل
    GRAPE = "grape"  # عنب
    OTHER = "other"  # أخرى
    UNKNOWN = "unknown"  # غير معروف


CROP_TYPE_AR = {
    CropType.WHEAT: "قمح",
    CropType.BARLEY: "شعير",
    CropType.RICE: "أرز",
    CropType.CORN: "ذرة",
    CropType.SORGHUM: "ذرة رفيعة",
    CropType.ALFALFA: "برسيم",
    CropType.DATE_PALM: "نخيل",
    CropType.CITRUS: "حمضيات",
    CropType.OLIVE: "زيتون",
    CropType.TOMATO: "طماطم",
    CropType.CUCUMBER: "خيار",
    CropType.POTATO: "بطاطا",
    CropType.ONION: "بصل",
    CropType.GRAPE: "عنب",
    CropType.OTHER: "أخرى",
    CropType.UNKNOWN: "غير معروف",
}


class TimeSeriesFrame(BaseModel):
    """A single frame in a time series sequence"""

    frame_id: str = Field(..., description="Unique frame identifier")
    camera_id: str = Field(..., description="Camera that captured this frame")
    captured_at: datetime = Field(..., description="Capture timestamp")
    storage_url: str = Field(..., description="URL to frame image in storage")
    thumbnail_url: str | None = Field(default=None, description="URL to thumbnail")

    # Metadata
    exposure_settings: dict | None = Field(default=None, description="Camera exposure settings")
    weather_conditions: dict | None = Field(default=None, description="Weather at capture time")

    # Processing state
    processed: bool = Field(default=False)
    processing_error: str | None = None


class CropTimelineEntry(BaseModel):
    """
    Crop growth stage timeline entry - سجل مرحلة نمو المحصول
    """

    entry_id: str = Field(..., description="Unique entry identifier")
    field_id: str = Field(..., description="Field this entry belongs to")

    # Crop identification
    crop_type: CropType
    crop_type_ar: str = Field(default="", description="Crop type in Arabic")
    variety: str | None = Field(default=None, description="Crop variety")

    # Growth stage
    growth_stage: GrowthStage
    growth_stage_ar: str = Field(default="", description="Growth stage in Arabic")
    days_in_stage: int | None = Field(default=None, description="Days since entering this stage")
    expected_days_remaining: int | None = Field(default=None, description="Expected days until next stage")

    # Confidence and evidence
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence_frames: list[str] = Field(default_factory=list, description="Frame IDs supporting this assessment")

    # Analysis details
    observed_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_method: str = Field(default="mllm", description="Method used: mllm, cv_model, manual")

    # Notes
    notes: str | None = None
    notes_ar: str | None = None

    # Multi-tenancy
    tenant_id: str

    # Verification
    verified: bool = Field(default=False)
    verified_by: str | None = None
    verified_at: datetime | None = None

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-fill Arabic translations
        if not self.crop_type_ar:
            self.crop_type_ar = CROP_TYPE_AR.get(self.crop_type, "غير معروف")
        if not self.growth_stage_ar:
            self.growth_stage_ar = GROWTH_STAGE_AR.get(self.growth_stage, "غير معروف")

    class Config:
        json_schema_extra = {
            "example": {
                "entry_id": "timeline_001",
                "field_id": "field_001",
                "crop_type": "wheat",
                "crop_type_ar": "قمح",
                "growth_stage": "tillering",
                "growth_stage_ar": "تفريع",
                "confidence": 0.89,
                "tenant_id": "sahool",
            }
        }


class StageTransition(BaseModel):
    """Detected transition between growth stages"""

    transition_id: str
    field_id: str
    crop_type: CropType

    from_stage: GrowthStage
    from_stage_ar: str
    to_stage: GrowthStage
    to_stage_ar: str

    detected_at: datetime
    confidence: float = Field(..., ge=0.0, le=1.0)

    # Evidence
    before_frame_id: str
    after_frame_id: str

    # Analysis
    transition_speed: str | None = Field(default=None, description="normal, accelerated, delayed")
    notes: str | None = None
    notes_ar: str | None = None


class CropTimelineAnalysis(BaseModel):
    """
    Complete MLLM analysis result for crop timeline
    Based on: Qin et al. (2026) - Change-triggered MLLM invocation
    """

    analysis_id: str = Field(..., description="Unique analysis identifier")
    field_id: str

    # Crop identification
    crop_type: CropType
    crop_type_ar: str
    variety_detected: str | None = None

    # Current state
    current_stage: GrowthStage
    current_stage_ar: str
    stage_confidence: float = Field(..., ge=0.0, le=1.0)

    # Health assessment
    health_score: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Overall crop health (1.0 = excellent)"
    )
    vigor_assessment: str | None = Field(default=None, description="excellent, good, fair, poor")

    # Operations detected
    operations_detected: list[dict] = Field(
        default_factory=list, description="List of detected agricultural operations"
    )

    # Anomalies
    anomalies: list[dict] = Field(default_factory=list, description="List of detected anomalies")

    # Reasoning (bilingual)
    reasoning: str = Field(..., description="Explanation in English")
    reasoning_ar: str = Field(..., description="التفسير بالعربية")

    # Recommendations
    recommendations: list[str] = Field(default_factory=list, description="Recommended actions")
    recommendations_ar: list[str] = Field(default_factory=list, description="الإجراءات الموصى بها")

    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    frames_analyzed: int = Field(default=0)
    processing_time_ms: int | None = None
    model_used: str = Field(default="unknown", description="MLLM model identifier")

    # Multi-tenancy
    tenant_id: str


class FieldContext(BaseModel):
    """Context information for field analysis"""

    field_id: str
    location_name: str
    location_name_ar: str | None = None
    lat: float
    lon: float
    area_hectares: float

    # Expected crop info
    expected_crop: CropType | None = None
    expected_crop_ar: str | None = None
    expected_planting_date: datetime | None = None
    expected_harvest_date: datetime | None = None

    # History
    rotation_history: list[dict] = Field(default_factory=list, description="Previous crop rotations")

    # Conditions
    soil_type: str | None = None
    irrigation_type: str | None = None

    # Multi-tenancy
    tenant_id: str
