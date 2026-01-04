"""
SAHOOL Crop Health Decision Engine
Rule-based diagnostic system for vegetation indices analysis
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal


class GrowthStage(str, Enum):
    """مراحل نمو المحصول"""

    seedling = "seedling"  # شتلة
    rapid = "rapid"  # نمو سريع
    mid = "mid"  # منتصف الموسم
    late = "late"  # نهاية الموسم


Priority = Literal["P0", "P1", "P2", "P3"]
ActionType = Literal["irrigation", "fertilization", "scouting", "none"]


@dataclass(frozen=True)
class Indices:
    """مؤشرات الغطاء النباتي"""

    ndvi: float  # Normalized Difference Vegetation Index
    evi: float  # Enhanced Vegetation Index
    ndre: float  # Normalized Difference Red Edge (nitrogen status)
    lci: float  # Leaf Chlorophyll Index
    ndwi: float  # Normalized Difference Water Index
    savi: float  # Soil-Adjusted Vegetation Index


@dataclass(frozen=True)
class ZoneObservation:
    """رصد منطقة واحدة"""

    zone_id: str
    growth_stage: GrowthStage
    indices: Indices


def _clamp01(x: float) -> float:
    """تقييد القيمة بين 0 و 1"""
    if x < 0:
        return 0.0
    if x > 1:
        return 1.0
    return x


def _dose_hint_from_ndre(ndre: float) -> str:
    """تحديد كمية التسميد بناءً على NDRE"""
    if ndre < 0.18:
        return "high"
    if ndre < 0.26:
        return "medium"
    return "low"


def _get_health_status(ndvi: float) -> tuple[str, str]:
    """تحديد حالة الصحة النباتية"""
    if ndvi >= 0.7:
        return "excellent", "ممتاز"
    elif ndvi >= 0.5:
        return "good", "جيد"
    elif ndvi >= 0.35:
        return "moderate", "متوسط"
    elif ndvi >= 0.2:
        return "poor", "ضعيف"
    else:
        return "critical", "حرج"


def diagnose_zone(obs: ZoneObservation) -> list[dict[str, Any]]:
    """
    تشخيص منطقة وإرجاع قائمة الإجراءات المطلوبة

    القواعد مبنية على أبحاث الاستشعار عن بعد الزراعي:
    - NDWI منخفض = إجهاد مائي
    - NDRE منخفض مع NDVI عالي = جوع خفي (نقص نيتروجين)
    - SAVI منخفض في مرحلة الشتلات = مشاكل إنبات
    - NDVI منخفض جداً = ضعف عام يحتاج تفقد
    """
    idx = obs.indices
    actions: list[dict[str, Any]] = []

    # تطبيع القيم
    ndvi = _clamp01(idx.ndvi)
    evi = _clamp01(idx.evi)
    health_en, health_ar = _get_health_status(ndvi)

    # ═══════════════════════════════════════════════════════════════
    # القاعدة 1: إجهاد مائي (NDWI منخفض)
    # ═══════════════════════════════════════════════════════════════
    if idx.ndwi <= -0.10 and ndvi <= 0.55:
        actions.append(
            {
                "zone_id": obs.zone_id,
                "type": "irrigation",
                "priority": "P0",
                "title": "ري عاجل خلال 24 ساعة",
                "title_en": "Urgent irrigation within 24 hours",
                "reason": "NDWI منخفض جدًا مع تراجع NDVI (إجهاد مائي محتمل)",
                "reason_en": "Very low NDWI with declining NDVI (potential water stress)",
                "evidence": {"ndwi": idx.ndwi, "ndvi": ndvi},
                "recommended_window_hours": 24,
                "severity": "critical",
            }
        )
    elif idx.ndwi <= -0.10:
        actions.append(
            {
                "zone_id": obs.zone_id,
                "type": "irrigation",
                "priority": "P1",
                "title": "جدولة ري قريبًا",
                "title_en": "Schedule irrigation soon",
                "reason": "NDWI منخفض (علامات عطش مبكر)",
                "reason_en": "Low NDWI (early thirst signs)",
                "evidence": {"ndwi": idx.ndwi, "ndvi": ndvi},
                "recommended_window_hours": 48,
                "severity": "warning",
            }
        )

    # ═══════════════════════════════════════════════════════════════
    # القاعدة 2: الجوع الخفي (NDRE منخفض مع NDVI عالي)
    # ═══════════════════════════════════════════════════════════════
    if obs.growth_stage in (GrowthStage.mid, GrowthStage.late):
        if ndvi >= 0.65 and idx.ndre <= 0.26:
            actions.append(
                {
                    "zone_id": obs.zone_id,
                    "type": "fertilization",
                    "priority": "P1",
                    "title": "تسميد نيتروجيني موضعي (VRT)",
                    "title_en": "Variable Rate Technology N-fertilization",
                    "reason": "جوع خفي: NDRE منخفض بينما NDVI مرتفع",
                    "reason_en": "Hidden hunger: Low NDRE while NDVI is high",
                    "evidence": {"ndre": idx.ndre, "ndvi": ndvi},
                    "recommended_dose_hint": _dose_hint_from_ndre(idx.ndre),
                    "severity": "warning",
                }
            )

    # ═══════════════════════════════════════════════════════════════
    # القاعدة 3: مشاكل الشتلات (SAVI منخفض في المرحلة المبكرة)
    # ═══════════════════════════════════════════════════════════════
    if obs.growth_stage == GrowthStage.seedling:
        if idx.savi <= 0.20:
            actions.append(
                {
                    "zone_id": obs.zone_id,
                    "type": "scouting",
                    "priority": "P1",
                    "title": "تفقد الشتلات وعدم التجانس",
                    "title_en": "Scout seedlings for non-uniformity",
                    "reason": "SAVI منخفض في مرحلة الشتلات (إنبات/تربة/توزيع بذور)",
                    "reason_en": "Low SAVI at seedling stage (germination/soil/seed distribution)",
                    "evidence": {"savi": idx.savi},
                    "recommended_window_hours": 72,
                    "severity": "warning",
                }
            )

    # ═══════════════════════════════════════════════════════════════
    # القاعدة 4: ضعف عام (NDVI منخفض جداً)
    # ═══════════════════════════════════════════════════════════════
    if ndvi < 0.35:
        actions.append(
            {
                "zone_id": obs.zone_id,
                "type": "scouting",
                "priority": "P2",
                "title": "تفقد ميداني: ضعف شديد بالغطاء",
                "title_en": "Field scouting: severe canopy weakness",
                "reason": "NDVI منخفض جدًا (قد يكون مرض/آفات/فراغات/تربة عارية)",
                "reason_en": "Very low NDVI (may be disease/pests/gaps/bare soil)",
                "evidence": {"ndvi": ndvi, "evi": evi},
                "recommended_window_hours": 96,
                "severity": "moderate",
            }
        )

    # ═══════════════════════════════════════════════════════════════
    # القاعدة 5: الكلوروفيل المنخفض (LCI)
    # ═══════════════════════════════════════════════════════════════
    if idx.lci < 0.20 and ndvi >= 0.50:
        actions.append(
            {
                "zone_id": obs.zone_id,
                "type": "fertilization",
                "priority": "P2",
                "title": "فحص مستوى الكلوروفيل",
                "title_en": "Check chlorophyll levels",
                "reason": "LCI منخفض مع NDVI معتدل (محتمل نقص عناصر صغرى)",
                "reason_en": "Low LCI with moderate NDVI (possible micronutrient deficiency)",
                "evidence": {"lci": idx.lci, "ndvi": ndvi},
                "severity": "low",
            }
        )

    # لا توجد مشاكل
    if not actions:
        actions.append(
            {
                "zone_id": obs.zone_id,
                "type": "none",
                "priority": "P3",
                "title": "لا إجراء حاليًا",
                "title_en": "No action required",
                "reason": "المؤشرات ضمن النطاق الطبيعي",
                "reason_en": "All indices within normal range",
                "evidence": {
                    "ndvi": ndvi,
                    "evi": evi,
                    "ndre": idx.ndre,
                    "ndwi": idx.ndwi,
                    "health_status": health_en,
                },
                "severity": "ok",
            }
        )

    # ترتيب حسب الأولوية
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    actions.sort(key=lambda a: priority_order.get(a["priority"], 9))

    return actions


def classify_zone_status(actions: list[dict[str, Any]]) -> str:
    """تصنيف حالة المنطقة بناءً على الإجراءات"""
    if not actions:
        return "ok"

    priorities = [a["priority"] for a in actions]
    if "P0" in priorities:
        return "critical"
    elif "P1" in priorities:
        return "warning"
    elif "P2" in priorities:
        return "attention"
    return "ok"


def generate_vrt_properties(
    zone_id: str, actions: list[dict[str, Any]]
) -> dict[str, Any]:
    """
    توليد خصائص VRT للمنطقة (للتصدير إلى آلات الرش/الري)
    """
    irrigation_actions = [a for a in actions if a["type"] == "irrigation"]
    fert_actions = [a for a in actions if a["type"] == "fertilization"]

    props = {
        "zone_id": zone_id,
        "status": classify_zone_status(actions),
        "irrigation_required": len(irrigation_actions) > 0,
        "irrigation_priority": (
            irrigation_actions[0]["priority"] if irrigation_actions else None
        ),
        "fertilization_required": len(fert_actions) > 0,
        "n_dose_hint": (
            fert_actions[0].get("recommended_dose_hint") if fert_actions else None
        ),
    }

    return props
