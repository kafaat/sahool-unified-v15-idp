"""
Pytest Configuration and Fixtures for NDVI Processor
إعدادات وتجهيزات Pytest لمعالج NDVI
"""

import pytest
from datetime import datetime
from typing import Dict, Any
from fastapi.testclient import TestClient


@pytest.fixture
def sample_process_request() -> Dict[str, Any]:
    """Sample NDVI processing request"""
    return {
        "tenant_id": "test_tenant",
        "field_id": "field_001",
        "source": "sentinel-2",
        "date_range": {"start": "2025-01-01", "end": "2025-01-15"},
        "options": {
            "cloud_threshold_percent": 20,
            "atmospheric_correction": True,
            "cloud_masking": True,
            "output_format": "geotiff",
        },
        "priority": 5,
    }


@pytest.fixture
def sample_composite_request() -> Dict[str, Any]:
    """Sample composite creation request"""
    return {
        "tenant_id": "test_tenant",
        "field_id": "field_001",
        "year": 2025,
        "month": 12,
        "method": "max_ndvi",
        "source": "sentinel-2",
    }


@pytest.fixture
def sample_change_analysis_request() -> Dict[str, Any]:
    """Sample change analysis request"""
    return {
        "tenant_id": "test_tenant",
        "field_id": "field_001",
        "date1": "2025-01-01",
        "date2": "2025-12-01",
        "include_zones": True,
    }


@pytest.fixture
def sample_ndvi_result() -> Dict[str, Any]:
    """Sample NDVI calculation result"""
    return {
        "id": "result_001",
        "field_id": "field_001",
        "date": "2025-12-27",
        "source": {
            "satellite": "sentinel-2",
            "scene_id": "S2A_20251227_001",
            "acquisition_time": datetime.now().isoformat(),
            "resolution_meters": 10,
        },
        "processing": {
            "atmospheric_correction": "sen2cor",
            "cloud_mask": "s2cloudless",
            "processed_at": datetime.now().isoformat(),
        },
        "statistics": {
            "mean": 0.65,
            "median": 0.66,
            "std": 0.12,
            "min": 0.45,
            "max": 0.85,
            "percentiles": {"p10": 0.50, "p25": 0.58, "p75": 0.75, "p90": 0.80},
        },
        "quality": {
            "cloud_cover_percent": 5.2,
            "shadow_percent": 1.5,
            "valid_pixels_percent": 93.3,
        },
        "files": {
            "geotiff": "s3://bucket/field_001/2025-12-27.tif",
            "png": "s3://bucket/field_001/2025-12-27.png",
            "thumbnail": "s3://bucket/field_001/2025-12-27_thumb.png",
        },
    }


@pytest.fixture
def test_client():
    """Create FastAPI test client"""
    from src.main import app

    return TestClient(app)
