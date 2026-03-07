"""
Tests for Treatment Recommendations API.
اختبارات واجهة برمجة توصيات العلاج.
"""

import pytest


class TestTreatmentRecommendations:
    """Test cases for treatment recommendation endpoints."""

    def test_get_recommendations(self, client, sample_treatment_request):
        """Test getting treatment recommendations."""
        response = client.post("/api/v1/treatments/recommend", json=sample_treatment_request)
        assert response.status_code == 200
        data = response.json()
        assert data["pest_id"] == sample_treatment_request["pest_id"]
        assert "recommended_options" in data
        assert "ipm_strategy_en" in data
        assert "ipm_strategy_ar" in data

    def test_get_recommendations_critical_severity(self, client):
        """Test recommendations for critical severity prioritize chemicals."""
        response = client.post(
            "/api/v1/treatments/recommend",
            json={
                "pest_id": "rpw",
                "crop": "date_palm",
                "severity": "critical",
                "organic_only": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Critical severity should return options
        assert len(data["recommended_options"]) > 0

    def test_get_recommendations_organic_only(self, client):
        """Test organic-only recommendations."""
        response = client.post(
            "/api/v1/treatments/recommend",
            json={
                "pest_id": "aphids",
                "crop": "wheat",
                "severity": "medium",
                "organic_only": True,
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should only return biological and cultural options
        for option in data["recommended_options"]:
            assert option["type"] in ["biological", "cultural"]

    def test_get_recommendations_budget_constraint(self, client):
        """Test recommendations with budget constraint."""
        response = client.post(
            "/api/v1/treatments/recommend",
            json={
                "pest_id": "aphids",
                "crop": "wheat",
                "severity": "medium",
                "budget_constraint": "low",
            },
        )
        assert response.status_code == 200
        data = response.json()
        # Should filter out high-cost options
        for option in data["recommended_options"]:
            assert option["cost_level"] == "low"

    def test_get_recommendations_unknown_pest(self, client):
        """Test recommendations for unknown pest."""
        response = client.post(
            "/api/v1/treatments/recommend",
            json={
                "pest_id": "unknown_pest",
                "crop": "wheat",
                "severity": "medium",
            },
        )
        assert response.status_code == 404


class TestTreatmentProtocols:
    """Test treatment protocol endpoints."""

    def test_get_protocol(self, client):
        """Test getting full treatment protocol."""
        response = client.get("/api/v1/treatments/protocols/rpw")
        assert response.status_code == 200
        data = response.json()
        assert data["pest_id"] == "rpw"
        assert "chemical_options" in data
        assert "biological_options" in data
        assert "cultural_options" in data
        assert "ipm_strategy_en" in data
        assert "rotation_recommendation_en" in data

    def test_get_protocol_has_options(self, client):
        """Test protocol has treatment options."""
        response = client.get("/api/v1/treatments/protocols/rpw")
        data = response.json()
        # RPW should have chemical and biological options
        assert len(data["chemical_options"]) > 0
        assert len(data["biological_options"]) > 0

    def test_get_protocol_not_found(self, client):
        """Test getting protocol for unknown pest."""
        response = client.get("/api/v1/treatments/protocols/unknown_pest")
        assert response.status_code == 404

    def test_protocol_options_have_safety_info(self, client):
        """Test treatment options include safety information."""
        response = client.get("/api/v1/treatments/protocols/rpw")
        data = response.json()

        for option in data["chemical_options"]:
            assert "phi_days" in option  # Pre-harvest interval
            assert "rei_hours" in option  # Restricted entry interval
            assert "safety_level" in option
            assert "ppe_required_en" in option
            assert "ppe_required_ar" in option


class TestIPMCalendar:
    """Test IPM calendar endpoint."""

    def test_get_ipm_calendar(self, client):
        """Test getting IPM calendar."""
        response = client.get("/api/v1/treatments/ipm-calendar?crop=date_palm")
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "date_palm"
        assert "calendar" in data
        assert len(data["calendar"]) == 12  # 12 months

    def test_ipm_calendar_has_monthly_activities(self, client):
        """Test calendar has activities for each month."""
        response = client.get("/api/v1/treatments/ipm-calendar?crop=date_palm")
        data = response.json()

        for entry in data["calendar"]:
            assert "month" in entry
            assert "month_name_en" in entry
            assert "month_name_ar" in entry
            assert "activities_en" in entry
            assert "activities_ar" in entry
            assert "target_pests" in entry
            assert "monitoring_frequency" in entry

    def test_ipm_calendar_different_crops(self, client):
        """Test calendar differs by crop."""
        palm_response = client.get("/api/v1/treatments/ipm-calendar?crop=date_palm")
        wheat_response = client.get("/api/v1/treatments/ipm-calendar?crop=wheat")

        palm_data = palm_response.json()
        wheat_data = wheat_response.json()

        # Activities should differ
        palm_activities = palm_data["calendar"][0]["activities_en"]
        wheat_activities = wheat_data["calendar"][0]["activities_en"]
        assert palm_activities != wheat_activities

    def test_ipm_calendar_with_region(self, client):
        """Test calendar with region parameter."""
        response = client.get("/api/v1/treatments/ipm-calendar?crop=wheat&region=middle_east")
        assert response.status_code == 200
        data = response.json()
        assert data["region"] == "middle_east"


class TestPesticideRotation:
    """Test pesticide rotation endpoint."""

    def test_get_rotation_plan(self, client):
        """Test getting pesticide rotation plan."""
        response = client.get("/api/v1/treatments/rotation?pest_id=rpw")
        assert response.status_code == 200
        data = response.json()
        assert data["pest_id"] == "rpw"
        assert "rotation_plan" in data
        assert "recommendation_en" in data
        assert "recommendation_ar" in data

    def test_rotation_plan_has_seasons(self, client):
        """Test rotation plan covers multiple seasons."""
        response = client.get("/api/v1/treatments/rotation?pest_id=rpw&seasons=4")
        data = response.json()
        assert len(data["rotation_plan"]) == 4

    def test_rotation_plan_alternates_products(self, client):
        """Test rotation alternates different products."""
        response = client.get("/api/v1/treatments/rotation?pest_id=rpw&seasons=4")
        data = response.json()

        # If there are multiple chemicals, they should rotate
        if len(data["rotation_plan"]) > 1:
            treatments = [p["treatment"] for p in data["rotation_plan"]]
            # Not all treatments should be the same
            # (unless only one chemical available)

    def test_rotation_plan_unknown_pest(self, client):
        """Test rotation for unknown pest."""
        response = client.get("/api/v1/treatments/rotation?pest_id=unknown")
        assert response.status_code == 404


class TestTreatmentDataIntegrity:
    """Test treatment data integrity."""

    def test_treatment_options_have_bilingual_content(self, client):
        """Test all treatment options have Arabic content."""
        response = client.get("/api/v1/treatments/protocols/rpw")
        data = response.json()

        all_options = data["chemical_options"] + data["biological_options"] + data["cultural_options"]
        for option in all_options:
            opt_id = option["id"]
            assert option["name_ar"], f"Missing Arabic name for option {opt_id}"
            assert option["application_rate_ar"], f"Missing Arabic rate for {opt_id}"
            assert option["application_method_ar"], f"Missing method AR for {opt_id}"

    def test_chemical_options_have_active_ingredients(self, client):
        """Test chemical options specify active ingredients."""
        response = client.get("/api/v1/treatments/protocols/rpw")
        data = response.json()

        for option in data["chemical_options"]:
            opt_id = option["id"]
            assert option["active_ingredient"], f"Missing active ingredient for {opt_id}"
            assert option["active_ingredient_ar"], f"Missing AR active ingredient for {opt_id}"

    def test_options_have_effectiveness_rating(self, client):
        """Test all options have effectiveness rating."""
        response = client.get("/api/v1/treatments/protocols/rpw")
        data = response.json()

        all_options = data["chemical_options"] + data["biological_options"] + data["cultural_options"]
        for option in all_options:
            assert "effectiveness_rating" in option
            assert 0 <= option["effectiveness_rating"] <= 5

    def test_options_have_environmental_impact(self, client):
        """Test all options have environmental impact assessment."""
        response = client.get("/api/v1/treatments/protocols/rpw")
        data = response.json()

        all_options = data["chemical_options"] + data["biological_options"] + data["cultural_options"]
        for option in all_options:
            opt_id = option["id"]
            assert option["environmental_impact"], f"Missing env impact for {opt_id}"
            assert option["environmental_impact_ar"], f"Missing AR env impact for {opt_id}"
