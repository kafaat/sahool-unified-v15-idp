"""
Tests for soil testing data models - اختبارات نماذج تحليل التربة

Covers:
- Enum values and string representations
- Dataclass initialization and defaults
- Computed properties (is_saline, is_sodic, is_calcareous)
- Validation methods (texture percentages, nutrient ratios)
- Serialization/JSON conversion
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from shared.soil_testing.models import (
    AmendmentPlan,
    AmendmentRecommendation,
    ExtractionMethod,
    HeavyMetals,
    InterpretationReport,
    LabInfo,
    LabStatus,
    MacronutrientResults,
    MicronutrientResults,
    NutrientInterpretation,
    NutrientStatus,
    NutrientTrend,
    SampleLocation,
    SampleType,
    SoilProperties,
    SoilTestResult,
    SoilTexture,
    SoilTextureClass,
    SoilType,
    TrendDataPoint,
    TrendReport,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Enum Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestNutrientStatus:
    """Test NutrientStatus enum."""

    def test_all_values_exist(self):
        statuses = [
            NutrientStatus.VERY_DEFICIENT,
            NutrientStatus.DEFICIENT,
            NutrientStatus.LOW,
            NutrientStatus.ADEQUATE,
            NutrientStatus.OPTIMAL,
            NutrientStatus.HIGH,
            NutrientStatus.EXCESSIVE,
            NutrientStatus.TOXIC,
        ]
        assert len(statuses) == 8

    def test_string_values(self):
        assert NutrientStatus.VERY_DEFICIENT == "very_deficient"
        assert NutrientStatus.OPTIMAL == "optimal"
        assert NutrientStatus.TOXIC == "toxic"

    def test_is_str_enum(self):
        assert isinstance(NutrientStatus.ADEQUATE, str)


class TestSoilTextureClass:
    """Test SoilTextureClass USDA classification."""

    def test_all_12_texture_classes(self):
        assert len(SoilTextureClass) == 12

    def test_string_values(self):
        assert SoilTextureClass.SAND == "sand"
        assert SoilTextureClass.CLAY == "clay"
        assert SoilTextureClass.LOAM == "loam"
        assert SoilTextureClass.SANDY_CLAY_LOAM == "sandy_clay_loam"


class TestSoilType:
    """Test Middle East soil type classifications."""

    def test_all_soil_types(self):
        assert len(SoilType) == 10

    def test_middle_east_types(self):
        assert SoilType.CALCAREOUS == "calcareous"
        assert SoilType.SALINE == "saline"
        assert SoilType.GYPSIFEROUS == "gypsiferous"
        assert SoilType.SANDY_DESERT == "sandy_desert"
        assert SoilType.ARIDISOL == "aridisol"


class TestExtractionMethod:
    """Test nutrient extraction methods."""

    def test_olsen_for_alkaline(self):
        assert ExtractionMethod.OLSEN == "olsen"

    def test_mehlich_for_acidic(self):
        assert ExtractionMethod.MEHLICH_3 == "mehlich_3"


class TestSampleType:
    """Test sample type enum."""

    def test_composite(self):
        assert SampleType.COMPOSITE == "composite"

    def test_depth_profile(self):
        assert SampleType.DEPTH_PROFILE == "depth_profile"


class TestLabStatus:
    """Test lab status enum."""

    def test_all_statuses(self):
        assert len(LabStatus) == 5
        assert LabStatus.PENDING == "pending"
        assert LabStatus.COMPLETED == "completed"
        assert LabStatus.FAILED == "failed"


# ═══════════════════════════════════════════════════════════════════════════════
# Dataclass Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSampleLocation:
    """Test SampleLocation dataclass."""

    def test_basic_creation(self):
        loc = SampleLocation(latitude=24.7, longitude=46.6)
        assert loc.latitude == 24.7
        assert loc.longitude == 46.6

    def test_defaults(self):
        loc = SampleLocation(latitude=24.7, longitude=46.6)
        assert loc.depth_cm_start == 0
        assert loc.depth_cm_end == 30
        assert loc.elevation_m is None


class TestMacronutrientResults:
    """Test MacronutrientResults dataclass."""

    def test_defaults(self):
        macro = MacronutrientResults(
            p_extraction_method=ExtractionMethod.OLSEN,
            k_extraction_method=ExtractionMethod.AMMONIUM_ACETATE,
        )
        assert macro.nitrogen_total_percent == 0.0
        assert macro.phosphorus_ppm == 0.0
        assert macro.potassium_ppm == 0.0

    def test_available_nitrogen(self):
        macro = MacronutrientResults(
            nitrogen_nitrate_ppm=20.0,
            nitrogen_ammonium_ppm=5.0,
            p_extraction_method=ExtractionMethod.OLSEN,
            k_extraction_method=ExtractionMethod.AMMONIUM_ACETATE,
        )
        assert macro.available_nitrogen_ppm == 25.0

    def test_ca_mg_ratio(self):
        macro = MacronutrientResults(
            calcium_ppm=1500.0,
            magnesium_ppm=300.0,
            p_extraction_method=ExtractionMethod.OLSEN,
            k_extraction_method=ExtractionMethod.AMMONIUM_ACETATE,
        )
        assert macro.ca_mg_ratio == 5.0

    def test_ca_mg_ratio_zero_mg(self):
        macro = MacronutrientResults(
            calcium_ppm=1500.0,
            magnesium_ppm=0.0,
            p_extraction_method=ExtractionMethod.OLSEN,
            k_extraction_method=ExtractionMethod.AMMONIUM_ACETATE,
        )
        assert macro.ca_mg_ratio == 0.0


class TestSoilProperties:
    """Test SoilProperties dataclass and computed properties."""

    def test_defaults(self):
        props = SoilProperties()
        assert props.ph == 7.0
        assert props.ec_ds_m == 0.0
        assert props.organic_matter_percent == 0.0

    def test_is_saline_true(self):
        props = SoilProperties(ec_ds_m=5.0)
        assert props.is_saline is True

    def test_is_saline_false(self):
        props = SoilProperties(ec_ds_m=3.0)
        assert props.is_saline is False

    def test_is_saline_boundary(self):
        props = SoilProperties(ec_ds_m=4.0)
        assert props.is_saline is False  # Not strictly > 4.0

    def test_is_sodic_by_esp(self):
        props = SoilProperties(esp=16.0, sar=5.0)
        assert props.is_sodic is True

    def test_is_sodic_by_sar(self):
        props = SoilProperties(esp=10.0, sar=14.0)
        assert props.is_sodic is True

    def test_is_sodic_false(self):
        props = SoilProperties(esp=10.0, sar=8.0)
        assert props.is_sodic is False

    def test_is_calcareous(self):
        props = SoilProperties(caco3_percent=20.0)
        assert props.is_calcareous is True

    def test_is_not_calcareous(self):
        props = SoilProperties(caco3_percent=10.0)
        assert props.is_calcareous is False

    def test_organic_carbon_from_om(self):
        props = SoilProperties(organic_matter_percent=2.0)
        # OM / 1.724 (Van Bemmelen factor)
        expected = 2.0 / 1.724
        assert abs(props.organic_carbon_from_om - expected) < 0.01


class TestSoilTexture:
    """Test SoilTexture dataclass and validation."""

    def test_basic_creation(self):
        texture = SoilTexture(
            sand_percent=40.0,
            silt_percent=40.0,
            clay_percent=20.0,
            texture_class=SoilTextureClass.LOAM,
        )
        assert texture.sand_percent == 40.0

    def test_validate_percentages_valid(self):
        texture = SoilTexture(
            sand_percent=40.0,
            silt_percent=40.0,
            clay_percent=20.0,
        )
        assert texture.validate_percentages() is True

    def test_validate_percentages_invalid(self):
        texture = SoilTexture(
            sand_percent=40.0,
            silt_percent=40.0,
            clay_percent=30.0,  # Sums to 110
        )
        assert texture.validate_percentages() is False

    def test_fine_earth_percent(self):
        texture = SoilTexture(
            sand_percent=40.0,
            silt_percent=40.0,
            clay_percent=20.0,
            gravel_percent=5.0,
            stones_percent=3.0,
        )
        assert texture.fine_earth_percent == 92.0


class TestHeavyMetals:
    """Test HeavyMetals dataclass."""

    def test_defaults_all_zero(self):
        metals = HeavyMetals()
        assert metals.lead_ppm == 0.0
        assert metals.cadmium_ppm == 0.0
        assert metals.arsenic_ppm == 0.0
        assert metals.mercury_ppm == 0.0


class TestSoilTestResult:
    """Test the main SoilTestResult dataclass."""

    def test_minimal_creation(self):
        result = SoilTestResult(
            id="test-001",
            tenant_id="tenant-001",
            field_id="field-001",
            sample_id="sample-001",
            sample_date=datetime.now(UTC),
            sample_location=SampleLocation(latitude=24.7, longitude=46.6),
        )
        assert result.id == "test-001"
        assert result.sample_type == SampleType.COMPOSITE  # Default

    def test_full_creation(self):
        result = SoilTestResult(
            id="test-002",
            tenant_id="tenant-001",
            field_id="field-001",
            sample_id="sample-002",
            sample_date=datetime.now(UTC),
            sample_location=SampleLocation(latitude=24.7, longitude=46.6),
            macronutrients=MacronutrientResults(
                nitrogen_nitrate_ppm=25,
                phosphorus_ppm=15,
                potassium_ppm=180,
                p_extraction_method=ExtractionMethod.OLSEN,
                k_extraction_method=ExtractionMethod.AMMONIUM_ACETATE,
            ),
            soil_properties=SoilProperties(
                ph=7.8,
                ec_ds_m=2.5,
                organic_matter_percent=1.5,
            ),
            soil_type=SoilType.CALCAREOUS,
        )
        assert result.macronutrients.phosphorus_ppm == 15
        assert result.soil_properties.ph == 7.8
        assert result.soil_type == SoilType.CALCAREOUS


class TestLabInfo:
    """Test LabInfo dataclass."""

    def test_creation(self):
        lab = LabInfo(
            lab_id="lab-001",
            lab_name="Central Soil Lab",
            lab_name_ar="مختبر التربة المركزي",
        )
        assert lab.turnaround_days == 7  # Default


# ═══════════════════════════════════════════════════════════════════════════════
# JSON/Serialization Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSoilTestResultSerialization:
    """Test SoilTestResult serialization."""

    def test_to_dict(self):
        result = SoilTestResult(
            id="test-ser",
            tenant_id="t-001",
            field_id="f-001",
            sample_id="s-001",
            sample_date=datetime(2025, 6, 15, tzinfo=UTC),
            sample_location=SampleLocation(latitude=24.7, longitude=46.6),
            soil_properties=SoilProperties(ph=7.5, ec_ds_m=2.0),
        )
        d = result.to_dict()
        assert d["id"] == "test-ser"
        assert d["field_id"] == "f-001"
        # Soil properties use standardized keys in to_dict
        assert "soil_properties" in d
        assert d["soil_properties"]["pH"] == 7.5
