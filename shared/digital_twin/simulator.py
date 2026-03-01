"""
Interactive Digital Twin Module | وحدة التوأم الرقمي التفاعلي

Provides "what-if" scenario simulation for agricultural fields:
- "What if I increase irrigation by 20%?"
- "What if I delay fertilization by a week?"
- "What if I plant a different variety?"

Competitive reference: Farmers Edge (exclusive to SAHOOL)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import StrEnum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ScenarioType(StrEnum):
    """Types of simulation scenarios | أنواع سيناريوهات المحاكاة"""

    IRRIGATION_CHANGE = "irrigation_change"
    FERTILIZER_TIMING = "fertilizer_timing"
    CROP_VARIETY = "crop_variety"
    PLANTING_DATE = "planting_date"
    PESTICIDE_APPLICATION = "pesticide_application"
    WEATHER_IMPACT = "weather_impact"
    SOIL_AMENDMENT = "soil_amendment"


class ImpactLevel(StrEnum):
    """Impact assessment levels | مستويات تقييم التأثير"""

    POSITIVE = "positive"  # إيجابي
    NEUTRAL = "neutral"  # محايد
    NEGATIVE = "negative"  # سلبي
    CRITICAL = "critical"  # حرج


SCENARIO_LABELS_AR = {
    ScenarioType.IRRIGATION_CHANGE: "تغيير الري",
    ScenarioType.FERTILIZER_TIMING: "توقيت التسميد",
    ScenarioType.CROP_VARIETY: "صنف المحصول",
    ScenarioType.PLANTING_DATE: "تاريخ الزراعة",
    ScenarioType.PESTICIDE_APPLICATION: "تطبيق المبيدات",
    ScenarioType.WEATHER_IMPACT: "تأثير الطقس",
    ScenarioType.SOIL_AMENDMENT: "تعديل التربة",
}

IMPACT_LABELS_AR = {
    ImpactLevel.POSITIVE: "إيجابي",
    ImpactLevel.NEUTRAL: "محايد",
    ImpactLevel.NEGATIVE: "سلبي",
    ImpactLevel.CRITICAL: "حرج",
}


@dataclass
class SimulationParameter:
    """A parameter for the simulation | معامل للمحاكاة"""

    name: str = ""
    name_ar: str = ""
    current_value: float = 0.0
    proposed_value: float = 0.0
    unit: str = ""
    unit_ar: str = ""
    change_percent: float = 0.0


@dataclass
class YieldImpact:
    """Yield impact prediction | تنبؤ تأثير الإنتاجية"""

    current_yield_ton_ha: float = 0.0
    predicted_yield_ton_ha: float = 0.0
    change_percent: float = 0.0
    confidence: float = 0.0
    impact_level: ImpactLevel = ImpactLevel.NEUTRAL
    impact_level_ar: str = "محايد"


@dataclass
class CostImpact:
    """Cost impact prediction | تنبؤ تأثير التكلفة"""

    current_cost_sar_ha: float = 0.0
    predicted_cost_sar_ha: float = 0.0
    change_sar: float = 0.0
    change_percent: float = 0.0


@dataclass
class WaterImpact:
    """Water usage impact | تأثير استخدام المياه"""

    current_usage_m3_ha: float = 0.0
    predicted_usage_m3_ha: float = 0.0
    change_percent: float = 0.0
    efficiency_change: str = ""
    efficiency_change_ar: str = ""


@dataclass
class RiskAssessment:
    """Risk assessment for scenario | تقييم المخاطر للسيناريو"""

    disease_risk_change: float = 0.0
    pest_risk_change: float = 0.0
    water_stress_risk: float = 0.0
    nutrient_deficiency_risk: float = 0.0
    overall_risk: str = "low"
    overall_risk_ar: str = "منخفض"
    warnings: list[str] = field(default_factory=list)
    warnings_ar: list[str] = field(default_factory=list)


@dataclass
class SimulationResult:
    """Complete simulation result | نتيجة المحاكاة الكاملة"""

    simulation_id: str = ""
    field_id: str = ""
    tenant_id: str = ""
    scenario_type: ScenarioType = ScenarioType.IRRIGATION_CHANGE
    scenario_type_ar: str = ""
    description: str = ""
    description_ar: str = ""
    parameters: list[SimulationParameter] = field(default_factory=list)
    yield_impact: YieldImpact = field(default_factory=YieldImpact)
    cost_impact: CostImpact = field(default_factory=CostImpact)
    water_impact: WaterImpact = field(default_factory=WaterImpact)
    risk_assessment: RiskAssessment = field(default_factory=RiskAssessment)
    recommendation: str = ""
    recommendation_ar: str = ""
    confidence_percent: float = 0.0
    generated_at: str = ""


class DigitalTwinSimulator:
    """Simulates agricultural scenarios for decision support.

    يحاكي السيناريوهات الزراعية لدعم اتخاذ القرار.
    """

    # Base crop models (simplified growth functions)
    CROP_MODELS = {
        "wheat": {
            "optimal_water_mm": 450,
            "optimal_nitrogen_kg_ha": 160,
            "base_yield_ton_ha": 4.5,
            "growth_stages": ["germination", "tillering", "heading", "grain_fill", "maturity"],
            "water_sensitivity": 0.8,
            "nitrogen_sensitivity": 0.6,
        },
        "barley": {
            "optimal_water_mm": 350,
            "optimal_nitrogen_kg_ha": 120,
            "base_yield_ton_ha": 3.8,
            "growth_stages": ["germination", "tillering", "heading", "grain_fill", "maturity"],
            "water_sensitivity": 0.7,
            "nitrogen_sensitivity": 0.5,
        },
        "date_palm": {
            "optimal_water_mm": 1200,
            "optimal_nitrogen_kg_ha": 200,
            "base_yield_ton_ha": 8.0,
            "growth_stages": ["dormancy", "flowering", "fruit_set", "khalal", "rutab", "tamar"],
            "water_sensitivity": 0.9,
            "nitrogen_sensitivity": 0.4,
        },
        "tomato": {
            "optimal_water_mm": 600,
            "optimal_nitrogen_kg_ha": 200,
            "base_yield_ton_ha": 40.0,
            "growth_stages": ["seedling", "vegetative", "flowering", "fruit_set", "ripening"],
            "water_sensitivity": 0.85,
            "nitrogen_sensitivity": 0.7,
        },
    }

    def __init__(self):
        pass

    def _get_impact_level(self, change_percent: float) -> tuple[ImpactLevel, str]:
        """Determine impact level from percentage change."""
        if change_percent > 5:
            return ImpactLevel.POSITIVE, IMPACT_LABELS_AR[ImpactLevel.POSITIVE]
        elif change_percent > -5:
            return ImpactLevel.NEUTRAL, IMPACT_LABELS_AR[ImpactLevel.NEUTRAL]
        elif change_percent > -15:
            return ImpactLevel.NEGATIVE, IMPACT_LABELS_AR[ImpactLevel.NEGATIVE]
        else:
            return ImpactLevel.CRITICAL, IMPACT_LABELS_AR[ImpactLevel.CRITICAL]

    def simulate_irrigation_change(
        self,
        field_id: str,
        tenant_id: str,
        crop_type: str,
        current_water_mm: float,
        proposed_change_percent: float,
        current_yield: float = 0.0,
        current_cost_per_ha: float = 0.0,
    ) -> SimulationResult:
        """Simulate changing irrigation amount.

        محاكاة تغيير كمية الري.
        "ماذا لو زدت الري 20%؟"
        """
        model = self.CROP_MODELS.get(crop_type, self.CROP_MODELS["wheat"])
        proposed_water = current_water_mm * (1 + proposed_change_percent / 100)

        if current_yield <= 0:
            current_yield = model["base_yield_ton_ha"]

        # Water response curve (diminishing returns)
        optimal = model["optimal_water_mm"]
        sensitivity = model["water_sensitivity"]

        current_efficiency = min(1.0, 1.0 - sensitivity * ((current_water_mm - optimal) / optimal) ** 2)
        proposed_efficiency = min(1.0, 1.0 - sensitivity * ((proposed_water - optimal) / optimal) ** 2)

        yield_change = ((proposed_efficiency - current_efficiency) / max(current_efficiency, 0.01)) * 100
        predicted_yield = current_yield * (1 + yield_change / 100)

        # Cost impact (water cost ~0.5 SAR/m3, 1mm = 10m3/ha)
        water_cost_change = (proposed_water - current_water_mm) * 10 * 0.5

        # Risk assessment
        warnings = []
        warnings_ar = []
        disease_risk = 0.0
        water_stress = 0.0

        if proposed_water > optimal * 1.3:
            disease_risk = 0.3
            warnings.append("Excess water may increase fungal disease risk")
            warnings_ar.append("المياه الزائدة قد تزيد من خطر الأمراض الفطرية")
        elif proposed_water < optimal * 0.6:
            water_stress = 0.5
            warnings.append("Insufficient water may cause water stress")
            warnings_ar.append("عدم كفاية المياه قد يسبب إجهاد مائي")

        impact_level, impact_ar = self._get_impact_level(yield_change)

        return SimulationResult(
            simulation_id=f"SIM-{field_id}-{datetime.now().strftime('%Y%m%d%H%M')}",
            field_id=field_id,
            tenant_id=tenant_id,
            scenario_type=ScenarioType.IRRIGATION_CHANGE,
            scenario_type_ar=SCENARIO_LABELS_AR[ScenarioType.IRRIGATION_CHANGE],
            description=f"Change irrigation by {proposed_change_percent:+.0f}%",
            description_ar=f"تغيير الري بنسبة {proposed_change_percent:+.0f}%",
            parameters=[
                SimulationParameter(
                    name="Water Amount",
                    name_ar="كمية المياه",
                    current_value=current_water_mm,
                    proposed_value=round(proposed_water, 1),
                    unit="mm",
                    unit_ar="مم",
                    change_percent=proposed_change_percent,
                ),
            ],
            yield_impact=YieldImpact(
                current_yield_ton_ha=current_yield,
                predicted_yield_ton_ha=round(predicted_yield, 2),
                change_percent=round(yield_change, 1),
                confidence=75.0,
                impact_level=impact_level,
                impact_level_ar=impact_ar,
            ),
            cost_impact=CostImpact(
                current_cost_sar_ha=current_cost_per_ha,
                predicted_cost_sar_ha=round(current_cost_per_ha + water_cost_change, 2),
                change_sar=round(water_cost_change, 2),
                change_percent=round(water_cost_change / max(current_cost_per_ha, 1) * 100, 1),
            ),
            water_impact=WaterImpact(
                current_usage_m3_ha=current_water_mm * 10,
                predicted_usage_m3_ha=round(proposed_water * 10, 1),
                change_percent=proposed_change_percent,
                efficiency_change="improved" if yield_change > 0 else "reduced",
                efficiency_change_ar="تحسن" if yield_change > 0 else "انخفض",
            ),
            risk_assessment=RiskAssessment(
                disease_risk_change=disease_risk,
                water_stress_risk=water_stress,
                overall_risk="low" if (disease_risk + water_stress) < 0.3 else "moderate",
                overall_risk_ar="منخفض" if (disease_risk + water_stress) < 0.3 else "متوسط",
                warnings=warnings,
                warnings_ar=warnings_ar,
            ),
            recommendation=f"{'Recommended' if yield_change > 0 else 'Not recommended'}: "
            f"Expected yield change {yield_change:+.1f}%",
            recommendation_ar=f"{'موصى به' if yield_change > 0 else 'غير موصى به'}: "
            f"تغيير الإنتاجية المتوقع {yield_change:+.1f}%",
            confidence_percent=75.0,
            generated_at=datetime.now(UTC).isoformat(),
        )

    def simulate_fertilizer_timing(
        self,
        field_id: str,
        tenant_id: str,
        crop_type: str,
        delay_days: int,
        current_yield: float = 0.0,
        growth_stage: str = "tillering",
    ) -> SimulationResult:
        """Simulate delaying fertilizer application.

        محاكاة تأخير التسميد.
        "ماذا لو تأخرت في التسميد أسبوع؟"
        """
        model = self.CROP_MODELS.get(crop_type, self.CROP_MODELS["wheat"])
        if current_yield <= 0:
            current_yield = model["base_yield_ton_ha"]

        sensitivity = model["nitrogen_sensitivity"]

        # Yield loss from delayed fertilization (roughly 2% per week delay)
        yield_loss_percent = -(delay_days / 7) * 2.0 * sensitivity * 100

        # Critical stages have higher sensitivity
        critical_stages = {"heading", "flowering", "fruit_set", "grain_fill"}
        if growth_stage in critical_stages:
            yield_loss_percent *= 1.5

        predicted_yield = current_yield * (1 + yield_loss_percent / 100)
        impact_level, impact_ar = self._get_impact_level(yield_loss_percent)

        warnings = []
        warnings_ar = []
        if abs(delay_days) > 14:
            warnings.append(f"Delay of {delay_days} days may significantly impact yield")
            warnings_ar.append(f"تأخير {delay_days} يوم قد يؤثر بشكل كبير على الإنتاجية")

        return SimulationResult(
            simulation_id=f"SIM-{field_id}-{datetime.now().strftime('%Y%m%d%H%M')}",
            field_id=field_id,
            tenant_id=tenant_id,
            scenario_type=ScenarioType.FERTILIZER_TIMING,
            scenario_type_ar=SCENARIO_LABELS_AR[ScenarioType.FERTILIZER_TIMING],
            description=f"Delay fertilizer application by {delay_days} days",
            description_ar=f"تأخير التسميد بـ {delay_days} يوم",
            parameters=[
                SimulationParameter(
                    name="Delay",
                    name_ar="التأخير",
                    current_value=0,
                    proposed_value=delay_days,
                    unit="days",
                    unit_ar="يوم",
                    change_percent=0,
                ),
            ],
            yield_impact=YieldImpact(
                current_yield_ton_ha=current_yield,
                predicted_yield_ton_ha=round(predicted_yield, 2),
                change_percent=round(yield_loss_percent, 1),
                confidence=70.0,
                impact_level=impact_level,
                impact_level_ar=impact_ar,
            ),
            cost_impact=CostImpact(),
            water_impact=WaterImpact(),
            risk_assessment=RiskAssessment(
                nutrient_deficiency_risk=min(1.0, abs(delay_days) / 30),
                warnings=warnings,
                warnings_ar=warnings_ar,
            ),
            recommendation="Apply fertilizer as scheduled" if delay_days > 0 else "Timing is acceptable",
            recommendation_ar="طبّق السماد في الموعد" if delay_days > 0 else "التوقيت مقبول",
            confidence_percent=70.0,
            generated_at=datetime.now(UTC).isoformat(),
        )

    def simulate_crop_variety(
        self,
        field_id: str,
        tenant_id: str,
        current_crop: str,
        proposed_crop: str,
        area_hectares: float = 1.0,
    ) -> SimulationResult:
        """Simulate changing crop variety.

        محاكاة تغيير صنف المحصول.
        "ماذا لو زرعت صنف مختلف؟"
        """
        current_model = self.CROP_MODELS.get(current_crop, self.CROP_MODELS["wheat"])
        proposed_model = self.CROP_MODELS.get(proposed_crop, self.CROP_MODELS["wheat"])

        current_yield = current_model["base_yield_ton_ha"]
        proposed_yield = proposed_model["base_yield_ton_ha"]
        yield_change = ((proposed_yield - current_yield) / current_yield) * 100

        current_water = current_model["optimal_water_mm"]
        proposed_water = proposed_model["optimal_water_mm"]
        water_change = ((proposed_water - current_water) / current_water) * 100

        impact_level, impact_ar = self._get_impact_level(yield_change)

        crop_ar = {
            "wheat": "قمح",
            "barley": "شعير",
            "date_palm": "نخيل",
            "tomato": "طماطم",
            "cucumber": "خيار",
            "alfalfa": "برسيم",
        }

        return SimulationResult(
            simulation_id=f"SIM-{field_id}-{datetime.now().strftime('%Y%m%d%H%M')}",
            field_id=field_id,
            tenant_id=tenant_id,
            scenario_type=ScenarioType.CROP_VARIETY,
            scenario_type_ar=SCENARIO_LABELS_AR[ScenarioType.CROP_VARIETY],
            description=f"Change from {current_crop} to {proposed_crop}",
            description_ar=f"التغيير من {crop_ar.get(current_crop, current_crop)} إلى {crop_ar.get(proposed_crop, proposed_crop)}",
            parameters=[
                SimulationParameter(
                    name="Crop Type",
                    name_ar="نوع المحصول",
                    current_value=0,
                    proposed_value=0,
                    unit=current_crop,
                    unit_ar=crop_ar.get(current_crop, current_crop),
                ),
            ],
            yield_impact=YieldImpact(
                current_yield_ton_ha=current_yield,
                predicted_yield_ton_ha=proposed_yield,
                change_percent=round(yield_change, 1),
                confidence=65.0,
                impact_level=impact_level,
                impact_level_ar=impact_ar,
            ),
            cost_impact=CostImpact(),
            water_impact=WaterImpact(
                current_usage_m3_ha=current_water * 10,
                predicted_usage_m3_ha=proposed_water * 10,
                change_percent=round(water_change, 1),
            ),
            risk_assessment=RiskAssessment(),
            recommendation=f"Yield {'increase' if yield_change > 0 else 'decrease'} of {abs(yield_change):.1f}% expected",
            recommendation_ar=f"{'زيادة' if yield_change > 0 else 'انخفاض'} متوقعة في الإنتاجية بنسبة {abs(yield_change):.1f}%",
            confidence_percent=65.0,
            generated_at=datetime.now(UTC).isoformat(),
        )
