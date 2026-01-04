"""
Integration Tests for AI Advisor API Endpoints
اختبارات التكامل لنقاط نهاية API المستشار الذكي
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_all_dependencies():
    """Mock all external dependencies"""
    mocks = {}

    # Mock langchain components
    with patch("src.main.ChatAnthropic") as mock_claude:
        mocks["claude"] = mock_claude

        # Mock agents
        with patch("src.main.FieldAnalystAgent") as mock_field:
            with patch("src.main.DiseaseExpertAgent") as mock_disease:
                with patch("src.main.IrrigationAdvisorAgent") as mock_irrigation:
                    with patch("src.main.YieldPredictorAgent") as mock_yield:

                        # Create mock agent instances
                        mock_field_instance = AsyncMock()
                        mock_field_instance.analyze_field = AsyncMock(
                            return_value={"analysis": "good"}
                        )
                        mock_field.return_value = mock_field_instance

                        mock_disease_instance = AsyncMock()
                        mock_disease_instance.diagnose = AsyncMock(
                            return_value={"disease": "none"}
                        )
                        mock_disease_instance.assess_risk = AsyncMock(
                            return_value={"risk": "low"}
                        )
                        mock_disease.return_value = mock_disease_instance

                        mock_irrigation_instance = AsyncMock()
                        mock_irrigation_instance.recommend_irrigation = AsyncMock(
                            return_value={"schedule": "daily"}
                        )
                        mock_irrigation.return_value = mock_irrigation_instance

                        mock_yield_instance = AsyncMock()
                        mock_yield_instance.predict_yield = AsyncMock(
                            return_value={"yield": 1000}
                        )
                        mock_yield.return_value = mock_yield_instance

                        mocks["field_agent"] = mock_field
                        mocks["disease_agent"] = mock_disease
                        mocks["irrigation_agent"] = mock_irrigation
                        mocks["yield_agent"] = mock_yield

                        # Mock tools
                        with patch("src.main.CropHealthTool") as mock_crop_tool:
                            with patch("src.main.WeatherTool") as mock_weather_tool:
                                with patch("src.main.SatelliteTool") as mock_sat_tool:
                                    with patch("src.main.AgroTool") as mock_agro_tool:

                                        crop_tool_instance = AsyncMock()
                                        crop_tool_instance.analyze_image = AsyncMock(
                                            return_value={"healthy": True}
                                        )
                                        mock_crop_tool.return_value = crop_tool_instance

                                        weather_tool_instance = AsyncMock()
                                        mock_weather_tool.return_value = (
                                            weather_tool_instance
                                        )

                                        sat_tool_instance = AsyncMock()
                                        sat_tool_instance.get_ndvi = AsyncMock(
                                            return_value={"ndvi": 0.8}
                                        )
                                        mock_sat_tool.return_value = sat_tool_instance

                                        agro_tool_instance = AsyncMock()
                                        mock_agro_tool.return_value = agro_tool_instance

                                        mocks["crop_tool"] = mock_crop_tool
                                        mocks["weather_tool"] = mock_weather_tool
                                        mocks["sat_tool"] = mock_sat_tool
                                        mocks["agro_tool"] = mock_agro_tool

                                        # Mock RAG components
                                        with (
                                            patch(
                                                "src.main.EmbeddingsManager"
                                            ) as mock_emb,
                                            patch(
                                                "src.main.KnowledgeRetriever"
                                            ) as mock_ret,
                                            patch("src.main.Supervisor") as mock_sup,
                                        ):

                                            emb_instance = Mock()
                                            mock_emb.return_value = emb_instance

                                            ret_instance = Mock()
                                            ret_instance.get_collection_info = Mock(
                                                return_value={"docs": 100}
                                            )
                                            mock_ret.return_value = ret_instance

                                            sup_instance = AsyncMock()
                                            sup_instance.coordinate = AsyncMock(
                                                return_value={
                                                    "answer": "Agricultural advice here",
                                                    "agents_used": ["field_analyst"],
                                                }
                                            )
                                            sup_instance.get_available_agents = Mock(
                                                return_value=[
                                                    {
                                                        "name": "field_analyst",
                                                        "role": "Field Analysis",
                                                    }
                                                ]
                                            )
                                            mock_sup.return_value = sup_instance

                                            mocks["embeddings"] = mock_emb
                                            mocks["retriever"] = mock_ret
                                            mocks["supervisor"] = mock_sup

                                            yield mocks


@pytest.fixture
def client(mock_env_vars, mock_all_dependencies):
    """Create test client with mocked dependencies"""
    from src.main import app

    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test /healthz endpoint"""
        response = client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-advisor-test"
        assert "version" in data


class TestAdvisorEndpoints:
    """Test AI advisor endpoints"""

    def test_ask_question(self, client, sample_question_request):
        """Test /v1/advisor/ask endpoint"""
        response = client.post("/v1/advisor/ask", json=sample_question_request)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["error"] is None

    def test_ask_question_without_context(self, client):
        """Test ask endpoint without context"""
        request_data = {"question": "What is crop rotation?", "language": "en"}

        response = client.post("/v1/advisor/ask", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_diagnose_disease(self, client, sample_diagnose_request):
        """Test /v1/advisor/diagnose endpoint"""
        response = client.post("/v1/advisor/diagnose", json=sample_diagnose_request)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data

    def test_diagnose_without_image(self, client):
        """Test diagnose endpoint without image"""
        request_data = {
            "crop_type": "tomato",
            "symptoms": {"leaf_color": "brown", "spots": True},
        }

        response = client.post("/v1/advisor/diagnose", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_get_recommendations_irrigation(
        self, client, sample_recommendation_request
    ):
        """Test /v1/advisor/recommend for irrigation"""
        response = client.post(
            "/v1/advisor/recommend", json=sample_recommendation_request
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data

    def test_get_recommendations_fertilizer(self, client):
        """Test recommendations for fertilizer"""
        request_data = {
            "crop_type": "wheat",
            "growth_stage": "tillering",
            "recommendation_type": "fertilizer",
            "field_data": {"soil": {"ph": 6.5, "nitrogen": "low"}},
        }

        response = client.post("/v1/advisor/recommend", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_get_recommendations_pest(self, client):
        """Test recommendations for pest control"""
        request_data = {
            "crop_type": "corn",
            "growth_stage": "vegetative",
            "recommendation_type": "pest",
        }

        response = client.post("/v1/advisor/recommend", json=request_data)

        assert response.status_code == 200

    def test_get_recommendations_invalid_type(self, client):
        """Test recommendations with invalid type"""
        request_data = {
            "crop_type": "wheat",
            "growth_stage": "flowering",
            "recommendation_type": "invalid_type",
        }

        response = client.post("/v1/advisor/recommend", json=request_data)

        assert response.status_code == 400

    def test_analyze_field(self, client, sample_field_analysis_request):
        """Test /v1/advisor/analyze-field endpoint"""
        response = client.post(
            "/v1/advisor/analyze-field", json=sample_field_analysis_request
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "analysis" in data["data"]

    def test_analyze_field_partial(self, client):
        """Test field analysis with partial options"""
        request_data = {
            "field_id": "field-456",
            "crop_type": "rice",
            "include_disease_check": True,
            "include_irrigation": False,
            "include_yield_prediction": False,
        }

        response = client.post("/v1/advisor/analyze-field", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestAgentManagement:
    """Test agent management endpoints"""

    def test_list_agents(self, client):
        """Test /v1/advisor/agents endpoint"""
        response = client.get("/v1/advisor/agents")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "agents" in data
        assert "total" in data
        assert data["total"] >= 0

    def test_list_tools(self, client):
        """Test /v1/advisor/tools endpoint"""
        response = client.get("/v1/advisor/tools")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "tools" in data
        assert isinstance(data["tools"], list)


class TestRAGEndpoints:
    """Test RAG system endpoints"""

    def test_get_rag_info(self, client):
        """Test /v1/advisor/rag/info endpoint"""
        response = client.get("/v1/advisor/rag/info")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "collection" in data


class TestInputValidation:
    """Test input validation"""

    def test_ask_question_missing_question(self, client):
        """Test ask endpoint with missing question"""
        request_data = {"language": "en"}

        response = client.post("/v1/advisor/ask", json=request_data)

        assert response.status_code == 422  # Validation error

    def test_diagnose_missing_crop_type(self, client):
        """Test diagnose with missing crop type"""
        request_data = {"symptoms": {"leaf_color": "yellow"}}

        response = client.post("/v1/advisor/diagnose", json=request_data)

        assert response.status_code == 422

    def test_recommend_missing_fields(self, client):
        """Test recommend with missing required fields"""
        request_data = {"crop_type": "wheat"}

        response = client.post("/v1/advisor/recommend", json=request_data)

        assert response.status_code == 422

    def test_analyze_field_missing_field_id(self, client):
        """Test field analysis with missing field_id"""
        request_data = {"crop_type": "corn"}

        response = client.post("/v1/advisor/analyze-field", json=request_data)

        assert response.status_code == 422
