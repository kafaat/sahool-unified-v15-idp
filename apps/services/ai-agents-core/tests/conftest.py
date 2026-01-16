"""
Test Configuration and Fixtures
إعداد الاختبارات والتهيئات

Provides common fixtures for all tests:
- Mock agents
- Test data
- Database fixtures
- API client
"""

import sys
from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agents import (
    AgentAction,
    AgentContext,
    AgentPercept,
    BaseAgent,
    DiseaseExpertAgent,
    IoTAgent,
    MasterCoordinatorAgent,
)

# ============================================================================
# Agent Fixtures
# ============================================================================


@pytest.fixture
def sample_context() -> AgentContext:
    """Create a sample agent context for testing"""
    return AgentContext(
        field_id="test_field_001",
        crop_type="wheat",
        location={"lat": 15.5527, "lon": 48.5164},  # Sana'a coordinates
        sensor_data={
            "soil_moisture": 0.35,
            "temperature": 25.5,
            "humidity": 45.0,
            "soil_ec": 1.5,
            "soil_ph": 6.8,
        },
        weather_data={
            "temperature": 26.0,
            "humidity": 40,
            "wind_speed": 10,
            "conditions": "sunny",
        },
        satellite_data={"ndvi": 0.75, "evi": 0.65},
        history=[],
        user_preferences={"language": "ar"},
    )


@pytest.fixture
def sample_percept() -> AgentPercept:
    """Create a sample percept for testing"""
    return AgentPercept(
        percept_type="sensor_reading",
        data={"soil_moisture": 0.20, "temperature": 30.0},
        source="test_sensor",
        reliability=0.95,
    )


@pytest.fixture
def sample_action() -> AgentAction:
    """Create a sample action for testing"""
    return AgentAction(
        action_type="test_action",
        parameters={"param1": "value1"},
        confidence=0.85,
        priority=2,
        reasoning="Test action reasoning",
        source_agent="test_agent",
    )


@pytest.fixture
def iot_agent() -> IoTAgent:
    """Create an IoT agent instance for testing"""
    return IoTAgent(agent_id="test_iot_001", device_id="test_device")


@pytest.fixture
def disease_expert_agent() -> DiseaseExpertAgent:
    """Create a disease expert agent for testing"""
    return DiseaseExpertAgent(agent_id="test_disease_001")


@pytest.fixture
def coordinator_agent() -> MasterCoordinatorAgent:
    """Create a coordinator agent for testing"""
    return MasterCoordinatorAgent(agent_id="test_coordinator_001")


# ============================================================================
# API Fixtures
# ============================================================================


@pytest.fixture
def api_client() -> TestClient:
    """Create a test client for the FastAPI app"""
    from main import app

    return TestClient(app)


@pytest.fixture
async def async_api_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app"""
    from main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================================================
# Mock Data Fixtures
# ============================================================================


@pytest.fixture
def mock_sensor_data() -> dict[str, Any]:
    """Mock sensor data for testing"""
    return {
        "device_id": "sensor_001",
        "soil_moisture": 0.35,
        "temperature": 28.5,
        "humidity": 50.0,
        "soil_ec": 1.8,
        "soil_ph": 7.0,
        "timestamp": datetime.now().isoformat(),
    }


@pytest.fixture
def mock_weather_data() -> dict[str, Any]:
    """Mock weather data for testing"""
    return {
        "current": {
            "temperature": 30.0,
            "humidity": 45,
            "wind_speed": 12,
            "conditions": "clear",
            "uv_index": 8,
        },
        "forecast": [
            {"day": "today", "temp_max": 32, "temp_min": 20, "rain_probability": 10},
            {"day": "tomorrow", "temp_max": 33, "temp_min": 21, "rain_probability": 5},
        ],
    }


@pytest.fixture
def mock_image_data() -> dict[str, Any]:
    """Mock image analysis data for testing"""
    return {
        "disease_id": "wheat_leaf_rust",
        "confidence": 0.87,
        "affected_area": 25.5,
        "bounding_boxes": [{"x": 100, "y": 100, "width": 50, "height": 50}],
    }


@pytest.fixture
def mock_disease_symptoms() -> list[str]:
    """Mock disease symptoms for testing"""
    return ["orange_spots", "yellowing", "leaf_drop"]


# ============================================================================
# Database and External Service Mocks
# ============================================================================


@pytest.fixture
def mock_ai_service(monkeypatch):
    """Mock external AI service calls"""

    async def mock_predict(*args, **kwargs):
        return {
            "prediction": "wheat_leaf_rust",
            "confidence": 0.85,
            "processing_time_ms": 45,
        }

    return mock_predict


@pytest.fixture
def mock_weather_api(monkeypatch):
    """Mock weather API calls"""

    async def mock_fetch_weather(*args, **kwargs):
        return {
            "temperature": 30.0,
            "humidity": 45,
            "wind_speed": 10,
            "conditions": "sunny",
        }

    return mock_fetch_weather


# ============================================================================
# Utility Fixtures
# ============================================================================


@pytest.fixture
def reset_agent_state():
    """Reset agent state between tests"""

    def _reset(agent: BaseAgent):
        agent.status = agent.__class__.IDLE
        agent.state.beliefs.clear()
        agent.state.goals.clear()
        agent.context = None
        agent.total_requests = 0
        agent.successful_requests = 0

    return _reset


@pytest.fixture
def rate_limit_headers() -> dict[str, str]:
    """Headers for rate limit testing"""
    return {
        "X-Internal-Service": "test-service",
        "X-Request-ID": "test-request-123",
    }


# ============================================================================
# Parametrized Test Data
# ============================================================================


@pytest.fixture(
    params=[
        {"soil_moisture": 0.10, "expected_action": "start_irrigation"},
        {"soil_moisture": 0.23, "expected_action": "irrigation_recommendation"},
        {"soil_moisture": 0.50, "expected_action": None},
    ]
)
def irrigation_scenarios(request):
    """Parametrized irrigation scenarios"""
    return request.param


@pytest.fixture(
    params=[
        {"temperature": 46.0, "expected_action": "heat_emergency"},
        {"temperature": 1.0, "expected_action": "frost_emergency"},
        {"temperature": 25.0, "expected_action": None},
    ]
)
def temperature_scenarios(request):
    """Parametrized temperature scenarios"""
    return request.param


@pytest.fixture(
    params=[
        {
            "disease_id": "wheat_leaf_rust",
            "crop_type": "wheat",
            "should_detect": True,
        },
        {
            "disease_id": "tomato_late_blight",
            "crop_type": "tomato",
            "should_detect": True,
        },
        {
            "disease_id": "coffee_leaf_rust",
            "crop_type": "wheat",
            "should_detect": False,
        },
    ]
)
def disease_scenarios(request):
    """Parametrized disease scenarios"""
    return request.param
