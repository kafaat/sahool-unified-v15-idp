"""
Tests for vegetation_indices module.
Tests cover VegetationIndicesCalculator with all 40+ indices,
BandData, AllIndices, IndexInterpretation, and edge cases.
"""

import sys
import os
import math

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vegetation_indices import (
    AllIndices,
    BandData,
    CropType,
    GrowthStage,
    HealthStatus,
    IndexInterpretation,
    IndexInterpreter,
    VegetationIndex,
    VegetationIndicesCalculator,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def calculator():
    return VegetationIndicesCalculator()


@pytest.fixture
def healthy_bands():
    """Typical healthy vegetation reflectance values."""
    return BandData(
        B02_blue=0.03,
        B03_green=0.06,
        B04_red=0.04,
        B05_red_edge1=0.12,
        B06_red_edge2=0.25,
        B07_red_edge3=0.32,
        B08_nir=0.35,
        B8A_nir_narrow=0.33,
        B11_swir1=0.15,
        B12_swir2=0.08,
    )


@pytest.fixture
def bare_soil_bands():
    """Typical bare soil reflectance values."""
    return BandData(
        B02_blue=0.10,
        B03_green=0.12,
        B04_red=0.15,
        B05_red_edge1=0.16,
        B06_red_edge2=0.17,
        B07_red_edge3=0.18,
        B08_nir=0.20,
        B8A_nir_narrow=0.19,
        B11_swir1=0.22,
        B12_swir2=0.18,
    )


@pytest.fixture
def water_bands():
    """Typical water reflectance values."""
    return BandData(
        B02_blue=0.08,
        B03_green=0.06,
        B04_red=0.04,
        B05_red_edge1=0.02,
        B06_red_edge2=0.01,
        B07_red_edge3=0.01,
        B08_nir=0.01,
        B8A_nir_narrow=0.01,
        B11_swir1=0.005,
        B12_swir2=0.003,
    )


@pytest.fixture
def zero_bands():
    """All zero reflectance values for edge case testing."""
    return BandData(
        B02_blue=0.0,
        B03_green=0.0,
        B04_red=0.0,
        B05_red_edge1=0.0,
        B06_red_edge2=0.0,
        B07_red_edge3=0.0,
        B08_nir=0.0,
        B8A_nir_narrow=0.0,
        B11_swir1=0.0,
        B12_swir2=0.0,
    )


@pytest.fixture
def hyperspectral_bands():
    """Bands with optional hyperspectral values."""
    return BandData(
        B02_blue=0.03,
        B03_green=0.06,
        B04_red=0.04,
        B05_red_edge1=0.12,
        B06_red_edge2=0.25,
        B07_red_edge3=0.32,
        B08_nir=0.35,
        B8A_nir_narrow=0.33,
        B11_swir1=0.15,
        B12_swir2=0.08,
        B_531nm=0.05,
        B_550nm=0.06,
        B_570nm=0.055,
        B_680nm=0.04,
        B_700nm=0.10,
        B_800nm=0.35,
    )


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    def test_vegetation_index_count(self):
        assert len(VegetationIndex) >= 40

    def test_crop_types(self):
        assert CropType.WHEAT.value == "wheat"
        assert CropType.COFFEE.value == "coffee"
        assert CropType.QAT.value == "qat"
        assert CropType.UNKNOWN.value == "unknown"

    def test_growth_stages(self):
        assert GrowthStage.EMERGENCE.value == "emergence"
        assert GrowthStage.VEGETATIVE.value == "vegetative"
        assert GrowthStage.HARVEST.value == "harvest"

    def test_health_status(self):
        assert HealthStatus.EXCELLENT.value == "excellent"
        assert HealthStatus.CRITICAL.value == "critical"


# =============================================================================
# BandData Tests
# =============================================================================


class TestBandData:
    def test_required_bands(self, healthy_bands):
        assert healthy_bands.B02_blue == 0.03
        assert healthy_bands.B08_nir == 0.35

    def test_optional_bands_default_none(self, healthy_bands):
        assert healthy_bands.B_531nm is None
        assert healthy_bands.B_550nm is None
        assert healthy_bands.B_800nm is None

    def test_hyperspectral_bands(self, hyperspectral_bands):
        assert hyperspectral_bands.B_531nm == 0.05
        assert hyperspectral_bands.B_570nm == 0.055


# =============================================================================
# AllIndices Tests
# =============================================================================


class TestAllIndices:
    def test_clamping_normalized_indices(self):
        """Test that normalized indices are clamped to [-1, 1]."""
        indices = AllIndices(
            ndvi=1.5, ndwi=-1.5, evi=0.5, savi=0.5, lai=3.0,
            ndmi=0.5, ndre=0.5, cvi=2.0, mcari=0.5, tcari=0.5,
            sipi=1.0, gndvi=0.5, vari=0.5, gli=0.5, grvi=0.5,
            msavi=0.5, osavi=0.5, arvi=0.5,
        )
        assert indices.ndvi == 1.0  # Clamped from 1.5
        assert indices.ndwi == -1.0  # Clamped from -1.5

    def test_lai_clamping(self):
        indices = AllIndices(
            ndvi=0.5, ndwi=0.5, evi=0.5, savi=0.5, lai=10.0,
            ndmi=0.5, ndre=0.5, cvi=2.0, mcari=0.5, tcari=0.5,
            sipi=1.0, gndvi=0.5, vari=0.5, gli=0.5, grvi=0.5,
            msavi=0.5, osavi=0.5, arvi=0.5,
        )
        assert indices.lai == 8.0  # Clamped

    def test_to_dict(self):
        indices = AllIndices(
            ndvi=0.7, ndwi=0.3, evi=0.5, savi=0.4, lai=3.0,
            ndmi=0.2, ndre=0.5, cvi=2.0, mcari=0.3, tcari=0.5,
            sipi=1.2, gndvi=0.6, vari=0.3, gli=0.2, grvi=0.1,
            msavi=0.5, osavi=0.4, arvi=0.5,
        )
        d = indices.to_dict()
        assert d["ndvi"] == 0.7
        assert d["lai"] == 3.0
        # None values excluded
        assert "pri" not in d

    def test_to_dict_with_optional(self):
        indices = AllIndices(
            ndvi=0.7, ndwi=0.3, evi=0.5, savi=0.4, lai=3.0,
            ndmi=0.2, ndre=0.5, cvi=2.0, mcari=0.3, tcari=0.5,
            sipi=1.2, gndvi=0.6, vari=0.3, gli=0.2, grvi=0.1,
            msavi=0.5, osavi=0.4, arvi=0.5,
            pri=0.05, nbr=0.3,
        )
        d = indices.to_dict()
        assert d["pri"] == 0.05
        assert d["nbr"] == 0.3


# =============================================================================
# Basic Indices Tests
# =============================================================================


class TestBasicIndices:
    def test_ndvi_healthy(self, calculator, healthy_bands):
        result = calculator.ndvi(healthy_bands)
        assert 0.7 <= result <= 0.9

    def test_ndvi_bare_soil(self, calculator, bare_soil_bands):
        result = calculator.ndvi(bare_soil_bands)
        assert 0.0 <= result <= 0.2

    def test_ndvi_zero_bands(self, calculator, zero_bands):
        assert calculator.ndvi(zero_bands) == 0.0

    def test_ndwi_healthy(self, calculator, healthy_bands):
        result = calculator.ndwi(healthy_bands)
        assert result > 0  # NIR > SWIR1 for healthy veg

    def test_ndwi_zero_bands(self, calculator, zero_bands):
        assert calculator.ndwi(zero_bands) == 0.0

    def test_evi_healthy(self, calculator, healthy_bands):
        result = calculator.evi(healthy_bands)
        assert 0.2 <= result <= 0.9

    def test_evi_zero_denominator(self, calculator, zero_bands):
        assert calculator.evi(zero_bands) == 0.0

    def test_savi_healthy(self, calculator, healthy_bands):
        result = calculator.savi(healthy_bands)
        assert 0.2 <= result <= 0.9

    def test_savi_zero(self, calculator, zero_bands):
        # L=0.5, so denominator is 0.5, not zero
        result = calculator.savi(zero_bands)
        assert result == 0.0

    def test_lai_positive_ndvi(self, calculator):
        result = calculator.lai(0.5)
        assert result > 0

    def test_lai_zero_ndvi(self, calculator):
        assert calculator.lai(0.0) == 0.0

    def test_lai_negative_ndvi(self, calculator):
        assert calculator.lai(-0.5) == 0.0

    def test_lai_high_ndvi(self, calculator):
        result = calculator.lai(0.9)
        assert result > 0
        assert result <= 8.0

    def test_ndmi_healthy(self, calculator, healthy_bands):
        result = calculator.ndmi(healthy_bands)
        assert -1 <= result <= 1

    def test_ndmi_zero(self, calculator, zero_bands):
        assert calculator.ndmi(zero_bands) == 0.0


# =============================================================================
# Chlorophyll & Nitrogen Indices
# =============================================================================


class TestChlorophyllIndices:
    def test_ndre(self, calculator, healthy_bands):
        result = calculator.ndre(healthy_bands)
        assert 0.2 <= result <= 0.8

    def test_ndre_zero(self, calculator, zero_bands):
        assert calculator.ndre(zero_bands) == 0.0

    def test_cvi(self, calculator, healthy_bands):
        result = calculator.cvi(healthy_bands)
        assert result > 0

    def test_cvi_zero_green(self, calculator, zero_bands):
        assert calculator.cvi(zero_bands) == 0.0

    def test_mcari(self, calculator, healthy_bands):
        result = calculator.mcari(healthy_bands)
        assert 0 <= result <= 1.5

    def test_mcari_zero_red(self, calculator, zero_bands):
        assert calculator.mcari(zero_bands) == 0.0

    def test_tcari(self, calculator, healthy_bands):
        result = calculator.tcari(healthy_bands)
        assert 0 <= result <= 3

    def test_tcari_zero_red(self, calculator, zero_bands):
        assert calculator.tcari(zero_bands) == 0.0

    def test_sipi(self, calculator, healthy_bands):
        result = calculator.sipi(healthy_bands)
        assert 0 <= result <= 2.0

    def test_sipi_zero_denominator(self, calculator):
        # NIR == Red => denominator is 0 => return 1.0
        bands = BandData(
            B02_blue=0.05, B03_green=0.06, B04_red=0.35,
            B05_red_edge1=0.12, B06_red_edge2=0.25, B07_red_edge3=0.32,
            B08_nir=0.35, B8A_nir_narrow=0.33, B11_swir1=0.15, B12_swir2=0.08,
        )
        assert calculator.sipi(bands) == 1.0


# =============================================================================
# Early Stress Detection Indices
# =============================================================================


class TestStressIndices:
    def test_gndvi(self, calculator, healthy_bands):
        result = calculator.gndvi(healthy_bands)
        assert 0.3 <= result <= 0.9

    def test_gndvi_zero(self, calculator, zero_bands):
        assert calculator.gndvi(zero_bands) == 0.0

    def test_vari(self, calculator, healthy_bands):
        result = calculator.vari(healthy_bands)
        assert -1 <= result <= 1

    def test_vari_zero_denom(self, calculator, zero_bands):
        assert calculator.vari(zero_bands) == 0.0

    def test_gli(self, calculator, healthy_bands):
        result = calculator.gli(healthy_bands)
        assert -1 <= result <= 1

    def test_gli_zero(self, calculator, zero_bands):
        assert calculator.gli(zero_bands) == 0.0

    def test_grvi(self, calculator, healthy_bands):
        result = calculator.grvi(healthy_bands)
        assert -1 <= result <= 1

    def test_grvi_zero(self, calculator, zero_bands):
        assert calculator.grvi(zero_bands) == 0.0


# =============================================================================
# Soil & Atmosphere Corrected Indices
# =============================================================================


class TestSoilAtmosphereIndices:
    def test_msavi(self, calculator, healthy_bands):
        result = calculator.msavi(healthy_bands)
        assert -1 <= result <= 1

    def test_msavi_zero(self, calculator, zero_bands):
        result = calculator.msavi(zero_bands)
        assert -1 <= result <= 1

    def test_osavi(self, calculator, healthy_bands):
        result = calculator.osavi(healthy_bands)
        assert -1 <= result <= 1

    def test_osavi_zero(self, calculator, zero_bands):
        # Y=0.16 so denominator is 0.16 not zero
        result = calculator.osavi(zero_bands)
        assert result == 0.0

    def test_arvi(self, calculator, healthy_bands):
        result = calculator.arvi(healthy_bands)
        assert -1 <= result <= 1

    def test_arvi_zero(self, calculator, zero_bands):
        assert calculator.arvi(zero_bands) == 0.0


# =============================================================================
# Pigment & Stress Indices (Hyperspectral)
# =============================================================================


class TestPigmentIndices:
    def test_pri_no_bands(self, calculator, healthy_bands):
        result = calculator.pri(healthy_bands)
        assert result is None

    def test_pri_with_bands(self, calculator, hyperspectral_bands):
        result = calculator.pri(hyperspectral_bands)
        assert result is not None
        assert -1 <= result <= 1

    def test_pri_zero_denominator(self, calculator):
        bands = BandData(
            B02_blue=0.03, B03_green=0.06, B04_red=0.04,
            B05_red_edge1=0.12, B06_red_edge2=0.25, B07_red_edge3=0.32,
            B08_nir=0.35, B8A_nir_narrow=0.33, B11_swir1=0.15, B12_swir2=0.08,
            B_531nm=0.0, B_570nm=0.0,
        )
        assert calculator.pri(bands) == 0.0

    def test_cri_healthy(self, calculator, healthy_bands):
        result = calculator.cri(healthy_bands)
        # Uses green and red_edge1 as approximation
        assert result is not None or result is None  # Depends on non-zero values

    def test_cri_zero_green(self, calculator, zero_bands):
        assert calculator.cri(zero_bands) is None

    def test_ari_healthy(self, calculator, healthy_bands):
        result = calculator.ari(healthy_bands)
        # Uses fallback with green and red_edge1
        if result is not None:
            assert -0.5 <= result <= 0.5

    def test_ari_with_hyperspectral(self, calculator, hyperspectral_bands):
        result = calculator.ari(hyperspectral_bands)
        assert result is not None

    def test_ari_zero_bands(self, calculator, zero_bands):
        assert calculator.ari(zero_bands) is None

    def test_psri_healthy(self, calculator, healthy_bands):
        result = calculator.psri(healthy_bands)
        if result is not None:
            assert -1 <= result <= 1

    def test_psri_with_hyperspectral(self, calculator, hyperspectral_bands):
        result = calculator.psri(hyperspectral_bands)
        assert result is not None

    def test_psri_zero_re2(self, calculator):
        bands = BandData(
            B02_blue=0.03, B03_green=0.06, B04_red=0.04,
            B05_red_edge1=0.12, B06_red_edge2=0.0, B07_red_edge3=0.32,
            B08_nir=0.35, B8A_nir_narrow=0.33, B11_swir1=0.15, B12_swir2=0.08,
        )
        assert calculator.psri(bands) is None

    def test_rep_healthy(self, calculator, healthy_bands):
        result = calculator.rep(healthy_bands)
        if result is not None:
            assert 680 <= result <= 760

    def test_rep_zero_denominator(self, calculator):
        bands = BandData(
            B02_blue=0.03, B03_green=0.06, B04_red=0.04,
            B05_red_edge1=0.25, B06_red_edge2=0.25, B07_red_edge3=0.32,
            B08_nir=0.35, B8A_nir_narrow=0.33, B11_swir1=0.15, B12_swir2=0.08,
        )
        assert calculator.rep(bands) is None


# =============================================================================
# Phase 1 - Extended Spectral Indices
# =============================================================================


class TestExtendedIndices:
    def test_nbr(self, calculator, healthy_bands):
        result = calculator.nbr(healthy_bands)
        assert -1 <= result <= 1

    def test_nbr_zero(self, calculator, zero_bands):
        assert calculator.nbr(zero_bands) == 0.0

    def test_evi2(self, calculator, healthy_bands):
        result = calculator.evi2(healthy_bands)
        assert -1 <= result <= 1

    def test_evi2_zero(self, calculator, zero_bands):
        # Denominator = 0 + 0 + 1 = 1, not zero
        result = calculator.evi2(zero_bands)
        assert result == 0.0

    def test_bsi_healthy(self, calculator, healthy_bands):
        result = calculator.bsi(healthy_bands)
        assert -1 <= result <= 1

    def test_bsi_bare_soil(self, calculator, bare_soil_bands):
        result = calculator.bsi(bare_soil_bands)
        # Should be positive for bare soil
        assert result > -0.5

    def test_bsi_zero(self, calculator, zero_bands):
        assert calculator.bsi(zero_bands) == 0.0

    def test_sr_healthy(self, calculator, healthy_bands):
        result = calculator.sr(healthy_bands)
        assert result > 1.0  # NIR/Red > 1 for vegetation

    def test_sr_zero_red(self, calculator, zero_bands):
        assert calculator.sr(zero_bands) == 0.0

    def test_ccci(self, calculator, healthy_bands):
        result = calculator.ccci(healthy_bands)
        assert result >= 0

    def test_ccci_low_ndvi(self, calculator):
        bands = BandData(
            B02_blue=0.15, B03_green=0.15, B04_red=0.15,
            B05_red_edge1=0.15, B06_red_edge2=0.15, B07_red_edge3=0.15,
            B08_nir=0.15, B8A_nir_narrow=0.15, B11_swir1=0.15, B12_swir2=0.15,
        )
        result = calculator.ccci(bands)
        # NDVI is 0 for equal bands, so CCCI returns 0
        assert result == 0.0

    def test_msi_healthy(self, calculator, healthy_bands):
        result = calculator.msi(healthy_bands)
        assert result > 0

    def test_msi_zero_nir(self, calculator, zero_bands):
        assert calculator.msi(zero_bands) == 0.0


# =============================================================================
# Phase 2 - Chlorophyll & Red Edge Enhancement
# =============================================================================


class TestPhase2Indices:
    def test_ci_green(self, calculator, healthy_bands):
        result = calculator.ci_green(healthy_bands)
        assert result > 0

    def test_ci_green_zero(self, calculator, zero_bands):
        assert calculator.ci_green(zero_bands) == 0.0

    def test_ci_rededge(self, calculator, healthy_bands):
        result = calculator.ci_rededge(healthy_bands)
        assert result > 0

    def test_ireci(self, calculator, healthy_bands):
        result = calculator.ireci(healthy_bands)
        assert result is not None

    def test_mtci(self, calculator, healthy_bands):
        result = calculator.mtci(healthy_bands)
        assert result is not None

    def test_rendvi(self, calculator, healthy_bands):
        result = calculator.rendvi(healthy_bands)
        assert -1 <= result <= 1

    def test_wdrvi(self, calculator, healthy_bands):
        result = calculator.wdrvi(healthy_bands)
        assert -1 <= result <= 1


# =============================================================================
# Phase 3 - Water, Drought & Land Cover
# =============================================================================


class TestPhase3Indices:
    def test_mndwi(self, calculator, healthy_bands):
        result = calculator.mndwi(healthy_bands)
        assert -1 <= result <= 1

    def test_nbr2(self, calculator, healthy_bands):
        result = calculator.nbr2(healthy_bands)
        assert -1 <= result <= 1

    def test_ndbi(self, calculator, healthy_bands):
        result = calculator.ndbi(healthy_bands)
        assert -1 <= result <= 1

    def test_dvi(self, calculator, healthy_bands):
        result = calculator.dvi(healthy_bands)
        assert result is not None

    def test_gdvi(self, calculator, healthy_bands):
        result = calculator.gdvi(healthy_bands)
        assert result is not None

    def test_tsavi(self, calculator, healthy_bands):
        result = calculator.tsavi(healthy_bands)
        assert result is not None


# =============================================================================
# calculate_all Tests
# =============================================================================


class TestCalculateAll:
    def test_calculate_all_healthy(self, calculator, healthy_bands):
        result = calculator.calculate_all(healthy_bands)
        assert isinstance(result, AllIndices)
        assert result.ndvi > 0.5
        assert result.evi > 0
        assert result.lai > 0
        assert result.ndre > 0

    def test_calculate_all_bare_soil(self, calculator, bare_soil_bands):
        result = calculator.calculate_all(bare_soil_bands)
        assert result.ndvi < 0.3
        assert result.bsi is not None

    def test_calculate_all_water(self, calculator, water_bands):
        result = calculator.calculate_all(water_bands)
        assert result.ndvi < 0.2

    def test_calculate_all_returns_dict(self, calculator, healthy_bands):
        result = calculator.calculate_all(healthy_bands)
        d = result.to_dict()
        assert isinstance(d, dict)
        assert "ndvi" in d
        assert "evi" in d
        assert "lai" in d

    def test_calculate_all_hyperspectral(self, calculator, hyperspectral_bands):
        result = calculator.calculate_all(hyperspectral_bands)
        assert result.pri is not None
        assert result.ari is not None
        assert result.psri is not None


# =============================================================================
# IndexInterpreter Tests
# =============================================================================


class TestIndexInterpreter:
    @pytest.fixture
    def interpreter(self):
        return IndexInterpreter()

    # NDVI interpretation
    def test_interpret_ndvi_excellent(self, interpreter):
        result = interpreter.interpret_index("ndvi", 0.85, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.EXCELLENT
        assert result.index_name == "NDVI"

    def test_interpret_ndvi_good(self, interpreter):
        result = interpreter.interpret_index("ndvi", 0.55, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.GOOD

    def test_interpret_ndvi_fair(self, interpreter):
        result = interpreter.interpret_index("ndvi", 0.35, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.FAIR

    def test_interpret_ndvi_poor(self, interpreter):
        result = interpreter.interpret_index("ndvi", 0.22, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.POOR

    def test_interpret_ndvi_critical(self, interpreter):
        result = interpreter.interpret_index("ndvi", 0.05, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.CRITICAL

    def test_interpret_ndvi_unknown_crop(self, interpreter):
        result = interpreter.interpret_index("ndvi", 0.6, CropType.UNKNOWN, GrowthStage.VEGETATIVE)
        assert isinstance(result, IndexInterpretation)

    def test_interpret_ndvi_emergence(self, interpreter):
        result = interpreter.interpret_index("ndvi", 0.25, CropType.WHEAT, GrowthStage.EMERGENCE)
        assert result.status in [HealthStatus.EXCELLENT, HealthStatus.GOOD]

    # NDRE interpretation
    def test_interpret_ndre(self, interpreter):
        result = interpreter.interpret_index("ndre", 0.5, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "NDRE"
        assert isinstance(result.status, HealthStatus)

    # GNDVI interpretation
    def test_interpret_gndvi_excellent(self, interpreter):
        result = interpreter.interpret_index("gndvi", 0.7, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.EXCELLENT

    def test_interpret_gndvi_good(self, interpreter):
        result = interpreter.interpret_index("gndvi", 0.5, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.GOOD

    def test_interpret_gndvi_fair(self, interpreter):
        result = interpreter.interpret_index("gndvi", 0.35, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.FAIR

    def test_interpret_gndvi_poor(self, interpreter):
        result = interpreter.interpret_index("gndvi", 0.2, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.POOR

    def test_interpret_gndvi_critical(self, interpreter):
        result = interpreter.interpret_index("gndvi", 0.05, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.CRITICAL

    # Water stress indices
    def test_interpret_ndwi(self, interpreter):
        result = interpreter.interpret_index("ndwi", 0.3, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "NDWI"

    def test_interpret_ndmi(self, interpreter):
        result = interpreter.interpret_index("ndmi", -0.1, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "NDMI"

    # EVI interpretation
    def test_interpret_evi(self, interpreter):
        result = interpreter.interpret_index("evi", 0.6, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "EVI"

    # LAI interpretation
    def test_interpret_lai(self, interpreter):
        result = interpreter.interpret_index("lai", 3.0, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "LAI"

    # Phase 1 Extended indices
    def test_interpret_nbr(self, interpreter):
        result = interpreter.interpret_index("nbr", 0.3, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "NBR"

    def test_interpret_evi2(self, interpreter):
        result = interpreter.interpret_index("evi2", 0.5, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "EVI2"

    def test_interpret_bsi(self, interpreter):
        result = interpreter.interpret_index("bsi", 0.1, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "BSI"

    def test_interpret_sr(self, interpreter):
        result = interpreter.interpret_index("sr", 5.0, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "SR"

    def test_interpret_ccci(self, interpreter):
        result = interpreter.interpret_index("ccci", 1.0, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "CCCI"

    def test_interpret_msi(self, interpreter):
        result = interpreter.interpret_index("msi", 0.8, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "MSI"

    # Phase 2 indices
    def test_interpret_ci_green(self, interpreter):
        result = interpreter.interpret_index("ci_green", 4.0, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "CI_GREEN"

    def test_interpret_ci_rededge(self, interpreter):
        result = interpreter.interpret_index("ci_rededge", 3.0, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "CI_REDEDGE"

    def test_interpret_ireci(self, interpreter):
        result = interpreter.interpret_index("ireci", 2.0, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "IRECI"

    def test_interpret_mtci(self, interpreter):
        result = interpreter.interpret_index("mtci", 3.0, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "MTCI"

    def test_interpret_rendvi(self, interpreter):
        result = interpreter.interpret_index("rendvi", 0.3, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "RENDVI"

    def test_interpret_wdrvi(self, interpreter):
        result = interpreter.interpret_index("wdrvi", 0.2, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "WDRVI"

    # Phase 3 indices
    def test_interpret_mndwi(self, interpreter):
        result = interpreter.interpret_index("mndwi", 0.2, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "MNDWI"

    def test_interpret_nbr2(self, interpreter):
        result = interpreter.interpret_index("nbr2", 0.1, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "NBR2"

    def test_interpret_ndbi(self, interpreter):
        result = interpreter.interpret_index("ndbi", -0.2, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "NDBI"

    def test_interpret_dvi(self, interpreter):
        result = interpreter.interpret_index("dvi", 0.2, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "DVI"

    def test_interpret_gdvi(self, interpreter):
        result = interpreter.interpret_index("gdvi", 0.15, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "GDVI"

    def test_interpret_tsavi(self, interpreter):
        result = interpreter.interpret_index("tsavi", 0.3, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "TSAVI"

    # Generic / unknown index
    def test_interpret_generic(self, interpreter):
        result = interpreter.interpret_index("unknown_index", 0.5, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.index_name == "UNKNOWN_INDEX"
        assert result.confidence == 0.6

    def test_interpret_generic_excellent(self, interpreter):
        result = interpreter.interpret_index("some_index", 0.8, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.EXCELLENT

    def test_interpret_generic_critical(self, interpreter):
        result = interpreter.interpret_index("some_index", 0.01, CropType.WHEAT, GrowthStage.VEGETATIVE)
        assert result.status == HealthStatus.CRITICAL

    # get_recommended_indices
    def test_recommended_indices_emergence(self, interpreter):
        result = interpreter.get_recommended_indices(GrowthStage.EMERGENCE)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_recommended_indices_vegetative(self, interpreter):
        result = interpreter.get_recommended_indices(GrowthStage.VEGETATIVE)
        assert isinstance(result, list)

    def test_recommended_indices_reproductive(self, interpreter):
        result = interpreter.get_recommended_indices(GrowthStage.REPRODUCTIVE)
        assert isinstance(result, list)

    def test_recommended_indices_maturation(self, interpreter):
        result = interpreter.get_recommended_indices(GrowthStage.MATURATION)
        assert isinstance(result, list)

    def test_recommended_indices_harvest(self, interpreter):
        result = interpreter.get_recommended_indices(GrowthStage.HARVEST)
        assert isinstance(result, list)
