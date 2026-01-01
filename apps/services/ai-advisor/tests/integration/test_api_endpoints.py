"""
Integration Tests for API Endpoints
اختبارات التكامل لنقاط النهاية API

Tests all FastAPI endpoints with mock dependencies.
"""

import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
class TestHealthEndpoints:
    """Test health check endpoints"""

    async def test_health_check(self, async_client):
        """Test /healthz endpoint returns healthy status"""
        response = await async_client.get("/healthz")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-advisor"
        assert "version" in data


@pytest.mark.asyncio
@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
class TestAdvisorEndpoints:
    """Test AI advisor endpoints"""

    async def test_ask_question_success(
        self, async_client, sample_question_request, mock_supervisor
    ):
        """Test /v1/advisor/ask endpoint with valid request"""
        response = await async_client.post(
            "/v1/advisor/ask", json=sample_question_request
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert mock_supervisor.coordinate.called

    async def test_ask_question_without_context(self, async_client, mock_supervisor):
        """Test ask endpoint without additional context"""
        request_data = {"question": "What crops grow best in Yemen?", "language": "en"}

        response = await async_client.post("/v1/advisor/ask", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"

    async def test_ask_question_arabic(self, async_client, mock_supervisor):
        """Test ask endpoint with Arabic language"""
        request_data = {"question": "ما هو أفضل وقت لزراعة القمح؟", "language": "ar"}

        response = await async_client.post("/v1/advisor/ask", json=request_data)

        assert response.status_code == status.HTTP_200_OK

    async def test_ask_question_service_not_initialized(self, async_client):
        """Test ask endpoint when service is not initialized"""
        with patch("main.app_state", {}):
            request_data = {"question": "Test question", "language": "en"}

            response = await async_client.post("/v1/advisor/ask", json=request_data)

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    async def test_diagnose_disease_success(
        self, async_client, sample_diagnose_request, mock_disease_expert
    ):
        """Test /v1/advisor/diagnose endpoint"""
        response = await async_client.post(
            "/v1/advisor/diagnose", json=sample_diagnose_request
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert mock_disease_expert.diagnose.called

    async def test_diagnose_disease_with_image(
        self, async_client, mock_disease_expert, mock_crop_health_tool
    ):
        """Test disease diagnosis with image analysis"""
        request_data = {
            "crop_type": "tomato",
            "symptoms": {"leaf_spots": True},
            "image_path": "/tmp/crop_image.jpg",
        }

        response = await async_client.post("/v1/advisor/diagnose", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        assert mock_crop_health_tool.analyze_image.called
        assert mock_disease_expert.diagnose.called

    async def test_diagnose_disease_without_image(
        self, async_client, mock_disease_expert
    ):
        """Test disease diagnosis without image"""
        request_data = {
            "crop_type": "wheat",
            "symptoms": {"yellowing": True, "wilting": False},
        }

        response = await async_client.post("/v1/advisor/diagnose", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        assert mock_disease_expert.diagnose.called

    async def test_get_recommendations_irrigation(
        self, async_client, sample_recommendation_request, mock_irrigation_advisor
    ):
        """Test /v1/advisor/recommend endpoint for irrigation"""
        response = await async_client.post(
            "/v1/advisor/recommend", json=sample_recommendation_request
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert mock_irrigation_advisor.recommend_irrigation.called

    async def test_get_recommendations_fertilizer(self, async_client, mock_supervisor):
        """Test recommendations endpoint for fertilizer"""
        request_data = {
            "crop_type": "corn",
            "growth_stage": "vegetative",
            "recommendation_type": "fertilizer",
            "field_data": {"soil": {"type": "clay"}},
        }

        response = await async_client.post("/v1/advisor/recommend", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        assert mock_supervisor.coordinate.called

    async def test_get_recommendations_pest(self, async_client, mock_supervisor):
        """Test recommendations endpoint for pest control"""
        request_data = {
            "crop_type": "wheat",
            "growth_stage": "flowering",
            "recommendation_type": "pest",
        }

        response = await async_client.post("/v1/advisor/recommend", json=request_data)

        assert response.status_code == status.HTTP_200_OK
        assert mock_supervisor.coordinate.called

    async def test_get_recommendations_invalid_type(self, async_client):
        """Test recommendations with invalid type"""
        request_data = {
            "crop_type": "corn",
            "growth_stage": "vegetative",
            "recommendation_type": "invalid_type",
        }

        response = await async_client.post("/v1/advisor/recommend", json=request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_analyze_field_complete(
        self,
        async_client,
        sample_field_analysis_request,
        mock_field_analyst,
        mock_disease_expert,
        mock_irrigation_advisor,
        mock_yield_predictor,
        mock_satellite_tool,
    ):
        """Test /v1/advisor/analyze-field with all analyses"""
        response = await async_client.post(
            "/v1/advisor/analyze-field", json=sample_field_analysis_request
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "analysis" in data["data"]

        # Verify all agents were called
        assert mock_satellite_tool.get_ndvi.called
        assert mock_field_analyst.analyze_field.called
        assert mock_disease_expert.assess_risk.called
        assert mock_irrigation_advisor.recommend_irrigation.called
        assert mock_yield_predictor.predict_yield.called

    async def test_analyze_field_partial(
        self, async_client, mock_field_analyst, mock_satellite_tool
    ):
        """Test field analysis with selective analyses"""
        request_data = {
            "field_id": "field_001",
            "crop_type": "wheat",
            "include_disease_check": False,
            "include_irrigation": False,
            "include_yield_prediction": False,
        }

        response = await async_client.post(
            "/v1/advisor/analyze-field", json=request_data
        )

        assert response.status_code == status.HTTP_200_OK
        # Should still call satellite and field analyst
        assert mock_satellite_tool.get_ndvi.called
        assert mock_field_analyst.analyze_field.called

    async def test_analyze_field_service_not_ready(self, async_client):
        """Test field analysis when service is not initialized"""
        with patch("main.app_state", {}):
            request_data = {"field_id": "field_001", "crop_type": "wheat"}

            response = await async_client.post(
                "/v1/advisor/analyze-field", json=request_data
            )

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    async def test_list_agents(self, async_client, mock_supervisor):
        """Test /v1/advisor/agents endpoint"""
        response = await async_client.get("/v1/advisor/agents")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "agents" in data
        assert "total" in data
        assert mock_supervisor.get_available_agents.called

    async def test_list_agents_not_initialized(self, async_client):
        """Test list agents when supervisor not initialized"""
        with patch("main.app_state", {}):
            response = await async_client.get("/v1/advisor/agents")

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    async def test_list_tools(self, async_client):
        """Test /v1/advisor/tools endpoint"""
        response = await async_client.get("/v1/advisor/tools")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "tools" in data
        assert "total" in data
        assert isinstance(data["tools"], list)

    async def test_list_tools_empty_state(self, async_client):
        """Test list tools with empty app state"""
        with patch("main.app_state", {}):
            response = await async_client.get("/v1/advisor/tools")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total"] == 0


@pytest.mark.asyncio
@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
class TestRAGEndpoints:
    """Test RAG system endpoints"""

    async def test_get_rag_info_success(
        self, async_client, mock_knowledge_retriever, mock_embeddings_manager
    ):
        """Test /v1/advisor/rag/info endpoint"""
        response = await async_client.get("/v1/advisor/rag/info")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "collection" in data
        assert "embeddings_model" in data
        assert mock_knowledge_retriever.get_collection_info.called
        assert mock_embeddings_manager.get_model_info.called

    async def test_get_rag_info_not_initialized(self, async_client):
        """Test RAG info when system not initialized"""
        with patch("main.app_state", {}):
            response = await async_client.get("/v1/advisor/rag/info")

            assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
class TestRequestValidation:
    """Test request validation"""

    async def test_ask_question_missing_required_field(self, async_client):
        """Test ask endpoint with missing required field"""
        request_data = {
            "language": "en"
            # Missing 'question' field
        }

        response = await async_client.post("/v1/advisor/ask", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_diagnose_missing_crop_type(self, async_client):
        """Test diagnose endpoint with missing crop_type"""
        request_data = {
            "symptoms": {"yellowing": True}
            # Missing 'crop_type'
        }

        response = await async_client.post("/v1/advisor/diagnose", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_recommend_missing_fields(self, async_client):
        """Test recommend endpoint with missing required fields"""
        request_data = {
            "crop_type": "wheat"
            # Missing 'growth_stage' and 'recommendation_type'
        }

        response = await async_client.post("/v1/advisor/recommend", json=request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_analyze_field_missing_field_id(self, async_client):
        """Test analyze field with missing field_id"""
        request_data = {
            "crop_type": "corn"
            # Missing 'field_id'
        }

        response = await async_client.post(
            "/v1/advisor/analyze-field", json=request_data
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
class TestErrorHandling:
    """Test error handling in endpoints"""

    async def test_ask_question_llm_error(self, async_client):
        """Test ask endpoint when LLM fails"""
        mock_supervisor = AsyncMock()
        mock_supervisor.coordinate = AsyncMock(side_effect=Exception("LLM API error"))

        with patch("main.app_state", {"supervisor": mock_supervisor}):
            request_data = {"question": "Test question", "language": "en"}

            response = await async_client.post("/v1/advisor/ask", json=request_data)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    async def test_diagnose_tool_error(self, async_client):
        """Test diagnose endpoint when tool fails"""
        mock_tool = AsyncMock()
        mock_tool.analyze_image = AsyncMock(
            side_effect=Exception("Image analysis failed")
        )

        mock_agent = AsyncMock()

        with patch(
            "main.app_state",
            {
                "agents": {"disease_expert": mock_agent},
                "tools": {"crop_health": mock_tool},
            },
        ):
            request_data = {
                "crop_type": "tomato",
                "symptoms": {"spots": True},
                "image_path": "/tmp/image.jpg",
            }

            response = await async_client.post(
                "/v1/advisor/diagnose", json=request_data
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    async def test_analyze_field_satellite_error(self, async_client):
        """Test field analysis when satellite tool fails"""
        mock_satellite = AsyncMock()
        mock_satellite.get_ndvi = AsyncMock(
            side_effect=Exception("Satellite data unavailable")
        )

        with patch(
            "main.app_state", {"agents": {}, "tools": {"satellite": mock_satellite}}
        ):
            request_data = {"field_id": "field_001", "crop_type": "wheat"}

            response = await async_client.post(
                "/v1/advisor/analyze-field", json=request_data
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
