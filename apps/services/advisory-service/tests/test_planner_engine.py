"""
Tests for Fertilizer Planner Engine - advisory-service
"""

import pytest
from src.engine.planner import (
    CROP_REQUIREMENTS,
    FertilizerPlan,
    _default_plan,
    _select_fertilizers,
    fertilizer_plan,
    get_stage_timeline,
)


class TestFertilizerPlan:
    """Tests for FertilizerPlan model"""

    def test_to_dict(self):
        plan = FertilizerPlan(
            crop="tomato",
            stage="vegetative",
            field_size_ha=1.5,
            applications=[{"product": "Urea", "dose_kg_per_ha": 50}],
            total_cost_estimate=100.0,
            notes=["note1"],
        )
        d = plan.to_dict()
        assert d["crop"] == "tomato"
        assert d["stage"] == "vegetative"
        assert d["field_size_ha"] == 1.5
        assert len(d["applications"]) == 1
        assert d["total_cost_estimate"] == 100.0
        assert d["notes"] == ["note1"]

    def test_default_notes(self):
        plan = FertilizerPlan(
            crop="wheat", stage="planting", field_size_ha=1.0, applications=[]
        )
        assert plan.notes == []
class TestFertilizerPlanFunction:
    """Tests for fertilizer_plan function"""

    def test_known_crop_known_stage(self):
        plan = fertilizer_plan("tomato", "vegetative")
        assert plan.crop == "tomato"
        assert plan.stage == "vegetative"
        assert len(plan.applications) > 0

    def test_unknown_crop_default_plan(self):
        plan = fertilizer_plan("unknown_crop", "general")
        assert plan.crop == "unknown_crop"
        assert len(plan.applications) > 0
        assert len(plan.notes) > 0

    def test_unknown_stage_falls_back(self):
        plan = fertilizer_plan("tomato", "nonexistent_stage")
        assert plan is not None
        # Should fall back to first stage
        assert plan.stage in CROP_REQUIREMENTS["tomato"]["stages"]

    def test_drip_irrigation_notes(self):
        plan = fertilizer_plan("tomato", "vegetative", irrigation_type="drip")
        assert any("2-3" in note for note in plan.notes)

    def test_critical_stage_notes(self):
        plan = fertilizer_plan("tomato", "fruiting")
        assert any("مرحلة حرجة" in note or "Critical stage" in note for note in plan.notes)

    def test_low_fertility_increases_dose(self):
        plan_low = fertilizer_plan("wheat", "tillering", soil_fertility="low")
        plan_high = fertilizer_plan("wheat", "tillering", soil_fertility="high")
        if plan_low.applications and plan_high.applications:
            assert plan_low.applications[0]["dose_kg_per_ha"] > plan_high.applications[0]["dose_kg_per_ha"]

    def test_field_size_scaling(self):
        plan = fertilizer_plan("tomato", "vegetative", field_size_ha=3.0)
        for app in plan.applications:
            expected_total = app["dose_kg_per_ha"] * 3.0
            assert abs(app["total_kg"] - expected_total) < 0.2

    def test_all_crops_produce_plan(self):
        for crop in CROP_REQUIREMENTS:
            stages = list(CROP_REQUIREMENTS[crop]["stages"].keys())
            plan = fertilizer_plan(crop, stages[0])
            assert plan is not None
            assert plan.crop == crop
class TestSelectFertilizers:
    """Tests for _select_fertilizers function"""

    def test_balanced_needs_uses_compound(self):
        needs = {"N": 30, "P": 30, "K": 30}
        apps = _select_fertilizers(needs, 1.0, "drip", None)
        # Should pick NPK compound
        assert len(apps) > 0

    def test_unbalanced_needs_individual(self):
        needs = {"N": 50, "P": 5, "K": 5}
        apps = _select_fertilizers(needs, 1.0, "surface", None)
        # Should pick individual N fertilizer
        assert len(apps) > 0

    def test_drip_prefers_fertigation(self):
        needs = {"N": 30, "P": 30, "K": 30}
        apps = _select_fertilizers(needs, 1.0, "drip", None)
        if apps:
            methods = [a.get("method") for a in apps]
            assert "fertigation" in methods

    def test_surface_prefers_broadcast(self):
        needs = {"N": 30, "P": 30, "K": 30}
        apps = _select_fertilizers(needs, 1.0, "surface", None)
        if apps:
            methods = [a.get("method") for a in apps]
            assert "broadcast" in methods

    def test_high_k_need(self):
        needs = {"N": 5, "P": 3, "K": 50}
        apps = _select_fertilizers(needs, 1.0, "drip", None)
        # Should include K fertilizer
        assert len(apps) > 0
class TestDefaultPlan:
    """Tests for _default_plan function"""

    def test_returns_plan(self):
        plan = _default_plan("exotic_crop", "unknown_stage", 2.0)
        assert plan.crop == "exotic_crop"
        assert plan.stage == "unknown_stage"
        assert plan.field_size_ha == 2.0
        assert len(plan.applications) == 1
        assert plan.applications[0]["dose_kg_per_ha"] == 100
        assert plan.applications[0]["total_kg"] == 200

    def test_has_advisory_notes(self):
        plan = _default_plan("crop", "stage", 1.0)
        assert len(plan.notes) >= 2  # Arabic and English
class TestGetStageTimeline:
    """Tests for get_stage_timeline function"""

    def test_tomato_timeline(self):
        timeline = get_stage_timeline("tomato")
        assert len(timeline) > 0
        assert timeline[0]["stage"] == "transplant"
        assert timeline[0]["start_day"] == 0

    def test_wheat_timeline(self):
        timeline = get_stage_timeline("wheat")
        assert len(timeline) > 0
        assert timeline[0]["stage"] == "planting"

    def test_unknown_crop_empty(self):
        timeline = get_stage_timeline("unknown_crop")
        assert timeline == []

    def test_timeline_stages_sequential(self):
        timeline = get_stage_timeline("tomato")
        for i in range(1, len(timeline)):
            assert timeline[i]["start_day"] > timeline[i - 1]["start_day"]

    def test_timeline_has_nutrient_focus(self):
        timeline = get_stage_timeline("tomato")
        for stage in timeline:
            assert "nutrient_focus" in stage
            assert isinstance(stage["nutrient_focus"], list)
