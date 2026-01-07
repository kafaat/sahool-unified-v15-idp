"""
Test Configuration and Fixtures
إعدادات الاختبار والتجهيزات
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app, _init_sample_data, ZONES, OBSERVATIONS


@pytest.fixture(scope="session", autouse=True)
def setup_test_data():
    """Initialize sample data before all tests run"""
    # Clear any existing data
    ZONES.clear()
    OBSERVATIONS.clear()

    # Initialize sample data
    _init_sample_data()

    yield

    # Cleanup after all tests
    ZONES.clear()
    OBSERVATIONS.clear()


@pytest.fixture
def client(setup_test_data):
    """Create test client with sample data initialized"""
    return TestClient(app)


@pytest.fixture
def sample_observation_data():
    """Sample observation data for testing"""
    return {
        "captured_at": "2025-12-27T10:00:00Z",
        "source": "sentinel-2",
        "growth_stage": "mid",
        "indices": {
            "ndvi": 0.75,
            "evi": 0.60,
            "ndre": 0.25,
            "lci": 0.30,
            "ndwi": -0.05,
            "savi": 0.65,
        },
        "cloud_pct": 5.0,
    }
