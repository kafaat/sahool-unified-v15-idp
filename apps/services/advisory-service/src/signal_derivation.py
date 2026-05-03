"""
Signal derivation: convert raw field telemetry into agronomic signals
and a composite risk score consumed by the advisor engine.

اشتقاق الإشارات: تحويل بيانات الحقل المباشرة إلى إشارات زراعية
ودرجة خطر مركبة يستخدمها محرك المستشار.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FieldContext:
    """Raw field telemetry / context."""

    ndvi: float  # vegetation index (0-1)
    ndwi: float  # water index (0-1)
    soil_moisture: float  # soil moisture (0-1)
    temperature: float  # °C
    crop_type: str
    growth_stage: str  # germination | vegetative | flowering | maturity
    region: str  # mena | saudi | yemen | ...
    soil_texture: str | None = None  # sandy | clay | loam
    nitrogen_level: float | None = None  # 0-1


@dataclass
class DerivedSignals:
    water_stress: bool
    heat_stress: bool
    nitrogen_deficiency: bool
    pest_risk: str  # low | medium | high
    growth_stage_appropriate: bool
    critical_ndvi: bool  # NDVI < 0.2


# Thresholds — kept as module-level constants for testability.
NDWI_STRESS_THRESHOLD = 0.2
SOIL_MOISTURE_STRESS_THRESHOLD = 0.3
HEAT_STRESS_TEMP_C = 35.0
NITROGEN_DEFICIENCY_THRESHOLD = 0.4
NDVI_PEST_THRESHOLD = 0.4
NDVI_CRITICAL_THRESHOLD = 0.2
NDVI_HEALTHY_VEGETATIVE = 0.4
NDVI_MATURITY_LOW = 0.5

_VEGETATIVE_STAGES = {"vegetative", "flowering"}


def derive_signals(field: FieldContext) -> DerivedSignals:
    """Convert raw field measurements into binary/categorical signals."""
    water_stress = field.ndwi < NDWI_STRESS_THRESHOLD or field.soil_moisture < SOIL_MOISTURE_STRESS_THRESHOLD
    heat_stress = field.temperature > HEAT_STRESS_TEMP_C
    nitrogen_deficiency = field.nitrogen_level is not None and field.nitrogen_level < NITROGEN_DEFICIENCY_THRESHOLD
    pest_risk = "medium" if (field.ndvi < NDVI_PEST_THRESHOLD and field.growth_stage in _VEGETATIVE_STAGES) else "low"
    growth_stage_appropriate = (field.growth_stage in _VEGETATIVE_STAGES and field.ndvi > NDVI_HEALTHY_VEGETATIVE) or (
        field.growth_stage == "maturity" and field.ndvi < NDVI_MATURITY_LOW
    )
    critical_ndvi = field.ndvi < NDVI_CRITICAL_THRESHOLD

    return DerivedSignals(
        water_stress=water_stress,
        heat_stress=heat_stress,
        nitrogen_deficiency=nitrogen_deficiency,
        pest_risk=pest_risk,
        growth_stage_appropriate=growth_stage_appropriate,
        critical_ndvi=critical_ndvi,
    )


def compute_risk_score(signals: DerivedSignals, field: FieldContext) -> float:
    """Composite risk score in [0, 1]."""
    score = 0.0
    if signals.water_stress:
        score += 0.30
    if signals.heat_stress:
        score += 0.20
    if signals.nitrogen_deficiency:
        score += 0.25
    if signals.pest_risk == "medium":
        score += 0.10
    elif signals.pest_risk == "high":
        score += 0.25
    if not signals.growth_stage_appropriate:
        score += 0.15
    if signals.critical_ndvi:
        score += 0.20
    # Sandy soils amplify stress because they retain less water.
    if field.soil_texture == "sandy":
        score *= 1.2
    return min(score, 1.0)
