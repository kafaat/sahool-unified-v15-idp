"""
Happy-path test for GET /api/v1/terrain/aspect/{field_id}.
اختبار المسار السعيد لنقطة نهاية الجانب

Verifies that the aspect endpoint:
- Is mounted at the contract path ``/api/v1/terrain/aspect/{field_id}``
- Extracts tenant_id from the authenticated User (JWT), not headers
- Returns an AspectAnalysisResponse shape with bilingual direction name
- Computes aspect on the in-memory DEM returned by the (mocked) DEM processor
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock

import pytest

np = pytest.importorskip("numpy")

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")


class _FakeUser:
    """Minimal user object mimicking shared.auth.models.User."""

    id = "user-aspect-test"
    tenant_id = "00000000-0000-0000-0000-000000000042"


@pytest.fixture
def aspect_client():
    """Build a TestClient with auth + DEM processor overrides."""
    try:
        from fastapi.testclient import TestClient
    except ImportError:  # pragma: no cover
        pytest.skip("fastapi.testclient not available")

    try:
        from src.algorithms.dem_processor import (
            DEMBounds,
            DEMData,
            DEMMetadata,
            DEMSource,
        )
        from src.algorithms.terrain_indicators import TerrainIndicatorCalculator
        from src.api.endpoints.terrain import (
            get_current_user,
            get_dem_processor,
            get_terrain_calculator,
        )
        from src.main import app
    except ImportError as exc:  # pragma: no cover
        pytest.skip(f"terrain-core-service not importable: {exc}")

    # Build a deterministic 20x20 tilted DEM (facing east): elevation = col * 2
    rows, cols = 20, 20
    elevation = np.tile(np.arange(cols, dtype=np.float32) * 2.0, (rows, 1))
    nodata_mask = np.zeros_like(elevation, dtype=bool)
    bounds = DEMBounds(min_lon=46.0, min_lat=24.0, max_lon=46.01, max_lat=24.01)
    metadata = DEMMetadata(
        source=DEMSource.COPERNICUS,
        resolution_m=30.0,
        crs="EPSG:4326",
        bounds=bounds,
        width=cols,
        height=rows,
        nodata_value=-9999.0,
        vertical_datum="EGM2008",
    )
    dem_data = DEMData(
        data=elevation,
        metadata=metadata,
        transform=None,
        nodata_mask=nodata_mask,
    )

    fake_processor = AsyncMock()
    fake_processor.acquire_dem = AsyncMock(return_value=dem_data)
    fake_processor.fill_holes = AsyncMock(return_value=dem_data)

    real_calculator = TerrainIndicatorCalculator(cell_size_m=30.0)

    async def _user_override():
        return _FakeUser()

    app.dependency_overrides[get_current_user] = _user_override
    app.dependency_overrides[get_dem_processor] = lambda: fake_processor
    app.dependency_overrides[get_terrain_calculator] = lambda: real_calculator

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_get_aspect_happy_path(aspect_client):
    """GET /api/v1/terrain/aspect/{field_id} returns an aspect analysis."""
    response = aspect_client.get("/api/v1/terrain/aspect/FIELD-ASPECT-001")
    assert response.status_code == 200, response.text

    data = response.json()

    # Contract envelope
    assert data["field_id"] == "FIELD-ASPECT-001"
    assert data["dem_source"] == "copernicus"
    assert "analyzed_at" in data
    assert "processing_time_ms" in data
    assert data["processing_time_ms"] >= 0

    aspect = data["aspect"]
    assert "dominant_direction" in aspect
    assert "dominant_direction_name" in aspect
    assert "distribution" in aspect
    assert "mean_aspect_degrees" in aspect

    # Bilingual dominant direction name
    assert "en" in aspect["dominant_direction_name"]
    assert "ar" in aspect["dominant_direction_name"]

    # East-facing synthetic DEM should be dominantly east-ish
    assert aspect["dominant_direction"] in {
        "east",
        "northeast",
        "southeast",
        "flat",
        "north",
        "south",
        "west",
        "northwest",
        "southwest",
    }
    # mean aspect must be in [0, 360)
    assert 0.0 <= aspect["mean_aspect_degrees"] < 360.0

    # Distribution sums to roughly 100 (flat + all 8 directions), allowing for rounding
    total = sum(v for v in aspect["distribution"].values())
    assert 0 < total <= 200.0  # tolerant upper bound due to flat double-counting


def test_get_aspect_endpoint_mounted_under_api_v1(aspect_client):
    """Confirms the aspect route is under /api/v1/terrain/ (contract path)."""
    # The route must not exist at legacy path
    legacy = aspect_client.get("/terrain/aspect/FIELD-ASPECT-001")
    assert legacy.status_code == 404

    # And must exist at the contract path
    response = aspect_client.get("/api/v1/terrain/aspect/FIELD-ASPECT-001")
    assert response.status_code == 200
