"""
Smart Crop Insurance Module | وحدة تأمين المحاصيل الذكي

Provides:
- Premium calculation based on actual data (NDVI + weather + historical)
- Automatic claims with satellite evidence
- Parametric insurance (automatic payout on weather events)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class InsuranceType(str, Enum):
    YIELD_BASED = "yield_based"           # مبني على الإنتاجية
    WEATHER_PARAMETRIC = "weather_parametric"  # بارامتري (طقس)
    NDVI_INDEX = "ndvi_index"             # مبني على مؤشر NDVI
    REVENUE = "revenue"                   # مبني على الإيراد


class ClaimStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class RiskLevel(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


INSURANCE_TYPE_AR = {
    InsuranceType.YIELD_BASED: "مبني على الإنتاجية",
    InsuranceType.WEATHER_PARAMETRIC: "بارامتري (طقس)",
    InsuranceType.NDVI_INDEX: "مبني على مؤشر NDVI",
    InsuranceType.REVENUE: "مبني على الإيراد",
}

RISK_LEVEL_AR = {
    RiskLevel.VERY_LOW: "منخفض جداً",
    RiskLevel.LOW: "منخفض",
    RiskLevel.MODERATE: "متوسط",
    RiskLevel.HIGH: "مرتفع",
    RiskLevel.VERY_HIGH: "مرتفع جداً",
}

CLAIM_STATUS_AR = {
    ClaimStatus.DRAFT: "مسودة",
    ClaimStatus.SUBMITTED: "مُقدّم",
    ClaimStatus.UNDER_REVIEW: "قيد المراجعة",
    ClaimStatus.APPROVED: "موافق عليه",
    ClaimStatus.REJECTED: "مرفوض",
    ClaimStatus.PAID: "مدفوع",
}


@dataclass
class RiskAssessment:
    """Field risk assessment for insurance | تقييم مخاطر الحقل للتأمين"""
    field_id: str = ""
    crop_type: str = ""
    crop_type_ar: str = ""
    risk_level: RiskLevel = RiskLevel.MODERATE
    risk_level_ar: str = "متوسط"
    risk_score: float = 0.5
    drought_risk: float = 0.0
    flood_risk: float = 0.0
    pest_risk: float = 0.0
    disease_risk: float = 0.0
    frost_risk: float = 0.0
    historical_loss_percent: float = 0.0
    ndvi_stability: float = 0.0
    factors: list[str] = field(default_factory=list)
    factors_ar: list[str] = field(default_factory=list)


@dataclass
class InsurancePremium:
    """Insurance premium calculation | حساب قسط التأمين"""
    policy_id: str = ""
    field_id: str = ""
    tenant_id: str = ""
    insurance_type: InsuranceType = InsuranceType.YIELD_BASED
    insurance_type_ar: str = ""
    crop_type: str = ""
    area_hectares: float = 0.0
    coverage_amount_sar: float = 0.0
    premium_sar: float = 0.0
    premium_rate_percent: float = 0.0
    deductible_percent: float = 10.0
    risk_assessment: RiskAssessment = field(default_factory=RiskAssessment)
    valid_from: str = ""
    valid_to: str = ""
    message: str = ""
    message_ar: str = ""


@dataclass
class InsuranceClaim:
    """Insurance claim with evidence | مطالبة تأمين مع الأدلة"""
    claim_id: str = ""
    policy_id: str = ""
    field_id: str = ""
    tenant_id: str = ""
    status: ClaimStatus = ClaimStatus.DRAFT
    status_ar: str = "مسودة"
    loss_type: str = ""
    loss_type_ar: str = ""
    loss_date: str = ""
    estimated_loss_percent: float = 0.0
    estimated_loss_sar: float = 0.0
    evidence: list[dict] = field(default_factory=list)
    ndvi_before: float = 0.0
    ndvi_after: float = 0.0
    weather_data: dict = field(default_factory=dict)
    satellite_images: list[str] = field(default_factory=list)
    payout_amount_sar: float = 0.0
    created_at: str = ""


@dataclass
class ParametricTrigger:
    """Parametric insurance trigger | محفز التأمين البارامتري"""
    trigger_id: str = ""
    trigger_type: str = ""
    trigger_type_ar: str = ""
    threshold: float = 0.0
    actual_value: float = 0.0
    triggered: bool = False
    payout_percent: float = 0.0
    description: str = ""
    description_ar: str = ""


class SmartInsuranceEngine:
    """Smart crop insurance with data-driven premiums.

    تأمين محاصيل ذكي بأقساط مبنية على البيانات.
    """

    # Base premium rates by crop risk category
    BASE_RATES = {
        "wheat": 3.5,
        "barley": 3.0,
        "date_palm": 5.0,
        "tomato": 7.0,
        "cucumber": 6.5,
        "rice": 4.5,
        "corn": 4.0,
    }

    # Average yields for coverage calculation (ton/ha)
    AVG_YIELDS = {
        "wheat": 4.5,
        "barley": 3.8,
        "date_palm": 8.0,
        "tomato": 40.0,
        "cucumber": 35.0,
        "rice": 6.0,
        "corn": 8.0,
    }

    # Crop prices for revenue calculation (SAR/ton)
    CROP_PRICES = {
        "wheat": 1850,
        "barley": 1500,
        "date_palm": 8000,
        "tomato": 2500,
        "cucumber": 3000,
        "rice": 2800,
        "corn": 1600,
    }

    # Parametric triggers
    PARAMETRIC_TRIGGERS = {
        "drought": {
            "type": "drought",
            "type_ar": "جفاف",
            "metric": "rainfall_mm_30d",
            "threshold": 10,  # Less than 10mm in 30 days
            "comparison": "below",
            "payout_percent": 50,
            "description": "No significant rainfall for 30 days",
            "description_ar": "لا أمطار مهمة لمدة 30 يوماً",
        },
        "frost": {
            "type": "frost",
            "type_ar": "صقيع",
            "metric": "min_temp_c",
            "threshold": 0,  # Below 0°C
            "comparison": "below",
            "payout_percent": 30,
            "description": "Temperature dropped below freezing",
            "description_ar": "انخفضت الحرارة تحت الصفر",
        },
        "heat_wave": {
            "type": "heat_wave",
            "type_ar": "موجة حر",
            "metric": "max_temp_c_3d",
            "threshold": 45,
            "comparison": "above",
            "payout_percent": 25,
            "description": "Temperature exceeded 45°C for 3+ days",
            "description_ar": "تجاوزت الحرارة 45 درجة لأكثر من 3 أيام",
        },
        "flood": {
            "type": "flood",
            "type_ar": "فيضان",
            "metric": "rainfall_mm_24h",
            "threshold": 100,
            "comparison": "above",
            "payout_percent": 40,
            "description": "Rainfall exceeded 100mm in 24 hours",
            "description_ar": "تجاوزت الأمطار 100 مم خلال 24 ساعة",
        },
        "ndvi_drop": {
            "type": "ndvi_drop",
            "type_ar": "انخفاض NDVI",
            "metric": "ndvi_change_30d",
            "threshold": -0.2,
            "comparison": "below",
            "payout_percent": 35,
            "description": "NDVI dropped by more than 0.2 in 30 days",
            "description_ar": "انخفض NDVI بأكثر من 0.2 خلال 30 يوماً",
        },
    }

    def assess_risk(
        self,
        field_id: str,
        crop_type: str,
        ndvi_history: list[float] | None = None,
        historical_losses: list[float] | None = None,
        region_risk_factors: dict | None = None,
    ) -> RiskAssessment:
        """Assess field risk for insurance.

        تقييم مخاطر الحقل للتأمين.
        """
        crop_ar = {"wheat": "قمح", "barley": "شعير", "date_palm": "نخيل",
                   "tomato": "طماطم", "cucumber": "خيار", "rice": "أرز", "corn": "ذرة"}

        # Calculate component risks
        ndvi_values = ndvi_history or [0.6]
        ndvi_stability = 1.0 - (max(ndvi_values) - min(ndvi_values)) if len(ndvi_values) > 1 else 0.5

        losses = historical_losses or [0.0]
        avg_loss = sum(losses) / len(losses)

        factors = region_risk_factors or {}
        drought = factors.get("drought_risk", 0.3)
        flood = factors.get("flood_risk", 0.1)
        pest = factors.get("pest_risk", 0.2)
        disease = factors.get("disease_risk", 0.2)
        frost = factors.get("frost_risk", 0.1)

        risk_score = (drought * 0.3 + flood * 0.1 + pest * 0.2 + disease * 0.2 + frost * 0.1 + (1 - ndvi_stability) * 0.1)

        if risk_score < 0.2:
            level = RiskLevel.VERY_LOW
        elif risk_score < 0.35:
            level = RiskLevel.LOW
        elif risk_score < 0.5:
            level = RiskLevel.MODERATE
        elif risk_score < 0.7:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.VERY_HIGH

        risk_factors = []
        risk_factors_ar = []
        if drought > 0.4:
            risk_factors.append("High drought risk")
            risk_factors_ar.append("خطر جفاف مرتفع")
        if pest > 0.3:
            risk_factors.append("Elevated pest risk")
            risk_factors_ar.append("خطر آفات مرتفع")

        return RiskAssessment(
            field_id=field_id,
            crop_type=crop_type,
            crop_type_ar=crop_ar.get(crop_type, crop_type),
            risk_level=level,
            risk_level_ar=RISK_LEVEL_AR[level],
            risk_score=round(risk_score, 3),
            drought_risk=drought,
            flood_risk=flood,
            pest_risk=pest,
            disease_risk=disease,
            frost_risk=frost,
            historical_loss_percent=round(avg_loss, 1),
            ndvi_stability=round(ndvi_stability, 3),
            factors=risk_factors,
            factors_ar=risk_factors_ar,
        )

    def calculate_premium(
        self,
        field_id: str,
        tenant_id: str,
        crop_type: str,
        area_hectares: float,
        insurance_type: InsuranceType = InsuranceType.YIELD_BASED,
        risk_assessment: RiskAssessment | None = None,
    ) -> InsurancePremium:
        """Calculate insurance premium.

        حساب قسط التأمين.
        """
        if risk_assessment is None:
            risk_assessment = self.assess_risk(field_id, crop_type)

        base_rate = self.BASE_RATES.get(crop_type, 5.0)
        avg_yield = self.AVG_YIELDS.get(crop_type, 4.0)
        price = self.CROP_PRICES.get(crop_type, 1500)

        coverage = avg_yield * price * area_hectares

        risk_multiplier = 1.0 + (risk_assessment.risk_score - 0.3)
        adjusted_rate = base_rate * max(0.5, min(2.0, risk_multiplier))
        premium = coverage * (adjusted_rate / 100)

        return InsurancePremium(
            policy_id=f"POL-{field_id}-{datetime.now().strftime('%Y%m%d')}",
            field_id=field_id,
            tenant_id=tenant_id,
            insurance_type=insurance_type,
            insurance_type_ar=INSURANCE_TYPE_AR.get(insurance_type, ""),
            crop_type=crop_type,
            area_hectares=area_hectares,
            coverage_amount_sar=round(coverage, 2),
            premium_sar=round(premium, 2),
            premium_rate_percent=round(adjusted_rate, 2),
            risk_assessment=risk_assessment,
            valid_from=datetime.now(timezone.utc).isoformat(),
            message=f"Premium: {premium:,.0f} SAR for {coverage:,.0f} SAR coverage",
            message_ar=f"القسط: {premium:,.0f} ريال لتغطية {coverage:,.0f} ريال",
        )

    def check_parametric_triggers(self, weather_data: dict) -> list[ParametricTrigger]:
        """Check if any parametric triggers are activated.

        التحقق من تفعيل أي محفزات بارامترية.
        """
        triggers = []
        for key, config in self.PARAMETRIC_TRIGGERS.items():
            metric = config["metric"]
            actual = weather_data.get(metric, None)
            if actual is None:
                continue

            threshold = config["threshold"]
            comparison = config["comparison"]
            triggered = False

            if comparison == "below" and actual < threshold:
                triggered = True
            elif comparison == "above" and actual > threshold:
                triggered = True

            triggers.append(ParametricTrigger(
                trigger_id=f"TRG-{key}",
                trigger_type=config["type"],
                trigger_type_ar=config["type_ar"],
                threshold=threshold,
                actual_value=actual,
                triggered=triggered,
                payout_percent=config["payout_percent"] if triggered else 0,
                description=config["description"],
                description_ar=config["description_ar"],
            ))

        return triggers
