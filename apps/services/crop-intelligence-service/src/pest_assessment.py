"""
SAHOOL Pest Risk Assessment Module
وحدة تقييم مخاطر الآفات

Pest risk assessment based on environmental conditions and vegetation indices.
Based on agricultural research for Yemen crops.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PestType(str, Enum):
    """أنواع الآفات الشائعة"""

    # Insects - حشرات
    APHIDS = "aphids"  # من
    WHITEFLY = "whitefly"  # ذبابة بيضاء
    THRIPS = "thrips"  # تربس
    MITES = "mites"  # أكاروس
    LOCUST = "locust"  # جراد
    ARMYWORM = "armyworm"  # دودة الجيش
    BOLLWORM = "bollworm"  # دودة اللوز
    FRUIT_FLY = "fruit_fly"  # ذبابة الفاكهة
    LEAF_MINER = "leaf_miner"  # صانعة الأنفاق
    STEM_BORER = "stem_borer"  # حفار الساق

    # Nematodes - نيماتودا
    ROOT_KNOT_NEMATODE = "root_knot_nematode"  # نيماتودا تعقد الجذور

    # Rodents - قوارض
    RATS = "rats"  # فئران

    # Birds - طيور
    BIRDS = "birds"  # طيور


class RiskLevel(str, Enum):
    """مستوى المخاطر"""

    VERY_LOW = "very_low"  # منخفض جداً
    LOW = "low"  # منخفض
    MODERATE = "moderate"  # متوسط
    HIGH = "high"  # مرتفع
    CRITICAL = "critical"  # حرج


class ControlMethod(str, Enum):
    """طريقة المكافحة"""

    BIOLOGICAL = "biological"  # حيوية
    CHEMICAL = "chemical"  # كيميائية
    CULTURAL = "cultural"  # زراعية
    MECHANICAL = "mechanical"  # ميكانيكية
    INTEGRATED = "integrated"  # متكاملة


@dataclass
class PestControl:
    """طريقة مكافحة الآفة"""

    method: ControlMethod
    product_name: str
    product_name_ar: str
    dosage: str
    dosage_ar: str
    timing: str
    timing_ar: str
    effectiveness: str  # high, medium, low
    safety_interval_days: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method.value,
            "product_name": self.product_name,
            "product_name_ar": self.product_name_ar,
            "dosage": self.dosage,
            "dosage_ar": self.dosage_ar,
            "timing": self.timing,
            "timing_ar": self.timing_ar,
            "effectiveness": self.effectiveness,
            "safety_interval_days": self.safety_interval_days,
        }


@dataclass
class PestRisk:
    """تقييم مخاطر الآفة"""

    pest_type: PestType
    risk_level: RiskLevel
    risk_score: float  # 0-100
    name_en: str
    name_ar: str
    description_en: str
    description_ar: str
    favorable_conditions: list[str]
    favorable_conditions_ar: list[str]
    damage_symptoms_en: list[str]
    damage_symptoms_ar: list[str]
    controls: list[PestControl]
    monitoring_advice_en: str
    monitoring_advice_ar: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "pest_type": self.pest_type.value,
            "risk_level": self.risk_level.value,
            "risk_score": round(self.risk_score, 1),
            "name_en": self.name_en,
            "name_ar": self.name_ar,
            "description_en": self.description_en,
            "description_ar": self.description_ar,
            "favorable_conditions": self.favorable_conditions,
            "favorable_conditions_ar": self.favorable_conditions_ar,
            "damage_symptoms_en": self.damage_symptoms_en,
            "damage_symptoms_ar": self.damage_symptoms_ar,
            "controls": [c.to_dict() for c in self.controls],
            "monitoring_advice_en": self.monitoring_advice_en,
            "monitoring_advice_ar": self.monitoring_advice_ar,
        }


# Pest database with conditions and controls
PEST_DATABASE = {
    PestType.APHIDS: {
        "name_en": "Aphids",
        "name_ar": "المن",
        "description_en": "Small sap-sucking insects that cause leaf curling and transmit viruses",
        "description_ar": "حشرات صغيرة ماصة للعصارة تسبب تجعد الأوراق ونقل الفيروسات",
        "favorable_temp_range": (15, 28),
        "favorable_humidity_min": 50,
        "favorable_humidity_max": 80,
        "ndvi_vulnerability_max": 0.65,  # Dense canopy favors aphids
        "damage_symptoms_en": ["Leaf curling", "Honeydew on leaves", "Stunted growth", "Sooty mold"],
        "damage_symptoms_ar": ["تجعد الأوراق", "ندوة عسلية على الأوراق", "تقزم النمو", "عفن أسود"],
        "controls": [
            PestControl(
                method=ControlMethod.BIOLOGICAL,
                product_name="Ladybugs/Lacewings release",
                product_name_ar="إطلاق أبو العيد/أسد المن",
                dosage="5000-10000 per hectare",
                dosage_ar="5000-10000 لكل هكتار",
                timing="At first detection",
                timing_ar="عند أول اكتشاف",
                effectiveness="medium",
                safety_interval_days=0,
            ),
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Imidacloprid (Confidor)",
                product_name_ar="إيميداكلوبريد (كونفيدور)",
                dosage="0.3-0.5 L/ha",
                dosage_ar="0.3-0.5 لتر/هكتار",
                timing="When population exceeds threshold",
                timing_ar="عند تجاوز الكثافة للعتبة الاقتصادية",
                effectiveness="high",
                safety_interval_days=21,
            ),
        ],
        "monitoring_advice_en": "Check undersides of leaves weekly, especially young shoots",
        "monitoring_advice_ar": "افحص أسفل الأوراق أسبوعياً، خاصة النموات الحديثة",
    },
    PestType.WHITEFLY: {
        "name_en": "Whitefly",
        "name_ar": "الذبابة البيضاء",
        "description_en": "Small white flying insects that suck plant sap and transmit viruses",
        "description_ar": "حشرات بيضاء صغيرة طائرة تمتص عصارة النبات وتنقل الفيروسات",
        "favorable_temp_range": (25, 35),
        "favorable_humidity_min": 40,
        "favorable_humidity_max": 70,
        "ndvi_vulnerability_max": 0.70,
        "damage_symptoms_en": ["Yellowing leaves", "Honeydew", "Virus symptoms", "Leaf drop"],
        "damage_symptoms_ar": ["اصفرار الأوراق", "ندوة عسلية", "أعراض فيروسية", "سقوط أوراق"],
        "controls": [
            PestControl(
                method=ControlMethod.MECHANICAL,
                product_name="Yellow sticky traps",
                product_name_ar="مصائد لاصقة صفراء",
                dosage="20-40 traps/ha",
                dosage_ar="20-40 مصيدة/هكتار",
                timing="Preventive",
                timing_ar="وقائياً",
                effectiveness="medium",
                safety_interval_days=0,
            ),
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Pyriproxyfen (Admiral)",
                product_name_ar="بيريبروكسيفين (أدميرال)",
                dosage="0.5-0.75 L/ha",
                dosage_ar="0.5-0.75 لتر/هكتار",
                timing="At egg stage",
                timing_ar="في مرحلة البيض",
                effectiveness="high",
                safety_interval_days=14,
            ),
        ],
        "monitoring_advice_en": "Shake plants over white paper to detect adults",
        "monitoring_advice_ar": "هز النباتات فوق ورقة بيضاء لاكتشاف الحشرات البالغة",
    },
    PestType.LOCUST: {
        "name_en": "Desert Locust",
        "name_ar": "الجراد الصحراوي",
        "description_en": "Migratory pest that can devastate crops in swarms",
        "description_ar": "آفة مهاجرة يمكن أن تدمر المحاصيل في أسراب",
        "favorable_temp_range": (25, 40),
        "favorable_humidity_min": 30,
        "favorable_humidity_max": 60,
        "seasonal_peak": ["spring", "summer"],
        "damage_symptoms_en": ["Complete defoliation", "Stripped stems", "Destroyed crops"],
        "damage_symptoms_ar": ["إزالة كاملة للأوراق", "سيقان عارية", "محاصيل مدمرة"],
        "controls": [
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Malathion ULV",
                product_name_ar="مالاثيون ULV",
                dosage="1-1.5 L/ha aerial",
                dosage_ar="1-1.5 لتر/هكتار جوي",
                timing="At swarm detection",
                timing_ar="عند اكتشاف السرب",
                effectiveness="high",
                safety_interval_days=7,
            ),
            PestControl(
                method=ControlMethod.BIOLOGICAL,
                product_name="Metarhizium acridum",
                product_name_ar="ميتاريزيوم أكريدوم",
                dosage="50g/ha",
                dosage_ar="50 جم/هكتار",
                timing="Preventive in breeding areas",
                timing_ar="وقائياً في مناطق التكاثر",
                effectiveness="medium",
                safety_interval_days=0,
            ),
        ],
        "monitoring_advice_en": "Monitor FAO Desert Locust bulletins and local reports",
        "monitoring_advice_ar": "راقب نشرات الفاو للجراد الصحراوي والتقارير المحلية",
    },
    PestType.THRIPS: {
        "name_en": "Thrips",
        "name_ar": "التربس",
        "description_en": "Tiny insects that rasp and suck plant tissue, causing silvering",
        "description_ar": "حشرات دقيقة تكشط وتمتص أنسجة النبات مسببة فضية الأوراق",
        "favorable_temp_range": (20, 30),
        "favorable_humidity_min": 30,
        "favorable_humidity_max": 60,
        "damage_symptoms_en": ["Silvery streaks", "Distorted growth", "Flower damage"],
        "damage_symptoms_ar": ["خطوط فضية", "نمو مشوه", "تلف الأزهار"],
        "controls": [
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Spinosad (Success)",
                product_name_ar="سبينوساد (ساكسس)",
                dosage="200-400 ml/ha",
                dosage_ar="200-400 مل/هكتار",
                timing="At flower stage",
                timing_ar="في مرحلة الإزهار",
                effectiveness="high",
                safety_interval_days=3,
            ),
        ],
        "monitoring_advice_en": "Use blue sticky traps for monitoring",
        "monitoring_advice_ar": "استخدم مصائد لاصقة زرقاء للمراقبة",
    },
    PestType.FRUIT_FLY: {
        "name_en": "Fruit Fly",
        "name_ar": "ذبابة الفاكهة",
        "description_en": "Lays eggs in fruit causing maggot infestation",
        "description_ar": "تضع بيضها في الثمار مسببة إصابة باليرقات",
        "favorable_temp_range": (25, 35),
        "favorable_humidity_min": 60,
        "favorable_humidity_max": 90,
        "damage_symptoms_en": ["Fruit punctures", "Maggots in fruit", "Premature fruit drop"],
        "damage_symptoms_ar": ["ثقوب في الثمار", "يرقات في الثمار", "سقوط مبكر للثمار"],
        "controls": [
            PestControl(
                method=ControlMethod.MECHANICAL,
                product_name="Protein bait traps",
                product_name_ar="مصائد طعوم بروتينية",
                dosage="10-15 traps/ha",
                dosage_ar="10-15 مصيدة/هكتار",
                timing="Before fruit ripening",
                timing_ar="قبل نضج الثمار",
                effectiveness="medium",
                safety_interval_days=0,
            ),
            PestControl(
                method=ControlMethod.CHEMICAL,
                product_name="Bait spray (protein + insecticide)",
                product_name_ar="رش طعوم (بروتين + مبيد)",
                dosage="Spot application",
                dosage_ar="رش موضعي",
                timing="Weekly during fruiting",
                timing_ar="أسبوعياً خلال الإثمار",
                effectiveness="high",
                safety_interval_days=7,
            ),
        ],
        "monitoring_advice_en": "Install McPhail traps 6 weeks before harvest",
        "monitoring_advice_ar": "ركب مصائد ماكفيل قبل 6 أسابيع من الحصاد",
    },
}


def assess_pest_risks(
    temp_c: float,
    humidity_pct: float,
    ndvi: float,
    crop_type: str = "general",
    season: str = "summer",
    region: str = "yemen",
) -> list[PestRisk]:
    """
    تقييم مخاطر الآفات بناءً على الظروف البيئية
    Assess pest risks based on environmental conditions

    Args:
        temp_c: Current temperature (°C)
        humidity_pct: Relative humidity (%)
        ndvi: NDVI value for canopy assessment
        crop_type: Type of crop
        season: Current season (spring, summer, fall, winter)
        region: Geographic region

    Returns:
        List of pest risks sorted by risk level
    """
    risks = []

    for pest_type, pest_data in PEST_DATABASE.items():
        # Calculate base risk score
        risk_score = 0.0
        favorable_conditions = []
        favorable_conditions_ar = []

        # Temperature factor
        temp_range = pest_data.get("favorable_temp_range", (15, 35))
        if temp_range[0] <= temp_c <= temp_range[1]:
            temp_factor = 1.0 - abs(temp_c - (temp_range[0] + temp_range[1]) / 2) / (temp_range[1] - temp_range[0])
            risk_score += 35 * temp_factor
            favorable_conditions.append(f"Temperature in favorable range ({temp_range[0]}-{temp_range[1]}°C)")
            favorable_conditions_ar.append(f"الحرارة في النطاق الملائم ({temp_range[0]}-{temp_range[1]} °م)")

        # Humidity factor
        humidity_min = pest_data.get("favorable_humidity_min", 40)
        humidity_max = pest_data.get("favorable_humidity_max", 80)
        if humidity_min <= humidity_pct <= humidity_max:
            humidity_factor = 1.0 - abs(humidity_pct - (humidity_min + humidity_max) / 2) / (humidity_max - humidity_min)
            risk_score += 25 * humidity_factor
            favorable_conditions.append(f"Humidity in favorable range ({humidity_min}-{humidity_max}%)")
            favorable_conditions_ar.append(f"الرطوبة في النطاق الملائم ({humidity_min}-{humidity_max}%)")

        # NDVI/canopy factor
        ndvi_max = pest_data.get("ndvi_vulnerability_max", 0.75)
        if ndvi >= ndvi_max - 0.15:
            ndvi_factor = min(1.0, (ndvi - (ndvi_max - 0.15)) / 0.15)
            risk_score += 20 * ndvi_factor
            favorable_conditions.append("Dense canopy providing favorable habitat")
            favorable_conditions_ar.append("مظلة كثيفة توفر بيئة ملائمة")

        # Seasonal factor
        seasonal_peak = pest_data.get("seasonal_peak", [])
        if season.lower() in seasonal_peak:
            risk_score += 20
            favorable_conditions.append(f"Peak season for this pest ({season})")
            favorable_conditions_ar.append(f"موسم الذروة لهذه الآفة ({season})")

        # Only include if risk score is meaningful
        if risk_score < 15:
            continue

        # Determine risk level
        if risk_score >= 75:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 55:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 35:
            risk_level = RiskLevel.MODERATE
        elif risk_score >= 20:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.VERY_LOW

        risks.append(
            PestRisk(
                pest_type=pest_type,
                risk_level=risk_level,
                risk_score=risk_score,
                name_en=pest_data["name_en"],
                name_ar=pest_data["name_ar"],
                description_en=pest_data["description_en"],
                description_ar=pest_data["description_ar"],
                favorable_conditions=favorable_conditions,
                favorable_conditions_ar=favorable_conditions_ar,
                damage_symptoms_en=pest_data["damage_symptoms_en"],
                damage_symptoms_ar=pest_data["damage_symptoms_ar"],
                controls=pest_data["controls"],
                monitoring_advice_en=pest_data["monitoring_advice_en"],
                monitoring_advice_ar=pest_data["monitoring_advice_ar"],
            )
        )

    # Sort by risk score (highest first)
    risks.sort(key=lambda r: r.risk_score, reverse=True)

    return risks


def get_pest_summary(risks: list[PestRisk]) -> dict[str, Any]:
    """
    ملخص تقييم مخاطر الآفات
    Get pest risk assessment summary

    Returns:
        Summary dictionary
    """
    if not risks:
        return {
            "overall_status_en": "Low Risk",
            "overall_status_ar": "مخاطر منخفضة",
            "total_pests_assessed": 0,
            "critical_risks": 0,
            "high_risks": 0,
            "action_required": False,
        }

    critical = sum(1 for r in risks if r.risk_level == RiskLevel.CRITICAL)
    high = sum(1 for r in risks if r.risk_level == RiskLevel.HIGH)
    moderate = sum(1 for r in risks if r.risk_level == RiskLevel.MODERATE)

    if critical > 0:
        status_en, status_ar = "Critical - Immediate Action Required", "حرج - إجراء فوري مطلوب"
    elif high > 0:
        status_en, status_ar = "High Risk - Monitor Closely", "مخاطر عالية - راقب عن كثب"
    elif moderate > 0:
        status_en, status_ar = "Moderate Risk - Regular Monitoring", "مخاطر متوسطة - مراقبة منتظمة"
    else:
        status_en, status_ar = "Low Risk - Routine Checks", "مخاطر منخفضة - فحوصات روتينية"

    return {
        "overall_status_en": status_en,
        "overall_status_ar": status_ar,
        "total_pests_assessed": len(risks),
        "critical_risks": critical,
        "high_risks": high,
        "moderate_risks": moderate,
        "action_required": critical > 0 or high > 0,
    }


def get_pest_types() -> list[dict[str, str]]:
    """Get list of all pest types"""
    return [
        {
            "value": pt.value,
            "name_en": PEST_DATABASE.get(pt, {}).get("name_en", pt.value),
            "name_ar": PEST_DATABASE.get(pt, {}).get("name_ar", pt.value),
        }
        for pt in PestType
        if pt in PEST_DATABASE
    ]
