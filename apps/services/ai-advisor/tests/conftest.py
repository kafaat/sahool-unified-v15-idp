"""
Pytest Configuration and Fixtures
تكوين pytest والتجهيزات
"""

import pytest
import os
from typing import Generator, Dict, Any
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_env_vars() -> Generator[Dict[str, str], None, None]:
    """
    Mock environment variables for testing
    محاكاة متغيرات البيئة للاختبار
    """
    env_vars = {
        "ANTHROPIC_API_KEY": "test-anthropic-key-123",
        "OPENAI_API_KEY": "test-openai-key-456",
        "GOOGLE_API_KEY": "test-google-key-789",
        "CLAUDE_MODEL": "claude-3-5-sonnet-20241022",
        "SERVICE_NAME": "ai-advisor-test",
        "SERVICE_PORT": "8200",
        "LOG_LEVEL": "INFO",
        "RAG_TOP_K": "5",
        "MAX_TOKENS": "4096",
        "TEMPERATURE": "0.7",
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def mock_anthropic_client():
    """
    Mock Anthropic API client
    محاكاة عميل Anthropic API
    """
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.content = [Mock(text="This is a test response from Claude.")]
    mock_response.model = "claude-3-5-sonnet-20241022"
    mock_response.usage = Mock(input_tokens=100, output_tokens=50)
    mock_response.stop_reason = "stop"

    mock_client.messages.create = AsyncMock(return_value=mock_response)
    return mock_client


@pytest.fixture
def mock_openai_client():
    """
    Mock OpenAI API client
    محاكاة عميل OpenAI API
    """
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.choices = [
        Mock(
            message=Mock(content="This is a test response from GPT."),
            finish_reason="stop"
        )
    ]
    mock_response.model = "gpt-4o"
    mock_response.usage = Mock(total_tokens=200)

    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    return mock_client


@pytest.fixture
def mock_embeddings_manager():
    """
    Mock embeddings manager
    محاكاة مدير التضمينات
    """
    mock_manager = Mock()
    mock_manager.get_model_info = Mock(return_value={
        "model_name": "test-embeddings-model",
        "dimensions": 384
    })
    return mock_manager


@pytest.fixture
def mock_knowledge_retriever(mock_embeddings_manager):
    """
    Mock RAG knowledge retriever
    محاكاة مسترجع المعرفة RAG
    """
    mock_retriever = Mock()
    mock_retriever.retrieve = Mock(return_value=[
        Mock(page_content="Agricultural knowledge 1", metadata={"source": "test1"}),
        Mock(page_content="Agricultural knowledge 2", metadata={"source": "test2"}),
    ])
    mock_retriever.get_collection_info = Mock(return_value={
        "collection_name": "test-collection",
        "documents_count": 100
    })
    return mock_retriever


@pytest.fixture
def mock_crop_health_tool():
    """
    Mock crop health tool
    محاكاة أداة صحة المحاصيل
    """
    mock_tool = AsyncMock()
    mock_tool.analyze_image = AsyncMock(return_value={
        "disease_detected": True,
        "disease_name": "Leaf Blight",
        "confidence": 0.85,
        "affected_area": 0.25
    })
    return mock_tool


@pytest.fixture
def mock_weather_tool():
    """
    Mock weather tool
    محاكاة أداة الطقس
    """
    mock_tool = AsyncMock()
    mock_tool.get_current_weather = AsyncMock(return_value={
        "temperature": 28.5,
        "humidity": 65,
        "conditions": "partly cloudy",
        "precipitation": 0
    })
    return mock_tool


@pytest.fixture
def mock_satellite_tool():
    """
    Mock satellite data tool
    محاكاة أداة بيانات الأقمار الصناعية
    """
    mock_tool = AsyncMock()
    mock_tool.get_ndvi = AsyncMock(return_value={
        "field_id": "test-field-123",
        "ndvi_average": 0.75,
        "ndvi_min": 0.6,
        "ndvi_max": 0.85,
        "date": "2024-12-01"
    })
    return mock_tool


@pytest.fixture
def sample_question_request() -> Dict[str, Any]:
    """
    Sample question request payload
    نموذج طلب سؤال
    """
    return {
        "question": "What is the best time to plant wheat?",
        "language": "en",
        "context": {
            "location": "Yemen",
            "season": "winter"
        }
    }


@pytest.fixture
def sample_diagnose_request() -> Dict[str, Any]:
    """
    Sample disease diagnosis request
    نموذج طلب تشخيص مرض
    """
    return {
        "crop_type": "wheat",
        "symptoms": {
            "leaf_color": "yellow",
            "spots": True,
            "wilting": False
        },
        "image_path": "/tmp/test-crop-image.jpg",
        "location": "test-field-123"
    }


@pytest.fixture
def sample_recommendation_request() -> Dict[str, Any]:
    """
    Sample recommendation request
    نموذج طلب توصيات
    """
    return {
        "crop_type": "tomato",
        "growth_stage": "flowering",
        "recommendation_type": "irrigation",
        "field_data": {
            "soil": {
                "moisture": 45,
                "type": "loamy"
            },
            "weather": {
                "temperature": 25,
                "humidity": 60
            }
        }
    }


@pytest.fixture
def sample_field_analysis_request() -> Dict[str, Any]:
    """
    Sample field analysis request
    نموذج طلب تحليل حقل
    """
    return {
        "field_id": "test-field-123",
        "crop_type": "corn",
        "include_disease_check": True,
        "include_irrigation": True,
        "include_yield_prediction": True
    }
