"""
Test configuration and fixtures for pest-detection-service.
"""

# Set test environment before importing app
import os
import sys

# Add service root to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Clear cached src module to avoid cross-service contamination in CI
for _mod in list(sys.modules):
    if _mod == "src" or _mod.startswith("src."):
        del sys.modules[_mod]

import pytest

os.environ["ENVIRONMENT"] = "test"
os.environ["NATS_URL"] = ""
os.environ["REDIS_URL"] = ""
os.environ["DATABASE_URL"] = ""
os.environ["VISION_SERVICE_URL"] = "http://mock-vision:8150"

try:
    from src.main import app
except (ImportError, OSError, RuntimeError):
    app = None


@pytest.fixture
def client():
    """Synchronous test client."""
    if app is None:
        pytest.skip("pest-detection-service src not available")
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        pytest.skip("fastapi not installed")
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def async_client():
    """Asynchronous test client."""
    if app is None:
        pytest.skip("pest-detection-service src not available")
    try:
        from httpx import AsyncClient
    except ImportError:
        pytest.skip("httpx not installed")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_pest_data():
    """Sample pest data for testing."""
    return {
        "id": "test_pest",
        "name_en": "Test Pest",
        "name_ar": "آفة اختبار",
        "scientific_name": "Testus pestus",
        "category": "insect",
        "description_en": "A test pest",
        "description_ar": "آفة للاختبار",
        "affected_crops": ["wheat", "barley"],
        "symptoms_en": ["Yellowing leaves"],
        "symptoms_ar": ["اصفرار الأوراق"],
        "is_quarantine": False,
    }


@pytest.fixture
def sample_scout_report():
    """Sample scout report for testing."""
    return {
        "field_id": "FIELD-001",
        "crop": "wheat",
        "growth_stage": "tillering",
        "scout_name": "Test Scout",
        "observations": [],
        "weather_conditions": "sunny",
        "general_notes": "Test notes",
        "general_notes_ar": "ملاحظات اختبار",
    }


@pytest.fixture
def sample_observation():
    """Sample observation for testing."""
    return {
        "pest_id": "aphids",
        "infestation_level": "low",
        "affected_area_percent": 10.0,
        "life_stage": "adult",
        "count": 15,
        "notes": "Found on lower leaves",
        "notes_ar": "وجدت على الأوراق السفلية",
        "image_urls": [],
    }


@pytest.fixture
def sample_threshold_assessment():
    """Sample threshold assessment request."""
    return {
        "pest_id": "aphids",
        "crop": "wheat",
        "current_value": 25.0,
        "field_id": "FIELD-001",
        "growth_stage": "tillering",
    }


@pytest.fixture
def sample_treatment_request():
    """Sample treatment recommendation request."""
    return {
        "pest_id": "aphids",
        "crop": "wheat",
        "severity": "medium",
        "growth_stage": "tillering",
        "organic_only": False,
        "budget_constraint": None,
    }
