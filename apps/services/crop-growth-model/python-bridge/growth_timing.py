"""
SAHOOL Crop Growth Timing Service v15.5
خدمة توقيت نمو المحاصيل - قرارات "متى"

Field-First Architecture:
- يخبر المزارع "متى" يتدخل وليس فقط "كيف"
- ينتج ActionTemplates لقرارات التوقيت
- يتكامل مع NATS للإشعارات الفورية

المدخلات:
- نوع المحصول
- تاريخ الزراعة
- الطقس المتوقع
- اتجاه NDVI

المخرجات:
- Growth Stage (Stage 1-5)
- Risk Window (Low/Medium/High)
- Action Timing Recommendation
"""

from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
import uuid
import logging

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# NATS publisher (optional)
_nats_available = False
try:
    import sys
    sys.path.insert(0, "/home/user/sahool-unified-v15-idp")
    from shared.libs.events.nats_publisher import publish_analysis_completed_sync
    _nats_available = True
except ImportError:
    logger.info("NATS publisher not available")
    publish_analysis_completed_sync = None


app = FastAPI(
    title="SAHOOL Crop Growth Timing | خدمة توقيت النمو",
    version="15.5.0",
    description="Timing decisions for agricultural interventions. Field-First Architecture.",
)


# =============================================================================
# Enums & Constants
# =============================================================================


class GrowthStage(str, Enum):
    """مراحل نمو المحصول"""
    GERMINATION = "germination"      # الإنبات
    SEEDLING = "seedling"            # البادرة
    VEGETATIVE = "vegetative"        # النمو الخضري
    FLOWERING = "flowering"          # الإزهار
    FRUITING = "fruiting"            # الإثمار
    MATURITY = "maturity"            # النضج


class RiskLevel(str, Enum):
    """مستوى المخاطر"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CropType(str, Enum):
    """أنواع المحاصيل"""
    WHEAT = "wheat"
    BARLEY = "barley"
    SORGHUM = "sorghum"
    MAIZE = "maize"
    TOMATO = "tomato"
    POTATO = "potato"
    ONION = "onion"
    COFFEE = "coffee"
    DATE_PALM = "date_palm"
    MANGO = "mango"
    GRAPE = "grape"
    BANANA = "banana"
    QAT = "qat"


# Crop growth stage definitions (days from planting)
CROP_GROWTH_STAGES = {
    CropType.WHEAT: {
        "germination": (0, 7),
        "seedling": (8, 20),
        "vegetative": (21, 50),
        "flowering": (51, 70),
        "fruiting": (71, 100),
        "maturity": (101, 130),
        "critical_stages": ["flowering", "fruiting"],
        "total_days": 130,
        "name_ar": "القمح",
    },
    CropType.TOMATO: {
        "germination": (0, 10),
        "seedling": (11, 30),
        "vegetative": (31, 55),
        "flowering": (56, 75),
        "fruiting": (76, 110),
        "maturity": (111, 140),
        "critical_stages": ["flowering", "fruiting"],
        "total_days": 140,
        "name_ar": "الطماطم",
    },
    CropType.COFFEE: {
        "germination": (0, 45),
        "seedling": (46, 180),
        "vegetative": (181, 365),
        "flowering": (366, 400),
        "fruiting": (401, 600),
        "maturity": (601, 730),
        "critical_stages": ["flowering", "fruiting"],
        "total_days": 730,
        "name_ar": "البن",
    },
    CropType.MAIZE: {
        "germination": (0, 10),
        "seedling": (11, 25),
        "vegetative": (26, 60),
        "flowering": (61, 75),
        "fruiting": (76, 100),
        "maturity": (101, 120),
        "critical_stages": ["flowering"],
        "total_days": 120,
        "name_ar": "الذرة",
    },
    CropType.BANANA: {
        "germination": (0, 30),
        "seedling": (31, 120),
        "vegetative": (121, 270),
        "flowering": (271, 300),
        "fruiting": (301, 380),
        "maturity": (381, 420),
        "critical_stages": ["flowering", "fruiting"],
        "total_days": 420,
        "name_ar": "الموز",
    },
}

# Default for crops not in database
DEFAULT_CROP_STAGES = {
    "germination": (0, 10),
    "seedling": (11, 30),
    "vegetative": (31, 60),
    "flowering": (61, 80),
    "fruiting": (81, 110),
    "maturity": (111, 130),
    "critical_stages": ["flowering"],
    "total_days": 130,
    "name_ar": "محصول عام",
}

# Stage translations
STAGE_NAMES_AR = {
    GrowthStage.GERMINATION: "الإنبات",
    GrowthStage.SEEDLING: "البادرة",
    GrowthStage.VEGETATIVE: "النمو الخضري",
    GrowthStage.FLOWERING: "الإزهار",
    GrowthStage.FRUITING: "الإثمار",
    GrowthStage.MATURITY: "النضج",
}


# =============================================================================
# Models
# =============================================================================


class GrowthTimingRequest(BaseModel):
    """Request for growth timing analysis"""
    field_id: str = Field(..., description="معرف الحقل")
    farmer_id: Optional[str] = Field(None, description="معرف المزارع")
    tenant_id: Optional[str] = Field(None, description="معرف المستأجر")
    crop_type: CropType = Field(..., description="نوع المحصول")
    planting_date: date = Field(..., description="تاريخ الزراعة")
    current_ndvi: Optional[float] = Field(None, ge=-1, le=1, description="قيمة NDVI الحالية")
    ndvi_trend: Optional[str] = Field(None, description="اتجاه NDVI: improving, stable, declining")
    expected_temperature: Optional[float] = Field(None, description="درجة الحرارة المتوقعة")
    expected_rainfall_mm: Optional[float] = Field(None, ge=0, description="هطول الأمطار المتوقع بالمم")
    publish_event: bool = Field(default=True, description="نشر الحدث عبر NATS")


class GrowthStageInfo(BaseModel):
    """Growth stage information"""
    current_stage: GrowthStage
    stage_name_ar: str
    days_in_stage: int
    stage_progress_percent: float
    days_until_next_stage: int
    next_stage: Optional[GrowthStage]
    next_stage_name_ar: Optional[str]
    is_critical_period: bool


class TimingRecommendation(BaseModel):
    """Timing recommendation"""
    action_type: str
    action_title_ar: str
    action_title_en: str
    timing_window_days: int
    urgency: RiskLevel
    reason_ar: str
    reason_en: str


class GrowthTimingResponse(BaseModel):
    """Growth timing analysis response"""
    field_id: str
    crop_type: str
    crop_name_ar: str
    planting_date: date
    days_after_planting: int
    growth_stage: GrowthStageInfo
    risk_window: RiskLevel
    risk_factors: List[str]
    timing_recommendations: List[TimingRecommendation]
    action_template: Optional[Dict[str, Any]]


# =============================================================================
# Core Functions
# =============================================================================


def get_current_growth_stage(
    crop_type: CropType,
    planting_date: date,
) -> GrowthStageInfo:
    """Determine current growth stage based on days after planting"""

    today = date.today()
    days_after_planting = (today - planting_date).days

    if days_after_planting < 0:
        days_after_planting = 0

    # Get crop-specific stages or default
    stages = CROP_GROWTH_STAGES.get(crop_type, DEFAULT_CROP_STAGES)

    # Determine current stage
    current_stage = GrowthStage.MATURITY  # Default to maturity if past all stages
    stage_start = 0
    stage_end = 0

    for stage_name in ["germination", "seedling", "vegetative", "flowering", "fruiting", "maturity"]:
        start, end = stages[stage_name]
        if start <= days_after_planting <= end:
            current_stage = GrowthStage(stage_name)
            stage_start = start
            stage_end = end
            break

    # Calculate progress in current stage
    stage_duration = stage_end - stage_start + 1
    days_in_stage = days_after_planting - stage_start
    progress_percent = min(100, (days_in_stage / stage_duration) * 100)

    # Determine next stage
    stage_order = list(GrowthStage)
    current_idx = stage_order.index(current_stage)
    next_stage = stage_order[current_idx + 1] if current_idx < len(stage_order) - 1 else None

    # Days until next stage
    days_until_next = max(0, stage_end - days_after_planting + 1)

    # Check if critical period
    is_critical = current_stage.value in stages.get("critical_stages", [])

    return GrowthStageInfo(
        current_stage=current_stage,
        stage_name_ar=STAGE_NAMES_AR[current_stage],
        days_in_stage=days_in_stage,
        stage_progress_percent=round(progress_percent, 1),
        days_until_next_stage=days_until_next,
        next_stage=next_stage,
        next_stage_name_ar=STAGE_NAMES_AR.get(next_stage) if next_stage else None,
        is_critical_period=is_critical,
    )


def analyze_risk_window(
    growth_stage: GrowthStageInfo,
    ndvi_trend: Optional[str],
    expected_temperature: Optional[float],
    expected_rainfall_mm: Optional[float],
) -> tuple[RiskLevel, List[str]]:
    """Analyze risk window based on growth stage and conditions"""

    risk_factors = []
    risk_score = 0

    # Critical growth stage increases risk
    if growth_stage.is_critical_period:
        risk_score += 2
        risk_factors.append(f"مرحلة نمو حرجة: {growth_stage.stage_name_ar}")

    # Stage transition increases risk
    if growth_stage.days_until_next_stage <= 5:
        risk_score += 1
        risk_factors.append(f"انتقال قريب لمرحلة: {growth_stage.next_stage_name_ar}")

    # Declining NDVI indicates stress
    if ndvi_trend == "declining":
        risk_score += 2
        risk_factors.append("اتجاه NDVI متراجع - إجهاد محتمل")

    # Temperature extremes
    if expected_temperature:
        if expected_temperature > 38:
            risk_score += 2
            risk_factors.append(f"حرارة مرتفعة جداً: {expected_temperature}°C")
        elif expected_temperature < 5:
            risk_score += 2
            risk_factors.append(f"برودة شديدة: {expected_temperature}°C")

    # Excess or lack of rainfall
    if expected_rainfall_mm is not None:
        if expected_rainfall_mm > 50:
            risk_score += 1
            risk_factors.append(f"أمطار غزيرة متوقعة: {expected_rainfall_mm}mm")

    # Determine risk level
    if risk_score >= 4:
        risk_level = RiskLevel.CRITICAL
    elif risk_score >= 3:
        risk_level = RiskLevel.HIGH
    elif risk_score >= 2:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW

    return risk_level, risk_factors


def generate_timing_recommendations(
    growth_stage: GrowthStageInfo,
    risk_level: RiskLevel,
    crop_type: CropType,
) -> List[TimingRecommendation]:
    """Generate timing recommendations based on growth stage and risk"""

    recommendations = []

    # Critical period recommendations
    if growth_stage.is_critical_period:
        if growth_stage.current_stage == GrowthStage.FLOWERING:
            recommendations.append(TimingRecommendation(
                action_type="fertilization",
                action_title_ar="تسميد فوسفوري",
                action_title_en="Phosphorus Fertilization",
                timing_window_days=5,
                urgency=RiskLevel.HIGH,
                reason_ar="مرحلة الإزهار تتطلب فوسفور إضافي",
                reason_en="Flowering stage requires additional phosphorus",
            ))
        elif growth_stage.current_stage == GrowthStage.FRUITING:
            recommendations.append(TimingRecommendation(
                action_type="irrigation",
                action_title_ar="ري منتظم",
                action_title_en="Regular Irrigation",
                timing_window_days=2,
                urgency=RiskLevel.HIGH,
                reason_ar="مرحلة الإثمار حساسة لنقص المياه",
                reason_en="Fruiting stage is sensitive to water stress",
            ))

    # Stage transition recommendations
    if growth_stage.days_until_next_stage <= 5 and growth_stage.next_stage:
        recommendations.append(TimingRecommendation(
            action_type="inspection",
            action_title_ar=f"فحص قبل {growth_stage.next_stage_name_ar}",
            action_title_en=f"Pre-{growth_stage.next_stage.value} inspection",
            timing_window_days=growth_stage.days_until_next_stage,
            urgency=RiskLevel.MEDIUM,
            reason_ar=f"المحصول سيدخل مرحلة {growth_stage.next_stage_name_ar} خلال {growth_stage.days_until_next_stage} أيام",
            reason_en=f"Crop will enter {growth_stage.next_stage.value} stage in {growth_stage.days_until_next_stage} days",
        ))

    # High risk recommendations
    if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        recommendations.append(TimingRecommendation(
            action_type="monitoring",
            action_title_ar="مراقبة يومية",
            action_title_en="Daily Monitoring",
            timing_window_days=1,
            urgency=risk_level,
            reason_ar="نافذة خطر مرتفعة - مراقبة مكثفة مطلوبة",
            reason_en="High risk window - intensive monitoring required",
        ))

    # Default recommendation if none generated
    if not recommendations:
        recommendations.append(TimingRecommendation(
            action_type="monitoring",
            action_title_ar="مراقبة دورية",
            action_title_en="Periodic Monitoring",
            timing_window_days=7,
            urgency=RiskLevel.LOW,
            reason_ar="نمو طبيعي - استمر في المراقبة الدورية",
            reason_en="Normal growth - continue periodic monitoring",
        ))

    return recommendations


def create_growth_timing_action(
    response: "GrowthTimingResponse",
    recommendations: List[TimingRecommendation],
) -> Dict[str, Any]:
    """Create ActionTemplate from growth timing analysis"""

    # Get most urgent recommendation
    most_urgent = max(recommendations, key=lambda r: ["low", "medium", "high", "critical"].index(r.urgency.value))

    urgency_map = {
        RiskLevel.LOW: "low",
        RiskLevel.MEDIUM: "medium",
        RiskLevel.HIGH: "high",
        RiskLevel.CRITICAL: "critical",
    }

    return {
        "action_id": str(uuid.uuid4()),
        "action_type": most_urgent.action_type,
        "title_ar": most_urgent.action_title_ar,
        "title_en": most_urgent.action_title_en,
        "description_ar": most_urgent.reason_ar,
        "description_en": most_urgent.reason_en,
        "summary_ar": f"مرحلة: {response.growth_stage.stage_name_ar} | خطر: {response.risk_window.value}",
        "source_service": "crop-growth-model",
        "source_analysis_type": "growth_timing_analysis",
        "confidence": 0.85,
        "urgency": urgency_map[response.risk_window],
        "field_id": response.field_id,
        "deadline": (datetime.now() + timedelta(days=most_urgent.timing_window_days)).isoformat(),
        "optimal_window": {
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=most_urgent.timing_window_days)).isoformat(),
        },
        "offline_executable": True,
        "fallback_instructions_ar": f"في حال عدم توفر البيانات، راقب المحصول يومياً خلال مرحلة {response.growth_stage.stage_name_ar}",
        "fallback_instructions_en": f"If data unavailable, monitor crop daily during {response.growth_stage.current_stage.value} stage",
        "estimated_duration_minutes": 45,
        "data": {
            "crop_type": response.crop_type,
            "days_after_planting": response.days_after_planting,
            "growth_stage": response.growth_stage.current_stage.value,
            "stage_progress_percent": response.growth_stage.stage_progress_percent,
            "is_critical_period": response.growth_stage.is_critical_period,
            "risk_window": response.risk_window.value,
            "risk_factors": response.risk_factors,
            "timing_window_days": most_urgent.timing_window_days,
        },
        "all_recommendations": [
            {
                "type": r.action_type,
                "title_ar": r.action_title_ar,
                "timing_days": r.timing_window_days,
                "urgency": r.urgency.value,
            }
            for r in recommendations
        ],
        "created_at": datetime.utcnow().isoformat(),
    }


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "service": "crop-growth-timing",
        "version": "15.5.0",
        "supported_crops": len(CROP_GROWTH_STAGES),
        "nats_available": _nats_available,
    }


@app.post("/v1/analyze-timing", response_model=GrowthTimingResponse)
async def analyze_growth_timing(
    request: GrowthTimingRequest,
    background_tasks: BackgroundTasks,
):
    """
    تحليل توقيت نمو المحصول

    Field-First: يخبر المزارع "متى" يتدخل
    ينتج ActionTemplate لقرارات التوقيت
    """

    # Get current growth stage
    growth_stage = get_current_growth_stage(
        crop_type=request.crop_type,
        planting_date=request.planting_date,
    )

    # Analyze risk window
    risk_level, risk_factors = analyze_risk_window(
        growth_stage=growth_stage,
        ndvi_trend=request.ndvi_trend,
        expected_temperature=request.expected_temperature,
        expected_rainfall_mm=request.expected_rainfall_mm,
    )

    # Generate timing recommendations
    recommendations = generate_timing_recommendations(
        growth_stage=growth_stage,
        risk_level=risk_level,
        crop_type=request.crop_type,
    )

    # Get crop name
    stages = CROP_GROWTH_STAGES.get(request.crop_type, DEFAULT_CROP_STAGES)
    crop_name_ar = stages.get("name_ar", "محصول")

    # Build response
    days_after_planting = (date.today() - request.planting_date).days

    response = GrowthTimingResponse(
        field_id=request.field_id,
        crop_type=request.crop_type.value,
        crop_name_ar=crop_name_ar,
        planting_date=request.planting_date,
        days_after_planting=max(0, days_after_planting),
        growth_stage=growth_stage,
        risk_window=risk_level,
        risk_factors=risk_factors,
        timing_recommendations=recommendations,
        action_template=None,
    )

    # Create ActionTemplate
    action_template = create_growth_timing_action(response, recommendations)
    response.action_template = action_template

    # Publish to NATS if high risk
    if request.publish_event and _nats_available and publish_analysis_completed_sync:
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            try:
                publish_analysis_completed_sync(
                    event_type="growth.timing_alert",
                    source_service="crop-growth-model",
                    field_id=request.field_id,
                    data=action_template.get("data", {}),
                    action_template=action_template,
                    priority=action_template.get("urgency", "medium"),
                    farmer_id=request.farmer_id,
                    tenant_id=request.tenant_id,
                )
                logger.info(f"NATS: Published growth timing alert for field {request.field_id}")
            except Exception as e:
                logger.error(f"Failed to publish NATS event: {e}")

    return response


@app.get("/v1/growth-stage")
async def get_growth_stage(
    crop_type: CropType = Query(..., description="نوع المحصول"),
    planting_date: date = Query(..., description="تاريخ الزراعة"),
):
    """الحصول على مرحلة النمو الحالية"""

    stage = get_current_growth_stage(crop_type, planting_date)
    stages = CROP_GROWTH_STAGES.get(crop_type, DEFAULT_CROP_STAGES)

    return {
        "crop_type": crop_type.value,
        "crop_name_ar": stages.get("name_ar", "محصول"),
        "planting_date": planting_date.isoformat(),
        "days_after_planting": (date.today() - planting_date).days,
        "growth_stage": stage,
    }


@app.get("/v1/crops")
async def list_supported_crops():
    """قائمة المحاصيل المدعومة"""

    crops = []
    for crop_type, stages in CROP_GROWTH_STAGES.items():
        crops.append({
            "type": crop_type.value,
            "name_ar": stages["name_ar"],
            "total_days": stages["total_days"],
            "critical_stages": stages["critical_stages"],
        })

    return {
        "crops": crops,
        "total": len(crops),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8098)
