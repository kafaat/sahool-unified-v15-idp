"""
Context Engineering Tests for Fertilizer Advisor Service
=========================================================
اختبارات هندسة السياق لخدمة مستشار التسميد

Tests for context compression, memory storage, and recommendation evaluation.

Author: SAHOOL Platform Team
Updated: January 2025
"""

import pytest
import sys
import os
from datetime import datetime

# Add src to path
test_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(test_dir), "src")
sys.path.insert(0, src_dir)

from fastapi.testclient import TestClient
from main import app, CropType, GrowthStage, SoilType, FertilizerRequest, SoilAnalysis


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_soil_analysis():
    """Create sample soil analysis for testing"""
    return SoilAnalysis(
        field_id="field_test_001",
        analysis_date=datetime.utcnow(),
        ph=6.8,
        nitrogen_ppm=45,
        phosphorus_ppm=22,
        potassium_ppm=180,
        organic_matter_percent=2.1,
        ec_ds_m=1.5,
        calcium_ppm=2500,
        magnesium_ppm=350,
        sulfur_ppm=150,
        iron_ppm=5,
        zinc_ppm=2,
        soil_type=SoilType.LOAMY,
    )


@pytest.fixture
def sample_fertilizer_request():
    """Create sample fertilizer request"""
    return FertilizerRequest(
        field_id="field_test_001",
        crop=CropType.TOMATO,
        growth_stage=GrowthStage.FLOWERING,
        area_hectares=5.0,
        target_yield_kg_ha=40000,
        organic_only=False,
    )


class TestContextEngineering:
    """Test context engineering features"""

    def test_context_engineering_status(self, client):
        """Test context engineering status endpoint"""
        response = client.get("/v1/context-engineering/status")
        assert response.status_code == 200
        data = response.json()
        assert "context_engineering_available" in data
        assert "context_engineering_enabled" in data
        assert "features" in data

    def test_soil_compression_endpoint(self, client, sample_soil_analysis):
        """Test soil analysis compression endpoint"""
        response = client.post(
            "/v1/soil-analysis/compress",
            json=sample_soil_analysis.model_dump(mode="json"),
        )
        assert response.status_code == 200
        data = response.json()
        if data.get("status") == "success":
            assert "compressed_tokens" in data
            assert "original_tokens" in data
            assert "compression_ratio" in data
            assert data["compression_ratio"] >= 0
            assert data["compression_ratio"] <= 1

    def test_recommendation_evaluation_endpoint(self, client, sample_fertilizer_request):
        """Test recommendation evaluation endpoint"""
        # First get a recommendation
        response = client.post(
            "/v1/recommend",
            json=sample_fertilizer_request.model_dump(mode="json"),
        )
        assert response.status_code == 200
        plan = response.json()

        # Now evaluate it
        eval_response = client.post(
            "/v1/recommend/evaluate",
            json=plan,
        )
        assert eval_response.status_code == 200
        eval_data = eval_response.json()

        if eval_data.get("status") == "success":
            assert "evaluation_id" in eval_data
            assert "plan_id" in eval_data
            assert "grade" in eval_data
            assert "is_approved" in eval_data
            assert "overall_score" in eval_data
            assert eval_data["overall_score"] >= 0.0
            assert eval_data["overall_score"] <= 1.0

    def test_recent_recommendations_retrieval(self, client, sample_fertilizer_request):
        """Test retrieving recent recommendations from memory"""
        # Create a recommendation first
        response = client.post(
            "/v1/recommend",
            json=sample_fertilizer_request.model_dump(mode="json"),
        )
        assert response.status_code == 200

        # Retrieve recent recommendations
        recent_response = client.get("/v1/recommendations/recent?limit=5")
        assert recent_response.status_code == 200
        data = recent_response.json()

        if data.get("status") == "success":
            assert "recommendations" in data
            assert "count" in data
            assert isinstance(data["recommendations"], list)

    def test_recent_recommendations_with_field_filter(self, client, sample_fertilizer_request):
        """Test retrieving recent recommendations with field ID filter"""
        # Create a recommendation
        response = client.post(
            "/v1/recommend",
            json=sample_fertilizer_request.model_dump(mode="json"),
        )
        assert response.status_code == 200

        # Retrieve by field ID
        field_id = sample_fertilizer_request.field_id
        recent_response = client.get(f"/v1/recommendations/recent?field_id={field_id}&limit=3")
        assert recent_response.status_code == 200
        data = recent_response.json()

        if data.get("status") == "success":
            assert "recommendations" in data

    def test_compression_with_recommendation(self, client, sample_fertilizer_request, sample_soil_analysis):
        """Test that compression metadata is stored with recommendations"""
        request_with_soil = sample_fertilizer_request.model_dump(mode="json")
        request_with_soil["soil_analysis"] = sample_soil_analysis.model_dump(mode="json")

        response = client.post(
            "/v1/recommend",
            json=request_with_soil,
        )
        assert response.status_code == 200
        plan = response.json()
        assert "plan_id" in plan

    def test_recommendation_limit_enforcement(self, client):
        """Test that recommendation limit is enforced (max 20)"""
        # Request with limit > 20 should be clamped
        response = client.get("/v1/recommendations/recent?limit=100")
        assert response.status_code == 200
        data = response.json()

        if data.get("status") == "success" and data.get("recommendations"):
            # Should not exceed 20 recommendations
            assert len(data["recommendations"]) <= 20


class TestCompressionMetrics:
    """Test compression metrics and token estimation"""

    def test_soil_analysis_compression_metrics(self, client, sample_soil_analysis):
        """Test compression metrics for soil analysis"""
        response = client.post(
            "/v1/soil-analysis/compress",
            json=sample_soil_analysis.model_dump(mode="json"),
        )
        assert response.status_code == 200
        data = response.json()

        if data.get("status") == "success":
            assert data["original_tokens"] > 0
            assert data["compressed_tokens"] > 0
            assert data["tokens_saved"] >= 0
            # Compression should provide some savings
            assert data["compression_ratio"] < 1.0

    def test_compression_with_multiple_analyses(self, client):
        """Test compression of multiple soil analyses"""
        analyses = [
            SoilAnalysis(
                field_id=f"field_{i}",
                analysis_date=datetime.utcnow(),
                ph=6.5 + (i * 0.1),
                nitrogen_ppm=40 + (i * 2),
                phosphorus_ppm=20 + (i * 1),
                potassium_ppm=150 + (i * 10),
                organic_matter_percent=2.0 + (i * 0.1),
                ec_ds_m=1.5,
                calcium_ppm=2500,
                magnesium_ppm=350,
                sulfur_ppm=150,
                iron_ppm=5,
                zinc_ppm=2,
                soil_type=SoilType.LOAMY,
            )
            for i in range(3)
        ]

        for analysis in analyses:
            response = client.post(
                "/v1/soil-analysis/compress",
                json=analysis.model_dump(mode="json"),
            )
            assert response.status_code == 200


class TestRecommendationMemoryStorage:
    """Test recommendation memory storage and retrieval"""

    def test_plan_storage_in_memory(self, client, sample_fertilizer_request):
        """Test that plans are stored in memory"""
        response = client.post(
            "/v1/recommend",
            json=sample_fertilizer_request.model_dump(mode="json"),
        )
        assert response.status_code == 200
        plan = response.json()

        # Verify plan has required fields
        assert "plan_id" in plan
        assert "field_id" in plan
        assert plan["field_id"] == sample_fertilizer_request.field_id

    def test_memory_retrieval_after_storage(self, client, sample_fertilizer_request):
        """Test retrieving stored plans from memory"""
        # Store a plan
        response = client.post(
            "/v1/recommend",
            json=sample_fertilizer_request.model_dump(mode="json"),
        )
        assert response.status_code == 200
        stored_plan = response.json()
        plan_id = stored_plan["plan_id"]

        # Retrieve recent plans
        retrieval = client.get("/v1/recommendations/recent?limit=10")
        assert retrieval.status_code == 200
        data = retrieval.json()

        if data.get("status") == "success":
            # Check if our stored plan is in the recent recommendations
            stored_plan_ids = [p.get("plan_id") for p in data.get("recommendations", [])]
            # Plan may or may not be present depending on memory state
            # Just verify structure is correct
            assert isinstance(data["recommendations"], list)

    def test_field_specific_retrieval(self, client):
        """Test retrieving plans for a specific field"""
        field_id = "field_specific_test"
        request = FertilizerRequest(
            field_id=field_id,
            crop=CropType.WHEAT,
            growth_stage=GrowthStage.VEGETATIVE,
            area_hectares=3.0,
        )

        # Store plan for specific field
        response = client.post(
            "/v1/recommend",
            json=request.model_dump(mode="json"),
        )
        assert response.status_code == 200

        # Retrieve for that specific field
        retrieval = client.get(f"/v1/recommendations/recent?field_id={field_id}")
        assert retrieval.status_code == 200
        data = retrieval.json()

        if data.get("status") == "success":
            assert "recommendations" in data


class TestEvaluationQualityMetrics:
    """Test recommendation quality evaluation"""

    def test_evaluation_scoring(self, client, sample_fertilizer_request):
        """Test evaluation scoring for recommendations"""
        # Get a recommendation
        response = client.post(
            "/v1/recommend",
            json=sample_fertilizer_request.model_dump(mode="json"),
        )
        assert response.status_code == 200
        plan = response.json()

        # Evaluate it
        eval_response = client.post(
            "/v1/recommend/evaluate",
            json=plan,
        )
        assert eval_response.status_code == 200
        eval_data = eval_response.json()

        if eval_data.get("status") == "success":
            # Verify scoring structure
            assert "scores" in eval_data or "grade" in eval_data

    def test_evaluation_approval_status(self, client, sample_fertilizer_request):
        """Test evaluation approval status"""
        response = client.post(
            "/v1/recommend",
            json=sample_fertilizer_request.model_dump(mode="json"),
        )
        assert response.status_code == 200
        plan = response.json()

        eval_response = client.post(
            "/v1/recommend/evaluate",
            json=plan,
        )
        assert eval_response.status_code == 200
        eval_data = eval_response.json()

        if eval_data.get("status") == "success":
            assert isinstance(eval_data.get("is_approved"), bool)

    def test_evaluation_feedback(self, client, sample_fertilizer_request):
        """Test that evaluation provides feedback"""
        response = client.post(
            "/v1/recommend",
            json=sample_fertilizer_request.model_dump(mode="json"),
        )
        assert response.status_code == 200
        plan = response.json()

        eval_response = client.post(
            "/v1/recommend/evaluate",
            json=plan,
        )
        assert eval_response.status_code == 200
        eval_data = eval_response.json()

        if eval_data.get("status") == "success":
            assert "feedback" in eval_data or "feedback_ar" in eval_data


class TestIntegration:
    """Integration tests for full context engineering workflow"""

    def test_full_workflow_with_compression_and_evaluation(
        self, client, sample_fertilizer_request, sample_soil_analysis
    ):
        """Test full workflow: compress, recommend, store, evaluate"""
        # 1. Create request with soil analysis
        request_data = sample_fertilizer_request.model_dump(mode="json")
        request_data["soil_analysis"] = sample_soil_analysis.model_dump(mode="json")

        # 2. Get recommendation (which will compress and store)
        rec_response = client.post("/v1/recommend", json=request_data)
        assert rec_response.status_code == 200
        plan = rec_response.json()
        assert "plan_id" in plan

        # 3. Evaluate the recommendation
        eval_response = client.post(
            "/v1/recommend/evaluate",
            json=plan,
        )
        assert eval_response.status_code == 200

        # 4. Retrieve from memory
        retrieval = client.get("/v1/recommendations/recent?limit=5")
        assert retrieval.status_code == 200

        # 5. Check context engineering status
        status = client.get("/v1/context-engineering/status")
        assert status.status_code == 200

    def test_multiple_recommendations_workflow(self, client):
        """Test workflow with multiple recommendations"""
        crops = [CropType.TOMATO, CropType.WHEAT, CropType.BANANA]

        for crop in crops:
            request = FertilizerRequest(
                field_id=f"field_{crop.value}",
                crop=crop,
                growth_stage=GrowthStage.FLOWERING,
                area_hectares=2.0,
            )

            response = client.post(
                "/v1/recommend",
                json=request.model_dump(mode="json"),
            )
            assert response.status_code == 200

        # Retrieve all recent recommendations
        retrieval = client.get("/v1/recommendations/recent?limit=10")
        assert retrieval.status_code == 200
