"""
Thresholds & Alerts API
واجهة برمجة العتبات والتنبيهات

Endpoints for economic thresholds and pest alerts.
"""

from datetime import datetime
from enum import Enum, StrEnum
from typing import Optional
from uuid import uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    _bearer_scheme = HTTPBearer(auto_error=False)
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Lightweight auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials}

logger = structlog.get_logger(__name__)

router = APIRouter()


# ============================================================================
# Enums
# ============================================================================


class ThresholdStatus(StrEnum):
    """Threshold status."""

    BELOW = "below"
    APPROACHING = "approaching"
    AT_THRESHOLD = "at_threshold"
    EXCEEDED = "exceeded"


class AlertPriority(StrEnum):
    """Alert priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(StrEnum):
    """Alert status."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


# ============================================================================
# Models
# ============================================================================


class EconomicThreshold(BaseModel):
    """Economic threshold for pest."""

    id: str
    pest_id: str
    pest_name_en: str
    pest_name_ar: str
    crop: str
    threshold_value: float
    threshold_unit: str  # e.g., "insects/plant", "% infestation"
    threshold_unit_ar: str
    action_threshold: float  # When to take action
    economic_injury_level: float  # Point of economic damage
    sampling_method_en: str
    sampling_method_ar: str
    notes_en: str | None = None
    notes_ar: str | None = None


class ThresholdAssessment(BaseModel):
    """Request to assess threshold status."""

    pest_id: str
    crop: str
    current_value: float
    field_id: str | None = None
    growth_stage: str | None = None


class ThresholdResult(BaseModel):
    """Threshold assessment result."""

    pest_id: str
    crop: str
    current_value: float
    threshold_value: float
    action_threshold: float
    status: ThresholdStatus
    status_ar: str
    yield_loss_estimate_percent: float | None = None
    recommendation_en: str
    recommendation_ar: str
    urgency: AlertPriority


class Alert(BaseModel):
    """Pest alert."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    field_id: str
    pest_id: str
    pest_name_en: str
    pest_name_ar: str
    priority: AlertPriority
    status: AlertStatus = AlertStatus.ACTIVE
    title_en: str
    title_ar: str
    message_en: str
    message_ar: str
    threshold_exceeded: float | None = None
    recommended_action_en: str | None = None
    recommended_action_ar: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: datetime | None = None
    acknowledged_by: str | None = None
    resolved_at: datetime | None = None


# ============================================================================
# Threshold Database
# ============================================================================

THRESHOLD_DATABASE: dict[str, EconomicThreshold] = {
    "rpw_date_palm": EconomicThreshold(
        id="rpw_date_palm",
        pest_id="rpw",
        pest_name_en="Red Palm Weevil",
        pest_name_ar="سوسة النخيل الحمراء",
        crop="date_palm",
        threshold_value=1,
        threshold_unit="trap catches/week",
        threshold_unit_ar="صيد/مصيدة/أسبوع",
        action_threshold=1,
        economic_injury_level=1,
        sampling_method_en="Pheromone trap monitoring, 5 traps per hectare",
        sampling_method_ar="مراقبة مصائد الفرمون، 5 مصائد لكل هكتار",
        notes_en="Zero tolerance - any detection requires immediate action",
        notes_ar="عدم تحمل - أي كشف يتطلب إجراء فوري",
    ),
    "aphids_wheat": EconomicThreshold(
        id="aphids_wheat",
        pest_id="aphids",
        pest_name_en="Aphids",
        pest_name_ar="المن",
        crop="wheat",
        threshold_value=20,
        threshold_unit="aphids/tiller",
        threshold_unit_ar="حشرة/فرع",
        action_threshold=15,
        economic_injury_level=30,
        sampling_method_en="Count aphids on 20 random tillers per field",
        sampling_method_ar="عد المن على 20 فرع عشوائي لكل حقل",
    ),
    "whitefly_tomato": EconomicThreshold(
        id="whitefly_tomato",
        pest_id="whitefly",
        pest_name_en="Whitefly",
        pest_name_ar="الذبابة البيضاء",
        crop="tomato",
        threshold_value=5,
        threshold_unit="adults/leaf",
        threshold_unit_ar="حشرة بالغة/ورقة",
        action_threshold=3,
        economic_injury_level=10,
        sampling_method_en="Count adults on 3rd leaf from top, 20 plants/field",
        sampling_method_ar="عد البالغات على الورقة الثالثة من القمة، 20 نبات/حقل",
    ),
    "spider_mite_cucumber": EconomicThreshold(
        id="spider_mite_cucumber",
        pest_id="spider_mite",
        pest_name_en="Spider Mite",
        pest_name_ar="العنكبوت الأحمر",
        crop="cucumber",
        threshold_value=5,
        threshold_unit="mites/leaf",
        threshold_unit_ar="عث/ورقة",
        action_threshold=3,
        economic_injury_level=10,
        sampling_method_en="Examine leaf undersides, 5 leaves per plant, 10 plants",
        sampling_method_ar="فحص أسفل الأوراق، 5 أوراق/نبات، 10 نباتات",
    ),
    "tuta_tomato": EconomicThreshold(
        id="tuta_tomato",
        pest_id="tuta",
        pest_name_en="Tomato Leafminer",
        pest_name_ar="حافرة أنفاق الطماطم",
        crop="tomato",
        threshold_value=30,
        threshold_unit="adults/trap/week",
        threshold_unit_ar="بالغ/مصيدة/أسبوع",
        action_threshold=20,
        economic_injury_level=50,
        sampling_method_en="Delta trap with pheromone, 2 traps/1000m²",
        sampling_method_ar="مصيدة دلتا مع فرمون، 2 مصيدة/1000م²",
    ),
    "thrips_onion": EconomicThreshold(
        id="thrips_onion",
        pest_id="thrips",
        pest_name_en="Thrips",
        pest_name_ar="التربس",
        crop="onion",
        threshold_value=30,
        threshold_unit="thrips/plant",
        threshold_unit_ar="حشرة/نبات",
        action_threshold=20,
        economic_injury_level=50,
        sampling_method_en="Shake plant over white paper, count thrips",
        sampling_method_ar="هز النبات فوق ورقة بيضاء، عد التربس",
    ),
    "locust_general": EconomicThreshold(
        id="locust_general",
        pest_id="locust",
        pest_name_en="Desert Locust",
        pest_name_ar="الجراد الصحراوي",
        crop="general",
        threshold_value=1,
        threshold_unit="swarm sighting",
        threshold_unit_ar="مشاهدة سرب",
        action_threshold=1,
        economic_injury_level=1,
        sampling_method_en="Visual observation and reporting",
        sampling_method_ar="المراقبة البصرية والإبلاغ",
        notes_en="Report immediately to Ministry of Agriculture",
        notes_ar="أبلغ فوراً وزارة الزراعة",
    ),
}

# In-memory alerts storage
ALERTS_DB: dict[str, Alert] = {}


# ============================================================================
# API Endpoints
# ============================================================================


@router.get("/thresholds")
async def list_thresholds(
    crop: str | None = None,
    pest_id: str | None = None,
    _user=Depends(get_current_user),
):
    """
    List economic thresholds.
    قائمة العتبات الاقتصادية.
    """
    thresholds = list(THRESHOLD_DATABASE.values())

    if crop:
        thresholds = [t for t in thresholds if t.crop.lower() == crop.lower()]

    if pest_id:
        thresholds = [t for t in thresholds if t.pest_id == pest_id]

    return thresholds


@router.get("/thresholds/crop/{crop}/pest/{pest_id}", response_model=EconomicThreshold)
async def get_threshold(crop: str, pest_id: str):
    """
    Get threshold for crop-pest combination.
    الحصول على العتبة لمزيج المحصول والآفة.
    """
    key = f"{pest_id}_{crop}"
    threshold = THRESHOLD_DATABASE.get(key)

    if not threshold:
        # Try general threshold
        key = f"{pest_id}_general"
        threshold = THRESHOLD_DATABASE.get(key)

    if not threshold:
        raise HTTPException(
            status_code=404,
            detail=f"No threshold defined for {pest_id} on {crop}",
        )

    return threshold


@router.post("/thresholds/assess", response_model=ThresholdResult)
async def assess_threshold(assessment: ThresholdAssessment):
    """
    Assess threshold status.
    تقييم حالة العتبة.
    """
    # Find threshold
    key = f"{assessment.pest_id}_{assessment.crop}"
    threshold = THRESHOLD_DATABASE.get(key)

    if not threshold:
        key = f"{assessment.pest_id}_general"
        threshold = THRESHOLD_DATABASE.get(key)

    if not threshold:
        raise HTTPException(
            status_code=404,
            detail=f"No threshold defined for {assessment.pest_id} on {assessment.crop}",
        )

    # Determine status
    current = assessment.current_value
    action = threshold.action_threshold
    economic = threshold.economic_injury_level

    if current < action * 0.5:
        status = ThresholdStatus.BELOW
        status_ar = "تحت العتبة"
        urgency = AlertPriority.LOW
        rec_en = "Continue regular monitoring"
        rec_ar = "استمر في المراقبة المنتظمة"
        yield_loss = None
    elif current < action:
        status = ThresholdStatus.APPROACHING
        status_ar = "يقترب من العتبة"
        urgency = AlertPriority.MEDIUM
        rec_en = "Increase monitoring frequency, prepare for treatment"
        rec_ar = "زد تكرار المراقبة، استعد للعلاج"
        yield_loss = None
    elif current < economic:
        status = ThresholdStatus.AT_THRESHOLD
        status_ar = "عند العتبة"
        urgency = AlertPriority.HIGH
        rec_en = "Begin treatment immediately"
        rec_ar = "ابدأ العلاج فوراً"
        yield_loss = ((current - action) / (economic - action)) * 10
    else:
        status = ThresholdStatus.EXCEEDED
        status_ar = "تجاوز العتبة"
        urgency = AlertPriority.CRITICAL
        rec_en = "Emergency treatment required - economic damage occurring"
        rec_ar = "علاج طارئ مطلوب - ضرر اقتصادي يحدث"
        yield_loss = min(((current - economic) / economic) * 30 + 10, 100)

    logger.info(
        "threshold_assessed",
        pest_id=assessment.pest_id,
        crop=assessment.crop,
        current=current,
        status=status,
    )

    return ThresholdResult(
        pest_id=assessment.pest_id,
        crop=assessment.crop,
        current_value=current,
        threshold_value=threshold.threshold_value,
        action_threshold=action,
        status=status,
        status_ar=status_ar,
        yield_loss_estimate_percent=yield_loss,
        recommendation_en=rec_en,
        recommendation_ar=rec_ar,
        urgency=urgency,
    )


@router.get("/alerts")
async def list_alerts(
    field_id: str | None = None,
    status: AlertStatus | None = None,
    priority: AlertPriority | None = None,
    limit: int = Query(50, ge=1, le=100),
):
    """
    List active pest alerts.
    قائمة تنبيهات الآفات النشطة.
    """
    alerts = list(ALERTS_DB.values())

    if field_id:
        alerts = [a for a in alerts if a.field_id == field_id]

    if status:
        alerts = [a for a in alerts if a.status == status]

    if priority:
        alerts = [a for a in alerts if a.priority == priority]

    # Sort by priority and created_at
    priority_order = {
        AlertPriority.CRITICAL: 0,
        AlertPriority.HIGH: 1,
        AlertPriority.MEDIUM: 2,
        AlertPriority.LOW: 3,
    }
    alerts.sort(key=lambda x: (priority_order[x.priority], -x.created_at.timestamp()))

    return {
        "total": len(alerts),
        "alerts": alerts[:limit],
    }


@router.get("/alerts/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str):
    """
    Get alert details.
    الحصول على تفاصيل التنبيه.
    """
    alert = ALERTS_DB.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert not found: {alert_id}")
    return alert


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str = Query(..., description="User acknowledging the alert"),
):
    """
    Acknowledge alert.
    الإقرار بالتنبيه.
    """
    alert = ALERTS_DB.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert not found: {alert_id}")

    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = acknowledged_by

    logger.info(
        "alert_acknowledged",
        alert_id=alert_id,
        acknowledged_by=acknowledged_by,
    )

    return {
        "message": "Alert acknowledged",
        "message_ar": "تم الإقرار بالتنبيه",
        "alert": alert,
    }


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolution_notes: str | None = None,
):
    """
    Resolve alert.
    حل التنبيه.
    """
    alert = ALERTS_DB.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert not found: {alert_id}")

    alert.status = AlertStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()

    logger.info("alert_resolved", alert_id=alert_id)

    return {
        "message": "Alert resolved",
        "message_ar": "تم حل التنبيه",
        "alert": alert,
    }


@router.post("/alerts/create", response_model=Alert)
async def create_alert(
    field_id: str,
    pest_id: str,
    priority: AlertPriority,
    message_en: str,
    message_ar: str,
):
    """
    Create manual alert.
    إنشاء تنبيه يدوي.
    """
    from src.api.v1.pests import PEST_DATABASE

    pest = PEST_DATABASE.get(pest_id)
    pest_name_en = pest.name_en if pest else pest_id
    pest_name_ar = pest.name_ar if pest else pest_id

    alert = Alert(
        field_id=field_id,
        pest_id=pest_id,
        pest_name_en=pest_name_en,
        pest_name_ar=pest_name_ar,
        priority=priority,
        title_en=f"{pest_name_en} Alert",
        title_ar=f"تنبيه {pest_name_ar}",
        message_en=message_en,
        message_ar=message_ar,
    )

    ALERTS_DB[alert.id] = alert

    logger.info(
        "alert_created",
        alert_id=alert.id,
        field_id=field_id,
        pest_id=pest_id,
        priority=priority,
    )

    return alert
