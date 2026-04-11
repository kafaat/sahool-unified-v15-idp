"""
Unit tests for the Phase 3 RUSLE erosion engine.

The engine is a pure calculation — no DB, no HTTP, no file I/O — so
the tests can pin every factor, every risk band, and every Yemeni
highland scenario against hand-computed expected values.

Test groups:

1. **Factor calculators** — R, K, LS, C, P in isolation
2. **Full assessment** — assess() on representative fields
3. **Risk classification** — FAO band boundaries
4. **Recommendations** — bilingual, targeted, escalate on severity
5. **Yemeni highland bench-terrace scenario** — the real-world case
   the engine was built to address
6. **Defensive edge cases** — zero rainfall, missing inputs, etc.
"""

from __future__ import annotations

import importlib.util
import os
import sys

import pytest


def _load_by_path(name: str, path: str):
    """Load a module by absolute path without polluting sys.path."""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_rusle_mod = _load_by_path(
    "phase3_rusle_engine",
    os.path.join(_REPO_ROOT, "shared", "terrain_erosion", "rusle.py"),
)

RUSLEEngine = _rusle_mod.RUSLEEngine
RUSLEFactors = _rusle_mod.RUSLEFactors
RUSLEResult = _rusle_mod.RUSLEResult
ErosionRiskLevel = _rusle_mod.ErosionRiskLevel
SoilTextureClass = _rusle_mod.SoilTextureClass


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def engine() -> RUSLEEngine:
    return RUSLEEngine()


# ---------------------------------------------------------------------------
# R-factor — rainfall erosivity
# ---------------------------------------------------------------------------


def test_r_factor_zero_rainfall_returns_zero(engine: RUSLEEngine):
    assert engine.compute_r_factor(0.0, 0) == 0.0
    assert engine.compute_r_factor(100.0, 0) == 0.0
    assert engine.compute_r_factor(0.0, 30) == 0.0


def test_r_factor_increases_monotonically_with_rainfall(engine: RUSLEEngine):
    low = engine.compute_r_factor(100.0, 30)
    mid = engine.compute_r_factor(500.0, 30)
    high = engine.compute_r_factor(1000.0, 30)
    assert 0 < low < mid < high


def test_r_factor_more_rainy_days_gives_higher_value(engine: RUSLEEngine):
    # Same total rainfall, more rainy days → fewer erosive bursts — but
    # the formula multiplies by (0.5 + 0.5 * days_factor), so more days
    # actually INCREASES R up to the 60-day cap. This encodes "more
    # rainy days → more erosion hours". Let's confirm the monotonicity.
    low_days = engine.compute_r_factor(300.0, 10)
    high_days = engine.compute_r_factor(300.0, 60)
    assert low_days < high_days


def test_r_factor_arid_yemeni_highlands(engine: RUSLEEngine):
    """
    Yemen highland averages: ~200 mm/yr rainfall, ~30 rainy days.
    Expected R should be in the low hundreds (arid baseline).
    """
    r = engine.compute_r_factor(200.0, 30)
    assert 300 < r < 1000  # arid-ish range


# ---------------------------------------------------------------------------
# K-factor — soil erodibility lookup
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "texture,expected_range",
    [
        (SoilTextureClass.SAND, (0.01, 0.05)),  # very coarse → low erodibility
        (SoilTextureClass.LOAMY_SAND, (0.04, 0.08)),
        (SoilTextureClass.SANDY_LOAM, (0.10, 0.20)),
        (SoilTextureClass.LOAM, (0.25, 0.35)),
        (SoilTextureClass.SILT_LOAM, (0.35, 0.45)),  # highest — Yemeni terraced soil
        (SoilTextureClass.CLAY_LOAM, (0.25, 0.35)),
        (SoilTextureClass.CLAY, (0.18, 0.28)),  # cohesive → moderate
    ],
)
def test_k_factor_lookup_matches_nrcs_ranges(
    engine: RUSLEEngine, texture: SoilTextureClass, expected_range: tuple
):
    k = engine.compute_k_factor(texture)
    lo, hi = expected_range
    assert lo <= k <= hi, f"{texture} K={k} not in {expected_range}"


def test_k_factor_silt_loam_is_most_erodible(engine: RUSLEEngine):
    """Silt loam is the USDA most-erodible class — must be max."""
    ks = {t: engine.compute_k_factor(t) for t in SoilTextureClass}
    assert max(ks, key=ks.get) == SoilTextureClass.SILT_LOAM


# ---------------------------------------------------------------------------
# LS-factor — slope length × steepness
# ---------------------------------------------------------------------------


def test_ls_factor_zero_slope_is_zero(engine: RUSLEEngine):
    assert engine.compute_ls_factor(0.0) == 0.0


def test_ls_factor_monotonic_in_slope(engine: RUSLEEngine):
    flat = engine.compute_ls_factor(0.5)
    gentle = engine.compute_ls_factor(5.0)
    steep = engine.compute_ls_factor(15.0)
    very_steep = engine.compute_ls_factor(40.0)
    assert flat < gentle < steep < very_steep


def test_ls_factor_default_slope_length_matches_rusle_reference(engine: RUSLEEngine):
    """
    At the RUSLE reference length (22.13 m) with 9% slope, the L
    component is exactly 1.0, so LS ≈ S alone. S(9%) ≈ 10.8·0.09 + 0.03
    in the gentler form OR ≈ 16.8·0.09 - 0.5 at the steeper form. The
    engine switches at slope=9.0, so 9% sits on the boundary and uses
    the steeper branch.
    """
    ls_at_9 = engine.compute_ls_factor(9.0)
    # 16.8 * 0.09 - 0.50 = 1.012 — (L=1 at reference length)
    assert 0.9 < ls_at_9 < 1.1


def test_ls_factor_custom_slope_length_grows_factor(engine: RUSLEEngine):
    short = engine.compute_ls_factor(10.0, slope_length_m=10.0)
    default = engine.compute_ls_factor(10.0)  # 22.13 m
    long = engine.compute_ls_factor(10.0, slope_length_m=100.0)
    assert short < default < long


def test_ls_factor_yemeni_terraced_slope_30pct(engine: RUSLEEngine):
    """Typical Yemeni terraced field slope 30% → severe LS."""
    ls = engine.compute_ls_factor(30.0)
    assert ls > 4.0  # severe LS regime


# ---------------------------------------------------------------------------
# C-factor — cover management
# ---------------------------------------------------------------------------


def test_c_factor_bare_soil_is_worst(engine: RUSLEEngine):
    bare = engine.compute_c_factor("bare_soil")
    wheat = engine.compute_c_factor("wheat")
    date_palm = engine.compute_c_factor("date_palm")
    forest = engine.compute_c_factor("forest")
    assert bare == 1.0
    assert forest < date_palm < wheat < bare


def test_c_factor_unknown_cover_falls_back(engine: RUSLEEngine):
    """Unknown cover type should default to a mid-range value, not crash."""
    unknown = engine.compute_c_factor("dragonfruit")
    assert 0.0 < unknown <= 1.0


def test_c_factor_case_insensitive(engine: RUSLEEngine):
    assert engine.compute_c_factor("WHEAT") == engine.compute_c_factor("wheat")


# ---------------------------------------------------------------------------
# P-factor — support practice
# ---------------------------------------------------------------------------


def test_p_factor_none_is_worst(engine: RUSLEEngine):
    none = engine.compute_p_factor("none")
    contour = engine.compute_p_factor("contour_farming")
    strip = engine.compute_p_factor("strip_cropping")
    terraces = engine.compute_p_factor("terraces")
    bench = engine.compute_p_factor("bench_terraces")
    assert bench < terraces < strip < contour < none
    assert bench == 0.10  # Yemeni highland target


def test_p_factor_unknown_defaults_to_worst(engine: RUSLEEngine):
    assert engine.compute_p_factor("laser_grading_3000") == 1.0


# ---------------------------------------------------------------------------
# Risk classification — FAO bands
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "soil_loss,expected_level",
    [
        (0.5, ErosionRiskLevel.NONE),
        (1.9, ErosionRiskLevel.NONE),
        (2.0, ErosionRiskLevel.LOW),
        (4.9, ErosionRiskLevel.LOW),
        (5.0, ErosionRiskLevel.MODERATE),
        (9.9, ErosionRiskLevel.MODERATE),
        (10.0, ErosionRiskLevel.HIGH),
        (19.9, ErosionRiskLevel.HIGH),
        (20.0, ErosionRiskLevel.SEVERE),
        (39.9, ErosionRiskLevel.SEVERE),
        (40.0, ErosionRiskLevel.CATASTROPHIC),
        (200.0, ErosionRiskLevel.CATASTROPHIC),
    ],
)
def test_classify_risk_fao_bands(soil_loss, expected_level):
    assert RUSLEEngine._classify_risk(soil_loss) == expected_level


# ---------------------------------------------------------------------------
# Full assessment — realistic scenarios
# ---------------------------------------------------------------------------


def test_assess_flat_forested_is_none_risk(engine: RUSLEEngine):
    """Flat forested field — should be 'none' risk regardless of rainfall."""
    result = engine.assess(
        field_id="flat_forest",
        tenant_id="t-1",
        slope_pct=0.5,
        soil_texture=SoilTextureClass.LOAM,
        annual_rainfall_mm=800,
        rainy_days_per_year=80,
        cover_type="forest",
        conservation_practice="none",
    )
    assert result.risk_level == ErosionRiskLevel.NONE
    assert result.soil_loss_t_ha_yr < 2.0
    # Forest + no slope → no mitigation needed
    assert any("safe" in r.lower() or "continue" in r.lower() for r in result.recommendations)


def test_assess_yemeni_highland_bench_terrace_scenario(engine: RUSLEEngine):
    """
    Core scenario — a Yemeni highland field with:
      * 30% slope (typical terraced landscape)
      * silt-loam soil (highest K)
      * 200 mm/yr rainfall, 30 rainy days
      * wheat cover
      * bench terraces (P=0.10, Yemeni highland standard)

    Expected: bench terraces should keep the loss manageable despite the
    severe LS factor. Without them the same field would be catastrophic.
    """
    with_terraces = engine.assess(
        field_id="yemen_terrace",
        tenant_id="t-1",
        slope_pct=30.0,
        soil_texture=SoilTextureClass.SILT_LOAM,
        annual_rainfall_mm=200,
        rainy_days_per_year=30,
        cover_type="wheat",
        conservation_practice="bench_terraces",
    )
    without_terraces = engine.assess(
        field_id="yemen_terrace",
        tenant_id="t-1",
        slope_pct=30.0,
        soil_texture=SoilTextureClass.SILT_LOAM,
        annual_rainfall_mm=200,
        rainy_days_per_year=30,
        cover_type="wheat",
        conservation_practice="none",
    )
    # Bench terraces must cut soil loss by ~10x (P goes from 1.0 to 0.10)
    assert without_terraces.soil_loss_t_ha_yr == pytest.approx(
        with_terraces.soil_loss_t_ha_yr * 10, rel=0.01
    )
    # Without terraces should be severe or catastrophic
    assert without_terraces.risk_level in (
        ErosionRiskLevel.HIGH,
        ErosionRiskLevel.SEVERE,
        ErosionRiskLevel.CATASTROPHIC,
    )


def test_assess_bare_soil_no_cover_escalates_risk(engine: RUSLEEngine):
    """Bare soil should escalate the risk band compared to cropped soil."""
    bare = engine.assess(
        field_id="bare",
        tenant_id="t-1",
        slope_pct=10.0,
        soil_texture=SoilTextureClass.LOAM,
        annual_rainfall_mm=400,
        rainy_days_per_year=40,
        cover_type="bare_soil",
    )
    wheat = engine.assess(
        field_id="wheat",
        tenant_id="t-1",
        slope_pct=10.0,
        soil_texture=SoilTextureClass.LOAM,
        annual_rainfall_mm=400,
        rainy_days_per_year=40,
        cover_type="wheat",
    )
    # Bare soil has C=1.0 vs wheat C=0.38 → bare should be ~2.6x higher
    assert bare.soil_loss_t_ha_yr == pytest.approx(
        wheat.soil_loss_t_ha_yr * (1.0 / 0.38), rel=0.01
    )


def test_assess_contributions_sum_to_100_when_all_nonzero(engine: RUSLEEngine):
    result = engine.assess(
        field_id="nonzero",
        tenant_id="t-1",
        slope_pct=15.0,
        soil_texture=SoilTextureClass.LOAM,
        annual_rainfall_mm=300,
        rainy_days_per_year=40,
        cover_type="wheat",
        conservation_practice="contour_farming",
    )
    assert result.factor_contributions_pct
    total = sum(result.factor_contributions_pct.values())
    assert 99.0 < total < 101.0  # rounding tolerance


def test_assess_contributions_empty_when_any_factor_is_zero(engine: RUSLEEngine):
    """Flat field → LS=0 → contributions dict is empty (log undefined)."""
    result = engine.assess(
        field_id="flat",
        tenant_id="t-1",
        slope_pct=0.0,
        soil_texture=SoilTextureClass.LOAM,
        annual_rainfall_mm=500,
        rainy_days_per_year=50,
        cover_type="wheat",
    )
    assert result.factor_contributions_pct == {}


# ---------------------------------------------------------------------------
# Recommendations — bilingual, targeted
# ---------------------------------------------------------------------------


def test_recommendations_low_risk_is_reassuring(engine: RUSLEEngine):
    result = engine.assess(
        field_id="safe",
        tenant_id="t-1",
        slope_pct=2.0,
        soil_texture=SoilTextureClass.SAND,
        annual_rainfall_mm=100,
        rainy_days_per_year=20,
        cover_type="forest",
        conservation_practice="none",
    )
    assert result.risk_level in (ErosionRiskLevel.NONE, ErosionRiskLevel.LOW)
    assert len(result.recommendations) >= 1
    assert len(result.recommendations_ar) >= 1
    # Each EN recommendation has an AR counterpart
    assert len(result.recommendations) == len(result.recommendations_ar)


def test_recommendations_high_slope_suggests_bench_terraces(engine: RUSLEEngine):
    result = engine.assess(
        field_id="steep",
        tenant_id="t-1",
        slope_pct=25.0,
        soil_texture=SoilTextureClass.SILT_LOAM,
        annual_rainfall_mm=300,
        rainy_days_per_year=40,
        cover_type="bare_soil",
        conservation_practice="none",
    )
    en_joined = " ".join(result.recommendations).lower()
    ar_joined = " ".join(result.recommendations_ar)
    assert "bench terrace" in en_joined or "terrac" in en_joined
    assert "مصاطب" in ar_joined


def test_recommendations_bare_soil_suggests_cover_crop(engine: RUSLEEngine):
    result = engine.assess(
        field_id="bare",
        tenant_id="t-1",
        slope_pct=12.0,
        soil_texture=SoilTextureClass.LOAM,
        annual_rainfall_mm=400,
        rainy_days_per_year=40,
        cover_type="bare_soil",
        conservation_practice="none",
    )
    en_joined = " ".join(result.recommendations).lower()
    ar_joined = " ".join(result.recommendations_ar)
    assert "cover crop" in en_joined
    assert "محصول تغطية" in ar_joined


def test_recommendations_catastrophic_escalates_to_extension(engine: RUSLEEngine):
    result = engine.assess(
        field_id="disaster",
        tenant_id="t-1",
        slope_pct=50.0,
        soil_texture=SoilTextureClass.SILT_LOAM,
        annual_rainfall_mm=1000,
        rainy_days_per_year=80,
        cover_type="bare_soil",
        conservation_practice="none",
    )
    assert result.risk_level in (
        ErosionRiskLevel.SEVERE,
        ErosionRiskLevel.CATASTROPHIC,
    )
    en_joined = " ".join(result.recommendations).lower()
    assert "extension officer" in en_joined or "stop tillage" in en_joined
    ar_joined = " ".join(result.recommendations_ar)
    assert "أوقف الحرث" in ar_joined or "مرشد زراعي" in ar_joined


# ---------------------------------------------------------------------------
# Structural checks on the returned dataclass
# ---------------------------------------------------------------------------


def test_assess_returns_expected_shape(engine: RUSLEEngine):
    result = engine.assess(
        field_id="F-42",
        tenant_id="t-42",
        slope_pct=5.0,
        soil_texture=SoilTextureClass.LOAM,
        annual_rainfall_mm=200,
        rainy_days_per_year=25,
        cover_type="wheat",
    )
    assert result.field_id == "F-42"
    assert result.tenant_id == "t-42"
    assert result.soil_loss_t_ha_yr >= 0
    assert isinstance(result.risk_level, ErosionRiskLevel)
    assert result.risk_level_ar  # non-empty Arabic label
    assert isinstance(result.factors, RUSLEFactors)
    assert result.factors.r_factor > 0
    assert result.factors.k_factor > 0
    assert result.factors.ls_factor > 0
    assert result.factors.c_factor > 0
    assert result.factors.p_factor > 0
    # A = RKLSCP — verify the multiply() helper agrees with the stored value
    expected_product = (
        result.factors.r_factor
        * result.factors.k_factor
        * result.factors.ls_factor
        * result.factors.c_factor
        * result.factors.p_factor
    )
    assert result.soil_loss_t_ha_yr == pytest.approx(expected_product, abs=0.01)
