"""
Improved Response Schemas for Crop Intelligence Service.

Provides structured, bilingual response models with comprehensive metadata
for all crop intelligence endpoints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum, StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ResponseStatus(StrEnum):
    """Response status."""

    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"


class AlertLevel(StrEnum):
    """Alert urgency level."""

    CRITICAL = "critical"  # P0 - حرج
    HIGH = "high"  # P1 - مرتفع
    MEDIUM = "medium"  # P2 - متوسط
    LOW = "low"  # P3 - منخفض
    INFO = "info"  # معلومات


class ActionType(StrEnum):
    """Recommended action type."""

    IRRIGATION = "irrigation"  # ري
    FERTILIZATION = "fertilization"  # تسميد
    PEST_CONTROL = "pest_control"  # مكافحة آفات
    DISEASE_TREATMENT = "disease_treatment"  # علاج أمراض
    SCOUTING = "scouting"  # استكشاف
    HARVEST = "harvest"  # حصاد
    PRUNING = "pruning"  # تقليم
    NONE = "none"  # لا إجراء


# =============================================================================
# Base Response Models
# =============================================================================


class BilingualText(BaseModel):
    """Bilingual text field."""

    en: str = Field(..., description="English text")
    ar: str = Field(..., description="Arabic text (النص العربي)")


class ResponseMetadata(BaseModel):
    """Standard response metadata."""

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    processing_time_ms: float = Field(default=0.0, description="Processing time in milliseconds")
    version: str = Field(default="16.0.0", description="API version")
    cached: bool = Field(default=False, description="Whether result was from cache")


class BaseResponse(BaseModel):
    """Base response model."""

    status: ResponseStatus = ResponseStatus.SUCCESS
    metadata: ResponseMetadata = Field(default_factory=ResponseMetadata)
    message: BilingualText | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Disease Detection Response
# =============================================================================


class DiseaseInfo(BaseModel):
    """Detailed disease information."""

    disease_type: str
    name: BilingualText
    description: BilingualText
    severity: str
    confidence: float = Field(ge=0.0, le=1.0)
    affected_indicator: str
    evidence: dict[str, Any] = Field(default_factory=dict)


class TreatmentInfo(BaseModel):
    """Treatment recommendation."""

    treatment_type: str
    product: BilingualText
    dosage: BilingualText
    application_method: BilingualText
    urgency_days: int
    precautions: list[BilingualText] = Field(default_factory=list)


class DiseaseDetectionResult(BaseModel):
    """Single disease detection result."""

    disease: DiseaseInfo
    treatments: list[TreatmentInfo] = Field(default_factory=list)
    prevention: list[BilingualText] = Field(default_factory=list)


class OverallHealthStatus(BaseModel):
    """Overall health status summary."""

    status: BilingualText
    score: float = Field(ge=0.0, le=100.0, description="Health score 0-100")
    alert_level: AlertLevel


class DiseaseDetectionResponse(BaseResponse):
    """Complete disease detection response."""

    health_status: OverallHealthStatus
    detection_count: int = 0
    detections: list[DiseaseDetectionResult] = Field(default_factory=list)
    input_indices: dict[str, float] = Field(default_factory=dict)
    environmental_context: dict[str, Any] = Field(default_factory=dict)
    recommendations_summary: BilingualText | None = None


# =============================================================================
# Nutrient Analysis Response
# =============================================================================


class NutrientInfo(BaseModel):
    """Nutrient deficiency information."""

    nutrient_type: str
    name: BilingualText
    deficiency_level: str
    confidence: float = Field(ge=0.0, le=1.0)
    indicators: dict[str, float] = Field(default_factory=dict)
    symptoms: list[BilingualText] = Field(default_factory=list)


class FertilizerRecommendation(BaseModel):
    """Fertilizer recommendation."""

    product: BilingualText
    rate_per_hectare: str
    application_timing: BilingualText
    application_method: BilingualText
    estimated_cost_usd: float | None = None


class NutrientStatusSummary(BaseModel):
    """Overall nutrient status summary."""

    status: BilingualText
    deficiency_count: int
    priority_nutrients: list[str] = Field(default_factory=list)


class NutrientAnalysisResponse(BaseResponse):
    """Complete nutrient analysis response."""

    nutrient_status: NutrientStatusSummary
    deficiencies: list[NutrientInfo] = Field(default_factory=list)
    fertilizer_plan: list[FertilizerRecommendation] = Field(default_factory=list)
    total_estimated_cost_usd: float | None = None
    input_indices: dict[str, float] = Field(default_factory=dict)
    field_area_hectares: float | None = None


# =============================================================================
# Yield Prediction Response
# =============================================================================


class YieldRange(BaseModel):
    """Yield range prediction."""

    low: float = Field(description="Lower bound (kg/ha)")
    expected: float = Field(description="Expected yield (kg/ha)")
    high: float = Field(description="Upper bound (kg/ha)")


class YieldComparisonBase(BaseModel):
    """Yield comparison base."""

    regional_average: float | None = None
    historical_average: float | None = None
    percent_vs_regional: float | None = None
    percent_vs_historical: float | None = None


class YieldFactors(BaseModel):
    """Factors affecting yield prediction."""

    ndvi_contribution: float = Field(description="NDVI impact on yield")
    evi_contribution: float = Field(description="EVI impact on yield")
    water_status: BilingualText
    nutrient_status: BilingualText
    growth_stage_effect: float


class YieldPredictionResponse(BaseResponse):
    """Complete yield prediction response."""

    crop_type: str
    crop_type_ar: str
    yield_prediction: YieldRange
    total_predicted_kg: float
    confidence: float = Field(ge=0.0, le=1.0)
    prediction_basis: BilingualText
    factors: YieldFactors | None = None
    comparison: YieldComparisonBase | None = None
    input_indices: dict[str, float] = Field(default_factory=dict)
    field_area_hectares: float


# =============================================================================
# Pest Risk Assessment Response
# =============================================================================


class PestRisk(BaseModel):
    """Individual pest risk assessment."""

    pest_type: str
    name: BilingualText
    risk_level: AlertLevel
    probability: float = Field(ge=0.0, le=1.0)
    conditions_favorable: list[BilingualText] = Field(default_factory=list)
    prevention_measures: list[BilingualText] = Field(default_factory=list)


class PestAssessmentSummary(BaseModel):
    """Pest risk assessment summary."""

    overall_risk: AlertLevel
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int


class PestAssessmentResponse(BaseResponse):
    """Complete pest assessment response."""

    assessment_summary: PestAssessmentSummary
    risks: list[PestRisk] = Field(default_factory=list)
    environmental_conditions: dict[str, Any] = Field(default_factory=dict)
    monitoring_recommendations: list[BilingualText] = Field(default_factory=list)


# =============================================================================
# Zone Diagnosis Response
# =============================================================================


class ZoneAction(BaseModel):
    """Recommended action for zone."""

    zone_id: str
    action_type: ActionType
    priority: AlertLevel
    title: BilingualText
    reason: BilingualText
    evidence: dict[str, Any] = Field(default_factory=dict)
    recommended_window_hours: int | None = None
    recommended_dose_hint: str | None = None


class ZoneSummary(BaseModel):
    """Zone status summary."""

    zones_total: int
    zones_critical: int
    zones_warning: int
    zones_ok: int


class MapLayer(BaseModel):
    """Map layer information."""

    layer_type: str
    name: BilingualText
    url: str
    available: bool = True


class ZoneDiagnosisResponse(BaseResponse):
    """Complete zone diagnosis response."""

    field_id: str
    diagnosis_date: str
    summary: ZoneSummary
    actions: list[ZoneAction] = Field(default_factory=list)
    map_layers: list[MapLayer] = Field(default_factory=list)
    next_observation_recommended: str | None = None


# =============================================================================
# Comprehensive Analysis Response
# =============================================================================


class AnalysisSectionSummary(BaseModel):
    """Summary of an analysis section."""

    status: BilingualText
    alert_level: AlertLevel
    key_findings: list[BilingualText] = Field(default_factory=list)
    action_required: bool = False


class ComprehensiveAnalysisResponse(BaseResponse):
    """Complete comprehensive analysis response."""

    field_id: str | None = None
    overall_status: AlertLevel
    overall_score: float = Field(ge=0.0, le=100.0)
    overall_message: BilingualText

    health_summary: AnalysisSectionSummary
    nutrient_summary: AnalysisSectionSummary
    pest_summary: AnalysisSectionSummary
    yield_summary: AnalysisSectionSummary

    priority_actions: list[ZoneAction] = Field(default_factory=list)

    input_indices: dict[str, float] = Field(default_factory=dict)
    environmental_context: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Timeline Response
# =============================================================================


class TimelineDataPoint(BaseModel):
    """Single data point in timeline."""

    date: str
    ndvi: float
    evi: float | None = None
    ndre: float | None = None
    ndwi: float | None = None
    lci: float | None = None
    savi: float | None = None
    health_status: str | None = None


class TimelineTrend(BaseModel):
    """Trend analysis for timeline."""

    direction: str  # improving, declining, stable
    direction_ar: str
    change_percent: float
    significance: str


class ZoneTimelineResponse(BaseResponse):
    """Zone timeline response."""

    field_id: str
    zone_id: str
    zone_name: BilingualText | None = None
    date_range: dict[str, str] = Field(default_factory=dict)
    series: list[TimelineDataPoint] = Field(default_factory=list)
    trend: TimelineTrend | None = None


# =============================================================================
# Cache Statistics Response
# =============================================================================


class CacheStatsResponse(BaseModel):
    """Cache statistics response."""

    hits: int
    misses: int
    hit_rate: float
    evictions: int
    total_entries: int
    memory_used_kb: float
    redis_connected: bool = False


# =============================================================================
# Helper Functions
# =============================================================================


def create_bilingual_text(en: str, ar: str) -> BilingualText:
    """Create bilingual text."""
    return BilingualText(en=en, ar=ar)


def create_success_response(
    data: dict[str, Any],
    processing_time_ms: float = 0.0,
    cached: bool = False,
) -> dict[str, Any]:
    """Create a standardized success response."""
    return {
        "status": "success",
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "processing_time_ms": round(processing_time_ms, 2),
            "version": "16.0.0",
            "cached": cached,
        },
        **data,
    }


def create_error_response(
    error_code: str,
    message_en: str,
    message_ar: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standardized error response."""
    response = {
        "status": "error",
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "16.0.0",
        },
        "error": {
            "code": error_code,
            "message": message_en,
            "message_ar": message_ar,
        },
    }

    if details:
        response["error"]["details"] = details

    return response


def get_alert_level_from_severity(severity: str) -> AlertLevel:
    """Convert severity string to AlertLevel."""
    severity_mapping = {
        "critical": AlertLevel.CRITICAL,
        "high": AlertLevel.HIGH,
        "medium": AlertLevel.MEDIUM,
        "low": AlertLevel.LOW,
        "healthy": AlertLevel.INFO,
        "none": AlertLevel.INFO,
    }
    return severity_mapping.get(severity.lower(), AlertLevel.INFO)


def get_health_score(detections: list, status: str) -> float:
    """Calculate health score from detections."""
    if not detections:
        return 100.0

    status_scores = {
        "healthy": 100.0,
        "good": 85.0,
        "fair": 65.0,
        "poor": 40.0,
        "critical": 15.0,
    }

    base_score = status_scores.get(status.lower(), 50.0)
    detection_penalty = min(len(detections) * 5, 30)

    return max(0.0, base_score - detection_penalty)
