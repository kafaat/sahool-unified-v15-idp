"""
Tests for Soil Test Interpreter - اختبارات مفسر تحليل التربة

Covers:
- Nutrient status determination from values
- pH interpretation (acidic/neutral/alkaline)
- EC interpretation (saline/non-saline)
- Organic matter evaluation
- Crop-specific sensitivity adjustments
- Full soil test interpretation reports
- Threshold lookups
- Convenience functions
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from shared.soil_testing.interpreter import (
    CROP_SENSITIVITY,
    NUTRIENT_THRESHOLDS,
    SOIL_PROPERTY_THRESHOLDS,
    InterpretationConfig,
    SoilTestInterpreter,
    get_ec_status,
    get_nutrient_status,
    get_ph_status,
    interpret_soil_test,
)
from shared.soil_testing.models import (
    ExtractionMethod,
    MacronutrientResults,
    MicronutrientResults,
    NutrientStatus,
    SampleLocation,
    SoilProperties,
    SoilTestResult,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Threshold Data Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestNutrientThresholds:
    """Test that threshold data is correctly defined."""

    def test_nitrogen_thresholds_exist(self):
        assert "N" in NUTRIENT_THRESHOLDS
        assert "very_deficient" in NUTRIENT_THRESHOLDS["N"]
        assert "excessive" in NUTRIENT_THRESHOLDS["N"]

    def test_phosphorus_olsen_thresholds(self):
        assert "P_olsen" in NUTRIENT_THRESHOLDS
        assert NUTRIENT_THRESHOLDS["P_olsen"]["deficient"] == 5

    def test_phosphorus_mehlich_thresholds(self):
        assert "P_mehlich" in NUTRIENT_THRESHOLDS
        assert NUTRIENT_THRESHOLDS["P_mehlich"]["deficient"] == 15

    def test_potassium_thresholds(self):
        assert "K" in NUTRIENT_THRESHOLDS
        assert NUTRIENT_THRESHOLDS["K"]["adequate"] == 180

    def test_micronutrient_thresholds(self):
        for nutrient in ["Fe", "Zn", "Mn", "Cu", "B"]:
            assert nutrient in NUTRIENT_THRESHOLDS, f"Missing thresholds for {nutrient}"

    def test_thresholds_are_ascending(self):
        """Ensure threshold values increase from deficient to excessive."""
        for key, thresholds in NUTRIENT_THRESHOLDS.items():
            values = [
                thresholds.get("very_deficient", 0),
                thresholds.get("deficient", 0),
                thresholds.get("low", 0),
                thresholds.get("adequate", 0),
                thresholds.get("high", 0),
                thresholds.get("excessive", 0),
            ]
            for i in range(len(values) - 1):
                assert values[i] <= values[i + 1], f"Non-ascending thresholds for {key}"

    def test_bilingual_names(self):
        for key, thresholds in NUTRIENT_THRESHOLDS.items():
            assert "name" in thresholds, f"Missing English name for {key}"
            assert "name_ar" in thresholds, f"Missing Arabic name for {key}"


class TestSoilPropertyThresholds:
    """Test soil property threshold definitions."""

    def test_ph_thresholds(self):
        assert "pH" in SOIL_PROPERTY_THRESHOLDS
        ph = SOIL_PROPERTY_THRESHOLDS["pH"]
        assert ph["very_acidic"] < ph["acidic"] < ph["neutral_low"]

    def test_ec_thresholds(self):
        assert "EC" in SOIL_PROPERTY_THRESHOLDS
        ec = SOIL_PROPERTY_THRESHOLDS["EC"]
        assert ec["non_saline"] < ec["slightly_saline"] < ec["moderately_saline"]

    def test_organic_matter_thresholds(self):
        assert "OM" in SOIL_PROPERTY_THRESHOLDS


class TestCropSensitivity:
    """Test crop sensitivity data."""

    def test_wheat_exists(self):
        assert "wheat" in CROP_SENSITIVITY
        assert "N" in CROP_SENSITIVITY["wheat"]

    def test_tomato_high_k(self):
        """Tomato should have higher K sensitivity."""
        assert CROP_SENSITIVITY["tomato"]["K"] > 1.0

    def test_alfalfa_low_n(self):
        """Alfalfa (N-fixing) should have low N sensitivity."""
        assert CROP_SENSITIVITY["alfalfa"]["N"] < 0.5

    def test_date_palm_high_fe(self):
        """Date palm should have higher iron sensitivity."""
        assert CROP_SENSITIVITY["date_palm"]["Fe"] > 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# Interpreter Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSoilTestInterpreter:
    """Test the main SoilTestInterpreter class."""

    @pytest.fixture
    def interpreter(self):
        return SoilTestInterpreter()

    @pytest.fixture
    def basic_soil_test(self):
        return SoilTestResult(
            id="test-001",
            tenant_id="tenant-001",
            field_id="field-001",
            sample_id="sample-001",
            sample_date=datetime.now(UTC),
            sample_location=SampleLocation(latitude=24.7, longitude=46.6),
            macronutrients=MacronutrientResults(
                nitrogen_nitrate_ppm=25.0,
                nitrogen_ammonium_ppm=5.0,
                phosphorus_ppm=15.0,
                potassium_ppm=180.0,
                calcium_ppm=1500.0,
                magnesium_ppm=200.0,
                p_extraction_method=ExtractionMethod.OLSEN,
                k_extraction_method=ExtractionMethod.AMMONIUM_ACETATE,
            ),
            micronutrients=MicronutrientResults(
                iron_ppm=10.0,
                zinc_ppm=2.0,
                manganese_ppm=15.0,
                copper_ppm=1.5,
                boron_ppm=1.0,
                extraction_method=ExtractionMethod.DTPA,
            ),
            soil_properties=SoilProperties(
                ph=7.5,
                ec_ds_m=2.0,
                organic_matter_percent=1.5,
                cec_meq_100g=15.0,
            ),
        )

    def test_interpreter_init_defaults(self, interpreter):
        assert interpreter.config is not None
        assert interpreter.config.region == "middle_east"
        assert interpreter.config.p_extraction == ExtractionMethod.OLSEN

    def test_interpreter_custom_config(self):
        config = InterpretationConfig(
            region="middle_east",
            crop="wheat",
            p_extraction=ExtractionMethod.MEHLICH_3,
        )
        interp = SoilTestInterpreter(config=config)
        assert interp.config.crop == "wheat"
        assert interp.config.p_extraction == ExtractionMethod.MEHLICH_3

    def test_interpret_full_report(self, interpreter, basic_soil_test):
        report = interpreter.interpret(basic_soil_test, crop="wheat")
        assert report is not None
        assert report.soil_test_id == "test-001"
        assert report.field_id == "field-001"
        assert len(report.interpretations) > 0
        assert 0 <= report.overall_fertility_score <= 100

    def test_interpret_generates_bilingual_summary(self, interpreter, basic_soil_test):
        report = interpreter.interpret(basic_soil_test)
        assert report.summary_en is not None and len(report.summary_en) > 0
        assert report.summary_ar is not None and len(report.summary_ar) > 0

    def test_interpret_ph_status(self, interpreter, basic_soil_test):
        report = interpreter.interpret(basic_soil_test)
        assert report.ph_status != ""
        assert report.ph_status_ar != ""

    def test_interpret_single_nutrient_nitrogen(self, interpreter):
        interp = interpreter.interpret_single_nutrient("N", 30.0)
        assert interp is not None
        assert interp.nutrient_name != ""
        assert interp.status in list(NutrientStatus)

    def test_interpret_single_nutrient_very_deficient(self, interpreter):
        interp = interpreter.interpret_single_nutrient("N", 3.0)
        assert interp.status == NutrientStatus.VERY_DEFICIENT

    def test_interpret_single_nutrient_excessive(self, interpreter):
        interp = interpreter.interpret_single_nutrient("N", 110.0)
        assert interp.status in [NutrientStatus.EXCESSIVE, NutrientStatus.TOXIC]

    def test_interpret_single_nutrient_adequate(self, interpreter):
        interp = interpreter.interpret_single_nutrient("K", 200.0)
        assert interp.status in [NutrientStatus.ADEQUATE, NutrientStatus.OPTIMAL]

    def test_crop_sensitivity_lowers_effective_value(self, interpreter):
        """Tomato has higher K sensitivity (1.3), so effective value should be lower."""
        interp_general = interpreter.interpret_single_nutrient("K", 150.0, crop=None)
        interp_tomato = interpreter.interpret_single_nutrient("K", 150.0, crop="tomato")
        # With higher sensitivity, tomato should be the same or worse status
        status_order = list(NutrientStatus)
        assert status_order.index(interp_tomato.status) <= status_order.index(interp_general.status)

    def test_deficient_soil_test_report(self, interpreter):
        """Test soil with multiple deficiencies."""
        deficient_test = SoilTestResult(
            id="test-def",
            tenant_id="t-001",
            field_id="f-001",
            sample_id="s-001",
            sample_date=datetime.now(UTC),
            sample_location=SampleLocation(latitude=24.7, longitude=46.6),
            macronutrients=MacronutrientResults(
                nitrogen_nitrate_ppm=3.0,  # Very deficient
                phosphorus_ppm=2.0,  # Very deficient
                potassium_ppm=40.0,  # Very deficient
                p_extraction_method=ExtractionMethod.OLSEN,
                k_extraction_method=ExtractionMethod.AMMONIUM_ACETATE,
            ),
            soil_properties=SoilProperties(
                ph=7.5,
                ec_ds_m=1.0,
                organic_matter_percent=0.3,
            ),
        )
        report = interpreter.interpret(deficient_test)
        assert report.overall_fertility_score <= 50
        assert len(report.deficiencies) > 0

    def test_saline_soil_reduces_score(self, interpreter):
        """Saline soil should reduce fertility score."""
        saline_test = SoilTestResult(
            id="test-saline",
            tenant_id="t-001",
            field_id="f-001",
            sample_id="s-001",
            sample_date=datetime.now(UTC),
            sample_location=SampleLocation(latitude=24.7, longitude=46.6),
            macronutrients=MacronutrientResults(
                nitrogen_nitrate_ppm=30.0,
                phosphorus_ppm=20.0,
                potassium_ppm=200.0,
                p_extraction_method=ExtractionMethod.OLSEN,
                k_extraction_method=ExtractionMethod.AMMONIUM_ACETATE,
            ),
            soil_properties=SoilProperties(
                ph=7.5,
                ec_ds_m=6.0,  # Saline!
                organic_matter_percent=2.0,
            ),
        )
        report = interpreter.interpret(saline_test)
        assert report.overall_fertility_score < 100


# ═══════════════════════════════════════════════════════════════════════════════
# Convenience Function Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestConvenienceFunctions:
    """Test convenience/standalone functions."""

    def test_get_nutrient_status_deficient(self):
        # Returns tuple: (status, description_en, description_ar)
        result = get_nutrient_status("N", 8.0)
        assert result[0] == NutrientStatus.DEFICIENT

    def test_get_nutrient_status_adequate(self):
        result = get_nutrient_status("N", 30.0)
        assert result[0] in [NutrientStatus.LOW, NutrientStatus.ADEQUATE]

    def test_get_nutrient_status_excessive(self):
        result = get_nutrient_status("K", 600.0)
        assert result[0] in [NutrientStatus.EXCESSIVE, NutrientStatus.TOXIC]

    def test_get_nutrient_status_returns_bilingual(self):
        result = get_nutrient_status("N", 8.0)
        assert len(result) == 3  # status, en, ar
        assert isinstance(result[1], str)  # English description
        assert isinstance(result[2], str)  # Arabic description

    def test_get_ph_status_neutral(self):
        # Returns tuple: (status_en, status_ar)
        result = get_ph_status(7.0)
        assert "neutral" in result[0].lower() or "optimal" in result[0].lower()

    def test_get_ph_status_acidic(self):
        result = get_ph_status(5.0)
        assert "acid" in result[0].lower()

    def test_get_ph_status_alkaline(self):
        result = get_ph_status(8.5)
        assert "alkaline" in result[0].lower() or "alkali" in result[0].lower()

    def test_get_ph_status_bilingual(self):
        result = get_ph_status(7.0)
        assert len(result) == 2
        assert isinstance(result[1], str)  # Arabic

    def test_get_ec_status_non_saline(self):
        result = get_ec_status(1.5)
        assert "saline" not in result[0].lower() or "non" in result[0].lower()

    def test_get_ec_status_saline(self):
        result = get_ec_status(5.0)
        assert "saline" in result[0].lower()

    def test_get_ec_status_bilingual(self):
        result = get_ec_status(1.5)
        assert len(result) == 2
        assert isinstance(result[1], str)  # Arabic

    def test_interpret_soil_test_function(self):
        """Test the interpret_soil_test convenience function."""
        soil_test = SoilTestResult(
            id="test-conv",
            tenant_id="t-001",
            field_id="f-001",
            sample_id="s-001",
            sample_date=datetime.now(UTC),
            sample_location=SampleLocation(latitude=24.7, longitude=46.6),
            macronutrients=MacronutrientResults(
                nitrogen_nitrate_ppm=25.0,
                phosphorus_ppm=15.0,
                potassium_ppm=180.0,
                p_extraction_method=ExtractionMethod.OLSEN,
                k_extraction_method=ExtractionMethod.AMMONIUM_ACETATE,
            ),
            soil_properties=SoilProperties(ph=7.5, ec_ds_m=2.0),
        )
        report = interpret_soil_test(soil_test)
        assert report is not None
        assert report.soil_test_id == "test-conv"
