"""
Critical Validation Tests: EC/NPK Separation

These tests ensure that SAHOOL maintains the scientific standard that
Electrical Conductivity (EC) is NEVER used to estimate or infer NPK nutrient levels.

⚠️ CRITICAL: These tests MUST pass to maintain scientific integrity.

If any test fails, it indicates a serious scientific flaw that could result in:
- 30-50% fertilizer waste
- 15-40% yield loss
- Long-term soil degradation

See docs/SCIENTIFIC_STANDARDS.md for detailed explanation.

Author: SAHOOL Platform Team
Version: 1.0.0
"""

import pytest
from decimal import Decimal

# Import soil testing modules
from shared.soil_testing.interpreter import SoilTestInterpreter
from shared.soil_testing.recommendations import SoilAmendmentAdvisor
from shared.soil_testing.models import (
    SoilTestResult,
    SoilProperties,
    MacronutrientResults,
    MicronutrientResults,
    SoilType,
)


class TestECNPKSeparation:
    """
    Test suite validating that EC (salinity) and NPK (nutrients) are properly separated.
    """

    @pytest.fixture
    def interpreter(self):
        """Create soil test interpreter instance."""
        return SoilTestInterpreter()

    @pytest.fixture
    def advisor(self):
        """Create soil amendment advisor instance."""
        return SoilAmendmentAdvisor()

    def test_ec_does_not_affect_npk_interpretation(self, interpreter):
        """
        CRITICAL TEST: Verify that EC changes don't affect NPK status interpretation.
        
        Two soil samples with identical NPK but different EC should have
        identical nutrient status classifications.
        """
        # Create two soil tests with same NPK, different EC
        soil_test_low_ec = SoilTestResult(
            field_id="test-field-1",
            sample_date="2026-01-28",
            properties=SoilProperties(
                ph=7.5,
                ec_ds_m=0.5,  # Low EC (non-saline)
                organic_matter_pct=2.0,
                soil_type=SoilType.LOAM,
            ),
            macronutrients=MacronutrientResults(
                nitrogen_ppm=15.0,
                phosphorus_ppm=10.0,
                potassium_ppm=100.0,
                calcium_ppm=1200.0,
                magnesium_ppm=150.0,
                sulfur_ppm=12.0,
            ),
            micronutrients=MicronutrientResults(
                iron_ppm=4.0,
                manganese_ppm=3.0,
                zinc_ppm=1.0,
                copper_ppm=0.5,
                boron_ppm=0.4,
            ),
        )

        soil_test_high_ec = SoilTestResult(
            field_id="test-field-2",
            sample_date="2026-01-28",
            properties=SoilProperties(
                ph=7.5,
                ec_ds_m=4.5,  # High EC (strongly saline)
                organic_matter_pct=2.0,
                soil_type=SoilType.LOAM,
            ),
            macronutrients=MacronutrientResults(
                nitrogen_ppm=15.0,  # IDENTICAL NPK values
                phosphorus_ppm=10.0,
                potassium_ppm=100.0,
                calcium_ppm=1200.0,
                magnesium_ppm=150.0,
                sulfur_ppm=12.0,
            ),
            micronutrients=MicronutrientResults(
                iron_ppm=4.0,
                manganese_ppm=3.0,
                zinc_ppm=1.0,
                copper_ppm=0.5,
                boron_ppm=0.4,
            ),
        )

        # Interpret both
        report_low_ec = interpreter.interpret(soil_test_low_ec)
        report_high_ec = interpreter.interpret(soil_test_high_ec)

        # NPK interpretations MUST be identical
        assert (
            report_low_ec.macronutrient_interpretations.nitrogen.status
            == report_high_ec.macronutrient_interpretations.nitrogen.status
        ), "EC should not affect nitrogen status interpretation"

        assert (
            report_low_ec.macronutrient_interpretations.phosphorus.status
            == report_high_ec.macronutrient_interpretations.phosphorus.status
        ), "EC should not affect phosphorus status interpretation"

        assert (
            report_low_ec.macronutrient_interpretations.potassium.status
            == report_high_ec.macronutrient_interpretations.potassium.status
        ), "EC should not affect potassium status interpretation"

        # But salinity interpretations SHOULD be different
        assert (
            report_low_ec.properties.ec_interpretation_en
            != report_high_ec.properties.ec_interpretation_en
        ), "EC should affect salinity interpretation"

    def test_fertilizer_recommendations_ignore_ec(self, advisor):
        """
        CRITICAL TEST: Verify fertilizer recommendations are based on NPK values only.
        
        Two fields with identical NPK but different EC should receive
        identical fertilizer amounts (though salinity warnings may differ).
        """
        # Create two soil tests with same NPK, different EC
        soil_test_low_ec = SoilTestResult(
            field_id="test-field-1",
            sample_date="2026-01-28",
            properties=SoilProperties(
                ph=7.5,
                ec_ds_m=0.5,  # Low salinity
                organic_matter_pct=2.0,
                soil_type=SoilType.LOAM,
            ),
            macronutrients=MacronutrientResults(
                nitrogen_ppm=15.0,
                phosphorus_ppm=10.0,
                potassium_ppm=100.0,
                calcium_ppm=1200.0,
                magnesium_ppm=150.0,
                sulfur_ppm=12.0,
            ),
            micronutrients=MicronutrientResults(
                iron_ppm=4.0,
                manganese_ppm=3.0,
                zinc_ppm=1.0,
                copper_ppm=0.5,
                boron_ppm=0.4,
            ),
        )

        soil_test_high_ec = SoilTestResult(
            field_id="test-field-2",
            sample_date="2026-01-28",
            properties=SoilProperties(
                ph=7.5,
                ec_ds_m=4.5,  # High salinity
                organic_matter_pct=2.0,
                soil_type=SoilType.LOAM,
            ),
            macronutrients=MacronutrientResults(
                nitrogen_ppm=15.0,  # IDENTICAL NPK
                phosphorus_ppm=10.0,
                potassium_ppm=100.0,
                calcium_ppm=1200.0,
                magnesium_ppm=150.0,
                sulfur_ppm=12.0,
            ),
            micronutrients=MicronutrientResults(
                iron_ppm=4.0,
                manganese_ppm=3.0,
                zinc_ppm=1.0,
                copper_ppm=0.5,
                boron_ppm=0.4,
            ),
        )

        # Generate recommendations for wheat
        plan_low_ec = advisor.generate_plan(
            soil_test=soil_test_low_ec,
            crop_type="wheat",
            target_yield_tons_ha=5.0,
            field_area_ha=Decimal("10.0"),
        )

        plan_high_ec = advisor.generate_plan(
            soil_test=soil_test_high_ec,
            crop_type="wheat",
            target_yield_tons_ha=5.0,
            field_area_ha=Decimal("10.0"),
        )

        # Extract NPK fertilizer amounts
        def extract_npk_amounts(plan):
            npk = {"N": 0, "P": 0, "K": 0}
            for rec in plan.fertilizer_recommendations:
                for nutrient, amount in rec.nutrients.items():
                    if nutrient in npk:
                        npk[nutrient] += amount
            return npk

        npk_low_ec = extract_npk_amounts(plan_low_ec)
        npk_high_ec = extract_npk_amounts(plan_high_ec)

        # Fertilizer amounts MUST be identical (EC should not affect NPK dosage)
        assert npk_low_ec["N"] == npk_high_ec["N"], (
            f"Nitrogen fertilizer amounts differ: {npk_low_ec['N']} vs {npk_high_ec['N']}. "
            "EC should NOT affect NPK fertilizer recommendations!"
        )

        assert npk_low_ec["P"] == npk_high_ec["P"], (
            f"Phosphorus fertilizer amounts differ: {npk_low_ec['P']} vs {npk_high_ec['P']}. "
            "EC should NOT affect NPK fertilizer recommendations!"
        )

        assert npk_low_ec["K"] == npk_high_ec["K"], (
            f"Potassium fertilizer amounts differ: {npk_low_ec['K']} vs {npk_high_ec['K']}. "
            "EC should NOT affect NPK fertilizer recommendations!"
        )

    def test_ec_only_affects_salinity_warnings(self, advisor):
        """
        TEST: Verify EC affects salinity warnings but not nutrient recommendations.
        """
        soil_test_saline = SoilTestResult(
            field_id="test-field-saline",
            sample_date="2026-01-28",
            properties=SoilProperties(
                ph=7.5,
                ec_ds_m=5.0,  # Very high salinity
                organic_matter_pct=2.0,
                soil_type=SoilType.LOAM,
            ),
            macronutrients=MacronutrientResults(
                nitrogen_ppm=30.0,
                phosphorus_ppm=25.0,
                potassium_ppm=200.0,
                calcium_ppm=1500.0,
                magnesium_ppm=180.0,
                sulfur_ppm=15.0,
            ),
            micronutrients=MicronutrientResults(
                iron_ppm=5.0,
                manganese_ppm=4.0,
                zinc_ppm=1.5,
                copper_ppm=0.6,
                boron_ppm=0.5,
            ),
        )

        plan = advisor.generate_plan(
            soil_test=soil_test_saline,
            crop_type="wheat",
            target_yield_tons_ha=5.0,
            field_area_ha=Decimal("10.0"),
        )

        # Should have salinity-related amendments (leaching/gypsum)
        has_salinity_amendment = any(
            "salinity" in rec.purpose.lower() or "leach" in rec.purpose.lower()
            for rec in plan.other_amendments
        )

        assert has_salinity_amendment, (
            "High EC should trigger salinity management recommendations"
        )

    def test_no_ec_to_npk_conversion_functions_exist(self):
        """
        SECURITY TEST: Ensure no functions exist that convert EC to NPK values.
        
        This test scans for common anti-patterns that would violate the
        EC/NPK separation principle.
        """
        # Import all soil testing modules
        import shared.soil_testing.interpreter as interpreter_module
        import shared.soil_testing.recommendations as recommendations_module

        # Check interpreter module
        interpreter_funcs = [
            name for name in dir(interpreter_module)
            if callable(getattr(interpreter_module, name))
        ]
        
        dangerous_patterns = [
            "ec_to_npk",
            "ec_to_nitrogen",
            "ec_to_phosphorus",
            "ec_to_potassium",
            "estimate_npk_from_ec",
            "calculate_nutrients_from_ec",
        ]

        for pattern in dangerous_patterns:
            assert pattern not in interpreter_funcs, (
                f"CRITICAL: Found dangerous function '{pattern}' in interpreter module. "
                "This violates EC/NPK separation principle!"
            )

        # Check recommendations module
        recommendations_funcs = [
            name for name in dir(recommendations_module)
            if callable(getattr(recommendations_module, name))
        ]

        for pattern in dangerous_patterns:
            assert pattern not in recommendations_funcs, (
                f"CRITICAL: Found dangerous function '{pattern}' in recommendations module. "
                "This violates EC/NPK separation principle!"
            )


class TestSalinityVsNutrients:
    """
    Additional tests to ensure salinity and nutrients are treated as separate concerns.
    """

    def test_saline_soil_with_adequate_nutrients(self):
        """
        TEST: A saline soil (high EC) can still have adequate nutrients.
        The system should recommend salinity management + fertilizer separately.
        """
        advisor = SoilAmendmentAdvisor()

        # Saline soil with good NPK levels
        soil_test = SoilTestResult(
            field_id="test-field",
            sample_date="2026-01-28",
            properties=SoilProperties(
                ph=7.5,
                ec_ds_m=4.0,  # High salinity
                organic_matter_pct=2.5,
                soil_type=SoilType.LOAM,
            ),
            macronutrients=MacronutrientResults(
                nitrogen_ppm=40.0,  # Adequate
                phosphorus_ppm=30.0,  # Adequate
                potassium_ppm=250.0,  # Adequate
                calcium_ppm=2000.0,
                magnesium_ppm=200.0,
                sulfur_ppm=20.0,
            ),
            micronutrients=MicronutrientResults(
                iron_ppm=5.0,
                manganese_ppm=4.0,
                zinc_ppm=2.0,
                copper_ppm=0.8,
                boron_ppm=0.6,
            ),
        )

        plan = advisor.generate_plan(
            soil_test=soil_test,
            crop_type="wheat",
            target_yield_tons_ha=5.0,
            field_area_ha=Decimal("10.0"),
        )

        # Should have salinity management
        has_salinity_management = any(
            "salinity" in rec.purpose.lower() or "leach" in rec.purpose.lower()
            for rec in plan.other_amendments
        )

        assert has_salinity_management, (
            "High EC should trigger salinity management even with adequate nutrients"
        )

        # Should have minimal fertilizer (nutrients are adequate)
        total_n_fertilizer = sum(
            rec.nutrients.get("N", 0) for rec in plan.fertilizer_recommendations
        )

        # With adequate N (40 ppm), minimal or no N fertilizer should be needed
        assert total_n_fertilizer < 50, (
            "Should not recommend excessive N fertilizer when soil N is adequate"
        )

    def test_non_saline_soil_with_deficient_nutrients(self):
        """
        TEST: A non-saline soil (low EC) can have nutrient deficiencies.
        The system should recommend fertilizer without salinity warnings.
        """
        advisor = SoilAmendmentAdvisor()

        # Non-saline soil with low NPK
        soil_test = SoilTestResult(
            field_id="test-field",
            sample_date="2026-01-28",
            properties=SoilProperties(
                ph=7.5,
                ec_ds_m=0.3,  # Low salinity
                organic_matter_pct=1.0,
                soil_type=SoilType.SANDY_LOAM,
            ),
            macronutrients=MacronutrientResults(
                nitrogen_ppm=8.0,  # Deficient
                phosphorus_ppm=4.0,  # Deficient
                potassium_ppm=60.0,  # Deficient
                calcium_ppm=500.0,
                magnesium_ppm=80.0,
                sulfur_ppm=5.0,
            ),
            micronutrients=MicronutrientResults(
                iron_ppm=2.0,
                manganese_ppm=1.5,
                zinc_ppm=0.5,
                copper_ppm=0.2,
                boron_ppm=0.2,
            ),
        )

        plan = advisor.generate_plan(
            soil_test=soil_test,
            crop_type="wheat",
            target_yield_tons_ha=5.0,
            field_area_ha=Decimal("10.0"),
        )

        # Should recommend significant fertilizer
        total_n_fertilizer = sum(
            rec.nutrients.get("N", 0) for rec in plan.fertilizer_recommendations
        )

        assert total_n_fertilizer > 0, (
            "Should recommend N fertilizer when soil N is deficient"
        )

        # Should NOT have salinity management (EC is low)
        has_salinity_management = any(
            "salinity" in rec.purpose.lower() or "leach" in rec.purpose.lower()
            for rec in plan.other_amendments
        )

        assert not has_salinity_management, (
            "Low EC should not trigger salinity management"
        )


# Mark all tests in this module as critical
pytestmark = pytest.mark.critical
