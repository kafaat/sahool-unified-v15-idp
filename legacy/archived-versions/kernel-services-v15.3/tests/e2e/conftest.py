"""
SAHOOL Kernel Services v15.3 - E2E Test Configuration
اختبارات شاملة للخدمات الزراعية
"""

import pytest
import httpx
import asyncio
from typing import Generator, AsyncGenerator
import os

# Service URLs
SATELLITE_URL = os.getenv("SATELLITE_URL", "http://localhost:8090")
INDICATORS_URL = os.getenv("INDICATORS_URL", "http://localhost:8091")
WEATHER_URL = os.getenv("WEATHER_URL", "http://localhost:8092")
FERTILIZER_URL = os.getenv("FERTILIZER_URL", "http://localhost:8093")
IRRIGATION_URL = os.getenv("IRRIGATION_URL", "http://localhost:8094")

# Test data
TEST_TENANT_ID = "tenant_test_001"
TEST_FIELD_ID = "field_test_001"
TEST_USER_ID = "user_test_001"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Shared async HTTP client for all tests."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture
def satellite_client(async_client: httpx.AsyncClient):
    """Client configured for satellite service."""
    return async_client, SATELLITE_URL


@pytest.fixture
def indicators_client(async_client: httpx.AsyncClient):
    """Client configured for indicators service."""
    return async_client, INDICATORS_URL


@pytest.fixture
def weather_client(async_client: httpx.AsyncClient):
    """Client configured for weather service."""
    return async_client, WEATHER_URL


@pytest.fixture
def fertilizer_client(async_client: httpx.AsyncClient):
    """Client configured for fertilizer service."""
    return async_client, FERTILIZER_URL


@pytest.fixture
def irrigation_client(async_client: httpx.AsyncClient):
    """Client configured for irrigation service."""
    return async_client, IRRIGATION_URL


@pytest.fixture
def test_field_data():
    """Sample field data for testing."""
    return {
        "field_id": TEST_FIELD_ID,
        "tenant_id": TEST_TENANT_ID,
        "name": "حقل الاختبار الشمالي",
        "name_en": "North Test Field",
        "area_hectares": 15.5,
        "crop_type": "tomato",
        "location": {
            "lat": 15.3694,
            "lon": 44.1910
        },
        "boundary": {
            "type": "Polygon",
            "coordinates": [[[44.19, 15.36], [44.20, 15.36], [44.20, 15.37], [44.19, 15.37], [44.19, 15.36]]]
        }
    }


@pytest.fixture
def test_soil_data():
    """Sample soil analysis data."""
    return {
        "ph": 6.5,
        "nitrogen_ppm": 25,
        "phosphorus_ppm": 15,
        "potassium_ppm": 180,
        "organic_matter_percent": 2.5,
        "ec_ds_m": 1.2
    }


@pytest.fixture
def yemen_locations():
    """Yemen governorate locations for testing."""
    return [
        {"id": "sana'a", "name_ar": "صنعاء", "lat": 15.3694, "lon": 44.1910},
        {"id": "aden", "name_ar": "عدن", "lat": 12.7855, "lon": 45.0187},
        {"id": "taiz", "name_ar": "تعز", "lat": 13.5789, "lon": 44.0219},
        {"id": "hodeidah", "name_ar": "الحديدة", "lat": 14.7979, "lon": 42.9540},
        {"id": "ibb", "name_ar": "إب", "lat": 13.9667, "lon": 44.1667},
    ]
