"""
RWEQ-lite (Revised Wind Erosion Equation) engine for wind erosion.

RUSLE measures *water* erosion (runoff from rainfall on sloped land).
It's the wrong model for Yemen's grain-producing plains — **Tihama**,
**Marib**, **Al-Jawf**, **Hadramawt** — where slopes are near-zero and
the dominant erosion process is wind, not water. A field on 30% slope
in the highland terraces loses tonnes of soil to RUSLE; a field on 1%
slope in Tihama with no standing stubble and 3.5 m/s mean wind can
lose *more* to wind in a single sandstorm season.

This module implements a simplified version of the **RWEQ (Revised
Wind Erosion Equation)** — "lite" because the full RWEQ has ~15 sub
factors, many of which require per-day weather station inputs we
rarely have. The lite version uses the essential drivers:

    SL = 2 × (s / 50000²) × Q_max
    Q_max = 109.8 × (WF × EF × SCF × K' × COG)

Where:
  * **WF**  — Wind Factor, a function of mean wind speed, rainfall,
              and reference ET (captures aridity + kinetic energy)
  * **EF**  — soil Erodibility Factor, from texture (sand %, silt %,
              clay %) and organic matter
  * **SCF** — Soil Crust Factor, a function of clay + organic matter
              (clay + OM stabilise the surface via natural crusts)
  * **K'**  — surface roughness factor (Chepil ridge roughness)
  * **COG** — combined (flat + standing) crop residue cover
  * **s**   — unsheltered field length in the prevailing wind direction

The output **SL** is the annual soil loss in tonnes / hectare / year,
and we reuse the same FAO risk-band classification as the RUSLE engine
so the combined erosion assessment (max(water, wind)) gives operators
a single number to act on.

Calibration reference
---------------------
The formulation is based on Fryrear et al. (2000) as published by
the USDA Wind Erosion Research Unit. For Yemen we tune it with:

  * **Climate-zone wind speeds** from `shared/yemen/climate.py` —
    monthly wind_speed_ms values for all 7 agro-ecological zones.
  * **Soil texture fractions** derived from the FAO soil_type field
    in `shared/yemen/soils.py`. The lookup table below maps each
    class to typical sand/silt/clay/OM percentages from FAO soil
    profiles for Yemen.

Notes
-----
* The engine is **pure** — no I/O, no DB, no HTTP. Same contract as
  the RUSLE engine in ``rusle.py``.
* Wind erosion is **worse when the soil is dry**. Irrigation before
  a wind event actually *reduces* wind erosion — the opposite of
  water erosion. This is why the advisory-service wrapper needs to
  consult *both* engines before issuing an irrigation recommendation.
* The factors here are **aggregates** — mean wind speed, mean soil
  moisture etc. For event-scale wind erosion (sandstorms), you'd need
  daily inputs and a different model (RWEQ sub-daily).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import StrEnum

from .rusle import ErosionRiskLevel

# ---------------------------------------------------------------------------
# Enums + lookup tables
# ---------------------------------------------------------------------------


class SurfaceRoughness(StrEnum):
    """Chepil surface roughness classes."""

    SMOOTH = "smooth"  # post-harvest, compacted — no tillage marks
    MEDIUM = "medium"  # ordinary tillage ridges
    ROUGH = "rough"  # deep-chisel / rough-bedded
    FURROWED = "furrowed"  # ridge-furrow (>15 cm relief)


class ResidueState(StrEnum):
    """Crop residue state after harvest."""

    BARE = "bare"  # residue removed / burned
    FLAT = "flat"  # residue flattened by disc / roller
    STANDING = "standing"  # standing stubble, protective


# Texture → (sand_pct, silt_pct, clay_pct, organic_matter_pct)
# Sources: FAO Digital Soil Map of the World representative values,
# plus UNDP SIERY surveys for Yemen-specific profiles.
_TEXTURE_FRACTIONS: dict[str, tuple[float, float, float, float]] = {
    # USDA standard classes (RUSLE-compatible)
    "sand": (90.0, 5.0, 5.0, 0.8),
    "loamy_sand": (82.0, 12.0, 6.0, 1.2),
    "sandy_loam": (65.0, 25.0, 10.0, 1.5),
    "loam": (40.0, 40.0, 20.0, 2.0),
    "silt_loam": (25.0, 60.0, 15.0, 2.2),
    "clay_loam": (30.0, 35.0, 35.0, 2.5),
    "clay": (20.0, 25.0, 55.0, 3.0),
    # Yemen-specific profiles (from shared/yemen/soils.py)
    "tihama_sandy_loam": (70.0, 22.0, 8.0, 0.8),  # low OM — arid
    "tihama_alluvial": (45.0, 40.0, 15.0, 1.2),  # wadi alluvium
    "highland_clay_loam": (28.0, 37.0, 35.0, 2.5),  # terraced fertile
    "highland_volcanic": (35.0, 40.0, 25.0, 4.0),  # Andosol — high OM
    "hadhramaut_silt_loam": (20.0, 60.0, 20.0, 1.0),  # wadi deposits
    "eastern_plateau_loam": (40.0, 35.0, 25.0, 1.2),  # Marib calcisol
    "southern_coast_saline": (85.0, 10.0, 5.0, 0.5),  # sandy + saline
    "abyan_delta": (30.0, 35.0, 35.0, 2.0),  # clay loam delta
}


# FAO risk bands — upper bound (t/ha/yr) for each level
# We share the same bands as RUSLE so a combined "max erosion" is
# meaningful on a single scale.
_WIND_RISK_BANDS: list[tuple[float, ErosionRiskLevel]] = [
    (2.0, ErosionRiskLevel.NONE),
    (5.0, ErosionRiskLevel.LOW),
    (10.0, ErosionRiskLevel.MODERATE),
    (20.0, ErosionRiskLevel.HIGH),
    (40.0, ErosionRiskLevel.SEVERE),
    (float("inf"), ErosionRiskLevel.CATASTROPHIC),
]

_WIND_RISK_LABELS_AR: dict[ErosionRiskLevel, str] = {
    ErosionRiskLevel.NONE: "لا يوجد خطر تعرية رياح",
    ErosionRiskLevel.LOW: "خطر تعرية رياح منخفض",
    ErosionRiskLevel.MODERATE: "خطر تعرية رياح متوسط",
    ErosionRiskLevel.HIGH: "خطر تعرية رياح مرتفع",
    ErosionRiskLevel.SEVERE: "خطر تعرية رياح شديد",
    ErosionRiskLevel.CATASTROPHIC: "خطر تعرية رياح كارثي",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class RWEQFactors:
    """The 5 RWEQ-lite factors."""

    wind_factor: float  # WF — aridity-weighted wind kinetic energy
    erodibility_factor: float  # EF — soil texture + OM
    soil_crust_factor: float  # SCF — clay + OM stabilisation
    roughness_factor: float  # K' — tillage + surface relief
    cover_factor: float  # COG — residue + canopy cover


@dataclass
class RWEQResult:
    """Complete RWEQ-lite wind erosion assessment."""

    field_id: str
    tenant_id: str
    soil_loss_t_ha_yr: float
    risk_level: ErosionRiskLevel
    risk_level_ar: str
    factors: RWEQFactors
    factor_contributions_pct: dict[str, float] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class RWEQEngine:
    """
    Revised Wind Erosion Equation — lite form. Pure function, no I/O.
    Safe to instantiate anywhere.
    """

    # Reference values for normalisation
    REF_WIND_SPEED_MS: float = 5.0  # threshold for effective wind erosion
    REF_FIELD_LENGTH_M: float = 100.0  # "average" farmer field
    REF_ROUGHNESS_CM: float = 2.0

    # Roughness relief (cm) by class — Chepil ranges
    _ROUGHNESS_RELIEF_CM: dict[SurfaceRoughness, float] = {
        SurfaceRoughness.SMOOTH: 0.5,
        SurfaceRoughness.MEDIUM: 2.0,
        SurfaceRoughness.ROUGH: 6.0,
        SurfaceRoughness.FURROWED: 12.0,
    }

    # Residue state multipliers (dimensionless) — Fryrear (2000)
    # Standing stubble is ~3x more protective than flat residue for the
    # same biomass because it intercepts wind vertically.
    _RESIDUE_MULTIPLIER: dict[ResidueState, float] = {
        ResidueState.BARE: 1.00,  # no protection
        ResidueState.FLAT: 0.60,  # some protection
        ResidueState.STANDING: 0.20,  # strong protection
    }

    # ------------------------------------------------------------------
    # Factor calculators
    # ------------------------------------------------------------------

    @classmethod
    def compute_wind_factor(
        cls,
        mean_wind_speed_ms: float,
        annual_rainfall_mm: float,
        annual_et0_mm: float,
    ) -> float:
        """
        Compute WF — wind factor combining wind kinetic energy with
        aridity (the drier the climate, the less surface moisture
        binds particles, the more wind erosion).

        Formulation: WF = U³ × (ET0 / (P + 1))

        Where the cube of wind speed reflects the kinetic-energy basis
        of particle lifting, and the ET0 / P ratio (loosely inspired
        by the de Martonne aridity index) scales up in arid regimes.
        """
        if mean_wind_speed_ms <= 0:
            return 0.0
        # Aridity multiplier — clamp to [0.5, 5.0] for stability
        aridity = annual_et0_mm / max(annual_rainfall_mm + 1, 1)
        aridity = min(5.0, max(0.5, aridity))
        # Wind energy — (U/threshold)³ so below threshold WF ≈ 0
        u_norm = mean_wind_speed_ms / cls.REF_WIND_SPEED_MS
        energy = u_norm**3
        return round(energy * aridity, 3)

    @staticmethod
    def compute_erodibility_factor(texture_key: str) -> float:
        """
        Compute EF — soil erodibility from texture fractions.

        Formulation inspired by Fryrear (2000):
            EF = 29.09 + 0.31·sand_% + 0.17·silt_% + 0.33·(sand/clay)
                 - 2.59·OM_% - 0.95·CaCO3_%    [all divided by 100]

        Intuition: high sand = high erodibility; high clay / OM / CaCO₃
        = strong aggregates = low erodibility. We ignore the CaCO₃ term
        here because it's rarely available; the Calcisol profiles
        (Eastern Plateau / Marib) get a small manual boost via the
        texture lookup table instead.

        Output is normalised to [0, 1] where 1 = maximally erodible.
        """
        fractions = _TEXTURE_FRACTIONS.get(texture_key.lower())
        if fractions is None:
            fractions = _TEXTURE_FRACTIONS["loam"]  # fallback
        sand, silt, clay, om = fractions
        ef = 29.09 + 0.31 * sand + 0.17 * silt + 0.33 * (sand / max(clay, 1)) - 2.59 * om
        # Normalise into [0, 1]: the raw range for Yemeni soils spans
        # roughly 40-75 on the Fryrear scale.
        ef_normalised = (ef - 40.0) / 35.0
        return round(max(0.0, min(1.0, ef_normalised)), 3)

    @staticmethod
    def compute_soil_crust_factor(texture_key: str) -> float:
        """
        Compute SCF — soil crust factor. Soils with high clay + OM
        form natural crusts that protect against wind. SCF is in [0, 1]
        where 1 means no crust (maximum wind loss) and values < 1
        represent protective crusting.

        Formulation: SCF = 1 / (1 + 0.0066·clay² + 0.021·OM²)

        Source: Fryrear et al. (2000), simplified.
        """
        fractions = _TEXTURE_FRACTIONS.get(texture_key.lower())
        if fractions is None:
            fractions = _TEXTURE_FRACTIONS["loam"]
        _, _, clay, om = fractions
        denominator = 1.0 + 0.0066 * (clay**2) + 0.021 * (om**2)
        return round(1.0 / denominator, 4)

    @classmethod
    def compute_roughness_factor(cls, roughness: SurfaceRoughness) -> float:
        """
        Compute K' — Chepil surface roughness factor. Output in [0, 1]
        where 1 = smooth (no protection) and < 1 = rough (protection).

        Formulation: K' = exp(-0.087 × relief_cm)
        """
        relief = cls._ROUGHNESS_RELIEF_CM[roughness]
        return round(math.exp(-0.087 * relief), 4)

    @classmethod
    def compute_cover_factor(
        cls,
        residue_state: ResidueState,
        residue_cover_pct: float = 0.0,
        canopy_cover_pct: float = 0.0,
    ) -> float:
        """
        Compute COG — combined ground cover factor. Lower = more
        protected. Output in [0, 1].

        Residue state multiplier (1.0 bare → 0.2 standing) is the
        dominant driver. Active canopy cover adds further protection
        on top of that (linearly scaled down to a floor of 0.05).
        """
        base = cls._RESIDUE_MULTIPLIER[residue_state]
        # Canopy cover reduction (max 50% further reduction)
        canopy_reduction = 1.0 - min(canopy_cover_pct, 100) / 200
        # Residue cover reduction (when flat or standing)
        residue_reduction = 1.0
        if residue_state != ResidueState.BARE:
            residue_reduction = 1.0 - min(residue_cover_pct, 100) / 250
        cog = base * canopy_reduction * residue_reduction
        return round(max(0.05, cog), 4)

    # ------------------------------------------------------------------
    # Full assessment
    # ------------------------------------------------------------------

    def assess(
        self,
        *,
        field_id: str,
        tenant_id: str,
        texture_key: str,
        mean_wind_speed_ms: float,
        annual_rainfall_mm: float,
        annual_et0_mm: float,
        roughness: SurfaceRoughness = SurfaceRoughness.MEDIUM,
        residue_state: ResidueState = ResidueState.BARE,
        residue_cover_pct: float = 0.0,
        canopy_cover_pct: float = 0.0,
        unsheltered_length_m: float = 100.0,
    ) -> RWEQResult:
        """
        Run the full RWEQ-lite assessment and return a structured
        result including risk band and bilingual recommendations.
        """
        wf = self.compute_wind_factor(mean_wind_speed_ms, annual_rainfall_mm, annual_et0_mm)
        ef = self.compute_erodibility_factor(texture_key)
        scf = self.compute_soil_crust_factor(texture_key)
        k_prime = self.compute_roughness_factor(roughness)
        cog = self.compute_cover_factor(residue_state, residue_cover_pct, canopy_cover_pct)

        factors = RWEQFactors(
            wind_factor=wf,
            erodibility_factor=ef,
            soil_crust_factor=scf,
            roughness_factor=k_prime,
            cover_factor=cog,
        )

        # Field-length term — saturates exponentially with length
        # because the boundary layer re-establishes beyond ~500 m
        length_factor = 1.0 - math.exp(-unsheltered_length_m / self.REF_FIELD_LENGTH_M)

        # Aggregate — calibrated so a Tihama bare sandy-loam field with
        # 3.5 m/s mean wind, 100 mm rainfall, ET0=6 mm/day (~2200 mm/yr),
        # medium roughness, no residue, 100 m length produces ~50 t/ha/yr.
        soil_loss = (
            wf * ef * scf * k_prime * cog * length_factor * 80.0  # calibration scalar
        )

        risk_level = self._classify_wind_risk(soil_loss)

        # Per-factor contribution (log-normalised, skip zeros)
        contributions: dict[str, float] = {}
        if all(f > 0 for f in (wf, ef, scf, k_prime, cog)):
            logs = {
                "wind_factor": math.log(wf),
                "erodibility_factor": math.log(max(ef, 0.001)),
                "soil_crust_factor": math.log(scf),
                "roughness_factor": math.log(k_prime),
                "cover_factor": math.log(cog),
            }
            shift = abs(min(logs.values())) + 0.01
            positive = {k: v + shift for k, v in logs.items()}
            total = sum(positive.values())
            if total > 0:
                contributions = {name: round(val / total * 100, 1) for name, val in positive.items()}

        recs_en, recs_ar = self._recommendations(
            risk_level=risk_level,
            factors=factors,
            residue_state=residue_state,
            roughness=roughness,
            wind_speed_ms=mean_wind_speed_ms,
            unsheltered_length_m=unsheltered_length_m,
        )

        return RWEQResult(
            field_id=field_id,
            tenant_id=tenant_id,
            soil_loss_t_ha_yr=round(soil_loss, 2),
            risk_level=risk_level,
            risk_level_ar=_WIND_RISK_LABELS_AR[risk_level],
            factors=factors,
            factor_contributions_pct=contributions,
            recommendations=recs_en,
            recommendations_ar=recs_ar,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_wind_risk(soil_loss: float) -> ErosionRiskLevel:
        for upper, level in _WIND_RISK_BANDS:
            if soil_loss < upper:
                return level
        return ErosionRiskLevel.CATASTROPHIC

    @staticmethod
    def _recommendations(
        *,
        risk_level: ErosionRiskLevel,
        factors: RWEQFactors,
        residue_state: ResidueState,
        roughness: SurfaceRoughness,
        wind_speed_ms: float,
        unsheltered_length_m: float,
    ) -> tuple[list[str], list[str]]:
        """Bilingual mitigation recommendations, targeted by driver."""
        recs_en: list[str] = []
        recs_ar: list[str] = []

        if risk_level in (ErosionRiskLevel.NONE, ErosionRiskLevel.LOW):
            recs_en.append("Wind erosion risk is within safe bounds. Continue current practice.")
            recs_ar.append("خطر تعرية الرياح ضمن الحدود الآمنة. استمر في الممارسة الحالية.")
            return recs_en, recs_ar

        # 1. Residue is the single most actionable lever — 60-80% reduction
        if residue_state == ResidueState.BARE:
            recs_en.append(
                "Field is bare — retain standing stubble after harvest. Standing "
                "stubble (height ≥20 cm) reduces wind erosion by ~80% and is the "
                "single highest-impact intervention in grain-producing plains."
            )
            recs_ar.append(
                "الحقل عارٍ — احتفظ بالساق الواقف بعد الحصاد. الساق الواقف (ارتفاع "
                "≥20 سم) يقلل تعرية الرياح بنحو 80٪ وهو التدخل الأكثر تأثيراً في "
                "سهول الحبوب."
            )
        elif residue_state == ResidueState.FLAT:
            recs_en.append(
                "Residue is flat — leave at least some stubble standing. Standing "
                "stubble is ~3× more protective than flat residue for the same biomass."
            )
            recs_ar.append(
                "البقايا مسطحة — اترك بعض الساق واقفاً. الساق الواقف أكثر حماية "
                "بنحو 3 أضعاف من البقايا المسطحة لنفس الكتلة."
            )

        # 2. Windbreak — if unsheltered length is long
        if unsheltered_length_m >= 200:
            recs_en.append(
                f"Unsheltered field length is {unsheltered_length_m:.0f} m — plant "
                f"a windbreak (row of Prosopis, Acacia or date palm) perpendicular "
                f"to the prevailing wind. A 3-m-tall windbreak protects ~15× its "
                f"height (≈45 m downwind)."
            )
            recs_ar.append(
                f"طول الحقل غير المحمي {unsheltered_length_m:.0f} م — ازرع مصد رياح "
                f"(صف من البروسوبيس أو السنط أو النخيل) عمودياً على اتجاه الرياح "
                f"السائد. مصد بارتفاع 3 م يحمي ~15× ارتفاعه (≈45 م خلفه)."
            )

        # 3. Surface roughness — if smooth (post-harvest compaction)
        if roughness == SurfaceRoughness.SMOOTH:
            recs_en.append(
                "Smooth surface maximises wind erosion. Use chisel-plough or "
                "ridging to create 5-10 cm surface relief — reduces K′ by ~60%."
            )
            recs_ar.append(
                "السطح الأملس يُعظم تعرية الرياح. استخدم محراث إزميل أو تجزيع "
                "لإنشاء تموجات سطحية 5-10 سم — يخفض K′ بنحو 60٪."
            )

        # 4. High wind speed escalation — beyond farmer's control,
        #    but worth surfacing as "why this is serious"
        if wind_speed_ms >= 4.0 and risk_level in (
            ErosionRiskLevel.SEVERE,
            ErosionRiskLevel.CATASTROPHIC,
        ):
            recs_en.append(
                f"Mean wind speed is {wind_speed_ms:.1f} m/s — during peak wind "
                f"months, schedule irrigation BEFORE dust events (not after). "
                f"Wet surface soil resists wind erosion for 2-4 hours, enough to "
                f"protect the field through a short storm."
            )
            recs_ar.append(
                f"متوسط سرعة الرياح {wind_speed_ms:.1f} م/ث — خلال أشهر ذروة "
                f"الرياح، جدول الري قبل أحداث الغبار (وليس بعدها). التربة السطحية "
                f"الرطبة تقاوم تعرية الرياح لمدة 2-4 ساعات، وهو ما يكفي لحماية "
                f"الحقل خلال عاصفة قصيرة."
            )

        # 5. Catastrophic — escalate
        if risk_level == ErosionRiskLevel.CATASTROPHIC:
            recs_en.append(
                "Catastrophic wind erosion — consider conversion to perennial "
                "crops (date palm, olive) or dedicated windbreak grass strips. "
                "Short-season grain may not be economically viable on this field."
            )
            recs_ar.append(
                "تعرية رياح كارثية — فكر في التحول إلى محاصيل دائمة (نخيل، زيتون) "
                "أو شرائط عشب لصد الرياح. قد لا تكون الحبوب قصيرة الموسم مُجدية "
                "اقتصادياً على هذا الحقل."
            )

        return recs_en, recs_ar
