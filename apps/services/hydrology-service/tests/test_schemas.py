"""
Tests for Hydrology Service Pydantic schemas and models.
اختبارات نماذج البيانات لخدمة الهيدرولوجيا
"""

from datetime import datetime

import pytest
from pydantic import ValidationError
from src.api.schemas import (
    DEPRESSION_RISK_AR,
    DRAINAGE_TYPE_AR,
    MAX_FLOW_THRESHOLD,
    MAX_RAINFALL_MM,
    MAX_RESOLUTION_M,
    MIN_FLOW_THRESHOLD,
    # Constants
    MIN_RESOLUTION_M,
    # Arabic mappings
    WETNESS_LEVEL_AR,
    BasinDelineation,
    BasinDelineationRequest,
    BasinDelineationResponse,
    BoundingBox,
    Depression,
    DepressionAnalysis,
    DepressionAnalysisRequest,
    DepressionAnalysisResponse,
    DepressionRisk,
    DrainageAnalysisRequest,
    DrainageNetwork,
    DrainageNetworkResponse,
    # Response models
    DrainageSegment,
    # Enums
    DrainageType,
    # Base models
    GeoPoint,
    GeoPolygon,
    # Request models
    HydrologyAnalysisRequest,
    HydrologyAnalysisResponse,
    HydrologyAnalysisResult,
    Stream,
    StreamDetectionRequest,
    StreamNetwork,
    StreamNetworkResponse,
    StreamOrder,
    SubBasin,
    WaterloggingPrediction,
    WetnessAnalysis,
    WetnessAnalysisRequest,
    WetnessAnalysisResponse,
    WetnessLevel,
    WetnessZone,
)


# ==============================================================================
# Enum Tests
# ==============================================================================
class TestEnums:
    """Tests for enum types."""

    def test_drainage_type_values(self):
        """Test DrainageType enum has all expected values."""
        assert DrainageType.DENDRITIC == "dendritic"
        assert DrainageType.PARALLEL == "parallel"
        assert DrainageType.TRELLIS == "trellis"
        assert DrainageType.RECTANGULAR == "rectangular"
        assert DrainageType.RADIAL == "radial"
        assert DrainageType.CENTRIPETAL == "centripetal"
        assert DrainageType.DERANGED == "deranged"
        assert DrainageType.UNKNOWN == "unknown"

    def test_wetness_level_values(self):
        """Test WetnessLevel enum values."""
        assert WetnessLevel.VERY_DRY == "very_dry"
        assert WetnessLevel.DRY == "dry"
        assert WetnessLevel.MODERATE == "moderate"
        assert WetnessLevel.WET == "wet"
        assert WetnessLevel.VERY_WET == "very_wet"
        assert WetnessLevel.WATERLOGGED == "waterlogged"

    def test_depression_risk_values(self):
        """Test DepressionRisk enum values."""
        assert DepressionRisk.LOW == "low"
        assert DepressionRisk.MEDIUM == "medium"
        assert DepressionRisk.HIGH == "high"
        assert DepressionRisk.CRITICAL == "critical"

    def test_stream_order_values(self):
        """Test StreamOrder enum values."""
        assert StreamOrder.FIRST == 1
        assert StreamOrder.SECOND == 2
        assert StreamOrder.HIGHER == 6


# ==============================================================================
# Arabic Mapping Tests
# ==============================================================================
class TestArabicMappings:
    """Test Arabic label mappings."""

    def test_wetness_level_ar_complete(self):
        """All WetnessLevel values have Arabic translations."""
        for level in WetnessLevel:
            assert level in WETNESS_LEVEL_AR
            assert isinstance(WETNESS_LEVEL_AR[level], str)
            assert len(WETNESS_LEVEL_AR[level]) > 0

    def test_drainage_type_ar_complete(self):
        """All DrainageType values have Arabic translations."""
        for dtype in DrainageType:
            assert dtype in DRAINAGE_TYPE_AR
            assert isinstance(DRAINAGE_TYPE_AR[dtype], str)

    def test_depression_risk_ar_complete(self):
        """All DepressionRisk values have Arabic translations."""
        for risk in DepressionRisk:
            assert risk in DEPRESSION_RISK_AR
            assert isinstance(DEPRESSION_RISK_AR[risk], str)


# ==============================================================================
# Base Model Tests
# ==============================================================================
class TestGeoPoint:
    """Tests for GeoPoint model."""

    def test_valid_geo_point(self):
        """Test creating a valid GeoPoint."""
        point = GeoPoint(lat=24.7, lon=46.7)
        assert point.lat == 24.7
        assert point.lon == 46.7

    def test_geo_point_boundary_values(self):
        """Test GeoPoint with boundary lat/lon values."""
        point = GeoPoint(lat=90.0, lon=180.0)
        assert point.lat == 90.0
        point2 = GeoPoint(lat=-90.0, lon=-180.0)
        assert point2.lat == -90.0

    def test_geo_point_invalid_lat(self):
        """Test GeoPoint rejects invalid latitude."""
        with pytest.raises(ValidationError):
            GeoPoint(lat=91.0, lon=0.0)

    def test_geo_point_invalid_lon(self):
        """Test GeoPoint rejects invalid longitude."""
        with pytest.raises(ValidationError):
            GeoPoint(lat=0.0, lon=181.0)


class TestBoundingBox:
    """Tests for BoundingBox model."""

    def test_valid_bounding_box(self):
        """Test creating a valid BoundingBox."""
        bbox = BoundingBox(min_lat=15.0, max_lat=15.1, min_lon=45.0, max_lon=45.1)
        assert bbox.min_lat == 15.0
        assert bbox.max_lon == 45.1


class TestGeoPolygon:
    """Tests for GeoPolygon model."""

    def test_valid_polygon(self):
        """Test creating a valid polygon."""
        coords = [[45.0, 15.0], [45.1, 15.0], [45.1, 15.1], [45.0, 15.1]]
        poly = GeoPolygon(coordinates=coords)
        assert len(poly.coordinates) == 4
        assert poly.type == "Polygon"

    def test_polygon_too_few_coords(self):
        """Test polygon rejects fewer than 3 coordinate pairs."""
        with pytest.raises(ValidationError):
            GeoPolygon(coordinates=[[45.0, 15.0], [45.1, 15.0]])

    def test_polygon_invalid_type(self):
        """Test polygon rejects non-Polygon type."""
        coords = [[45.0, 15.0], [45.1, 15.0], [45.1, 15.1]]
        with pytest.raises(ValidationError):
            GeoPolygon(coordinates=coords, type="LineString")

    def test_polygon_invalid_coordinate_range(self):
        """Test polygon rejects out-of-range coordinates."""
        coords = [[200.0, 15.0], [45.1, 15.0], [45.1, 15.1]]
        with pytest.raises(ValidationError):
            GeoPolygon(coordinates=coords)

    def test_polygon_invalid_latitude_range(self):
        """Test polygon rejects latitude out of range."""
        coords = [[45.0, 100.0], [45.1, 15.0], [45.1, 15.1]]
        with pytest.raises(ValidationError):
            GeoPolygon(coordinates=coords)

    def test_polygon_non_numeric_coordinate(self):
        """Test polygon rejects non-numeric coordinates."""
        with pytest.raises(ValidationError):
            GeoPolygon(coordinates=[["abc", 15.0], [45.1, 15.0], [45.1, 15.1]])

    def test_polygon_incomplete_coordinate(self):
        """Test polygon rejects coordinate with fewer than 2 elements."""
        with pytest.raises(ValidationError):
            GeoPolygon(coordinates=[[45.0], [45.1, 15.0], [45.1, 15.1]])


# ==============================================================================
# Request Model Tests
# ==============================================================================
class TestHydrologyAnalysisRequest:
    """Tests for HydrologyAnalysisRequest."""

    def test_valid_request(self):
        """Test valid analysis request."""
        req = HydrologyAnalysisRequest(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            resolution_m=30.0,
        )
        assert req.field_id == "FIELD-001"
        assert req.tenant_id == "TENANT-001"
        assert req.resolution_m == 30.0
        assert req.include_rainfall is True

    def test_request_strips_whitespace(self):
        """Test that field_id and tenant_id are stripped."""
        req = HydrologyAnalysisRequest(
            field_id="  FIELD-001  ",
            tenant_id="  TENANT-001  ",
        )
        assert req.field_id == "FIELD-001"
        assert req.tenant_id == "TENANT-001"

    def test_request_empty_field_id(self):
        """Test request rejects empty field_id."""
        with pytest.raises(ValidationError):
            HydrologyAnalysisRequest(field_id="", tenant_id="T1")

    def test_request_empty_tenant_id(self):
        """Test request rejects empty tenant_id."""
        with pytest.raises(ValidationError):
            HydrologyAnalysisRequest(field_id="F1", tenant_id="")

    def test_request_whitespace_only_id(self):
        """Test request rejects whitespace-only IDs."""
        with pytest.raises(ValidationError):
            HydrologyAnalysisRequest(field_id="   ", tenant_id="T1")

    def test_request_resolution_range(self):
        """Test resolution_m validation."""
        with pytest.raises(ValidationError):
            HydrologyAnalysisRequest(field_id="F1", tenant_id="T1", resolution_m=0.5)
        with pytest.raises(ValidationError):
            HydrologyAnalysisRequest(field_id="F1", tenant_id="T1", resolution_m=1001)

    def test_request_valid_dem_sources(self):
        """Test valid DEM source values."""
        for source in ["srtm", "aster", "copernicus", "local", "custom"]:
            req = HydrologyAnalysisRequest(field_id="F1", tenant_id="T1", dem_source=source)
            assert req.dem_source == source

    def test_request_invalid_dem_source(self):
        """Test request rejects invalid DEM source."""
        with pytest.raises(ValidationError):
            HydrologyAnalysisRequest(field_id="F1", tenant_id="T1", dem_source="invalid")

    def test_request_dem_source_case_insensitive(self):
        """Test DEM source is case-insensitive."""
        req = HydrologyAnalysisRequest(field_id="F1", tenant_id="T1", dem_source="SRTM")
        assert req.dem_source == "srtm"

    def test_request_defaults(self):
        """Test default values."""
        req = HydrologyAnalysisRequest(field_id="F1", tenant_id="T1")
        assert req.resolution_m == 30.0
        assert req.include_rainfall is True
        assert req.rainfall_period_days == 30
        assert req.boundary is None
        assert req.dem_source is None
        assert req.correlation_id is None


class TestDrainageAnalysisRequest:
    """Tests for DrainageAnalysisRequest."""

    def test_valid_drainage_request(self):
        """Test valid drainage request."""
        req = DrainageAnalysisRequest(field_id="FIELD-001", flow_threshold=200)
        assert req.field_id == "FIELD-001"
        assert req.flow_threshold == 200

    def test_drainage_request_flow_threshold_bounds(self):
        """Test flow threshold validation bounds."""
        with pytest.raises(ValidationError):
            DrainageAnalysisRequest(field_id="F1", flow_threshold=0)
        with pytest.raises(ValidationError):
            DrainageAnalysisRequest(field_id="F1", flow_threshold=100001)

    def test_drainage_request_empty_field_id(self):
        """Test drainage request rejects empty field_id."""
        with pytest.raises(ValidationError):
            DrainageAnalysisRequest(field_id="   ")


class TestWetnessAnalysisRequest:
    """Tests for WetnessAnalysisRequest."""

    def test_valid_wetness_request(self):
        """Test valid wetness request."""
        req = WetnessAnalysisRequest(field_id="FIELD-001", rainfall_mm=50.0)
        assert req.rainfall_mm == 50.0

    def test_wetness_request_rainfall_bounds(self):
        """Test rainfall_mm validation."""
        with pytest.raises(ValidationError):
            WetnessAnalysisRequest(field_id="F1", rainfall_mm=-1.0)
        with pytest.raises(ValidationError):
            WetnessAnalysisRequest(field_id="F1", rainfall_mm=2001.0)


class TestDepressionAnalysisRequest:
    """Tests for DepressionAnalysisRequest."""

    def test_valid_depression_request(self):
        """Test valid depression request."""
        req = DepressionAnalysisRequest(field_id="F1", min_depth_m=0.5, min_area_sqm=100.0)
        assert req.min_depth_m == 0.5
        assert req.min_area_sqm == 100.0

    def test_depression_request_depth_bounds(self):
        """Test min_depth_m validation."""
        with pytest.raises(ValidationError):
            DepressionAnalysisRequest(field_id="F1", min_depth_m=0.001)
        with pytest.raises(ValidationError):
            DepressionAnalysisRequest(field_id="F1", min_depth_m=11.0)


class TestStreamDetectionRequest:
    """Tests for StreamDetectionRequest."""

    def test_valid_stream_request(self):
        """Test valid stream detection request."""
        req = StreamDetectionRequest(field_id="F1", min_order=2)
        assert req.min_order == 2

    def test_stream_request_order_bounds(self):
        """Test min_order bounds."""
        with pytest.raises(ValidationError):
            StreamDetectionRequest(field_id="F1", min_order=0)
        with pytest.raises(ValidationError):
            StreamDetectionRequest(field_id="F1", min_order=7)


class TestBasinDelineationRequest:
    """Tests for BasinDelineationRequest."""

    def test_valid_basin_request(self):
        """Test valid basin delineation request."""
        req = BasinDelineationRequest(field_id="F1", min_area_ha=1.0)
        assert req.min_area_ha == 1.0

    def test_basin_request_with_pour_point(self):
        """Test basin request with pour point."""
        req = BasinDelineationRequest(
            field_id="F1",
            pour_point=GeoPoint(lat=15.0, lon=45.0),
        )
        assert req.pour_point is not None
        assert req.pour_point.lat == 15.0

    def test_basin_request_area_bounds(self):
        """Test min_area_ha bounds."""
        with pytest.raises(ValidationError):
            BasinDelineationRequest(field_id="F1", min_area_ha=0.01)


# ==============================================================================
# Response Model Tests
# ==============================================================================
class TestDrainageSegment:
    """Tests for DrainageSegment response model."""

    def test_valid_segment(self):
        """Test creating a valid drainage segment."""
        seg = DrainageSegment(
            segment_id="seg-001",
            coordinates=[[45.0, 15.0], [45.01, 15.01]],
            stream_order=1,
            length_m=100.0,
            upstream_area_ha=5.0,
            slope_percent=3.5,
        )
        assert seg.segment_id == "seg-001"
        assert seg.stream_order == 1


class TestWaterloggingPrediction:
    """Tests for WaterloggingPrediction response model."""

    def test_valid_prediction(self):
        """Test creating a valid waterlogging prediction."""
        pred = WaterloggingPrediction(
            rainfall_mm=50.0,
            risk_level=DepressionRisk.MEDIUM,
            risk_level_ar="متوسط",
            affected_area_ha=2.5,
            affected_percentage=10.0,
            time_to_drain_hours=48.0,
        )
        assert pred.rainfall_mm == 50.0
        assert pred.risk_level == DepressionRisk.MEDIUM


class TestValidationConstants:
    """Test validation constants are correct."""

    def test_resolution_bounds(self):
        """Test resolution min/max constants."""
        assert MIN_RESOLUTION_M == 1.0
        assert MAX_RESOLUTION_M == 1000.0

    def test_flow_threshold_bounds(self):
        """Test flow threshold min/max constants."""
        assert MIN_FLOW_THRESHOLD == 1
        assert MAX_FLOW_THRESHOLD == 100000

    def test_max_rainfall(self):
        """Test max rainfall constant."""
        assert MAX_RAINFALL_MM == 2000.0
