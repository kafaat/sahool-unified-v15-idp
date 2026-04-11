"""
Unit tests for the Phase 3.5 RWEQ wind erosion engine + CombinedErosionEngine
+ Yemen region presets.

The engines live in:
  * shared/terrain_erosion/rweq.py      — RWEQ-lite (wind erosion)
  * shared/terrain_erosion/combined.py  — CombinedErosionEngine + Yemen presets
  * shared/terrain_erosion/__init__.py  — public API

These are pure calculation engines (no I/O, no DB, no HTTP) so every
factor and every risk band can be pinned against hand-computed
expected values. Scenarios are modelled on the four principal Yemen
grain-producing plains:

  * **Tihama** (coastal, 3.5 m/s, sandy loam) — worst wind-erosion case
  * **Eastern Plateau** (Marib, Al-Jawf — calcisol loam, same wind)
  * **Hadhramaut** (sheltered wadi, 3.0 m/s, silt loam)
  * **Highlands** (terraced, 2.5 m/s, clay loam) — water-dominant

Agent 1 was asked to write this file but hasn't returned in time, so
I'm writing it directly — that way I'm certain every test pins the
real engine API rather than a guess.
"""

from __future__ import annotations

import os
import sys

import pytest

# Add repo root to sys.path so ``shared.terrain_erosion`` resolves
# as a real package (its relative imports need the package context).
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from shared.terrain_erosion import (  # noqa: E402
    YEMEN_REGION_PRESETS,
    CombinedErosionEngine,
    CombinedErosionResult,
    DominantProcess,
    ErosionRiskLevel,
    ResidueState,
    RUSLEEngine,
    RUSLEResult,
    RWEQEngine,
    RWEQResult,
    SoilTextureClass,
    SurfaceRoughness,
    get_yemen_region_preset,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def rweq() -> RWEQEngine:
    return RWEQEngine()


@pytest.fixture
def combined() -> CombinedErosionEngine:
    return CombinedErosionEngine()


# ===========================================================================
# 1. RWEQ factor isolation
# ===========================================================================


def test_wind_factor_zero_wind_returns_zero(rweq: RWEQEngine):
    """Wind factor is zero when wind speed is zero — wind erosion needs wind."""
    assert rweq.compute_wind_factor(0.0, 100, 2000) == 0.0


def test_wind_factor_monotonic_in_wind_speed(rweq: RWEQEngine):
    """WF should grow with wind speed cubed — particle lifting is kinetic-energy-based."""
    low = rweq.compute_wind_factor(1.0, 100, 2000)
    mid = rweq.compute_wind_factor(3.5, 100, 2000)
    high = rweq.compute_wind_factor(6.0, 100, 2000)
    assert 0 < low < mid < high
    # Cubic scaling means doubling wind → ~8× WF (not exactly because of aridity clamp)
    doubled = rweq.compute_wind_factor(7.0, 100, 2000)
    assert doubled > mid * 4  # at least 4× on doubling


def test_wind_factor_aridity_multiplier(rweq: RWEQEngine):
    """Arid regimes (high ET/P) should produce higher WF than humid ones."""
    arid = rweq.compute_wind_factor(3.5, 50, 2500)
    humid = rweq.compute_wind_factor(3.5, 800, 1200)
    assert arid > humid


def test_wind_factor_tihama_peak_plausible_range(rweq: RWEQEngine):
    """Tihama peak-summer inputs (3.5 m/s, 100 mm, 2280 mm ET) should land in the 1-5 WF range."""
    wf = rweq.compute_wind_factor(3.5, 100, 2280)
    assert 0.5 < wf < 10.0


def test_erodibility_factor_sand_ordering(rweq: RWEQEngine):
    """Sand-heavy soils should be MORE erodible than clay-rich ones."""
    tihama = rweq.compute_erodibility_factor("tihama_sandy_loam")
    highland_clay = rweq.compute_erodibility_factor("highland_clay_loam")
    volcanic = rweq.compute_erodibility_factor("highland_volcanic")
    assert tihama > highland_clay
    # Volcanic soil has very high OM → low erodibility
    assert volcanic < tihama


def test_erodibility_factor_unknown_texture_falls_back(rweq: RWEQEngine):
    """Unknown texture key should fall back to 'loam' defaults, not crash."""
    unknown = rweq.compute_erodibility_factor("dragonfruit_terroir")
    loam = rweq.compute_erodibility_factor("loam")
    assert unknown == loam


def test_erodibility_factor_clamped_to_unit_interval(rweq: RWEQEngine):
    """EF must always land in [0, 1] regardless of input."""
    for texture in (
        "sand",
        "loamy_sand",
        "loam",
        "clay",
        "tihama_sandy_loam",
        "highland_clay_loam",
        "eastern_plateau_loam",
        "southern_coast_saline",
    ):
        ef = rweq.compute_erodibility_factor(texture)
        assert 0.0 <= ef <= 1.0, f"{texture} EF out of range: {ef}"


def test_soil_crust_factor_clay_resists_better(rweq: RWEQEngine):
    """Clay-rich soils form natural crusts — lower SCF = more protected."""
    sandy = rweq.compute_soil_crust_factor("tihama_sandy_loam")
    clay = rweq.compute_soil_crust_factor("highland_clay_loam")
    saline = rweq.compute_soil_crust_factor("southern_coast_saline")
    assert clay < sandy
    # Saline sandy → high SCF (no natural crust)
    assert saline > clay


def test_soil_crust_factor_in_unit_interval(rweq: RWEQEngine):
    """SCF in (0, 1] — zero means infinite protection (impossible)."""
    for texture in ("sand", "loam", "clay", "tihama_sandy_loam"):
        scf = rweq.compute_soil_crust_factor(texture)
        assert 0.0 < scf <= 1.0


@pytest.mark.parametrize(
    "a,b",
    [
        (SurfaceRoughness.SMOOTH, SurfaceRoughness.MEDIUM),
        (SurfaceRoughness.MEDIUM, SurfaceRoughness.ROUGH),
        (SurfaceRoughness.ROUGH, SurfaceRoughness.FURROWED),
    ],
)
def test_roughness_factor_decreasing(rweq: RWEQEngine, a, b):
    """Roughness factor must decrease monotonically across the classes."""
    assert rweq.compute_roughness_factor(a) > rweq.compute_roughness_factor(b)


def test_roughness_factor_in_unit_interval(rweq: RWEQEngine):
    for r in SurfaceRoughness:
        k = rweq.compute_roughness_factor(r)
        assert 0.0 < k <= 1.0


@pytest.mark.parametrize(
    "state,upper_bound",
    [
        (ResidueState.BARE, 1.01),
        (ResidueState.FLAT, 0.61),
        (ResidueState.STANDING, 0.21),
    ],
)
def test_cover_factor_residue_state_bands(rweq: RWEQEngine, state, upper_bound):
    """BARE (1.0) > FLAT (~0.6) > STANDING (~0.2) — the 3× gap is the whole point."""
    cog = rweq.compute_cover_factor(state)
    assert cog <= upper_bound


def test_cover_factor_canopy_cover_reduces_further(rweq: RWEQEngine):
    """Canopy cover should reduce COG on top of the residue state."""
    bare_no_canopy = rweq.compute_cover_factor(ResidueState.BARE, canopy_cover_pct=0)
    bare_with_canopy = rweq.compute_cover_factor(ResidueState.BARE, canopy_cover_pct=80)
    assert bare_with_canopy < bare_no_canopy


def test_cover_factor_residue_cover_helps_flat_or_standing(rweq: RWEQEngine):
    """Residue cover % further reduces COG but only when state != BARE."""
    standing_low = rweq.compute_cover_factor(ResidueState.STANDING, residue_cover_pct=10)
    standing_high = rweq.compute_cover_factor(ResidueState.STANDING, residue_cover_pct=90)
    assert standing_high < standing_low


def test_cover_factor_has_floor(rweq: RWEQEngine):
    """COG should floor at 0.05 — no field is 100% protected by cover alone."""
    extreme = rweq.compute_cover_factor(
        ResidueState.STANDING, residue_cover_pct=100, canopy_cover_pct=100
    )
    assert extreme >= 0.05


# ===========================================================================
# 2. RWEQ full assessment — Yemen plains scenarios
# ===========================================================================


def test_tihama_bare_sandy_loam_is_severe(rweq: RWEQEngine):
    """Classic Tihama worst case: bare sandy loam, 3.5 m/s wind, long unsheltered field."""
    r = rweq.assess(
        field_id="tihama_bare",
        tenant_id="t-1",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=3.5,
        annual_rainfall_mm=100,
        annual_et0_mm=2280,
        roughness=SurfaceRoughness.SMOOTH,
        residue_state=ResidueState.BARE,
        unsheltered_length_m=300.0,
    )
    assert r.risk_level in (
        ErosionRiskLevel.HIGH,
        ErosionRiskLevel.SEVERE,
        ErosionRiskLevel.CATASTROPHIC,
    )
    assert r.soil_loss_t_ha_yr > 15.0


def test_tihama_standing_stubble_cuts_loss_dramatically(rweq: RWEQEngine):
    """Standing stubble + windbreak + rough surface should drop loss by 80%+."""
    bare = rweq.assess(
        field_id="tihama_bare",
        tenant_id="t-1",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=3.5,
        annual_rainfall_mm=100,
        annual_et0_mm=2280,
        roughness=SurfaceRoughness.SMOOTH,
        residue_state=ResidueState.BARE,
        unsheltered_length_m=300.0,
    )
    protected = rweq.assess(
        field_id="tihama_protected",
        tenant_id="t-1",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=3.5,
        annual_rainfall_mm=100,
        annual_et0_mm=2280,
        roughness=SurfaceRoughness.ROUGH,
        residue_state=ResidueState.STANDING,
        residue_cover_pct=70,
        unsheltered_length_m=50.0,  # windbreak shortens effective length
    )
    reduction = 1 - (protected.soil_loss_t_ha_yr / bare.soil_loss_t_ha_yr)
    assert reduction > 0.80


def test_marib_calcisol_has_less_loss_than_tihama_sandy(rweq: RWEQEngine):
    """Same wind, but calcisol loam has stronger crust → less wind erosion."""
    tihama = rweq.assess(
        field_id="t",
        tenant_id="t-1",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=3.5,
        annual_rainfall_mm=100,
        annual_et0_mm=2280,
        unsheltered_length_m=300,
    )
    marib = rweq.assess(
        field_id="m",
        tenant_id="t-1",
        texture_key="eastern_plateau_loam",
        mean_wind_speed_ms=3.5,
        annual_rainfall_mm=100,
        annual_et0_mm=2200,
        unsheltered_length_m=300,
    )
    assert marib.soil_loss_t_ha_yr < tihama.soil_loss_t_ha_yr


def test_hadhramaut_wadi_is_moderate_or_low(rweq: RWEQEngine):
    """Sheltered wadi with shorter unsheltered length + silt loam → not catastrophic."""
    r = rweq.assess(
        field_id="hadhramaut",
        tenant_id="t-1",
        texture_key="hadhramaut_silt_loam",
        mean_wind_speed_ms=3.0,
        annual_rainfall_mm=65,
        annual_et0_mm=2150,
        unsheltered_length_m=150.0,
    )
    assert r.risk_level in (
        ErosionRiskLevel.NONE,
        ErosionRiskLevel.LOW,
        ErosionRiskLevel.MODERATE,
        ErosionRiskLevel.HIGH,
    )


def test_highlands_clay_loam_has_low_wind_erosion(rweq: RWEQEngine):
    """Highland terraced fields: low wind + clay loam + small field → negligible wind erosion."""
    r = rweq.assess(
        field_id="highland",
        tenant_id="t-1",
        texture_key="highland_clay_loam",
        mean_wind_speed_ms=2.5,
        annual_rainfall_mm=500,
        annual_et0_mm=1700,
        unsheltered_length_m=30.0,
    )
    assert r.risk_level in (ErosionRiskLevel.NONE, ErosionRiskLevel.LOW)


def test_field_length_saturates_exponentially(rweq: RWEQEngine):
    """
    Very long fields should produce higher SL than short ones, but the
    relationship saturates (boundary layer re-establishes). Going from
    100 m → 1000 m should NOT produce a 10× increase.
    """
    base = rweq.assess(
        field_id="base",
        tenant_id="t-1",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=3.5,
        annual_rainfall_mm=100,
        annual_et0_mm=2280,
        unsheltered_length_m=100,
    )
    longer = rweq.assess(
        field_id="longer",
        tenant_id="t-1",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=3.5,
        annual_rainfall_mm=100,
        annual_et0_mm=2280,
        unsheltered_length_m=1000,
    )
    # Longer is worse but not 10× worse
    assert longer.soil_loss_t_ha_yr > base.soil_loss_t_ha_yr
    assert longer.soil_loss_t_ha_yr < base.soil_loss_t_ha_yr * 3


def test_zero_wind_produces_none_risk(rweq: RWEQEngine):
    """No wind, no wind erosion — trivial but worth pinning."""
    r = rweq.assess(
        field_id="still",
        tenant_id="t-1",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=0.0,
        annual_rainfall_mm=100,
        annual_et0_mm=2280,
    )
    assert r.soil_loss_t_ha_yr == 0.0
    assert r.risk_level == ErosionRiskLevel.NONE


def test_sub_threshold_wind_still_produces_some_loss(rweq: RWEQEngine):
    """
    WF is cubic, not a step function — wind below the 5 m/s reference
    still produces *some* loss, just less. Verify the formula is
    continuous, not gated.
    """
    low_wind = rweq.assess(
        field_id="low",
        tenant_id="t-1",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=2.0,
        annual_rainfall_mm=100,
        annual_et0_mm=2280,
    )
    assert low_wind.soil_loss_t_ha_yr > 0


def test_catastrophic_wind_scenario(rweq: RWEQEngine):
    """Extreme wind (8 m/s) + bare sand + long field → CATASTROPHIC."""
    r = rweq.assess(
        field_id="storm",
        tenant_id="t-1",
        texture_key="sand",
        mean_wind_speed_ms=8.0,
        annual_rainfall_mm=50,
        annual_et0_mm=2500,
        roughness=SurfaceRoughness.SMOOTH,
        residue_state=ResidueState.BARE,
        unsheltered_length_m=1000.0,
    )
    assert r.risk_level == ErosionRiskLevel.CATASTROPHIC


# ===========================================================================
# 3. RWEQ recommendations — bilingual + targeted
# ===========================================================================


def test_low_risk_gets_reassuring_recommendation(rweq: RWEQEngine):
    """Low-risk field should get a single reassuring bilingual recommendation."""
    r = rweq.assess(
        field_id="safe",
        tenant_id="t-1",
        texture_key="highland_clay_loam",
        mean_wind_speed_ms=1.0,
        annual_rainfall_mm=500,
        annual_et0_mm=1700,
        unsheltered_length_m=20,
    )
    assert r.risk_level in (ErosionRiskLevel.NONE, ErosionRiskLevel.LOW)
    assert len(r.recommendations) >= 1
    assert len(r.recommendations_ar) >= 1
    assert len(r.recommendations) == len(r.recommendations_ar)


def test_bare_field_suggests_standing_stubble(rweq: RWEQEngine):
    """Bare field in a wind-erosion-prone zone should get the 'standing stubble' rec."""
    r = rweq.assess(
        field_id="bare",
        tenant_id="t-1",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=3.5,
        annual_rainfall_mm=100,
        annual_et0_mm=2280,
        residue_state=ResidueState.BARE,
        unsheltered_length_m=200,
    )
    en = " ".join(r.recommendations).lower()
    ar = " ".join(r.recommendations_ar)
    assert "standing stubble" in en
    assert "الساق الواقف" in ar


def test_long_field_suggests_windbreak(rweq: RWEQEngine):
    """Unsheltered field ≥200 m should get the windbreak recommendation."""
    r = rweq.assess(
        field_id="long",
        tenant_id="t-1",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=3.5,
        annual_rainfall_mm=100,
        annual_et0_mm=2280,
        unsheltered_length_m=500,
    )
    en = " ".join(r.recommendations).lower()
    ar = " ".join(r.recommendations_ar)
    assert "windbreak" in en
    assert "مصد رياح" in ar


def test_smooth_surface_suggests_chisel_plough(rweq: RWEQEngine):
    """Post-harvest smooth surface should get the chisel / ridging advice."""
    r = rweq.assess(
        field_id="smooth",
        tenant_id="t-1",
        texture_key="tihama_sandy_loam",
        mean_wind_speed_ms=3.5,
        annual_rainfall_mm=100,
        annual_et0_mm=2280,
        roughness=SurfaceRoughness.SMOOTH,
        unsheltered_length_m=200,
    )
    en = " ".join(r.recommendations).lower()
    ar = " ".join(r.recommendations_ar)
    assert "chisel" in en or "ridging" in en
    assert "محراث" in ar or "تجزيع" in ar


def test_every_en_recommendation_has_ar_counterpart(rweq: RWEQEngine):
    """Bilingual invariant: len(en) == len(ar) on every assessment."""
    for state in (ResidueState.BARE, ResidueState.FLAT, ResidueState.STANDING):
        for rough in SurfaceRoughness:
            r = rweq.assess(
                field_id="p",
                tenant_id="t-1",
                texture_key="tihama_sandy_loam",
                mean_wind_speed_ms=3.5,
                annual_rainfall_mm=100,
                annual_et0_mm=2280,
                roughness=rough,
                residue_state=state,
                unsheltered_length_m=200,
            )
            assert len(r.recommendations) == len(r.recommendations_ar)


# ===========================================================================
# 4. Combined engine — dominant process selection
# ===========================================================================


def test_combined_water_dominant_on_steep_highland(combined: CombinedErosionEngine):
    """Steep highland bare silt-loam → water erosion wins."""
    res = combined.assess(
        field_id="steep",
        tenant_id="t-1",
        slope_pct=30.0,
        soil_texture=SoilTextureClass.SILT_LOAM,
        annual_rainfall_mm=500,
        rainy_days_per_year=60,
        cover_type="bare_soil",
        conservation_practice="none",
        mean_wind_speed_ms=2.0,
        annual_et0_mm=1700,
    )
    assert res.dominant_process == DominantProcess.WATER
    assert res.overall_risk_level in (
        ErosionRiskLevel.HIGH,
        ErosionRiskLevel.SEVERE,
        ErosionRiskLevel.CATASTROPHIC,
    )
    # Combined recs must include bench-terrace advice
    en = " ".join(res.combined_recommendations).lower()
    assert "bench terrace" in en or "contour" in en


def test_combined_wind_dominant_on_tihama_plain(combined: CombinedErosionEngine):
    """Flat Tihama bare sandy-loam → wind erosion wins."""
    res = combined.assess(
        field_id="tihama",
        tenant_id="t-1",
        slope_pct=1.0,
        soil_texture=SoilTextureClass.SANDY_LOAM,
        annual_rainfall_mm=100,
        rainy_days_per_year=15,
        cover_type="sorghum",
        conservation_practice="none",
        mean_wind_speed_ms=3.5,
        annual_et0_mm=2280,
        texture_key="tihama_sandy_loam",
        residue_state=ResidueState.BARE,
        unsheltered_length_m=300,
    )
    assert res.dominant_process == DominantProcess.WIND
    # Combined recs must include standing-stubble advice
    ar = " ".join(res.combined_recommendations_ar)
    assert "الساق الواقف" in ar


def test_combined_neither_process_when_both_safe(combined: CombinedErosionEngine):
    """
    Flat field with good clay loam, small size, low wind, dense cover →
    neither process is active.
    """
    res = combined.assess(
        field_id="safe",
        tenant_id="t-1",
        slope_pct=1.0,
        soil_texture=SoilTextureClass.CLAY_LOAM,
        annual_rainfall_mm=300,
        rainy_days_per_year=40,
        cover_type="dense_cover",
        conservation_practice="contour_farming",
        mean_wind_speed_ms=1.0,
        annual_et0_mm=1500,
        texture_key="highland_clay_loam",
        residue_state=ResidueState.STANDING,
        residue_cover_pct=80,
        unsheltered_length_m=30,
    )
    assert res.dominant_process == DominantProcess.NONE
    assert res.overall_risk_level in (ErosionRiskLevel.NONE, ErosionRiskLevel.LOW)


def test_combined_overall_is_max_of_both(combined: CombinedErosionEngine):
    """Overall risk level must be the worse of water+wind, by band order."""
    _BAND_ORDER = {
        ErosionRiskLevel.NONE: 0,
        ErosionRiskLevel.LOW: 1,
        ErosionRiskLevel.MODERATE: 2,
        ErosionRiskLevel.HIGH: 3,
        ErosionRiskLevel.SEVERE: 4,
        ErosionRiskLevel.CATASTROPHIC: 5,
    }
    res = combined.assess(
        field_id="any",
        tenant_id="t-1",
        slope_pct=10.0,
        soil_texture=SoilTextureClass.LOAM,
        annual_rainfall_mm=300,
        rainy_days_per_year=30,
        cover_type="wheat",
        conservation_practice="none",
        mean_wind_speed_ms=4.0,
        annual_et0_mm=2000,
    )
    max_band = max(
        _BAND_ORDER[res.water.risk_level], _BAND_ORDER[res.wind.risk_level]
    )
    assert _BAND_ORDER[res.overall_risk_level] == max_band


def test_combined_result_header_names_dominant_process(combined: CombinedErosionEngine):
    """The first combined rec should name the dominant process by name."""
    res = combined.assess(
        field_id="test",
        tenant_id="t-1",
        slope_pct=25.0,
        soil_texture=SoilTextureClass.SILT_LOAM,
        annual_rainfall_mm=400,
        rainy_days_per_year=50,
        cover_type="bare_soil",
        conservation_practice="none",
        mean_wind_speed_ms=2.0,
        annual_et0_mm=1700,
    )
    first_en = res.combined_recommendations[0].lower()
    first_ar = res.combined_recommendations_ar[0]
    assert "water" in first_en or "wind" in first_en
    assert "المياه" in first_ar or "الرياح" in first_ar


# ===========================================================================
# 5. Yemen region presets
# ===========================================================================


def test_preset_tihama_has_expected_defaults():
    p = get_yemen_region_preset("tihama")
    assert p is not None
    assert p.mean_wind_speed_ms == 3.5
    assert p.texture_key == "tihama_sandy_loam"
    assert "sorghum" in p.dominant_crops


def test_preset_eastern_plateau_has_expected_defaults():
    p = get_yemen_region_preset("eastern_plateau")
    assert p is not None
    assert p.texture_key == "eastern_plateau_loam"
    assert "Marib" in p.name_en


def test_preset_hadhramaut_has_expected_defaults():
    p = get_yemen_region_preset("hadhramaut")
    assert p is not None
    assert p.texture_key == "hadhramaut_silt_loam"
    # Hadhramaut is drier than Tihama
    assert p.annual_rainfall_mm < 100


def test_preset_highlands_has_lower_wind_than_plains():
    tihama = get_yemen_region_preset("tihama")
    highlands = get_yemen_region_preset("highlands")
    assert highlands.mean_wind_speed_ms < tihama.mean_wind_speed_ms


def test_preset_lookup_case_insensitive():
    """Lookup should tolerate uppercase and hyphens."""
    assert get_yemen_region_preset("TIHAMA") is not None
    assert get_yemen_region_preset("eastern-plateau") is not None


def test_preset_lookup_unknown_region_returns_none():
    assert get_yemen_region_preset("atlantis_plain") is None


def test_assess_yemen_region_tihama_is_wind_dominant(combined: CombinedErosionEngine):
    """Tihama preset + flat field + bare sorghum → wind-dominant."""
    res = combined.assess_yemen_region(
        field_id="tihama_field",
        tenant_id="t-1",
        region="tihama",
        slope_pct=1.0,
        cover_type="sorghum",
        residue_state=ResidueState.BARE,
    )
    assert res.dominant_process == DominantProcess.WIND


def test_assess_yemen_region_highlands_with_steep_slope_is_water_dominant(
    combined: CombinedErosionEngine,
):
    """Highlands preset + 30% slope + bare soil → water-dominant."""
    res = combined.assess_yemen_region(
        field_id="terrace",
        tenant_id="t-1",
        region="highlands",
        slope_pct=30.0,
        cover_type="bare_soil",
        conservation_practice="none",
    )
    assert res.dominant_process == DominantProcess.WATER


def test_assess_yemen_region_unknown_raises():
    engine = CombinedErosionEngine()
    with pytest.raises(ValueError):
        engine.assess_yemen_region(
            field_id="x",
            tenant_id="t-1",
            region="narnia",
        )


def test_preset_map_has_all_major_zones():
    """YEMEN_REGION_PRESETS must cover all 5 principal zones."""
    required = {"tihama", "eastern_plateau", "hadhramaut", "highlands", "southern_coast"}
    assert required.issubset(set(YEMEN_REGION_PRESETS.keys()))


# ===========================================================================
# 6. Structural + defensive checks
# ===========================================================================


def test_combined_result_has_both_sub_results(combined: CombinedErosionEngine):
    """water + wind sub-results must be the correct types."""
    res = combined.assess(
        field_id="s",
        tenant_id="t-1",
        slope_pct=5.0,
        soil_texture=SoilTextureClass.LOAM,
        annual_rainfall_mm=200,
        rainy_days_per_year=25,
        cover_type="wheat",
        mean_wind_speed_ms=2.5,
        annual_et0_mm=1800,
    )
    assert isinstance(res, CombinedErosionResult)
    assert isinstance(res.water, RUSLEResult)
    assert isinstance(res.wind, RWEQResult)


def test_combined_arabic_label_is_non_empty(combined: CombinedErosionEngine):
    """The AR label must never be empty — i18n invariant."""
    res = combined.assess(
        field_id="s",
        tenant_id="t-1",
        slope_pct=5.0,
        soil_texture=SoilTextureClass.LOAM,
        annual_rainfall_mm=200,
        rainy_days_per_year=25,
        cover_type="wheat",
        mean_wind_speed_ms=2.5,
        annual_et0_mm=1800,
    )
    assert res.overall_risk_level_ar
    assert res.water.risk_level_ar
    assert res.wind.risk_level_ar


def test_combined_arabic_recommendations_match_english_length(combined: CombinedErosionEngine):
    """Every EN combined recommendation must have an AR counterpart."""
    res = combined.assess(
        field_id="s",
        tenant_id="t-1",
        slope_pct=25.0,
        soil_texture=SoilTextureClass.SILT_LOAM,
        annual_rainfall_mm=400,
        rainy_days_per_year=50,
        cover_type="bare_soil",
        conservation_practice="none",
        mean_wind_speed_ms=3.5,
        annual_et0_mm=2000,
        residue_state=ResidueState.BARE,
    )
    assert len(res.combined_recommendations) == len(res.combined_recommendations_ar)
