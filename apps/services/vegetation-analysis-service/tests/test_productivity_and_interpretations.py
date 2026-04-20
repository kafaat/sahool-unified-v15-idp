"""Regression tests for the productivity indices + dedicated
interpretations added on top of the residual-gaps PR.

Pins:
  * FPAR + fAPAR calculated correctly from NDVI, clipped to [0,1].
  * FPAR + fAPAR surfaced through ``calculate_all``.
  * 16 previously-generic interpretations now route to dedicated
    methods (CVI, MCARI, TCARI, SIPI, VARI, GLI, GRVI, MSAVI, OSAVI,
    ARVI, PRI, CRI, ARI, PSRI, REP, SOC).
  * FPAR/fAPAR interpretations return a bilingual status.
"""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# =============================================================================
# FPAR + fAPAR calculations
# =============================================================================


def test_fpar_from_ndvi_follows_myneni_linear_map():
    """FPAR ≈ 1.24 * NDVI - 0.168 (Myneni & Williams 1994 / MODIS MOD15A2H)."""
    from vegetation_indices import VegetationIndicesCalculator

    calc = VegetationIndicesCalculator()
    # NDVI=0.5 → FPAR ≈ 0.452
    assert abs(calc.fpar(0.5) - 0.452) < 0.01
    # NDVI=0.8 → FPAR ≈ 0.824
    assert abs(calc.fpar(0.8) - 0.824) < 0.01
    # Clipped to [0, 1]
    assert calc.fpar(-1.0) == 0.0
    assert calc.fpar(1.0) == 1.0


def test_fapar_from_ndvi_follows_esa_linear_map():
    """fAPAR ≈ 1.08 * NDVI - 0.10 (ESA SNAP BiophysicalOp convention)."""
    from vegetation_indices import VegetationIndicesCalculator

    calc = VegetationIndicesCalculator()
    # NDVI=0.5 → fAPAR ≈ 0.44
    assert abs(calc.fapar(0.5) - 0.44) < 0.01
    assert calc.fapar(-1.0) == 0.0
    # NDVI=1 → 1.08 - 0.10 = 0.98 (max physical output of the linear map)
    assert abs(calc.fapar(1.0) - 0.98) < 0.01


def test_calculate_all_includes_fpar_and_fapar():
    """Productivity proxies must appear on AllIndices — otherwise they
    don't reach the API response envelope."""
    from vegetation_indices import BandData, VegetationIndicesCalculator

    calc = VegetationIndicesCalculator()
    bands = BandData(
        B02_blue=0.05,
        B03_green=0.08,
        B04_red=0.07,
        B05_red_edge1=0.15,
        B06_red_edge2=0.22,
        B07_red_edge3=0.28,
        B08_nir=0.42,
        B8A_nir_narrow=0.40,
        B11_swir1=0.18,
        B12_swir2=0.12,
    )
    all_indices = calc.calculate_all(bands)
    assert all_indices.fpar is not None
    assert all_indices.fapar is not None
    assert 0 <= all_indices.fpar <= 1
    assert 0 <= all_indices.fapar <= 1


# =============================================================================
# Dedicated interpretations (the 16 that previously fell through to generic)
# =============================================================================


_DEDICATED = [
    # (index_name, value, expected_status_name)
    ("cvi", 12.0, "excellent"),
    ("cvi", 0.1, "critical"),
    ("mcari", 1.2, "excellent"),
    ("tcari", 0.9, "excellent"),
    ("sipi", 2.0, "critical"),  # >1.8 = stress (reverse scale)
    ("sipi", 1.0, "good"),
    ("pri", 0.08, "excellent"),
    ("pri", -0.1, "poor"),
    ("cri", 9.0, "poor"),  # high carotenoids = stress
    ("ari", 4.0, "critical"),  # high anthocyanin = stress
    ("psri", 0.3, "poor"),  # senescence
    ("rep", 732.0, "excellent"),
    ("rep", 712.0, "critical"),
    ("vari", 0.3, "excellent"),
    ("gli", 0.4, "excellent"),
    ("grvi", 0.2, "excellent"),
    ("grvi", -0.2, "critical"),
    ("msavi", 0.6, "excellent"),
    ("osavi", 0.6, "excellent"),
    ("arvi", 0.6, "excellent"),
    ("soc", 3.0, "excellent"),
    ("soc", 0.2, "critical"),
]


@pytest.mark.parametrize("index_name,value,expected_status", _DEDICATED)
def test_dedicated_interpretations_return_expected_status(index_name: str, value: float, expected_status: str):
    """Each previously-generic index now returns a specific status
    from its dedicated interpretation method (not HealthStatus fallback)."""
    from vegetation_indices import CropType, GrowthStage, IndexInterpreter

    interp = IndexInterpreter()
    result = interp.interpret_index(index_name, value, CropType.WHEAT, GrowthStage.VEGETATIVE)
    assert result.status.value == expected_status, (
        f"{index_name}={value} should be {expected_status}, got {result.status.value}"
    )


@pytest.mark.parametrize(
    "index_name,value",
    [
        ("cvi", 7.0),
        ("mcari", 0.6),
        ("tcari", 0.5),
        ("sipi", 1.2),
        ("pri", 0.02),
        ("cri", 3.0),
        ("ari", 1.0),
        ("psri", 0.05),
        ("rep", 728.0),
        ("vari", 0.1),
        ("gli", 0.2),
        ("grvi", 0.1),
        ("msavi", 0.4),
        ("osavi", 0.4),
        ("arvi", 0.4),
        ("soc", 2.0),
        ("fpar", 0.7),
        ("fapar", 0.6),
    ],
)
def test_dedicated_interpretations_return_bilingual_descriptions(index_name: str, value: float):
    """Every dedicated interpretation must populate BOTH description_ar
    and description_en — Arabic is required for farmer-facing output."""
    from vegetation_indices import CropType, GrowthStage, IndexInterpreter

    interp = IndexInterpreter()
    result = interp.interpret_index(index_name, value, CropType.WHEAT, GrowthStage.VEGETATIVE)
    assert result.description_ar, f"{index_name}: missing Arabic description"
    assert result.description_en, f"{index_name}: missing English description"
    # Confidence must be explicit (not the 0.6 fallback used by generic)
    assert result.confidence >= 0.65, f"{index_name}: suspiciously generic confidence"


def test_fpar_and_fapar_interpretations_return_specific_status():
    """FPAR/fAPAR route to ``_interpret_fpar`` — verify the dispatcher
    hooked them (not the generic fallback)."""
    from vegetation_indices import CropType, GrowthStage, IndexInterpreter

    interp = IndexInterpreter()
    for idx in ("fpar", "fapar"):
        r = interp.interpret_index(idx, 0.85, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert r.status.value == "excellent"
        # Must mention productivity in Arabic OR English
        combined = (r.description_ar + " " + r.description_en).lower()
        assert "productivity" in combined or "إنتاجية" in combined


# =============================================================================
# Industry-catalog completeness pin
# =============================================================================


def test_vegetation_index_enum_covers_industry_catalog():
    """The enum must still cover every major commercial-platform index
    after this PR — checks SAHOOL maintains coverage vs OneSoil/EOSDA/
    Sentera/Farmonaut/Planet NICFI baselines."""
    from vegetation_indices import VegetationIndex

    names = {v.value for v in VegetationIndex}
    must_have = {
        "ndvi",
        "ndre",
        "ndwi",
        "ndmi",
        "evi",
        "savi",
        "msavi",
        "lai",
        "gndvi",
        "nbr",
        "bsi",
        "ci_green",
        "ci_rededge",
        # Newly added productivity proxies
        "fpar",
        "fapar",
    }
    missing = must_have - names
    assert not missing, f"Industry-standard indices missing: {missing}"
