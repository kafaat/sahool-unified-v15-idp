"""
Combined water + wind erosion assessor.

RUSLE measures water erosion (dominant in the highland terraces);
RWEQ-lite measures wind erosion (dominant in the grain-producing
plains — Tihama, Marib, Al-Jawf, Hadramawt). A field can be safe on
one axis and catastrophic on the other — e.g. a flat Tihama sandy
loam with no standing stubble has ~zero water erosion but ~50 t/ha/yr
of wind erosion.

This module runs both engines and returns a unified assessment where
the overall risk is the **worst of the two** (not the sum, because
they operate on different time scales and physical processes). The
per-process breakdown is preserved so operators can see which
process dominates.

The module also provides **Yemen region presets** that pre-fill
sensible RWEQ inputs from `shared/yemen/climate.py` and
`shared/yemen/soils.py`, so an advisory-service caller only needs to
know the region name (e.g. ``"tihama"``) to get a complete
wind-erosion baseline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .rusle import ErosionRiskLevel, RUSLEEngine, RUSLEResult, SoilTextureClass
from .rweq import (
    ResidueState,
    RWEQEngine,
    RWEQResult,
    SurfaceRoughness,
)


# ---------------------------------------------------------------------------
# Combined result
# ---------------------------------------------------------------------------


class DominantProcess(StrEnum):
    """Which erosion process dominates the field's risk."""

    WATER = "water"  # RUSLE dominates
    WIND = "wind"  # RWEQ dominates
    BOTH = "both"  # both at the same level
    NONE = "none"  # neither has non-trivial erosion


@dataclass
class CombinedErosionResult:
    """
    Unified erosion assessment across water + wind processes.

    The ``overall_risk_level`` is the *worst* of the two individual
    assessments (the one with the highest FAO band). The
    ``dominant_process`` tells the operator which engine is driving
    the risk — this is the actionable signal:

      * ``water`` → use the RUSLE recommendations (bench terraces,
                    cover crops, contour farming, residue retention)
      * ``wind``  → use the RWEQ recommendations (standing stubble,
                    windbreaks, chisel-plough roughness, dust-event
                    scheduling, perennial conversion)

    Both sub-results are preserved (``water`` + ``wind``) so callers
    that care about the per-process breakdown can introspect them.
    """

    field_id: str
    tenant_id: str
    overall_risk_level: ErosionRiskLevel
    overall_risk_level_ar: str
    dominant_process: DominantProcess
    water: RUSLEResult
    wind: RWEQResult
    combined_recommendations: list[str] = field(default_factory=list)
    combined_recommendations_ar: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Yemen region presets
# ---------------------------------------------------------------------------


@dataclass
class YemenRegionPreset:
    """
    Sensible RWEQ defaults for a Yemen climate zone. Derived from
    ``shared/yemen/climate.py`` monthly data (picks the windiest
    month's wind speed as a conservative value) and
    ``shared/yemen/soils.py`` dominant texture profile.
    """

    zone: str
    name_en: str
    name_ar: str
    texture_key: str
    mean_wind_speed_ms: float  # conservatively = max monthly mean
    annual_rainfall_mm: float
    annual_et0_mm: float
    typical_field_length_m: float
    dominant_crops: list[str]


# Presets calibrated from the existing `shared/yemen/climate.py` +
# `shared/yemen/soils.py` datasets. Values are the *per-zone
# worst-case* wind speed (max monthly mean) because wind erosion is
# an event-driven process and farmers need to plan for the peak
# season, not the annual average.
YEMEN_REGION_PRESETS: dict[str, YemenRegionPreset] = {
    "tihama": YemenRegionPreset(
        zone="tihama",
        name_en="Tihama Coastal Plain",
        name_ar="سهل تهامة الساحلي",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=3.5,  # peak summer months
        annual_rainfall_mm=125,  # mid of 50-200 range
        annual_et0_mm=2280,  # ~6.25 × 365 days (peak)
        typical_field_length_m=300,  # long open fields
        dominant_crops=["sorghum", "millet", "sesame"],
    ),
    "eastern_plateau": YemenRegionPreset(
        zone="eastern_plateau",
        name_en="Eastern Plateau (Marib, Al-Jawf)",
        name_ar="الهضبة الشرقية (مأرب، الجوف)",
        texture_key="eastern_plateau_loam",
        mean_wind_speed_ms=3.5,  # peak summer months
        annual_rainfall_mm=100,  # semi-arid desert margin
        annual_et0_mm=2200,  # 5.0-7.5 mid-range
        typical_field_length_m=400,  # very long open fields
        dominant_crops=["sorghum", "millet", "alfalfa"],
    ),
    "hadhramaut": YemenRegionPreset(
        zone="hadhramaut",
        name_en="Wadi Hadhramaut",
        name_ar="وادي حضرموت",
        texture_key="hadhramaut_silt_loam",
        mean_wind_speed_ms=3.0,  # sheltered wadi, peak summer
        annual_rainfall_mm=65,  # extremely arid
        annual_et0_mm=2150,  # 5.0-7.0 mid-range
        typical_field_length_m=150,  # wadi-constrained, narrower
        dominant_crops=["date_palm", "sesame", "alfalfa"],
    ),
    "southern_coast": YemenRegionPreset(
        zone="southern_coast",
        name_en="Southern Coast (Aden, Lahj, Abyan)",
        name_ar="الساحل الجنوبي (عدن، لحج، أبين)",
        texture_key="abyan_delta",
        mean_wind_speed_ms=3.2,
        annual_rainfall_mm=120,
        annual_et0_mm=2300,
        typical_field_length_m=200,
        dominant_crops=["cotton", "sorghum", "sesame"],
    ),
    "highlands": YemenRegionPreset(
        zone="highlands",
        name_en="Central Highlands (Sana'a, Ibb, Taiz)",
        name_ar="المرتفعات الوسطى (صنعاء، إب، تعز)",
        texture_key="highland_clay_loam",
        mean_wind_speed_ms=2.5,  # lower than plains
        annual_rainfall_mm=500,
        annual_et0_mm=1700,
        typical_field_length_m=50,  # small terraced fields
        dominant_crops=["wheat", "barley", "qat", "coffee"],
    ),
}


def get_yemen_region_preset(zone: str) -> YemenRegionPreset | None:
    """Look up a Yemen region preset by zone key."""
    return YEMEN_REGION_PRESETS.get(zone.lower().replace("-", "_").replace(" ", "_"))


# ---------------------------------------------------------------------------
# Combined engine
# ---------------------------------------------------------------------------


# FAO band → ordinal for "which is worse?" comparison
_BAND_ORDER: dict[ErosionRiskLevel, int] = {
    ErosionRiskLevel.NONE: 0,
    ErosionRiskLevel.LOW: 1,
    ErosionRiskLevel.MODERATE: 2,
    ErosionRiskLevel.HIGH: 3,
    ErosionRiskLevel.SEVERE: 4,
    ErosionRiskLevel.CATASTROPHIC: 5,
}

_RISK_AR: dict[ErosionRiskLevel, str] = {
    ErosionRiskLevel.NONE: "لا يوجد خطر تعرية",
    ErosionRiskLevel.LOW: "خطر تعرية منخفض",
    ErosionRiskLevel.MODERATE: "خطر تعرية متوسط",
    ErosionRiskLevel.HIGH: "خطر تعرية مرتفع",
    ErosionRiskLevel.SEVERE: "خطر تعرية شديد",
    ErosionRiskLevel.CATASTROPHIC: "خطر تعرية كارثي",
}


class CombinedErosionEngine:
    """
    Runs both RUSLE (water) and RWEQ (wind) and returns a combined
    assessment. Use this from advisory-service / terrain-core wherever
    a per-field erosion risk is needed without making assumptions
    about which process dominates.
    """

    def __init__(self):
        self._rusle = RUSLEEngine()
        self._rweq = RWEQEngine()

    def assess(
        self,
        *,
        field_id: str,
        tenant_id: str,
        # Water erosion inputs (RUSLE)
        slope_pct: float,
        soil_texture: SoilTextureClass,
        annual_rainfall_mm: float,
        rainy_days_per_year: int,
        cover_type: str = "bare_soil",
        conservation_practice: str = "none",
        slope_length_m: float | None = None,
        # Wind erosion inputs (RWEQ)
        mean_wind_speed_ms: float,
        annual_et0_mm: float,
        texture_key: str | None = None,
        roughness: SurfaceRoughness = SurfaceRoughness.MEDIUM,
        residue_state: ResidueState = ResidueState.BARE,
        residue_cover_pct: float = 0.0,
        canopy_cover_pct: float = 0.0,
        unsheltered_length_m: float = 100.0,
    ) -> CombinedErosionResult:
        """
        Run both engines on the same field and return the combined
        result. ``texture_key`` defaults to the RUSLE ``soil_texture``
        value (so callers can pass a single class when using USDA
        textures); pass an explicit key for Yemen-specific profiles.
        """
        if texture_key is None:
            texture_key = soil_texture.value

        water = self._rusle.assess(
            field_id=field_id,
            tenant_id=tenant_id,
            slope_pct=slope_pct,
            soil_texture=soil_texture,
            annual_rainfall_mm=annual_rainfall_mm,
            rainy_days_per_year=rainy_days_per_year,
            cover_type=cover_type,
            conservation_practice=conservation_practice,
            slope_length_m=slope_length_m,
        )
        wind = self._rweq.assess(
            field_id=field_id,
            tenant_id=tenant_id,
            texture_key=texture_key,
            mean_wind_speed_ms=mean_wind_speed_ms,
            annual_rainfall_mm=annual_rainfall_mm,
            annual_et0_mm=annual_et0_mm,
            roughness=roughness,
            residue_state=residue_state,
            residue_cover_pct=residue_cover_pct,
            canopy_cover_pct=canopy_cover_pct,
            unsheltered_length_m=unsheltered_length_m,
        )

        # Determine overall risk — worst band wins
        water_ord = _BAND_ORDER[water.risk_level]
        wind_ord = _BAND_ORDER[wind.risk_level]
        if water_ord > wind_ord:
            overall = water.risk_level
            dominant = DominantProcess.WATER
        elif wind_ord > water_ord:
            overall = wind.risk_level
            dominant = DominantProcess.WIND
        else:
            overall = water.risk_level
            if overall == ErosionRiskLevel.NONE:
                dominant = DominantProcess.NONE
            else:
                dominant = DominantProcess.BOTH

        # Combined recommendations: dominant first, then the other
        # process's recs (even secondary process may have actionable
        # advice if it's above NONE/LOW).
        recs_en: list[str] = []
        recs_ar: list[str] = []
        if dominant == DominantProcess.WATER:
            recs_en.append(
                f"Water erosion is the dominant process on this field "
                f"({water.soil_loss_t_ha_yr:.1f} t/ha/yr vs "
                f"{wind.soil_loss_t_ha_yr:.1f} for wind). Primary actions:"
            )
            recs_ar.append(
                f"تعرية المياه هي العملية المسيطرة على هذا الحقل "
                f"({water.soil_loss_t_ha_yr:.1f} طن/هـ/سنة مقابل "
                f"{wind.soil_loss_t_ha_yr:.1f} للرياح). الإجراءات الأساسية:"
            )
            recs_en.extend(water.recommendations)
            recs_ar.extend(water.recommendations_ar)
            if wind_ord >= _BAND_ORDER[ErosionRiskLevel.LOW]:
                recs_en.append(
                    "Also keep an eye on wind erosion — secondary actions:"
                )
                recs_ar.append("راقب أيضاً تعرية الرياح — إجراءات ثانوية:")
                recs_en.extend(wind.recommendations)
                recs_ar.extend(wind.recommendations_ar)
        elif dominant == DominantProcess.WIND:
            recs_en.append(
                f"Wind erosion is the dominant process on this field "
                f"({wind.soil_loss_t_ha_yr:.1f} t/ha/yr vs "
                f"{water.soil_loss_t_ha_yr:.1f} for water). Primary actions:"
            )
            recs_ar.append(
                f"تعرية الرياح هي العملية المسيطرة على هذا الحقل "
                f"({wind.soil_loss_t_ha_yr:.1f} طن/هـ/سنة مقابل "
                f"{water.soil_loss_t_ha_yr:.1f} للمياه). الإجراءات الأساسية:"
            )
            recs_en.extend(wind.recommendations)
            recs_ar.extend(wind.recommendations_ar)
            if water_ord >= _BAND_ORDER[ErosionRiskLevel.LOW]:
                recs_en.append(
                    "Also keep an eye on water erosion — secondary actions:"
                )
                recs_ar.append("راقب أيضاً تعرية المياه — إجراءات ثانوية:")
                recs_en.extend(water.recommendations)
                recs_ar.extend(water.recommendations_ar)
        elif dominant == DominantProcess.BOTH:
            recs_en.append(
                f"Both water and wind erosion are active at the {overall.value} level. "
                f"Implement the full mitigation set:"
            )
            recs_ar.append(
                f"كلا تعريتي المياه والرياح نشطتان عند مستوى {_RISK_AR[overall]}. "
                f"نفّذ مجموعة التخفيف الكاملة:"
            )
            recs_en.extend(water.recommendations)
            recs_ar.extend(water.recommendations_ar)
            recs_en.extend(wind.recommendations)
            recs_ar.extend(wind.recommendations_ar)
        else:
            recs_en.append(
                "Both erosion processes are within safe bounds. Continue current practice."
            )
            recs_ar.append(
                "كلا عمليتي التعرية ضمن الحدود الآمنة. استمر في الممارسة الحالية."
            )

        return CombinedErosionResult(
            field_id=field_id,
            tenant_id=tenant_id,
            overall_risk_level=overall,
            overall_risk_level_ar=_RISK_AR[overall],
            dominant_process=dominant,
            water=water,
            wind=wind,
            combined_recommendations=recs_en,
            combined_recommendations_ar=recs_ar,
        )

    def assess_yemen_region(
        self,
        *,
        field_id: str,
        tenant_id: str,
        region: str,
        slope_pct: float = 1.0,
        soil_texture: SoilTextureClass | None = None,
        cover_type: str = "bare_soil",
        conservation_practice: str = "none",
        residue_state: ResidueState = ResidueState.BARE,
        residue_cover_pct: float = 0.0,
        canopy_cover_pct: float = 0.0,
    ) -> CombinedErosionResult:
        """
        Shortcut for Yemeni fields: look up the regional preset for
        climate + soil defaults, then run the combined assessment.
        Only the field-specific variables (slope, cover, residue) need
        to come from the caller — everything else is inferred.
        """
        preset = get_yemen_region_preset(region)
        if preset is None:
            raise ValueError(f"Unknown Yemen region: {region!r}")

        # Infer USDA soil texture from the Yemen profile if not given
        if soil_texture is None:
            _usda_map = {
                "tihama_sandy_loam": SoilTextureClass.SANDY_LOAM,
                "tihama_alluvial": SoilTextureClass.LOAM,
                "highland_clay_loam": SoilTextureClass.CLAY_LOAM,
                "highland_volcanic": SoilTextureClass.LOAM,
                "hadhramaut_silt_loam": SoilTextureClass.SILT_LOAM,
                "eastern_plateau_loam": SoilTextureClass.LOAM,
                "southern_coast_saline": SoilTextureClass.SAND,
                "abyan_delta": SoilTextureClass.CLAY_LOAM,
            }
            soil_texture = _usda_map.get(
                preset.texture_key, SoilTextureClass.LOAM
            )

        # Approximate rainy-days count from the monthly distribution
        rainy_days = max(15, int(preset.annual_rainfall_mm / 8))

        return self.assess(
            field_id=field_id,
            tenant_id=tenant_id,
            slope_pct=slope_pct,
            soil_texture=soil_texture,
            annual_rainfall_mm=preset.annual_rainfall_mm,
            rainy_days_per_year=rainy_days,
            cover_type=cover_type,
            conservation_practice=conservation_practice,
            mean_wind_speed_ms=preset.mean_wind_speed_ms,
            annual_et0_mm=preset.annual_et0_mm,
            texture_key=preset.texture_key,
            residue_state=residue_state,
            residue_cover_pct=residue_cover_pct,
            canopy_cover_pct=canopy_cover_pct,
            unsheltered_length_m=preset.typical_field_length_m,
        )
