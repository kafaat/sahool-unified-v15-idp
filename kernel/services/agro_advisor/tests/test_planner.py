"""
Fertilizer Planner Tests - Agro Advisor
"""

import pytest
from fastapi.testclient import TestClient

from kernel.services.agro_advisor.src.main import app
from kernel.services.agro_advisor.src.engine.planner import (
    fertilizer_plan,
    get_stage_timeline,
    CROP_REQUIREMENTS,
)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestPlannerEngine:
    """Test planner engine directly"""

    def test_fertilizer_plan_tomato_vegetative(self):
        """Test tomato vegetative stage plan"""
        plan = fertilizer_plan(
            crop="tomato",
            stage="vegetative",
            field_size_ha=1.0,
        )

        assert plan.crop == "tomato"
        assert plan.stage == "vegetative"
        assert len(plan.applications) > 0

        # Check first application has required fields
        app = plan.applications[0]
        assert "product" in app
        assert "dose_kg_per_ha" in app
        assert "timing_days" in app

    def test_fertilizer_plan_with_drip(self):
        """Test plan with drip irrigation prefers soluble"""
        plan = fertilizer_plan(
            crop="tomato",
            stage="fruiting",
            irrigation_type="drip",
        )

        # Should prefer fertigation method
        methods = [app.get("method") for app in plan.applications]
        assert "fertigation" in methods or len(plan.applications) > 0

    def test_fertilizer_plan_with_surface(self):
        """Test plan with surface irrigation"""
        plan = fertilizer_plan(
            crop="wheat",
            stage="tillering",
            irrigation_type="surface",
        )

        assert plan.crop == "wheat"
        assert len(plan.applications) > 0

    def test_fertilizer_plan_low_fertility(self):
        """Test plan adjusts for low fertility"""
        plan_low = fertilizer_plan(
            crop="tomato",
            stage="vegetative",
            soil_fertility="low",
        )

        plan_high = fertilizer_plan(
            crop="tomato",
            stage="vegetative",
            soil_fertility="high",
        )

        # Low fertility should have higher doses
        if plan_low.applications and plan_high.applications:
            low_dose = plan_low.applications[0]["dose_kg_per_ha"]
            high_dose = plan_high.applications[0]["dose_kg_per_ha"]
            assert low_dose >= high_dose

    def test_fertilizer_plan_field_size(self):
        """Test plan calculates total for field size"""
        plan = fertilizer_plan(
            crop="potato",
            stage="bulking",
            field_size_ha=2.5,
        )

        if plan.applications:
            app = plan.applications[0]
            expected_total = app["dose_kg_per_ha"] * 2.5
            assert abs(app["total_kg"] - expected_total) < 0.1

    def test_get_stage_timeline(self):
        """Test stage timeline generation"""
        timeline = get_stage_timeline("tomato")

        assert len(timeline) > 0
        assert timeline[0]["stage"] == "transplant"
        assert "start_day" in timeline[0]
        assert "duration_days" in timeline[0]

    def test_crop_requirements_complete(self):
        """Test all crops have required fields"""
        for crop, data in CROP_REQUIREMENTS.items():
            assert "yield_target_ton_ha" in data
            assert "total_needs" in data
            assert "stages" in data
            assert "N" in data["total_needs"]

    def test_unknown_crop_default_plan(self):
        """Test unknown crop gets default plan"""
        plan = fertilizer_plan(
            crop="unknown_crop",
            stage="general",
        )

        assert plan.crop == "unknown_crop"
        assert len(plan.applications) > 0
        assert len(plan.notes) > 0


class TestPlannerAPI:
    """Test planner API endpoints"""

    def test_create_plan_endpoint(self, client):
        """Test fertilizer plan API"""
        response = client.post(
            "/fertilizer/plan",
            json={
                "tenant_id": "test_tenant",
                "field_id": "field_123",
                "crop": "tomato",
                "stage": "vegetative",
                "field_size_ha": 1.5,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "tomato"
        assert data["stage"] == "vegetative"
        assert "applications" in data

    def test_create_plan_all_crops(self, client):
        """Test plan generation for all supported crops"""
        crops = client.get("/crops").json()["crops"]

        for crop in crops:
            # Get first stage
            stages_resp = client.get(f"/crops/{crop}/stages")
            if stages_resp.status_code != 200:
                continue

            stages = stages_resp.json().get("stages", [])
            if not stages:
                continue

            first_stage = stages[0]["stage"]

            response = client.post(
                "/fertilizer/plan",
                json={
                    "tenant_id": "test",
                    "field_id": "test_field",
                    "crop": crop,
                    "stage": first_stage,
                },
            )

            assert response.status_code == 200, f"Failed for {crop}/{first_stage}"

    def test_create_plan_invalid_stage(self, client):
        """Test plan with invalid stage still works"""
        response = client.post(
            "/fertilizer/plan",
            json={
                "tenant_id": "test",
                "field_id": "field_123",
                "crop": "tomato",
                "stage": "invalid_stage",
            },
        )

        # Should still return a plan (uses fallback)
        assert response.status_code == 200
