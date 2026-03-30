"""
Tests for Fertilizer Management Module - اختبارات وحدة إدارة الأسمدة

Covers:
- Fertilizer data models and enums
- Application rate calculator
- NPK calculations and cost analysis
- Recommendation engine (crop requirements, soil test based)
- Environmental compliance checks
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from shared.fertilizer_management.calculator import (
    ApplicationRateResult,
    BlendCalculation,
    FertilizerCalculator,
    calculate_blend_for_targets,
)
from shared.fertilizer_management.models import (
    ApplicationMethod,
    ComplianceLevel,
    Fertilizer,
    FertilizerForm,
    FertilizerType,
    InventoryItem,
    InventoryStatus,
    NutrientComposition,
    NutrientStatus,
    SoilTest,
)
from shared.fertilizer_management.recommendations import (
    CROP_NUTRIENT_REQUIREMENTS,
    FertilizerRecommendationEngine,
    calculate_quick_recommendation,
    get_crop_requirements,
    get_supported_crops,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Enum Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestFertilizerEnums:
    """Test fertilizer-related enums."""

    def test_fertilizer_type_values(self):
        assert FertilizerType.NITROGEN == "nitrogen"
        assert FertilizerType.NPK_COMPOUND == "npk_compound"
        assert FertilizerType.ORGANIC == "organic"
        assert FertilizerType.FOLIAR == "foliar"
        assert len(FertilizerType) == 9

    def test_fertilizer_form_values(self):
        assert FertilizerForm.GRANULAR == "granular"
        assert FertilizerForm.LIQUID == "liquid"
        assert FertilizerForm.POWDER == "powder"

    def test_application_method_values(self):
        assert ApplicationMethod.BROADCAST == "broadcast"
        assert ApplicationMethod.FERTIGATION == "fertigation"
        assert ApplicationMethod.FOLIAR_SPRAY == "foliar_spray"
        assert ApplicationMethod.INJECTION == "injection"

    def test_nutrient_status_values(self):
        assert NutrientStatus.DEFICIENT == "deficient"
        assert NutrientStatus.OPTIMAL == "optimal"
        assert NutrientStatus.EXCESSIVE == "excessive"

    def test_inventory_status_values(self):
        assert InventoryStatus.IN_STOCK == "in_stock"
        assert InventoryStatus.LOW_STOCK == "low_stock"
        assert InventoryStatus.EXPIRED == "expired"

    def test_compliance_level_values(self):
        assert ComplianceLevel.COMPLIANT == "compliant"
        assert ComplianceLevel.VIOLATION == "violation"


# ═══════════════════════════════════════════════════════════════════════════════
# Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestNutrientComposition:
    """Test NutrientComposition dataclass."""

    def test_defaults_all_zero(self):
        comp = NutrientComposition()
        assert comp.nitrogen_n == 0.0
        assert comp.phosphorus_p2o5 == 0.0
        assert comp.potassium_k2o == 0.0

    def test_urea_composition(self):
        urea = NutrientComposition(nitrogen_n=46.0)
        assert urea.nitrogen_n == 46.0
        assert urea.phosphorus_p2o5 == 0.0

    def test_npk_composition(self):
        npk = NutrientComposition(
            nitrogen_n=20.0,
            phosphorus_p2o5=20.0,
            potassium_k2o=20.0,
        )
        assert npk.nitrogen_n == 20.0
        assert npk.phosphorus_p2o5 == 20.0
        assert npk.potassium_k2o == 20.0


class TestFertilizer:
    """Test Fertilizer dataclass."""

    def test_basic_creation(self):
        fert = Fertilizer(
            id="fert-001",
            name="Urea 46%",
            name_ar="يوريا 46%",
            fertilizer_type=FertilizerType.NITROGEN,
            form=FertilizerForm.GRANULAR,
            composition=NutrientComposition(nitrogen_n=46.0),
            unit_price=Decimal("2.50"),
            unit_size_kg=50.0,
        )
        assert fert.name == "Urea 46%"
        assert fert.composition.nitrogen_n == 46.0
        assert fert.unit_price == Decimal("2.50")

    def test_bilingual_names(self):
        fert = Fertilizer(
            id="fert-002",
            name="DAP",
            name_ar="داب",
            fertilizer_type=FertilizerType.NPK_COMPOUND,
            form=FertilizerForm.GRANULAR,
            composition=NutrientComposition(nitrogen_n=18.0, phosphorus_p2o5=46.0),
            unit_price=Decimal("3.20"),
            unit_size_kg=50.0,
        )
        assert fert.name_ar == "داب"


class TestSoilTest:
    """Test SoilTest dataclass for fertilizer module."""

    def test_basic_creation(self):
        soil_test = SoilTest(
            id="st-001",
            tenant_id="t-001",
            field_id="f-001",
            sample_date=datetime.now(UTC),
            ph=7.5,
            nitrogen_ppm=25.0,
            phosphorus_ppm=15.0,
            potassium_ppm=180.0,
            organic_matter_percent=1.5,
        )
        assert soil_test.ph == 7.5
        assert soil_test.nitrogen_ppm == 25.0


class TestInventoryItem:
    """Test InventoryItem dataclass."""

    def test_basic_creation(self):
        item = InventoryItem(
            id="inv-001",
            tenant_id="t-001",
            fertilizer_id="fert-001",
            fertilizer_name="Urea 46%",
            fertilizer_name_ar="يوريا 46%",
            quantity_kg=500.0,
        )
        assert item.quantity_kg == 500.0


class TestApplicationRateResult:
    """Test ApplicationRateResult dataclass."""

    def test_basic_creation(self):
        result = ApplicationRateResult(
            fertilizer_name="Urea 46%",
            fertilizer_name_ar="يوريا 46%",
            npk_ratio="46-0-0",
            rate_kg_per_ha=260.9,
            rate_kg_per_dunum=26.09,
            rate_kg_total=1304.5,
            area_ha=5.0,
            n_kg_per_ha=120.0,
            p2o5_kg_per_ha=0.0,
            k2o_kg_per_ha=0.0,
            cost_per_ha=Decimal("652.25"),
            cost_total=Decimal("3261.25"),
        )
        assert result.rate_kg_per_ha == 260.9
        assert result.n_kg_per_ha == 120.0

    def test_to_dict(self):
        result = ApplicationRateResult(
            fertilizer_name="Urea",
            fertilizer_name_ar="يوريا",
            npk_ratio="46-0-0",
            rate_kg_per_ha=260.9,
            rate_kg_per_dunum=26.09,
            rate_kg_total=1304.5,
            area_ha=5.0,
            n_kg_per_ha=120.0,
            p2o5_kg_per_ha=0.0,
            k2o_kg_per_ha=0.0,
        )
        d = result.to_dict()
        assert "fertilizer_name" in d
        assert "rate_kg_per_ha" in d
        assert "nutrients_per_ha" in d
        assert d["nutrients_per_ha"]["N"] == 120.0


# ═══════════════════════════════════════════════════════════════════════════════
# Calculator Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestFertilizerCalculator:
    """Test FertilizerCalculator class."""

    @pytest.fixture
    def calculator(self):
        return FertilizerCalculator()

    def test_calculator_has_standard_fertilizers(self, calculator):
        assert "urea" in calculator.fertilizers
        assert "dap" in calculator.fertilizers
        assert "mop" in calculator.fertilizers
        assert "npk_20_20_20" in calculator.fertilizers

    def test_urea_rate_for_120_n(self, calculator):
        """Calculate urea rate to supply 120 kg N/ha."""
        result = calculator.calculate_rate_for_nutrient(
            fertilizer_code="urea",
            target_nutrient="N",
            target_kg_per_ha=120.0,
            area_ha=1.0,
        )
        assert result is not None
        # Urea is 46% N, so need 120/0.46 = 260.9 kg/ha
        assert abs(result.rate_kg_per_ha - 260.9) < 1.0
        assert abs(result.n_kg_per_ha - 120.0) < 1.0

    def test_dap_rate_for_phosphorus(self, calculator):
        """Calculate DAP rate to supply 60 kg P2O5/ha."""
        result = calculator.calculate_rate_for_nutrient(
            fertilizer_code="dap",
            target_nutrient="P2O5",
            target_kg_per_ha=60.0,
            area_ha=1.0,
        )
        assert result is not None
        # DAP is 46% P2O5, so need 60/0.46 = 130.4 kg/ha
        assert abs(result.rate_kg_per_ha - 130.4) < 1.0
        # DAP also provides N (18%), so check N is calculated
        assert result.n_kg_per_ha > 0

    def test_mop_rate_for_potassium(self, calculator):
        """Calculate MOP rate for K2O."""
        result = calculator.calculate_rate_for_nutrient(
            fertilizer_code="mop",
            target_nutrient="K2O",
            target_kg_per_ha=40.0,
            area_ha=1.0,
        )
        assert result is not None
        # MOP is 60% K2O
        expected_rate = (40.0 / 60.0) * 100
        assert abs(result.rate_kg_per_ha - expected_rate) < 1.0

    def test_rate_scales_with_area(self, calculator):
        """Total quantity should scale with area."""
        result_1ha = calculator.calculate_rate_for_nutrient("urea", "N", 120.0, 1.0)
        result_5ha = calculator.calculate_rate_for_nutrient("urea", "N", 120.0, 5.0)
        assert abs(result_5ha.rate_kg_total - result_1ha.rate_kg_total * 5) < 1.0

    def test_rate_per_dunum(self, calculator):
        """Rate per dunum should be 1/10 of rate per hectare."""
        result = calculator.calculate_rate_for_nutrient("urea", "N", 120.0, 1.0)
        assert abs(result.rate_kg_per_dunum - result.rate_kg_per_ha / 10) < 0.01

    def test_cost_calculation(self, calculator):
        """Cost should be calculated based on price per kg."""
        result = calculator.calculate_rate_for_nutrient("urea", "N", 120.0, 1.0)
        assert result.cost_per_ha > Decimal("0")
        assert result.cost_total > Decimal("0")

    def test_unknown_fertilizer_raises(self, calculator):
        with pytest.raises(ValueError, match="Unknown fertilizer"):
            calculator.calculate_rate_for_nutrient("nonexistent", "N", 100.0, 1.0)

    def test_fertilizer_without_nutrient_raises(self, calculator):
        """Urea has no K2O, should raise."""
        with pytest.raises(ValueError, match="does not contain"):
            calculator.calculate_rate_for_nutrient("urea", "K2O", 40.0, 1.0)

    def test_npk_ratio_string(self, calculator):
        result = calculator.calculate_rate_for_nutrient("dap", "P2O5", 60.0, 1.0)
        assert result.npk_ratio == "18-46-0"

    def test_environmental_limits_defined(self, calculator):
        assert calculator.ENVIRONMENTAL_LIMITS["N_max_annual"] == 200.0
        assert calculator.ENVIRONMENTAL_LIMITS["P_max_annual"] == 50.0


# ═══════════════════════════════════════════════════════════════════════════════
# Recommendation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCropNutrientRequirements:
    """Test crop nutrient requirement data."""

    def test_wheat_requirements_exist(self):
        assert "wheat" in CROP_NUTRIENT_REQUIREMENTS
        wheat = CROP_NUTRIENT_REQUIREMENTS["wheat"]
        assert "N" in wheat
        assert "P2O5" in wheat
        assert "K2O" in wheat
        assert "typical_yield" in wheat

    def test_tomato_requirements(self):
        assert "tomato" in CROP_NUTRIENT_REQUIREMENTS
        tomato = CROP_NUTRIENT_REQUIREMENTS["tomato"]
        assert tomato["typical_yield"] == 60.0

    def test_date_palm_requirements(self):
        assert "date_palm" in CROP_NUTRIENT_REQUIREMENTS

    def test_alfalfa_low_n(self):
        """Alfalfa is N-fixing, should have 0 N requirement."""
        alfalfa = CROP_NUTRIENT_REQUIREMENTS["alfalfa"]
        assert alfalfa["N"] == 0

    def test_growth_stages_defined(self):
        """All crops should have growth stage splits."""
        for crop_name, crop_data in CROP_NUTRIENT_REQUIREMENTS.items():
            assert "growth_stages" in crop_data, f"{crop_name} missing growth_stages"
            stages = crop_data["growth_stages"]
            for stage_name, splits in stages.items():
                # Each stage should have N, P2O5, K2O splits that sum to valid fractions
                assert "N" in splits, f"{crop_name}/{stage_name} missing N split"

    def test_bilingual_names(self):
        for crop_name, crop_data in CROP_NUTRIENT_REQUIREMENTS.items():
            assert "name_ar" in crop_data, f"{crop_name} missing Arabic name"


class TestRecommendationHelpers:
    """Test recommendation helper functions."""

    def test_get_supported_crops(self):
        crops = get_supported_crops()
        assert len(crops) > 0
        # Returns list of dicts with name/name_ar
        crop_names = [c["name"] for c in crops]
        assert "wheat" in crop_names
        assert "tomato" in crop_names

    def test_get_crop_requirements_existing(self):
        reqs = get_crop_requirements("wheat")
        assert reqs is not None
        assert "N" in reqs

    def test_get_crop_requirements_nonexistent(self):
        reqs = get_crop_requirements("nonexistent_crop")
        assert reqs is None

    def test_calculate_quick_recommendation(self):
        """Test quick recommendation calculation."""
        rec = calculate_quick_recommendation(
            crop="wheat",
            soil_n_ppm=15.0,
            soil_p_ppm=10.0,
            soil_k_ppm=100.0,
        )
        assert rec is not None


class TestFertilizerRecommendationEngine:
    """Test the full recommendation engine."""

    @pytest.fixture
    def engine(self):
        return FertilizerRecommendationEngine()

    def test_engine_init(self, engine):
        assert engine is not None

    def test_generate_recommendation_wheat(self, engine):
        """Generate fertilizer recommendation for wheat."""
        soil_test = SoilTest(
            id="st-001",
            tenant_id="t-001",
            field_id="f-001",
            sample_date=datetime.now(UTC),
            ph=7.5,
            nitrogen_ppm=15.0,  # Low N
            phosphorus_ppm=10.0,  # Low P
            potassium_ppm=150.0,
            organic_matter_percent=1.5,
        )
        rec = engine.generate_recommendation(
            recommendation_id="rec-001",
            tenant_id="t-001",
            field_id="f-001",
            soil_test=soil_test,
            crop="wheat",
        )
        assert rec is not None
        assert rec.crop == "wheat"
        assert len(rec.nutrient_recommendations) > 0

    def test_recommendation_has_n_p_k(self, engine):
        """Recommendation for deficient soil should include N, P, and/or K."""
        soil_test = SoilTest(
            id="st-002",
            tenant_id="t-001",
            field_id="f-001",
            sample_date=datetime.now(UTC),
            ph=7.5,
            nitrogen_ppm=5.0,  # Very low
            phosphorus_ppm=3.0,  # Very low
            potassium_ppm=50.0,  # Very low
            organic_matter_percent=0.5,
        )
        rec = engine.generate_recommendation(
            recommendation_id="rec-002",
            tenant_id="t-001",
            field_id="f-001",
            soil_test=soil_test,
            crop="wheat",
        )
        assert rec is not None
        nutrients = [nr.nutrient for nr in rec.nutrient_recommendations]
        assert "N" in nutrients or len(nutrients) > 0

    def test_recommendation_for_sufficient_soil(self, engine):
        """Recommendation for well-fertilized soil should have lower rates."""
        low_soil = SoilTest(
            id="st-low",
            tenant_id="t-001",
            field_id="f-001",
            sample_date=datetime.now(UTC),
            ph=7.0,
            nitrogen_ppm=5.0,
            phosphorus_ppm=3.0,
            potassium_ppm=50.0,
            organic_matter_percent=1.0,
        )
        high_soil = SoilTest(
            id="st-high",
            tenant_id="t-001",
            field_id="f-001",
            sample_date=datetime.now(UTC),
            ph=7.0,
            nitrogen_ppm=60.0,
            phosphorus_ppm=40.0,
            potassium_ppm=300.0,
            organic_matter_percent=3.0,
        )
        rec_low = engine.generate_recommendation(
            recommendation_id="rec-low", tenant_id="t-001", field_id="f-001",
            soil_test=low_soil, crop="wheat",
        )
        rec_high = engine.generate_recommendation(
            recommendation_id="rec-high", tenant_id="t-001", field_id="f-001",
            soil_test=high_soil, crop="wheat",
        )
        # High soil should need less fertilizer
        if rec_low and rec_high:
            total_low = sum(nr.required_kg_ha for nr in rec_low.nutrient_recommendations)
            total_high = sum(nr.required_kg_ha for nr in rec_high.nutrient_recommendations)
            assert total_high <= total_low

    def test_recommendation_bilingual(self, engine):
        soil_test = SoilTest(
            id="st-bilin",
            tenant_id="t-001",
            field_id="f-001",
            sample_date=datetime.now(UTC),
            ph=7.5,
            nitrogen_ppm=15.0,
            phosphorus_ppm=10.0,
            potassium_ppm=150.0,
            organic_matter_percent=1.5,
        )
        rec = engine.generate_recommendation(
            recommendation_id="rec-bil", tenant_id="t-001", field_id="f-001",
            soil_test=soil_test, crop="wheat",
        )
        if rec:
            assert rec.summary_ar is not None or rec.summary_en is not None


# ═══════════════════════════════════════════════════════════════════════════════
# Blend Calculation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestBlendCalculation:
    """Test fertilizer blend calculations."""

    def test_basic_blend(self):
        blend = BlendCalculation(
            target_n_kg_ha=120.0,
            target_p_kg_ha=60.0,
            target_k_kg_ha=40.0,
        )
        assert blend.target_n_kg_ha == 120.0

    def test_to_dict(self):
        blend = BlendCalculation(
            target_n_kg_ha=120.0,
            target_p_kg_ha=60.0,
            target_k_kg_ha=40.0,
            total_n_kg_ha=115.0,
            total_p_kg_ha=58.0,
            total_k_kg_ha=42.0,
        )
        d = blend.to_dict()
        assert "target" in d
        assert "actual" in d
        assert d["target"]["N"] == 120.0

    def test_calculate_blend_for_targets(self):
        """Test blend calculation convenience function."""
        result = calculate_blend_for_targets(
            n_kg_ha=120.0,
            p_kg_ha=60.0,
            k_kg_ha=40.0,
        )
        assert result is not None
