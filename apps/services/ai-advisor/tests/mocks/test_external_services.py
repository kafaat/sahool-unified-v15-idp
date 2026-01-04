"""
Mock Tests for External Service Dependencies
اختبارات محاكاة للتبعيات الخارجية
"""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest


class TestCropHealthToolMock:
    """Test CropHealthTool with mocked external API"""

    @pytest.mark.asyncio
    async def test_analyze_image_success(self):
        """Test successful image analysis"""
        from src.tools.crop_health_tool import CropHealthTool

        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "disease_detected": True,
            "disease_name": "Leaf Blight",
            "confidence": 0.87,
            "affected_area": 0.25,
        }

        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_response)):
            tool = CropHealthTool()

            result = await tool.analyze_image(
                image_path="/tmp/test_crop.jpg", crop_type="wheat"
            )

            assert result["disease_detected"] is True
            assert result["confidence"] > 0.8
            assert "disease_name" in result

    @pytest.mark.asyncio
    async def test_analyze_image_no_disease(self):
        """Test image analysis with healthy crop"""
        from src.tools.crop_health_tool import CropHealthTool

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "disease_detected": False,
            "confidence": 0.92,
            "status": "healthy",
        }

        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_response)):
            tool = CropHealthTool()

            result = await tool.analyze_image(
                image_path="/tmp/healthy_crop.jpg", crop_type="tomato"
            )

            assert result["disease_detected"] is False
            assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_analyze_image_api_failure(self):
        """Test handling of API failure"""
        from src.tools.crop_health_tool import CropHealthTool

        with patch(
            "httpx.AsyncClient.post",
            new=AsyncMock(side_effect=httpx.RequestError("API Error")),
        ):
            tool = CropHealthTool()

            with pytest.raises(Exception):
                await tool.analyze_image(image_path="/tmp/test.jpg", crop_type="corn")


class TestWeatherToolMock:
    """Test WeatherTool with mocked weather API"""

    @pytest.mark.asyncio
    async def test_get_current_weather(self):
        """Test getting current weather data"""
        from src.tools.weather_tool import WeatherTool

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "temperature": 28.5,
            "humidity": 65,
            "conditions": "partly cloudy",
            "precipitation": 0,
            "wind_speed": 12,
            "wind_direction": "NW",
        }

        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            tool = WeatherTool()

            result = await tool.get_current_weather(location="Sana'a, Yemen")

            assert "temperature" in result
            assert "humidity" in result
            assert result["temperature"] > 0

    @pytest.mark.asyncio
    async def test_get_weather_forecast(self):
        """Test getting weather forecast"""
        from src.tools.weather_tool import WeatherTool

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "forecast": [
                {
                    "date": "2024-12-27",
                    "temp_max": 30,
                    "temp_min": 18,
                    "precipitation": 0,
                },
                {
                    "date": "2024-12-28",
                    "temp_max": 29,
                    "temp_min": 17,
                    "precipitation": 5,
                },
                {
                    "date": "2024-12-29",
                    "temp_max": 28,
                    "temp_min": 16,
                    "precipitation": 0,
                },
            ]
        }

        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            tool = WeatherTool()

            result = await tool.get_forecast(location="Sana'a, Yemen", days=3)

            assert "forecast" in result
            assert len(result["forecast"]) == 3

    @pytest.mark.asyncio
    async def test_get_weather_timeout(self):
        """Test weather API timeout handling"""
        from src.tools.weather_tool import WeatherTool

        with patch(
            "httpx.AsyncClient.get",
            new=AsyncMock(side_effect=httpx.TimeoutException("Timeout")),
        ):
            tool = WeatherTool()

            with pytest.raises(Exception):
                await tool.get_current_weather(location="Test")


class TestSatelliteToolMock:
    """Test SatelliteTool with mocked satellite API"""

    @pytest.mark.asyncio
    async def test_get_ndvi_data(self):
        """Test getting NDVI satellite data"""
        from src.tools.satellite_tool import SatelliteTool

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "field_id": "test-field-123",
            "ndvi_average": 0.75,
            "ndvi_min": 0.6,
            "ndvi_max": 0.85,
            "date": "2024-12-01",
            "coverage": 95,
        }

        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            tool = SatelliteTool()

            result = await tool.get_ndvi(field_id="test-field-123")

            assert result["field_id"] == "test-field-123"
            assert 0 <= result["ndvi_average"] <= 1
            assert result["ndvi_average"] >= result["ndvi_min"]
            assert result["ndvi_average"] <= result["ndvi_max"]

    @pytest.mark.asyncio
    async def test_get_ndvi_time_series(self):
        """Test getting NDVI time series data"""
        from src.tools.satellite_tool import SatelliteTool

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "field_id": "test-field-123",
            "time_series": [
                {"date": "2024-11-01", "ndvi": 0.65},
                {"date": "2024-11-15", "ndvi": 0.70},
                {"date": "2024-12-01", "ndvi": 0.75},
            ],
        }

        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            tool = SatelliteTool()

            result = await tool.get_ndvi_time_series(
                field_id="test-field-123",
                start_date="2024-11-01",
                end_date="2024-12-01",
            )

            assert "time_series" in result
            assert len(result["time_series"]) > 0

    @pytest.mark.asyncio
    async def test_get_ndvi_no_data_available(self):
        """Test handling when no satellite data is available"""
        from src.tools.satellite_tool import SatelliteTool

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "No data available for this field"}

        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            tool = SatelliteTool()

            with pytest.raises(Exception):
                await tool.get_ndvi(field_id="nonexistent-field")


class TestAgroToolMock:
    """Test AgroTool with mocked agricultural API"""

    @pytest.mark.asyncio
    async def test_get_crop_calendar(self):
        """Test getting crop calendar information"""
        from src.tools.agro_tool import AgroTool

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "crop": "wheat",
            "planting_season": "November-December",
            "harvest_season": "April-May",
            "growth_duration_days": 120,
        }

        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            tool = AgroTool()

            result = await tool.get_crop_calendar(crop_type="wheat", location="Yemen")

            assert result["crop"] == "wheat"
            assert "planting_season" in result
            assert "harvest_season" in result

    @pytest.mark.asyncio
    async def test_get_soil_recommendations(self):
        """Test getting soil recommendations"""
        from src.tools.agro_tool import AgroTool

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "crop": "tomato",
            "soil_type": "loamy",
            "ph_range": {"min": 6.0, "max": 6.8},
            "amendments": ["organic matter", "lime if acidic"],
        }

        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
            tool = AgroTool()

            result = await tool.get_soil_recommendations(crop_type="tomato")

            assert result["crop"] == "tomato"
            assert "ph_range" in result
            assert "amendments" in result


class TestEmbeddingsManagerMock:
    """Test EmbeddingsManager with mocked model"""

    def test_get_embeddings(self):
        """Test text embedding generation"""
        from src.rag.embeddings_manager import EmbeddingsManager

        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3, 0.4]]  # Mock embedding vector

        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_model
        ):
            manager = EmbeddingsManager()

            result = manager.get_embeddings(["Test agricultural text"])

            assert result is not None
            assert len(result) > 0
            assert isinstance(result[0], list)

    def test_get_model_info(self):
        """Test getting model information"""
        from src.rag.embeddings_manager import EmbeddingsManager

        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension = Mock(return_value=384)

        with patch(
            "sentence_transformers.SentenceTransformer", return_value=mock_model
        ):
            manager = EmbeddingsManager()

            info = manager.get_model_info()

            assert "model_name" in info
            assert "dimensions" in info


class TestKnowledgeRetrieverMock:
    """Test KnowledgeRetriever with mocked vector database"""

    @pytest.mark.asyncio
    async def test_retrieve_documents(self):
        """Test document retrieval from RAG system"""
        from src.rag.knowledge_retriever import KnowledgeRetriever

        mock_embeddings = Mock()
        mock_embeddings.get_embeddings.return_value = [[0.1, 0.2, 0.3]]

        retriever = KnowledgeRetriever(embeddings_manager=mock_embeddings)

        # Mock vector store
        mock_docs = [
            Mock(page_content="Document 1 about wheat", metadata={"source": "test1"}),
            Mock(
                page_content="Document 2 about irrigation", metadata={"source": "test2"}
            ),
        ]

        with patch.object(retriever, "_search_vector_store", return_value=mock_docs):
            results = retriever.retrieve(query="Tell me about wheat farming", top_k=2)

            assert len(results) == 2
            assert results[0].page_content is not None

    def test_get_collection_info(self):
        """Test getting vector store collection information"""
        from src.rag.knowledge_retriever import KnowledgeRetriever

        mock_embeddings = Mock()
        retriever = KnowledgeRetriever(embeddings_manager=mock_embeddings)

        with patch.object(
            retriever,
            "_get_collection_stats",
            return_value={
                "collection_name": "agricultural-knowledge",
                "documents_count": 1500,
            },
        ):
            info = retriever.get_collection_info()

            assert info["collection_name"] == "agricultural-knowledge"
            assert info["documents_count"] > 0
