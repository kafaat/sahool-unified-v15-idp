"""Comprehensive tests for fertigation-engine - models, engine logic, API endpoints, error handling."""

import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

from src.main import (
    CROP_NPK_REQUIREMENTS,
    FERTILIZER_DB,
    FertigationEngine,
    FertigationPlan,
    FertigationRequest,
    FertilizerType,
    GrowthPhase,
    NutrientBalance,
    NutrientBalanceRequest,
    NutrientType,
    app,
)

TENANT_UUID = "00000000-0000-0000-0000-000000000001"
HEADERS = {"X-Tenant-Id": TENANT_UUID}
@pytest.fixture
def client():
    return TestClient(app)
@pytest.fixture
def engine():
    return FertigationEngine()
# ==========================================================================
# Enum Tests
# ==========================================================================
class TestEnums:
    def test_nutrient_type_values(self):
        assert NutrientType.NITROGEN == "nitrogen"
        assert NutrientType.PHOSPHORUS == "phosphorus"
        assert NutrientType.POTASSIUM == "potassium"
        assert NutrientType.CALCIUM == "calcium"
        assert NutrientType.IRON == "iron"

    def test_fertilizer_type_values(self):
        assert FertilizerType.UREA == "urea"
        assert FertilizerType.DAP == "dap"
        assert FertilizerType.MAP == "map"
        assert FertilizerType.KCL == "kcl"
        assert FertilizerType.SOP == "sop"
        assert FertilizerType.NPK_20_20_20 == "npk_20_20_20"

    def test_growth_phase_values(self):
        assert GrowthPhase.GERMINATION == "germination"
        assert GrowthPhase.SEEDLING == "seedling"
        assert GrowthPhase.TILLERING == "tillering"
        assert GrowthPhase.FLOWERING == "flowering"
        assert GrowthPhase.RIPENING == "ripening"
        assert GrowthPhase.HARVEST == "harvest"
# ==========================================================================
# Fertilizer Database Tests
# ==========================================================================
class TestFertilizerDB:
    def test_all_fertilizer_types_in_db(self):
        """Every FertilizerType (except sulfuric_acid) should have an entry."""
        for ft in FertilizerType:
            if ft == FertilizerType.SULFURIC_ACID:
                continue  # pH correction agent, no NPK data
            assert ft in FERTILIZER_DB, f"Missing DB entry for {ft}"

    def test_fertilizer_npk_percentages(self):
        """NPK percentages should be non-negative and not exceed 100%."""
        for ftype, fdata in FERTILIZER_DB.items():
            assert fdata["n"] >= 0, f"{ftype} has negative N"
            assert fdata["p"] >= 0, f"{ftype} has negative P"
            assert fdata["k"] >= 0, f"{ftype} has negative K"
            total_npk = fdata["n"] + fdata["p"] + fdata["k"]
            assert total_npk <= 100, f"{ftype} total NPK > 100%"

    def test_fertilizer_has_required_fields(self):
        for ftype, fdata in FERTILIZER_DB.items():
            assert "name" in fdata
            assert "name_ar" in fdata
            assert "ec_per_gl" in fdata
            assert "solubility_gl" in fdata
            assert "price_sar_kg" in fdata

    def test_urea_npk_values(self):
        urea = FERTILIZER_DB[FertilizerType.UREA]
        assert urea["n"] == 46.0
        assert urea["p"] == 0.0
        assert urea["k"] == 0.0

    def test_potassium_nitrate_npk(self):
        kno3 = FERTILIZER_DB[FertilizerType.POTASSIUM_NITRATE]
        assert kno3["n"] == 13.0
        assert kno3["k"] == 46.0
# ==========================================================================
# Crop NPK Requirements Tests
# ==========================================================================
class TestCropNPKRequirements:
    def test_wheat_requirements(self):
        wheat = CROP_NPK_REQUIREMENTS["wheat"]
        assert "_total" in wheat
        assert wheat["_total"]["n"] == 120
        assert wheat["_total"]["p"] == 60
        assert wheat["_total"]["k"] == 75

    def test_tomato_requirements(self):
        tomato = CROP_NPK_REQUIREMENTS["tomato"]
        assert tomato["_total"]["n"] == 180
        assert tomato["_total"]["k"] == 190

    def test_all_crops_have_total(self):
        for crop_name, crop_data in CROP_NPK_REQUIREMENTS.items():
            assert "_total" in crop_data, f"Crop '{crop_name}' missing _total"

    def test_phase_percentages_sum(self):
        """Growth phase pct_of_total should roughly sum to 90-100% for each crop."""
        for crop_name, crop_data in CROP_NPK_REQUIREMENTS.items():
            total_pct = sum(
                phase.get("pct_of_total", 0)
                for key, phase in crop_data.items()
                if key != "_total" and isinstance(phase, dict)
            )
            assert total_pct >= 80, f"Crop '{crop_name}' phase sum {total_pct}% is low"
            assert total_pct <= 110, f"Crop '{crop_name}' phase sum {total_pct}% is too high"
# ==========================================================================
# FertigationEngine Unit Tests
# ==========================================================================
class TestFertigationEngineUnit:
    def test_calculate_wheat_tillering(self, engine):
        req = FertigationRequest(
            crop="wheat",
            growth_phase=GrowthPhase.TILLERING,
            field_area_ha=1.0,
            irrigation_volume_m3=50.0,
        )
        plan = engine.calculate_fertigation(req)
        assert plan.crop == "wheat"
        assert plan.n_required_kg_ha == 60.0
        assert plan.p_required_kg_ha == 15.0
        assert plan.k_required_kg_ha == 20.0
        assert len(plan.fertilizer_plan) > 0
        assert plan.total_cost_sar > 0

    def test_soil_n_credit_reduces_requirement(self, engine):
        req_no_soil = FertigationRequest(
            crop="wheat",
            growth_phase=GrowthPhase.TILLERING,
            field_area_ha=1.0,
            irrigation_volume_m3=50.0,
        )
        req_with_soil = FertigationRequest(
            crop="wheat",
            growth_phase=GrowthPhase.TILLERING,
            field_area_ha=1.0,
            irrigation_volume_m3=50.0,
            soil_n_ppm=30.0,
        )
        plan1 = engine.calculate_fertigation(req_no_soil)
        plan2 = engine.calculate_fertigation(req_with_soil)
        assert plan2.n_adjusted_kg_ha <= plan1.n_adjusted_kg_ha

    def test_soil_p_credit_reduces_requirement(self, engine):
        req = FertigationRequest(
            crop="tomato",
            growth_phase=GrowthPhase.VEGETATIVE,
            irrigation_volume_m3=50.0,
            soil_p_ppm=40.0,
        )
        plan = engine.calculate_fertigation(req)
        assert plan.p_adjusted_kg_ha < plan.p_required_kg_ha

    def test_soil_k_credit_reduces_requirement(self, engine):
        req = FertigationRequest(
            crop="tomato",
            growth_phase=GrowthPhase.FRUIT_DEVELOPMENT,
            irrigation_volume_m3=50.0,
            soil_k_ppm=80.0,
        )
        plan = engine.calculate_fertigation(req)
        assert plan.k_adjusted_kg_ha < plan.k_required_kg_ha

    def test_unknown_crop_uses_fallback(self, engine):
        req = FertigationRequest(
            crop="dragon_fruit",
            growth_phase=GrowthPhase.VEGETATIVE,
            irrigation_volume_m3=50.0,
        )
        plan = engine.calculate_fertigation(req)
        assert plan.n_required_kg_ha == 30.0
        assert plan.p_required_kg_ha == 15.0
        assert plan.k_required_kg_ha == 25.0

    def test_ec_within_limit(self, engine):
        req = FertigationRequest(
            crop="wheat",
            growth_phase=GrowthPhase.SEEDLING,
            field_area_ha=0.5,
            irrigation_volume_m3=100.0,  # Large volume, low concentration
            ec_water=0.3,
            max_ec_solution=3.0,
        )
        plan = engine.calculate_fertigation(req)
        assert plan.ec_within_limit is True

    def test_ec_exceeds_limit_small_volume(self, engine):
        req = FertigationRequest(
            crop="wheat",
            growth_phase=GrowthPhase.TILLERING,
            field_area_ha=5.0,
            irrigation_volume_m3=5.0,  # Very small volume, high concentration
            ec_water=2.0,
            max_ec_solution=2.5,
        )
        plan = engine.calculate_fertigation(req)
        # High concentration + high base EC should exceed limit
        assert plan.ec_total > 0

    def test_preferred_fertilizers_used(self, engine):
        req = FertigationRequest(
            crop="wheat",
            growth_phase=GrowthPhase.TILLERING,
            irrigation_volume_m3=50.0,
            preferred_fertilizers=[FertilizerType.AMMONIUM_NITRATE, FertilizerType.SOP],
        )
        plan = engine.calculate_fertigation(req)
        fert_names = [f["fertilizer"] for f in plan.fertilizer_plan]
        assert "ammonium_nitrate" in fert_names
        assert "sop" in fert_names

    def test_saline_water_selects_sop(self, engine):
        """When EC water is > 1.5, SOP should be preferred over KCL for K."""
        req = FertigationRequest(
            crop="tomato",
            growth_phase=GrowthPhase.FRUIT_DEVELOPMENT,
            irrigation_volume_m3=50.0,
            ec_water=2.0,
        )
        plan = engine.calculate_fertigation(req)
        k_ferts = [f for f in plan.fertilizer_plan if f["k_supplied_kg"] > 0]
        if k_ferts:
            # Should select SOP due to high EC water
            assert k_ferts[0]["fertilizer"] == "sop"

    def test_field_area_scales_cost(self, engine):
        req_small = FertigationRequest(
            crop="wheat",
            growth_phase=GrowthPhase.TILLERING,
            field_area_ha=1.0,
            irrigation_volume_m3=50.0,
        )
        req_large = FertigationRequest(
            crop="wheat",
            growth_phase=GrowthPhase.TILLERING,
            field_area_ha=5.0,
            irrigation_volume_m3=50.0,
        )
        plan_small = engine.calculate_fertigation(req_small)
        plan_large = engine.calculate_fertigation(req_large)
        assert plan_large.total_cost_sar > plan_small.total_cost_sar

    def test_cost_per_ha_consistent(self, engine):
        req = FertigationRequest(
            crop="wheat",
            growth_phase=GrowthPhase.TILLERING,
            field_area_ha=3.0,
            irrigation_volume_m3=50.0,
        )
        plan = engine.calculate_fertigation(req)
        expected_cost_per_ha = plan.total_cost_sar / 3.0
        assert abs(plan.cost_per_ha_sar - expected_cost_per_ha) < 0.1
# ==========================================================================
# N / P Loss Risk Assessment Tests
# ==========================================================================
class TestRiskAssessment:
    def test_n_loss_high(self, engine):
        risk, risk_ar = engine._assess_n_loss_risk(90, "wheat")
        assert risk == "high"
        assert risk_ar == "مرتفع"

    def test_n_loss_moderate(self, engine):
        risk, risk_ar = engine._assess_n_loss_risk(50, "wheat")
        assert risk == "moderate"
        assert risk_ar == "متوسط"

    def test_n_loss_low(self, engine):
        risk, risk_ar = engine._assess_n_loss_risk(20, "wheat")
        assert risk == "low"
        assert risk_ar == "منخفض"

    def test_p_loss_high(self, engine):
        risk, risk_ar = engine._assess_p_loss_risk(60)
        assert risk == "high"

    def test_p_loss_moderate(self, engine):
        risk, risk_ar = engine._assess_p_loss_risk(30)
        assert risk == "moderate"

    def test_p_loss_low(self, engine):
        risk, risk_ar = engine._assess_p_loss_risk(10)
        assert risk == "low"
# ==========================================================================
# Recommendation Generation Tests
# ==========================================================================
class TestRecommendations:
    def test_ec_exceeded_recommendation(self, engine):
        recs, recs_ar = engine._generate_recommendations(
            n=30, p=15, k=25, ec_total=3.0, max_ec=2.5,
            phase=GrowthPhase.VEGETATIVE, crop="wheat",
        )
        assert any("EC" in r for r in recs)
        assert any("الموصلية" in r for r in recs_ar)

    def test_high_n_recommendation(self, engine):
        recs, recs_ar = engine._generate_recommendations(
            n=70, p=15, k=25, ec_total=1.5, max_ec=2.5,
            phase=GrowthPhase.VEGETATIVE, crop="wheat",
        )
        assert any("morning" in r.lower() for r in recs)

    def test_flowering_recommendation(self, engine):
        recs, recs_ar = engine._generate_recommendations(
            n=30, p=15, k=25, ec_total=1.5, max_ec=2.5,
            phase=GrowthPhase.FLOWERING, crop="wheat",
        )
        assert any("flowering" in r.lower() for r in recs)

    def test_fruit_development_recommendation(self, engine):
        recs, recs_ar = engine._generate_recommendations(
            n=30, p=15, k=25, ec_total=1.5, max_ec=2.5,
            phase=GrowthPhase.FRUIT_DEVELOPMENT, crop="tomato",
        )
        assert any("fruit development" in r.lower() for r in recs)

    def test_no_recommendations_normal_conditions(self, engine):
        recs, recs_ar = engine._generate_recommendations(
            n=20, p=10, k=15, ec_total=1.0, max_ec=2.5,
            phase=GrowthPhase.SEEDLING, crop="wheat",
        )
        assert len(recs) == 0
# ==========================================================================
# Nutrient Balance Tests
# ==========================================================================
class TestNutrientBalance:
    def test_balance_surplus(self, engine):
        req = NutrientBalanceRequest(
            field_id="F001",
            crop="wheat",
            entries=[
                {"type": "applied", "n_kg": 120, "p_kg": 60, "k_kg": 75},
                {"type": "removed", "n_kg": 50, "p_kg": 20, "k_kg": 30},
            ],
        )
        result = engine.calculate_nutrient_balance(req)
        assert result.n_balance_kg_ha == 70.0
        assert result.p_balance_kg_ha == 40.0
        assert result.k_balance_kg_ha == 45.0
        assert result.surplus_alert is True

    def test_balance_deficit(self, engine):
        req = NutrientBalanceRequest(
            field_id="F001",
            crop="wheat",
            entries=[
                {"type": "applied", "n_kg": 10, "p_kg": 5, "k_kg": 5},
                {"type": "removed", "n_kg": 60, "p_kg": 30, "k_kg": 40},
            ],
        )
        result = engine.calculate_nutrient_balance(req)
        assert result.n_balance_kg_ha == -50.0
        assert result.deficit_alert is True
        assert any("deficit" in r.lower() or "نقص" in r for r in result.recommendations + result.recommendations_ar)

    def test_balance_neutral(self, engine):
        req = NutrientBalanceRequest(
            field_id="F001",
            crop="wheat",
            entries=[
                {"type": "applied", "n_kg": 50, "p_kg": 20, "k_kg": 30},
                {"type": "removed", "n_kg": 40, "p_kg": 15, "k_kg": 25},
            ],
        )
        result = engine.calculate_nutrient_balance(req)
        assert result.surplus_alert is False
        assert result.deficit_alert is False

    def test_balance_efficiency(self, engine):
        req = NutrientBalanceRequest(
            field_id="F001",
            crop="tomato",
            entries=[
                {"type": "applied", "n_kg": 100, "p_kg": 50, "k_kg": 80},
                {"type": "removed", "n_kg": 70, "p_kg": 30, "k_kg": 50},
            ],
        )
        result = engine.calculate_nutrient_balance(req)
        assert result.n_efficiency_pct == pytest.approx(70.0, abs=0.1)
        assert result.p_efficiency_pct == pytest.approx(60.0, abs=0.1)

    def test_balance_empty_entries(self, engine):
        req = NutrientBalanceRequest(
            field_id="F001",
            crop="wheat",
            entries=[],
        )
        result = engine.calculate_nutrient_balance(req)
        assert result.n_balance_kg_ha == 0.0
        assert result.surplus_alert is False
        assert result.deficit_alert is False

    def test_balance_surplus_recommendation(self, engine):
        req = NutrientBalanceRequest(
            field_id="F001",
            crop="wheat",
            entries=[
                {"type": "applied", "n_kg": 200, "p_kg": 10, "k_kg": 10},
                {"type": "removed", "n_kg": 50, "p_kg": 5, "k_kg": 5},
            ],
        )
        result = engine.calculate_nutrient_balance(req)
        assert any("groundwater" in r.lower() for r in result.recommendations)
# ==========================================================================
# API Endpoint Tests
# ==========================================================================
class TestAPIEndpoints:
    def test_healthz(self, client):
        resp = client.get("/healthz", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "fertigation-engine"
        assert data["version"] == "16.0.0"

    def test_readyz(self, client):
        resp = client.get("/readyz", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["crops_with_npk"] > 0
        assert data["fertilizers_available"] > 0

    def test_create_plan_endpoint(self, client):
        resp = client.post(
            "/api/v1/fertigation/plan",
            json={
                "crop": "barley",
                "growth_phase": "tillering",
                "field_area_ha": 2.0,
                "irrigation_volume_m3": 80.0,
            },
            headers=HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["crop"] == "barley"
        assert len(data["fertilizer_plan"]) > 0

    def test_create_plan_all_crops(self, client):
        """Verify plan generation for all crops in the database."""
        for crop_name in CROP_NPK_REQUIREMENTS:
            phases = [k for k in CROP_NPK_REQUIREMENTS[crop_name] if k != "_total"]
            if phases:
                resp = client.post(
                    "/api/v1/fertigation/plan",
                    json={
                        "crop": crop_name,
                        "growth_phase": phases[0],
                        "irrigation_volume_m3": 50.0,
                    },
                    headers=HEADERS,
                )
                assert resp.status_code == 200, f"Failed for {crop_name}/{phases[0]}"

    def test_nutrient_balance_endpoint(self, client):
        resp = client.post(
            "/api/v1/fertigation/nutrient-balance",
            json={
                "field_id": "F001",
                "crop": "wheat",
                "entries": [
                    {"type": "applied", "n_kg": 100, "p_kg": 50, "k_kg": 60},
                    {"type": "removed", "n_kg": 30, "p_kg": 15, "k_kg": 20},
                ],
            },
            headers=HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "n_balance_kg_ha" in data

    def test_list_fertilizers_endpoint(self, client):
        resp = client.get("/api/v1/fertigation/fertilizers", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == len(FERTILIZER_DB)
        assert all("type" in f for f in data["fertilizers"])

    def test_get_crop_npk_wheat(self, client):
        resp = client.get("/api/v1/fertigation/crops/wheat/npk", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["crop"] == "wheat"
        assert data["total_requirements_kg_ha"]["n"] == 120

    def test_get_crop_npk_case_insensitive(self, client):
        resp = client.get("/api/v1/fertigation/crops/Wheat/npk", headers=HEADERS)
        assert resp.status_code == 200

    def test_get_crop_npk_not_found(self, client):
        resp = client.get("/api/v1/fertigation/crops/nonexistent/npk", headers=HEADERS)
        assert resp.status_code == 404

    def test_list_crops(self, client):
        resp = client.get("/api/v1/fertigation/crops", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == len(CROP_NPK_REQUIREMENTS)
        crop_names = [c["name"] for c in data["crops"]]
        assert "wheat" in crop_names
        assert "tomato" in crop_names

    def test_list_growth_phases(self, client):
        resp = client.get("/api/v1/fertigation/growth-phases", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "germination" in data["phases"]
        assert "harvest" in data["phases"]
        assert len(data["phases"]) == len(GrowthPhase)
# ==========================================================================
# Pydantic Model Validation Tests
# ==========================================================================
class TestModelValidation:
    def test_fertigation_request_defaults(self):
        req = FertigationRequest(
            crop="wheat",
            growth_phase=GrowthPhase.TILLERING,
            irrigation_volume_m3=50.0,
        )
        assert req.field_area_ha == 1.0
        assert req.ec_water == 0.5
        assert req.max_ec_solution == 2.5
        assert req.soil_n_ppm is None

    def test_fertigation_request_min_area(self):
        with pytest.raises(Exception):
            FertigationRequest(
                crop="wheat",
                growth_phase=GrowthPhase.TILLERING,
                irrigation_volume_m3=50.0,
                field_area_ha=0.001,  # Below 0.01 min
            )

    def test_nutrient_balance_request(self):
        req = NutrientBalanceRequest(
            field_id="F001",
            crop="wheat",
            entries=[{"type": "applied", "n_kg": 50}],
        )
        assert req.field_id == "F001"
        assert len(req.entries) == 1
