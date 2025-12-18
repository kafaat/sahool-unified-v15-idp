"""
E2E Tests for Fertilizer Advisor Service - خدمة مستشار الأسمدة
Tests NPK recommendations, soil analysis, and deficiency detection
"""

import pytest
import httpx
from conftest import FERTILIZER_URL


class TestFertilizerServiceHealth:
    """Health check tests for fertilizer service."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: httpx.AsyncClient):
        """Test /healthz returns healthy status."""
        response = await async_client.get(f"{FERTILIZER_URL}/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "crop_count" in data
        assert data["crop_count"] >= 12  # At least 12 crops supported


class TestCropsEndpoint:
    """Tests for /v1/crops endpoint."""

    @pytest.mark.asyncio
    async def test_get_supported_crops(self, async_client: httpx.AsyncClient):
        """Test listing supported crops with NPK requirements."""
        response = await async_client.get(f"{FERTILIZER_URL}/v1/crops")
        assert response.status_code == 200
        data = response.json()

        assert "crops" in data
        crops = data["crops"]

        # Should have at least 12 crops
        assert len(crops) >= 12

        # Check for Yemen-specific crops
        crop_ids = [c["id"] for c in crops]
        expected_crops = ["tomato", "wheat", "coffee", "qat", "banana", "date_palm"]
        for expected in expected_crops:
            assert expected in crop_ids

        # Validate crop structure
        tomato = next(c for c in crops if c["id"] == "tomato")
        assert "name_ar" in tomato
        assert "npk_requirements" in tomato
        assert "n" in tomato["npk_requirements"]
        assert "p" in tomato["npk_requirements"]
        assert "k" in tomato["npk_requirements"]


class TestFertilizersEndpoint:
    """Tests for /v1/fertilizers endpoint."""

    @pytest.mark.asyncio
    async def test_get_fertilizer_catalog(self, async_client: httpx.AsyncClient):
        """Test fertilizer catalog with prices."""
        response = await async_client.get(f"{FERTILIZER_URL}/v1/fertilizers")
        assert response.status_code == 200
        data = response.json()

        assert "fertilizers" in data
        fertilizers = data["fertilizers"]

        # Should have synthetic and organic options
        assert len(fertilizers) >= 10

        # Check for common fertilizers
        fertilizer_ids = [f["id"] for f in fertilizers]
        expected = ["urea", "dap", "npk_15_15_15", "organic_compost"]
        for expected_id in expected:
            assert expected_id in fertilizer_ids

        # Validate structure
        urea = next(f for f in fertilizers if f["id"] == "urea")
        assert "name_ar" in urea
        assert "npk_content" in urea
        assert "price_per_kg" in urea  # Price in YER
        assert "type" in urea  # synthetic or organic
        assert urea["npk_content"]["n"] > 0  # Urea is nitrogen-rich

    @pytest.mark.asyncio
    async def test_fertilizer_prices_are_positive(self, async_client: httpx.AsyncClient):
        """Test that all fertilizer prices are positive."""
        response = await async_client.get(f"{FERTILIZER_URL}/v1/fertilizers")
        data = response.json()

        for fertilizer in data["fertilizers"]:
            assert fertilizer["price_per_kg"] > 0


class TestRecommendEndpoint:
    """Tests for /v1/recommend endpoint - NPK recommendations."""

    @pytest.mark.asyncio
    async def test_basic_recommendation(self, async_client: httpx.AsyncClient, test_field_data, test_soil_data):
        """Test basic fertilizer recommendation."""
        request_data = {
            "field_id": test_field_data["field_id"],
            "crop": "tomato",
            "area_hectares": test_field_data["area_hectares"],
            "growth_stage": "vegetative",
            "soil_analysis": test_soil_data
        }

        response = await async_client.post(
            f"{FERTILIZER_URL}/v1/recommend",
            json=request_data
        )
        assert response.status_code == 200
        data = response.json()

        # Check recommendation structure
        assert "field_id" in data
        assert "crop" in data
        assert "recommendations" in data
        assert "total_cost" in data

        recommendations = data["recommendations"]
        assert len(recommendations) > 0

        for rec in recommendations:
            assert "fertilizer_id" in rec
            assert "amount_kg" in rec
            assert "cost" in rec
            assert "application_method" in rec
            assert rec["amount_kg"] > 0

    @pytest.mark.asyncio
    async def test_recommendation_with_budget(self, async_client: httpx.AsyncClient, test_field_data, test_soil_data):
        """Test recommendation respects budget constraints."""
        request_data = {
            "field_id": test_field_data["field_id"],
            "crop": "wheat",
            "area_hectares": 10,
            "growth_stage": "tillering",
            "soil_analysis": test_soil_data,
            "budget_limit": 50000  # 50,000 YER limit
        }

        response = await async_client.post(
            f"{FERTILIZER_URL}/v1/recommend",
            json=request_data
        )
        assert response.status_code == 200
        data = response.json()

        # Total cost should not exceed budget
        assert data["total_cost"] <= 50000

    @pytest.mark.asyncio
    async def test_recommendation_all_growth_stages(self, async_client: httpx.AsyncClient, test_field_data, test_soil_data):
        """Test recommendations for different growth stages."""
        growth_stages = ["seedling", "vegetative", "flowering", "fruiting", "maturity"]

        for stage in growth_stages:
            request_data = {
                "field_id": test_field_data["field_id"],
                "crop": "tomato",
                "area_hectares": 5,
                "growth_stage": stage,
                "soil_analysis": test_soil_data
            }

            response = await async_client.post(
                f"{FERTILIZER_URL}/v1/recommend",
                json=request_data
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_recommendation_includes_schedule(self, async_client: httpx.AsyncClient, test_field_data, test_soil_data):
        """Test that recommendation includes application schedule."""
        request_data = {
            "field_id": test_field_data["field_id"],
            "crop": "coffee",
            "area_hectares": 2,
            "growth_stage": "vegetative",
            "soil_analysis": test_soil_data,
            "split_applications": True
        }

        response = await async_client.post(
            f"{FERTILIZER_URL}/v1/recommend",
            json=request_data
        )
        assert response.status_code == 200
        data = response.json()

        assert "schedule" in data
        schedule = data["schedule"]
        assert len(schedule) > 0

        for application in schedule:
            assert "week" in application or "date" in application
            assert "fertilizers" in application


class TestSoilAnalysisInterpretation:
    """Tests for /v1/soil-analysis/interpret endpoint."""

    @pytest.mark.asyncio
    async def test_interpret_soil_analysis(self, async_client: httpx.AsyncClient, test_soil_data):
        """Test soil analysis interpretation."""
        response = await async_client.post(
            f"{FERTILIZER_URL}/v1/soil-analysis/interpret",
            json=test_soil_data
        )
        assert response.status_code == 200
        data = response.json()

        # Check interpretation structure
        assert "ph_status" in data
        assert "nitrogen_status" in data
        assert "phosphorus_status" in data
        assert "potassium_status" in data
        assert "recommendations" in data
        assert "recommendations_ar" in data

    @pytest.mark.asyncio
    async def test_interpret_deficient_soil(self, async_client: httpx.AsyncClient):
        """Test interpretation of nutrient-deficient soil."""
        deficient_soil = {
            "ph": 5.0,  # Too acidic
            "nitrogen_ppm": 5,  # Very low
            "phosphorus_ppm": 3,  # Very low
            "potassium_ppm": 50,  # Low
            "organic_matter_percent": 0.5
        }

        response = await async_client.post(
            f"{FERTILIZER_URL}/v1/soil-analysis/interpret",
            json=deficient_soil
        )
        assert response.status_code == 200
        data = response.json()

        # Should indicate deficiencies
        assert data["nitrogen_status"] in ["low", "very_low", "deficient"]
        assert data["phosphorus_status"] in ["low", "very_low", "deficient"]

        # Should have multiple recommendations
        assert len(data["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_interpret_includes_warnings(self, async_client: httpx.AsyncClient):
        """Test that interpretation includes warnings for extreme values."""
        extreme_soil = {
            "ph": 8.5,  # Very alkaline
            "nitrogen_ppm": 100,  # Very high
            "ec_ds_m": 4.0  # High salinity
        }

        response = await async_client.post(
            f"{FERTILIZER_URL}/v1/soil-analysis/interpret",
            json=extreme_soil
        )
        assert response.status_code == 200
        data = response.json()

        assert "warnings" in data
        assert len(data["warnings"]) > 0


class TestDeficiencySymptoms:
    """Tests for /v1/deficiency-symptoms/{crop} endpoint."""

    @pytest.mark.asyncio
    async def test_get_deficiency_symptoms(self, async_client: httpx.AsyncClient):
        """Test getting nutrient deficiency symptoms for a crop."""
        response = await async_client.get(f"{FERTILIZER_URL}/v1/deficiency-symptoms/tomato")
        assert response.status_code == 200
        data = response.json()

        assert "crop" in data
        assert "symptoms" in data

        symptoms = data["symptoms"]
        # Should have symptoms for main nutrients
        nutrient_types = [s["nutrient"] for s in symptoms]
        assert "nitrogen" in nutrient_types
        assert "phosphorus" in nutrient_types
        assert "potassium" in nutrient_types

        # Each symptom should have description
        for symptom in symptoms:
            assert "nutrient" in symptom
            assert "visual_symptoms" in symptom
            assert "visual_symptoms_ar" in symptom

    @pytest.mark.asyncio
    async def test_deficiency_symptoms_all_crops(self, async_client: httpx.AsyncClient):
        """Test deficiency symptoms available for all supported crops."""
        crops = ["tomato", "wheat", "coffee", "banana", "potato"]

        for crop in crops:
            response = await async_client.get(f"{FERTILIZER_URL}/v1/deficiency-symptoms/{crop}")
            assert response.status_code == 200
            data = response.json()
            assert data["crop"] == crop
            assert len(data["symptoms"]) > 0
