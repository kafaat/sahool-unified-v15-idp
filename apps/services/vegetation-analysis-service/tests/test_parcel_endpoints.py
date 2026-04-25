"""
Tests for parcel_endpoints module.
Tests cover request/response models, endpoint registration, helper functions,
and the strategies listing endpoint.
"""

import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Mock user with a valid tenant_id — every handler now passes through
# `require_tenant_id(_user)` (defense-in-depth even when Kong hasn't
# stripped the call, e.g., a unit-test direct call). Tests that want to
# exercise the tenant-missing 403 path should pass None / MagicMock()
# without the tenant_id attribute instead of this fixture.
_MOCK_USER = MagicMock(tenant_id="test-tenant")

from src.parcel_endpoints import (
    BatchAssignRequest,
    ParcelClassifyRequest,
    ParcelConnectRequest,
    ParcelDetectionRequest,
    ParcelMergeRequest,
    ParcelSplitRequest,
    RegionDetectionRequest,
    _geojson_to_parcels,
    register_parcel_endpoints,
)

# =============================================================================
# Request Model Tests
# =============================================================================


class TestParcelDetectionRequest:
    def test_defaults(self):
        req = ParcelDetectionRequest()
        assert req.strategy == "hybrid"
        assert req.precision == "high"
        assert req.target_shape == "irregular"
        assert req.min_area_hectares == 0.05
        assert req.max_area_hectares == 1000.0
        assert req.ndvi_threshold == 0.25
        assert req.smoothing_iterations == 2
        assert req.use_gpu is True

    def test_custom_values(self):
        req = ParcelDetectionRequest(
            strategy="training_free",
            precision="very_high",
            target_shape="rectangle",
            min_area_hectares=1.0,
            max_area_hectares=500.0,
            ndvi_threshold=0.3,
            smoothing_iterations=5,
            use_gpu=False,
        )
        assert req.strategy == "training_free"
        assert req.precision == "very_high"
        assert req.target_shape == "rectangle"
        assert req.min_area_hectares == 1.0
        assert req.use_gpu is False


class TestRegionDetectionRequest:
    def test_creation(self):
        req = RegionDetectionRequest(north=15.6, south=15.4, east=44.3, west=44.1)
        assert req.north == 15.6
        assert req.south == 15.4
        assert req.east == 44.3
        assert req.west == 44.1
        assert req.strategy == "hybrid"
        assert req.precision == "high"
        assert req.min_area_hectares == 0.05

    def test_custom_strategy(self):
        req = RegionDetectionRequest(
            north=16.0,
            south=15.0,
            east=45.0,
            west=44.0,
            strategy="semantic_segmentation",
            precision="very_high",
            min_area_hectares=0.5,
        )
        assert req.strategy == "semantic_segmentation"
        assert req.precision == "very_high"
        assert req.min_area_hectares == 0.5


class TestParcelClassifyRequest:
    def test_creation(self):
        parcels = [{"type": "Feature", "geometry": {}, "properties": {}}]
        req = ParcelClassifyRequest(parcels=parcels)
        assert len(req.parcels) == 1

    def test_empty_parcels(self):
        req = ParcelClassifyRequest(parcels=[])
        assert req.parcels == []


class TestParcelMergeRequest:
    def test_creation(self):
        req = ParcelMergeRequest(
            parcel_ids=["p1", "p2"],
            parcels=[{"type": "Feature"}, {"type": "Feature"}],
        )
        assert len(req.parcel_ids) == 2
        assert len(req.parcels) == 2


class TestParcelSplitRequest:
    def test_creation(self):
        req = ParcelSplitRequest(
            parcel={"type": "Feature", "geometry": {}},
            cutting_line=[[44.2, 15.5], [44.3, 15.6]],
        )
        assert len(req.cutting_line) == 2


class TestParcelConnectRequest:
    def test_defaults(self):
        req = ParcelConnectRequest(
            parcels=[{"type": "Feature"}, {"type": "Feature"}],
            max_gap_meters=10.0,
        )
        assert req.max_gap_meters == 10.0
        assert len(req.parcels) == 2

    def test_custom_gap(self):
        req = ParcelConnectRequest(
            parcels=[{"type": "Feature"}, {"type": "Feature"}],
            max_gap_meters=25.0,
        )
        assert req.max_gap_meters == 25.0


class TestBatchAssignRequest:
    def test_creation(self):
        req = BatchAssignRequest(
            parcel_ids=["p1", "p2"],
            parcels=[{"type": "Feature"}, {"type": "Feature"}],
            attribute="crop_type",
            value="wheat",
        )
        assert req.attribute == "crop_type"
        assert req.value == "wheat"
        assert len(req.parcel_ids) == 2


# =============================================================================
# _geojson_to_parcels Helper Tests
# =============================================================================


class TestGeojsonToParcels:
    """Test the _geojson_to_parcels helper function."""

    @pytest.fixture
    def mock_land_detector(self):
        """Create a mock land detector with required attributes."""
        from src.agricultural_land_detector import DetectionConfig

        detector = MagicMock()
        detector.config = DetectionConfig()
        return detector

    @pytest.fixture
    def sample_geojson_features(self):
        return [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[44.2, 15.5], [44.3, 15.5], [44.3, 15.6], [44.2, 15.6], [44.2, 15.5]]],
                },
                "properties": {
                    "parcel_id": "test-parcel-1",
                    "area_hectares": 10.5,
                    "perimeter_meters": 400,
                    "mean_ndvi": 0.65,
                    "mean_evi": 0.45,
                    "mean_ndwi": 0.1,
                    "detection_confidence": 0.85,
                    "land_cover": "cropland",
                    "ndvi_std": 0.05,
                    "compactness": 0.8,
                    "elongation": 1.2,
                    "rectangularity": 0.9,
                    "crop_type": "wheat",
                    "is_irrigated": True,
                    "quality_score": 0.92,
                },
            },
        ]

    def test_valid_features(self, mock_land_detector, sample_geojson_features):
        parcels = _geojson_to_parcels(sample_geojson_features, mock_land_detector)
        assert len(parcels) == 1
        p = parcels[0]
        assert p.parcel_id == "test-parcel-1"
        assert p.area_hectares == 10.5
        assert p.mean_ndvi == 0.65
        assert p.mean_evi == 0.45
        assert p.mean_ndwi == 0.1
        assert p.crop_type == "wheat"
        assert p.is_irrigated is True
        assert p.quality_score == 0.92
        assert len(p.coordinates) == 5

    def test_empty_features(self, mock_land_detector):
        parcels = _geojson_to_parcels([], mock_land_detector)
        assert parcels == []

    def test_feature_without_coordinates(self, mock_land_detector):
        features = [{"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[]]}, "properties": {}}]
        parcels = _geojson_to_parcels(features, mock_land_detector)
        assert len(parcels) == 0

    def test_feature_no_geometry(self, mock_land_detector):
        features = [{"type": "Feature", "properties": {}}]
        parcels = _geojson_to_parcels(features, mock_land_detector)
        assert len(parcels) == 0

    def test_default_properties(self, mock_land_detector):
        """Test that missing properties get default values."""
        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[44.2, 15.5], [44.3, 15.5], [44.3, 15.6]]],
                },
                "properties": {},
            },
        ]
        parcels = _geojson_to_parcels(features, mock_land_detector)
        assert len(parcels) == 1
        p = parcels[0]
        assert p.parcel_id == "parcel_0"
        assert p.area_hectares == 0
        assert p.mean_ndvi == 0.0
        assert p.detection_confidence == 0.0

    def test_unknown_land_cover(self, mock_land_detector):
        """Test that invalid land_cover defaults to UNKNOWN."""
        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[44.2, 15.5], [44.3, 15.5], [44.3, 15.6]]],
                },
                "properties": {"land_cover": "invalid_cover_type"},
            },
        ]
        parcels = _geojson_to_parcels(features, mock_land_detector)
        assert len(parcels) == 1
        from src.agricultural_land_detector import LandCoverClass

        assert parcels[0].land_cover == LandCoverClass.UNKNOWN

    def test_multiple_features(self, mock_land_detector):
        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[44.2, 15.5], [44.3, 15.5], [44.3, 15.6]]],
                },
                "properties": {"parcel_id": f"p{i}"},
            }
            for i in range(5)
        ]
        parcels = _geojson_to_parcels(features, mock_land_detector)
        assert len(parcels) == 5
        for i, p in enumerate(parcels):
            assert p.parcel_id == f"p{i}"

    def test_centroid_calculation(self, mock_land_detector):
        """Test that centroid is computed as average of coordinates."""
        features = [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0.0, 0.0], [2.0, 0.0], [2.0, 2.0], [0.0, 2.0]]],
                },
                "properties": {},
            },
        ]
        parcels = _geojson_to_parcels(features, mock_land_detector)
        assert len(parcels) == 1
        assert parcels[0].centroid == (1.0, 1.0)


# =============================================================================
# Endpoint Registration and Strategies Tests
# =============================================================================


class TestRegisterParcelEndpoints:
    """Test endpoint registration and the strategies endpoint."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock FastAPI app that captures registered endpoints."""
        app = MagicMock()
        registered_endpoints = {}

        def mock_post(path, **kwargs):
            def decorator(func):
                registered_endpoints[("POST", path)] = func
                return func

            return decorator

        def mock_get(path, **kwargs):
            def decorator(func):
                registered_endpoints[("GET", path)] = func
                return func

            return decorator

        app.post = mock_post
        app.get = mock_get
        app._registered = registered_endpoints
        return app

    @pytest.fixture
    def mock_detector(self):
        from src.agricultural_land_detector import DetectionConfig

        detector = MagicMock()
        detector.config = DetectionConfig()
        return detector

    def test_endpoints_registered(self, mock_app, mock_detector):
        register_parcel_endpoints(mock_app, mock_detector)
        registered = mock_app._registered

        assert ("POST", "/v1/parcels/auto-generate") in registered
        assert ("POST", "/v1/parcels/detect-region") in registered
        assert ("POST", "/v1/parcels/classify") in registered
        assert ("GET", "/v1/parcels/strategies") in registered
        assert ("POST", "/v1/parcels/classify-crops") in registered
        assert ("POST", "/v1/parcels/merge") in registered
        assert ("POST", "/v1/parcels/split") in registered
        assert ("POST", "/v1/parcels/connect") in registered
        assert ("POST", "/v1/parcels/inspect") in registered
        assert ("POST", "/v1/parcels/export-wkt") in registered
        assert ("POST", "/v1/parcels/batch-assign") in registered
        assert ("POST", "/v1/parcels/statistics") in registered
        assert ("POST", "/v1/parcels/simplify-topology") in registered

    @pytest.mark.asyncio
    async def test_strategies_endpoint(self, mock_app, mock_detector):
        register_parcel_endpoints(mock_app, mock_detector)
        strategies_func = mock_app._registered[("GET", "/v1/parcels/strategies")]
        result = await strategies_func()

        assert "strategies" in result
        assert "precision_levels" in result
        assert "shape_options" in result

        strategy_ids = [s["id"] for s in result["strategies"]]
        assert "hybrid" in strategy_ids
        assert "semantic_segmentation" in strategy_ids
        assert "boundary_detection" in strategy_ids
        assert "training_free" in strategy_ids

        precision_ids = [p["id"] for p in result["precision_levels"]]
        assert "very_high" in precision_ids
        assert "high" in precision_ids
        assert "acceptable" in precision_ids
        assert "speed_focused" in precision_ids

        shape_ids = [s["id"] for s in result["shape_options"]]
        assert "irregular" in shape_ids
        assert "rectangle" in shape_ids
        assert "convex_hull" in shape_ids
        assert "minimum_bounding" in shape_ids

    @pytest.mark.asyncio
    async def test_strategies_bilingual(self, mock_app, mock_detector):
        register_parcel_endpoints(mock_app, mock_detector)
        strategies_func = mock_app._registered[("GET", "/v1/parcels/strategies")]
        result = await strategies_func()

        for strategy in result["strategies"]:
            assert "en" in strategy["name"]
            assert "ar" in strategy["name"]
            assert "en" in strategy["description"]
            assert "ar" in strategy["description"]

    @pytest.mark.asyncio
    async def test_auto_generate_no_detector(self, mock_app):
        """Test that auto-generate raises 503 when detector is None."""
        register_parcel_endpoints(mock_app, None)
        auto_gen_func = mock_app._registered[("POST", "/v1/parcels/auto-generate")]

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await auto_gen_func(lat=15.5, lon=44.2, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_detect_region_no_detector(self, mock_app):
        """Test that detect-region raises 503 when detector is None."""
        register_parcel_endpoints(mock_app, None)
        detect_func = mock_app._registered[("POST", "/v1/parcels/detect-region")]
        req = RegionDetectionRequest(north=16.0, south=15.0, east=45.0, west=44.0)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await detect_func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_classify_no_detector(self, mock_app):
        register_parcel_endpoints(mock_app, None)
        classify_func = mock_app._registered[("POST", "/v1/parcels/classify")]
        req = ParcelClassifyRequest(parcels=[])

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await classify_func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_classify_crops_no_detector(self, mock_app):
        register_parcel_endpoints(mock_app, None)
        func = mock_app._registered[("POST", "/v1/parcels/classify-crops")]
        req = ParcelClassifyRequest(parcels=[])

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_merge_no_detector(self, mock_app):
        register_parcel_endpoints(mock_app, None)
        func = mock_app._registered[("POST", "/v1/parcels/merge")]
        req = ParcelMergeRequest(parcel_ids=["p1"], parcels=[{}])

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_split_no_detector(self, mock_app):
        register_parcel_endpoints(mock_app, None)
        func = mock_app._registered[("POST", "/v1/parcels/split")]
        req = ParcelSplitRequest(parcel={}, cutting_line=[[0, 0], [1, 1]])

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_connect_no_detector(self, mock_app):
        register_parcel_endpoints(mock_app, None)
        func = mock_app._registered[("POST", "/v1/parcels/connect")]
        req = ParcelConnectRequest(parcels=[{}, {}])

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_inspect_no_detector(self, mock_app):
        register_parcel_endpoints(mock_app, None)
        func = mock_app._registered[("POST", "/v1/parcels/inspect")]
        req = ParcelClassifyRequest(parcels=[])

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_export_wkt_no_detector(self, mock_app):
        register_parcel_endpoints(mock_app, None)
        func = mock_app._registered[("POST", "/v1/parcels/export-wkt")]
        req = ParcelClassifyRequest(parcels=[])

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_batch_assign_no_detector(self, mock_app):
        register_parcel_endpoints(mock_app, None)
        func = mock_app._registered[("POST", "/v1/parcels/batch-assign")]
        req = BatchAssignRequest(parcel_ids=[], parcels=[], attribute="crop_type", value="wheat")

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_statistics_no_detector(self, mock_app):
        register_parcel_endpoints(mock_app, None)
        func = mock_app._registered[("POST", "/v1/parcels/statistics")]
        req = ParcelClassifyRequest(parcels=[])

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_simplify_topology_no_detector(self, mock_app):
        register_parcel_endpoints(mock_app, None)
        func = mock_app._registered[("POST", "/v1/parcels/simplify-topology")]
        req = ParcelClassifyRequest(parcels=[])

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_detect_region_invalid_bounds(self, mock_app, mock_detector):
        """Test that detect-region raises 400 for invalid bounds."""
        register_parcel_endpoints(mock_app, mock_detector)
        detect_func = mock_app._registered[("POST", "/v1/parcels/detect-region")]

        # north <= south
        req = RegionDetectionRequest(north=15.0, south=16.0, east=45.0, west=44.0)
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await detect_func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_detect_region_east_west_invalid(self, mock_app, mock_detector):
        register_parcel_endpoints(mock_app, mock_detector)
        detect_func = mock_app._registered[("POST", "/v1/parcels/detect-region")]

        # east <= west
        req = RegionDetectionRequest(north=16.0, south=15.0, east=44.0, west=45.0)
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await detect_func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_classify_empty_parcels_raises_400(self, mock_app, mock_detector):
        """Test that classify raises 400 when no valid parcels provided."""
        register_parcel_endpoints(mock_app, mock_detector)
        classify_func = mock_app._registered[("POST", "/v1/parcels/classify")]
        req = ParcelClassifyRequest(parcels=[])

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await classify_func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_merge_insufficient_parcels(self, mock_app, mock_detector):
        """Test that merge raises 400 with fewer than 2 parcels."""
        register_parcel_endpoints(mock_app, mock_detector)
        func = mock_app._registered[("POST", "/v1/parcels/merge")]

        # One valid parcel
        req = ParcelMergeRequest(
            parcel_ids=["p1"],
            parcels=[
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[44.2, 15.5], [44.3, 15.5], [44.3, 15.6]]],
                    },
                    "properties": {},
                }
            ],
        )
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_split_invalid_parcel(self, mock_app, mock_detector):
        """Test that split raises 400 for invalid parcel."""
        register_parcel_endpoints(mock_app, mock_detector)
        func = mock_app._registered[("POST", "/v1/parcels/split")]
        req = ParcelSplitRequest(
            parcel={"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[]]}},
            cutting_line=[[44.2, 15.5], [44.3, 15.6]],
        )

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_split_insufficient_cutting_line(self, mock_app, mock_detector):
        """Test that split raises 400 for cutting line with < 2 points."""
        register_parcel_endpoints(mock_app, mock_detector)
        func = mock_app._registered[("POST", "/v1/parcels/split")]
        req = ParcelSplitRequest(
            parcel={
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[44.2, 15.5], [44.3, 15.5], [44.3, 15.6]]],
                },
            },
            cutting_line=[[44.2, 15.5]],
        )

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_batch_assign_invalid_attribute(self, mock_app, mock_detector):
        """Test that batch-assign raises 400 for invalid attribute."""
        register_parcel_endpoints(mock_app, mock_detector)
        func = mock_app._registered[("POST", "/v1/parcels/batch-assign")]
        req = BatchAssignRequest(
            parcel_ids=["p1"],
            parcels=[
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[44.2, 15.5], [44.3, 15.5], [44.3, 15.6]]],
                    },
                    "properties": {},
                }
            ],
            attribute="invalid_attr",
            value="test",
        )

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_connect_insufficient_parcels(self, mock_app, mock_detector):
        """Test that connect raises 400 with fewer than 2 parcels."""
        register_parcel_endpoints(mock_app, mock_detector)
        func = mock_app._registered[("POST", "/v1/parcels/connect")]
        req = ParcelConnectRequest(
            parcels=[
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[44.2, 15.5], [44.3, 15.5], [44.3, 15.6]]],
                    },
                    "properties": {},
                }
            ],
        )

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await func(req, _user=_MOCK_USER)
        assert exc_info.value.status_code == 400
