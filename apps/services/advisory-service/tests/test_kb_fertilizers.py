"""
Tests for Fertilizer Knowledge Base - advisory-service
"""

import pytest
from src.kb.fertilizers import (
    FERTILIZERS,
    calculate_dose,
    get_fertilizer,
    get_fertilizers_by_type,
    get_fertilizers_for_nutrient,
)


class TestGetFertilizer:
    """Tests for get_fertilizer function"""

    def test_get_urea(self):
        f = get_fertilizer("urea")
        assert f is not None
        assert f["analysis"]["N"] == 46
        assert f["name_en"] == "Urea"

    def test_get_nonexistent(self):
        assert get_fertilizer("nonexistent") is None

    def test_all_fertilizers_have_required_fields(self):
        for fert_id, fert in FERTILIZERS.items():
            assert "name_ar" in fert, f"{fert_id} missing name_ar"
            assert "name_en" in fert, f"{fert_id} missing name_en"
            assert "analysis" in fert, f"{fert_id} missing analysis"
            assert "type" in fert, f"{fert_id} missing type"
            assert "application_methods" in fert, f"{fert_id} missing application_methods"


class TestGetFertilizersByType:
    """Tests for get_fertilizers_by_type function"""

    def test_nitrogen_fertilizers(self):
        results = get_fertilizers_by_type("nitrogen")
        assert len(results) > 0
        for r in results:
            assert r["type"] == "nitrogen"
            assert "id" in r

    def test_compound_fertilizers(self):
        results = get_fertilizers_by_type("compound")
        assert len(results) > 0

    def test_unknown_type(self):
        results = get_fertilizers_by_type("unknown_type")
        assert len(results) == 0


class TestGetFertilizersForNutrient:
    """Tests for get_fertilizers_for_nutrient function"""

    def test_nitrogen_providers(self):
        results = get_fertilizers_for_nutrient("N")
        assert len(results) > 0
        # Should be sorted by nutrient content descending
        contents = [r["nutrient_content"] for r in results]
        assert contents == sorted(contents, reverse=True)

    def test_potassium_providers(self):
        results = get_fertilizers_for_nutrient("K")
        assert len(results) > 0

    def test_unknown_nutrient(self):
        results = get_fertilizers_for_nutrient("Xx")
        assert len(results) == 0


class TestCalculateDose:
    """Tests for calculate_dose function"""

    def test_urea_nitrogen_dose(self):
        # Urea is 46% N. To supply 46 kg/ha N, need 100 kg/ha urea
        dose = calculate_dose("urea", "N", 46)
        assert dose is not None
        assert abs(dose - 100.0) < 0.01

    def test_nonexistent_fertilizer(self):
        assert calculate_dose("nonexistent", "N", 50) is None

    def test_nutrient_not_in_fertilizer(self):
        # Urea has no K
        assert calculate_dose("urea", "K", 50) is None

    def test_zero_nutrient_content(self):
        # Urea has 0% P
        assert calculate_dose("urea", "P", 50) is None

    def test_dap_phosphorus_dose(self):
        # DAP is 46% P. To supply 46 kg/ha P, need 100 kg/ha DAP
        dose = calculate_dose("dap", "P", 46)
        assert dose is not None
        assert abs(dose - 100.0) < 0.01
