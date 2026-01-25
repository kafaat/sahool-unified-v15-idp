"""
Pytest Configuration and Fixtures for Fertilizer Advisor
إعدادات وتجهيزات Pytest لمستشار السماد
"""

from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client():
    """Create FastAPI test client"""
    from src.main import app

    return TestClient(app)


@pytest.fixture
def sample_soil_analysis() -> dict[str, Any]:
    """Sample soil analysis data"""
    return {
        "field_id": "field_001",
        "analysis_date": datetime.now().isoformat(),
        "ph": 6.5,
        "nitrogen_ppm": 120.0,
        "phosphorus_ppm": 45.0,
        "potassium_ppm": 180.0,
        "organic_matter_percent": 3.5,
        "ec_ds_m": 1.2,
        "texture": "loamy",
    }


@pytest.fixture
def sample_recommendation_request() -> dict[str, Any]:
    """Sample fertilizer recommendation request"""
    return {
        "field_id": "field_001",
        "crop_type": "wheat",
        "growth_stage": "vegetative",
        "soil_type": "loamy",
        "area_hectares": 2.5,
        "current_soil_data": {
            "ph": 6.5,
            "nitrogen_ppm": 120.0,
            "phosphorus_ppm": 45.0,
            "potassium_ppm": 180.0,
        },
    }


@pytest.fixture
def sample_schedule_request() -> dict[str, Any]:
    """Sample fertilization schedule request"""
    return {
        "field_id": "field_001",
        "crop_type": "tomato",
        "planting_date": "2025-01-15",
        "area_hectares": 1.5,
        "soil_type": "clay",
        "irrigation_method": "drip",
    }
