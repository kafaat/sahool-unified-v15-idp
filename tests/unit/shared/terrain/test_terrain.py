"""
Unit tests for shared/terrain/ module.

Tests cover:
- Validators: coordinate, GeoJSON, elevation, grade, field ID, resolution, batch size
- GeoJSON utilities: parsing, creation, calculations, bbox, WKT conversion, simplification
- Cache: LRU cache, cache key generation, TerrainCache, geometry hash
- Responses: success/error/paginated/batch responses, bilingual messages, ResponseTimer
- Batch processing: BatchProcessor, process_batch, BatchResult, format_batch_result
"""

from __future__ import annotations

import asyncio
import math
import time

import pytest

# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------
from shared.terrain.validators import (
    AGRICULTURAL_ELEVATION_MAX_M,
    AGRICULTURAL_ELEVATION_MIN_M,
    ELEVATION_MAX_M,
    ELEVATION_MIN_M,
    GLOBAL_BOUNDS,
    MAX_GRADE_PERCENT,
    MENA_BOUNDS,
    MIN_GRADE_PERCENT,
    SAUDI_ARABIA_BOUNDS,
    BoundingBoxModel,
    CoordinateModel,
    ElevationPointModel,
    GradeModel,
    ValidationError,
    sanitize_field_id,
    validate_batch_size,
    validate_coordinate,
    validate_coordinate_list,
    validate_elevation,
    validate_elevation_point,
    validate_field_id,
    validate_geojson_linestring,
    validate_geojson_point,
    validate_geojson_polygon,
    validate_grade_percentage,
    validate_resolution,
    validate_slope_degrees,
)

# ---------------------------------------------------------------------------
# GeoJSON utilities
# ---------------------------------------------------------------------------
from shared.terrain.geojson_utils import (
    EARTH_RADIUS_M,
    calculate_bbox_linestring,
    calculate_bbox_polygon,
    calculate_linestring_centroid,
    calculate_linestring_length,
    calculate_polygon_area_geodesic,
    calculate_polygon_centroid,
    calculate_polygon_perimeter,
    create_feature_collection,
    create_linestring,
    create_point,
    create_polygon,
    geometry_to_wkt,
    haversine_distance,
    merge_bboxes,
    parse_geojson_feature,
    parse_geojson_geometry,
    round_coordinates,
    simplify_coordinates,
    wkt_to_geometry,
)

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------
from shared.terrain.cache import (
    DEFAULT_TTL_SECONDS,
    CacheEntry,
    LRUCache,
    TerrainCache,
    generate_cache_key,
    generate_geometry_hash,
)

# ---------------------------------------------------------------------------
# Responses
# ---------------------------------------------------------------------------
from shared.terrain.responses import (
    MESSAGES,
    ERROR_MESSAGES,
    BilingualMessage,
    ResponseStatus,
    ResponseTimer,
    batch_response,
    error_response,
    geojson_response,
    paginated_response,
    success_response,
)

# ---------------------------------------------------------------------------
# Batch
# ---------------------------------------------------------------------------
from shared.terrain.batch import (
    BatchItemResult,
    BatchItemStatus,
    BatchProcessor,
    BatchRequest,
    BatchResult,
    BatchStatus,
    create_batch_requests,
    format_batch_result,
    process_batch,
)


# =============================================================================
# Helpers / Fixtures
# =============================================================================

# A simple closed polygon ring in Riyadh area (4 points + closing)
RIYADH_RING = [
    [46.7, 24.7],
    [46.8, 24.7],
    [46.8, 24.8],
    [46.7, 24.8],
    [46.7, 24.7],
]

RIYADH_POLYGON_GEOMETRY = {
    "type": "Polygon",
    "coordinates": [RIYADH_RING],
}


# =============================================================================
# 1. Validator Tests
# =============================================================================


@pytest.mark.unit
class TestValidateCoordinate:
    """Tests for validate_coordinate and validate_coordinate_list."""

    def test_valid_global_coordinate(self):
        result = validate_coordinate(46.7, 24.7)
        assert result == (46.7, 24.7)

    def test_coordinate_outside_latitude_range(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_coordinate(46.0, 100.0)
        assert "Latitude" in exc_info.value.message
        assert "خط العرض" in exc_info.value.message_ar

    def test_coordinate_outside_longitude_range(self):
        with pytest.raises(ValidationError):
            validate_coordinate(200.0, 24.0)

    def test_coordinate_with_saudi_bounds(self):
        result = validate_coordinate(46.0, 24.0, bounds=SAUDI_ARABIA_BOUNDS)
        assert result == (46.0, 24.0)

    def test_coordinate_outside_saudi_bounds(self):
        with pytest.raises(ValidationError):
            validate_coordinate(10.0, 24.0, bounds=SAUDI_ARABIA_BOUNDS)

    def test_validate_coordinate_list_valid(self):
        coords = [[46.7, 24.7], [46.8, 24.7], [46.8, 24.8]]
        result = validate_coordinate_list(coords, min_points=3)
        assert len(result) == 3

    def test_validate_coordinate_list_empty(self):
        with pytest.raises(ValidationError):
            validate_coordinate_list([])

    def test_validate_coordinate_list_too_few_points(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_coordinate_list([[46.7, 24.7]], min_points=3)
        assert "3" in exc_info.value.message

    def test_validate_coordinate_list_require_closed(self):
        closed = [[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.7]]
        result = validate_coordinate_list(closed, min_points=3, require_closed=True)
        assert result[0] == result[-1]

    def test_validate_coordinate_list_not_closed_raises(self):
        not_closed = [[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.9]]
        with pytest.raises(ValidationError) as exc_info:
            validate_coordinate_list(not_closed, min_points=3, require_closed=True)
        assert "closed" in exc_info.value.message.lower()

    def test_validate_coordinate_list_non_numeric(self):
        with pytest.raises(ValidationError):
            validate_coordinate_list([["abc", "def"]], min_points=1)


@pytest.mark.unit
class TestGeoJSONValidation:
    """Tests for GeoJSON geometry validators."""

    def test_valid_polygon(self):
        result = validate_geojson_polygon(RIYADH_POLYGON_GEOMETRY)
        assert result["type"] == "Polygon"

    def test_polygon_wrong_type(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_geojson_polygon({"type": "Point", "coordinates": [46.7, 24.7]})
        assert "Polygon" in exc_info.value.message

    def test_polygon_not_dict(self):
        with pytest.raises(ValidationError):
            validate_geojson_polygon("not a dict")

    def test_polygon_missing_coordinates(self):
        with pytest.raises(ValidationError):
            validate_geojson_polygon({"type": "Polygon"})

    def test_valid_point(self):
        geom = {"type": "Point", "coordinates": [46.7, 24.7]}
        result = validate_geojson_point(geom)
        assert result["type"] == "Point"

    def test_point_wrong_type(self):
        with pytest.raises(ValidationError):
            validate_geojson_point({"type": "Polygon", "coordinates": [RIYADH_RING]})

    def test_valid_linestring(self):
        geom = {"type": "LineString", "coordinates": [[46.7, 24.7], [46.8, 24.8]]}
        result = validate_geojson_linestring(geom)
        assert result["type"] == "LineString"

    def test_linestring_too_few_points(self):
        geom = {"type": "LineString", "coordinates": [[46.7, 24.7]]}
        with pytest.raises(ValidationError):
            validate_geojson_linestring(geom)


@pytest.mark.unit
class TestElevationGradeValidation:
    """Tests for elevation and grade validators."""

    def test_valid_elevation(self):
        assert validate_elevation(500.0) == 500.0

    def test_elevation_below_min(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_elevation(-500.0)
        assert "الارتفاع" in exc_info.value.message_ar

    def test_elevation_above_max(self):
        with pytest.raises(ValidationError):
            validate_elevation(4000.0)

    def test_elevation_custom_range(self):
        assert validate_elevation(100.0, min_elevation=0.0, max_elevation=200.0) == 100.0

    def test_validate_elevation_point(self):
        result = validate_elevation_point(46.7, 24.7, 500.0)
        assert result == (46.7, 24.7, 500.0)

    def test_valid_grade_percentage(self):
        assert validate_grade_percentage(1.0) == 1.0

    def test_grade_out_of_range(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_grade_percentage(20.0)
        assert "الميل" in exc_info.value.message_ar

    def test_valid_slope_degrees(self):
        assert validate_slope_degrees(45.0) == 45.0

    def test_slope_out_of_range(self):
        with pytest.raises(ValidationError):
            validate_slope_degrees(100.0)

    def test_validate_resolution_valid(self):
        assert validate_resolution(10.0) == 10.0

    def test_validate_resolution_out_of_range(self):
        with pytest.raises(ValidationError):
            validate_resolution(0.01)


@pytest.mark.unit
class TestFieldIDValidation:
    """Tests for field ID validation and sanitization."""

    def test_valid_field_id_prefix(self):
        assert validate_field_id("FIELD-ABCDEFGH") == "FIELD-ABCDEFGH"

    def test_valid_uuid_field_id(self):
        uid = "550e8400-e29b-41d4-a716-446655440000"
        assert validate_field_id(uid) == uid

    def test_empty_field_id(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_field_id("")
        assert "معرف الحقل" in exc_info.value.message_ar

    def test_invalid_field_id_format(self):
        with pytest.raises(ValidationError):
            validate_field_id("!!", allow_uuid=False)

    def test_sanitize_field_id_strips_special_chars(self):
        assert sanitize_field_id("FIELD<script>-001") == "FIELDscript-001"

    def test_sanitize_field_id_empty(self):
        assert sanitize_field_id("") == ""

    def test_sanitize_field_id_truncates(self):
        long_id = "A" * 100
        assert len(sanitize_field_id(long_id)) == 64

    def test_validate_batch_size_valid(self):
        assert validate_batch_size(50) == 50

    def test_validate_batch_size_out_of_range(self):
        with pytest.raises(ValidationError):
            validate_batch_size(0)


# =============================================================================
# 2. Pydantic Model Tests
# =============================================================================


@pytest.mark.unit
class TestPydanticModels:
    """Tests for Pydantic terrain models."""

    def test_coordinate_model_valid(self):
        m = CoordinateModel(longitude=46.7, latitude=24.7)
        assert m.longitude == 46.7

    def test_coordinate_model_invalid_longitude(self):
        with pytest.raises(Exception):
            CoordinateModel(longitude=200.0, latitude=24.7)

    def test_elevation_point_model_valid(self):
        m = ElevationPointModel(x=46.7, y=24.7, elevation=500.0)
        assert m.elevation == 500.0

    def test_elevation_point_model_invalid_elevation(self):
        with pytest.raises(Exception):
            ElevationPointModel(x=46.7, y=24.7, elevation=5000.0)

    def test_grade_model_valid(self):
        m = GradeModel(grade_x_percent=1.0, grade_y_percent=-2.0)
        assert m.grade_x_percent == 1.0

    def test_grade_model_none_allowed(self):
        m = GradeModel()
        assert m.grade_x_percent is None

    def test_grade_model_out_of_range(self):
        with pytest.raises(Exception):
            GradeModel(grade_x_percent=20.0)

    def test_bounding_box_model_valid(self):
        m = BoundingBoxModel(min_lon=46.0, min_lat=24.0, max_lon=47.0, max_lat=25.0)
        assert m.max_lon > m.min_lon

    def test_bounding_box_model_invalid_order(self):
        with pytest.raises(Exception):
            BoundingBoxModel(min_lon=47.0, min_lat=24.0, max_lon=46.0, max_lat=25.0)


# =============================================================================
# 3. GeoJSON Utilities Tests
# =============================================================================


@pytest.mark.unit
class TestGeoJSONUtilities:
    """Tests for GeoJSON creation, parsing, and calculation utilities."""

    def test_create_point(self):
        feature = create_point(46.7, 24.7, properties={"name": "test"})
        assert feature["type"] == "Feature"
        assert feature["geometry"]["type"] == "Point"
        assert feature["properties"]["name"] == "test"

    def test_create_point_with_id(self):
        feature = create_point(46.7, 24.7, feature_id="p1")
        assert feature["id"] == "p1"

    def test_create_linestring(self):
        coords = [(46.7, 24.7), (46.8, 24.8)]
        feature = create_linestring(coords, feature_id="ls1")
        assert feature["geometry"]["type"] == "LineString"
        assert len(feature["geometry"]["coordinates"]) == 2

    def test_create_polygon_auto_closes(self):
        coords = [(46.7, 24.7), (46.8, 24.7), (46.8, 24.8)]
        feature = create_polygon(coords, ensure_closed=True)
        ring = feature["geometry"]["coordinates"][0]
        assert ring[0] == ring[-1]

    def test_create_feature_collection(self):
        p1 = create_point(46.7, 24.7)
        p2 = create_point(46.8, 24.8)
        fc = create_feature_collection([p1, p2])
        assert fc["type"] == "FeatureCollection"
        assert len(fc["features"]) == 2
        assert "bbox" in fc

    def test_haversine_distance_same_point(self):
        d = haversine_distance(46.7, 24.7, 46.7, 24.7)
        assert d == pytest.approx(0.0, abs=1e-6)

    def test_haversine_distance_known_value(self):
        # Approx distance Riyadh to Jeddah (~950 km)
        d = haversine_distance(46.7, 24.7, 39.2, 21.5)
        assert 800_000 < d < 1_100_000

    def test_polygon_area_nonzero(self):
        area = calculate_polygon_area_geodesic([RIYADH_RING])
        assert area > 0

    def test_polygon_area_empty(self):
        assert calculate_polygon_area_geodesic([]) == 0.0

    def test_polygon_perimeter_nonzero(self):
        perimeter = calculate_polygon_perimeter([RIYADH_RING])
        assert perimeter > 0

    def test_polygon_centroid(self):
        centroid = calculate_polygon_centroid([RIYADH_RING])
        assert centroid is not None
        lon, lat = centroid
        assert 46.7 <= lon <= 46.8
        assert 24.7 <= lat <= 24.8

    def test_linestring_length(self):
        coords = [[46.7, 24.7], [46.8, 24.8]]
        length = calculate_linestring_length(coords)
        assert length > 0

    def test_linestring_centroid(self):
        coords = [[46.7, 24.7], [46.9, 24.9]]
        centroid = calculate_linestring_centroid(coords)
        assert centroid is not None
        assert centroid[0] == pytest.approx(46.8)
        assert centroid[1] == pytest.approx(24.8)

    def test_bbox_polygon(self):
        bbox = calculate_bbox_polygon([RIYADH_RING])
        min_lon, min_lat, max_lon, max_lat = bbox
        assert min_lon == pytest.approx(46.7)
        assert max_lon == pytest.approx(46.8)

    def test_bbox_linestring(self):
        coords = [[10.0, 20.0], [30.0, 40.0]]
        bbox = calculate_bbox_linestring(coords)
        assert bbox == (10.0, 20.0, 30.0, 40.0)

    def test_merge_bboxes(self):
        b1 = (0.0, 0.0, 1.0, 1.0)
        b2 = (2.0, 2.0, 3.0, 3.0)
        merged = merge_bboxes([b1, b2])
        assert merged == (0.0, 0.0, 3.0, 3.0)

    def test_merge_bboxes_empty(self):
        assert merge_bboxes([]) == (0.0, 0.0, 0.0, 0.0)

    def test_parse_geojson_geometry_polygon(self):
        geom = parse_geojson_geometry(RIYADH_POLYGON_GEOMETRY)
        assert geom.is_valid
        assert geom.type == "Polygon"
        assert geom.area_sqm is not None and geom.area_sqm > 0
        assert geom.bbox is not None

    def test_parse_geojson_geometry_invalid_type(self):
        geom = parse_geojson_geometry({"type": "InvalidType", "coordinates": []})
        assert not geom.is_valid

    def test_parse_geojson_feature(self):
        data = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [46.7, 24.7]},
            "properties": {"field_id": "F1"},
            "id": "feat-1",
        }
        feat = parse_geojson_feature(data)
        assert feat.id == "feat-1"
        assert feat.geometry is not None
        assert feat.geometry.type == "Point"

    def test_round_coordinates(self):
        coords = [46.123456789, 24.987654321]
        rounded = round_coordinates(coords, precision=3)
        assert rounded == [46.123, 24.988]

    def test_simplify_coordinates_short_list(self):
        # 4 or fewer points returned as-is
        coords = [[0, 0], [1, 1], [2, 0], [0, 0]]
        result = simplify_coordinates(coords)
        assert result == coords

    def test_geometry_to_wkt_point(self):
        geom = {"type": "Point", "coordinates": [46.7, 24.7]}
        wkt = geometry_to_wkt(geom)
        assert wkt == "POINT(46.7 24.7)"

    def test_geometry_to_wkt_linestring(self):
        geom = {"type": "LineString", "coordinates": [[1, 2], [3, 4]]}
        wkt = geometry_to_wkt(geom)
        assert "LINESTRING" in wkt

    def test_wkt_to_geometry_point(self):
        geom = wkt_to_geometry("POINT(46.7 24.7)")
        assert geom is not None
        assert geom["type"] == "Point"
        assert geom["coordinates"] == [46.7, 24.7]

    def test_wkt_to_geometry_linestring(self):
        geom = wkt_to_geometry("LINESTRING(1 2, 3 4)")
        assert geom is not None
        assert geom["type"] == "LineString"
        assert len(geom["coordinates"]) == 2

    def test_wkt_to_geometry_invalid(self):
        assert wkt_to_geometry("GARBAGE") is None


# =============================================================================
# 4. Cache Tests
# =============================================================================


@pytest.mark.unit
class TestLRUCache:
    """Tests for LRUCache."""

    def test_set_and_get(self):
        cache = LRUCache(max_size=10)
        cache.set("k1", "v1", ttl=60)
        assert cache.get("k1") == "v1"

    def test_get_miss(self):
        cache = LRUCache()
        assert cache.get("nonexistent") is None

    def test_expiry(self):
        cache = LRUCache()
        cache.set("k1", "v1", ttl=0)
        # TTL=0 means it expires immediately (time.time() + 0 is already past)
        time.sleep(0.01)
        assert cache.get("k1") is None

    def test_eviction_on_max_size(self):
        cache = LRUCache(max_size=2)
        cache.set("k1", "v1", ttl=600)
        cache.set("k2", "v2", ttl=600)
        cache.set("k3", "v3", ttl=600)
        # k1 should have been evicted (oldest)
        assert cache.get("k1") is None
        assert cache.get("k3") == "v3"

    def test_delete(self):
        cache = LRUCache()
        cache.set("k1", "v1", ttl=60)
        assert cache.delete("k1") is True
        assert cache.get("k1") is None
        assert cache.delete("k1") is False

    def test_clear(self):
        cache = LRUCache()
        cache.set("k1", "v1", ttl=60)
        cache.clear()
        assert cache.get("k1") is None

    def test_stats(self):
        cache = LRUCache(max_size=100)
        cache.set("k1", "v1", ttl=60)
        cache.get("k1")  # hit
        cache.get("k2")  # miss
        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["size"] == 1

    def test_cleanup_expired(self):
        cache = LRUCache()
        cache.set("k1", "v1", ttl=0)
        time.sleep(0.01)
        removed = cache.cleanup_expired()
        assert removed == 1


@pytest.mark.unit
class TestCacheKeyGeneration:
    """Tests for cache key and geometry hash generation."""

    def test_generate_cache_key_deterministic(self):
        key1 = generate_cache_key("slope", "FIELD-001", resolution=10)
        key2 = generate_cache_key("slope", "FIELD-001", resolution=10)
        assert key1 == key2

    def test_generate_cache_key_different_params(self):
        key1 = generate_cache_key("slope", "FIELD-001", resolution=10)
        key2 = generate_cache_key("slope", "FIELD-001", resolution=20)
        assert key1 != key2

    def test_generate_cache_key_format(self):
        key = generate_cache_key("twi", "FIELD-001")
        assert key.startswith("FIELD-001:twi:")

    def test_generate_geometry_hash_deterministic(self):
        geom = {"type": "Point", "coordinates": [46.7, 24.7]}
        h1 = generate_geometry_hash(geom)
        h2 = generate_geometry_hash(geom)
        assert h1 == h2

    def test_generate_geometry_hash_different_geom(self):
        g1 = {"type": "Point", "coordinates": [46.7, 24.7]}
        g2 = {"type": "Point", "coordinates": [46.8, 24.8]}
        assert generate_geometry_hash(g1) != generate_geometry_hash(g2)


@pytest.mark.unit
class TestCacheEntry:
    """Tests for CacheEntry."""

    def test_not_expired(self):
        entry = CacheEntry(value="data", expires_at=time.time() + 3600)
        assert not entry.is_expired()

    def test_expired(self):
        entry = CacheEntry(value="data", expires_at=time.time() - 1)
        assert entry.is_expired()


@pytest.mark.unit
class TestTerrainCache:
    """Tests for TerrainCache (memory-only, no Redis)."""

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        cache = TerrainCache(namespace="test", use_redis=False)
        await cache.set("k1", {"slope": 5.0}, ttl=60)
        result = await cache.get("k1")
        assert result == {"slope": 5.0}

    @pytest.mark.asyncio
    async def test_get_miss(self):
        cache = TerrainCache(namespace="test", use_redis=False)
        assert await cache.get("nonexistent") is None

    @pytest.mark.asyncio
    async def test_delete(self):
        cache = TerrainCache(namespace="test", use_redis=False)
        await cache.set("k1", "v1", ttl=60)
        deleted = await cache.delete("k1")
        assert deleted is True
        assert await cache.get("k1") is None

    @pytest.mark.asyncio
    async def test_invalidate_field(self):
        cache = TerrainCache(namespace="test", use_redis=False)
        # The internal key is namespace:key, and invalidate_field uses namespace:field_id prefix
        # We need to set keys that match the invalidation prefix
        cache._memory_cache.set("test:FIELD-001:slope:abc", "v1", ttl=60)
        cache._memory_cache.set("test:FIELD-001:twi:def", "v2", ttl=60)
        count = await cache.invalidate_field("FIELD-001")
        assert count == 2

    def test_stats(self):
        cache = TerrainCache(namespace="test", use_redis=False)
        stats = cache.stats()
        assert stats["enabled"] is True
        assert stats["namespace"] == "test"
        assert "memory" in stats


# =============================================================================
# 5. Response Tests
# =============================================================================


@pytest.mark.unit
class TestResponses:
    """Tests for response builders and bilingual messages."""

    def test_bilingual_message_to_dict(self):
        msg = BilingualMessage(en="Hello", ar="مرحبا")
        d = msg.to_dict()
        assert d["en"] == "Hello"
        assert d["ar"] == "مرحبا"

    def test_messages_bilingual_keys(self):
        for key, msg in MESSAGES.items():
            assert msg.en, f"Missing English for MESSAGES['{key}']"
            assert msg.ar, f"Missing Arabic for MESSAGES['{key}']"

    def test_error_messages_bilingual_keys(self):
        for key, msg in ERROR_MESSAGES.items():
            assert msg.en, f"Missing English for ERROR_MESSAGES['{key}']"
            assert msg.ar, f"Missing Arabic for ERROR_MESSAGES['{key}']"

    def test_success_response_structure(self):
        resp = success_response(data={"slope": 5.0}, message_key="slope_complete")
        assert resp["success"] is True
        assert resp["status"] == ResponseStatus.SUCCESS
        assert "Slope" in resp["message"]
        assert "الميل" in resp["message_ar"]
        assert resp["data"] == {"slope": 5.0}
        assert "meta" in resp

    def test_success_response_cached(self):
        resp = success_response(data={}, cached=True)
        assert "cache" in resp["message"].lower()
        assert resp["meta"]["processing"]["cached"] is True

    def test_error_response_structure(self):
        resp = error_response(
            error_key="validation_error",
            detail="Bad input",
            detail_ar="مدخلات سيئة",
            field="geometry",
        )
        assert resp["success"] is False
        assert resp["error"] == "validation_error"
        assert resp["detail"] == "Bad input"
        assert resp["detail_ar"] == "مدخلات سيئة"
        assert resp["field"] == "geometry"

    def test_error_response_unknown_key_falls_back(self):
        resp = error_response(error_key="unknown_key")
        # Falls back to "processing_error"
        assert "processing" in resp["message"].lower() or "error" in resp["message"].lower()

    def test_paginated_response(self):
        items = list(range(10))
        resp = paginated_response(data=items, total_items=100, page=2, page_size=10)
        assert resp["success"] is True
        pagination = resp["meta"]["pagination"]
        assert pagination["page"] == 2
        assert pagination["total_pages"] == 10
        assert pagination["has_next"] is True
        assert pagination["has_prev"] is True

    def test_paginated_response_first_page(self):
        resp = paginated_response(data=[], total_items=20, page=1, page_size=10)
        assert resp["meta"]["pagination"]["has_prev"] is False
        assert resp["meta"]["pagination"]["has_next"] is True

    def test_batch_response_all_success(self):
        results = [{"id": "1", "status": "success"}]
        resp = batch_response(results, success_count=1, error_count=0)
        assert resp["success"] is True
        assert resp["status"] == ResponseStatus.SUCCESS

    def test_batch_response_partial(self):
        results = [{"id": "1"}, {"id": "2"}]
        resp = batch_response(results, success_count=1, error_count=1)
        assert resp["success"] is False
        assert resp["status"] == ResponseStatus.PARTIAL
        assert resp["data"]["summary"]["error_count"] == 1

    def test_response_timer(self):
        with ResponseTimer() as timer:
            time.sleep(0.01)
        assert timer.elapsed_ms > 0
        assert timer.elapsed_seconds > 0

    def test_geojson_response(self):
        geom = {"type": "Point", "coordinates": [46.7, 24.7]}
        resp = geojson_response(geom, properties={"name": "test"})
        assert resp["success"] is True
        assert resp["data"]["type"] == "Feature"
        assert resp["data"]["geometry"]["type"] == "Point"
        assert resp["data"]["properties"]["name"] == "test"


# =============================================================================
# 6. Batch Processing Tests
# =============================================================================


@pytest.mark.unit
class TestBatchDataClasses:
    """Tests for batch data classes."""

    def test_batch_request_defaults(self):
        req = BatchRequest(data="item1")
        assert req.data == "item1"
        assert req.priority == 0
        assert req.id  # auto-generated UUID

    def test_batch_item_result(self):
        r = BatchItemResult(request_id="r1", status=BatchItemStatus.SUCCESS, result=42)
        assert r.result == 42
        assert r.status == BatchItemStatus.SUCCESS

    def test_batch_result_add_and_finalize(self):
        br = BatchResult()
        br.add_result(BatchItemResult(request_id="1", status=BatchItemStatus.SUCCESS))
        br.add_result(BatchItemResult(request_id="2", status=BatchItemStatus.ERROR, error="fail"))
        br.add_result(BatchItemResult(request_id="3", status=BatchItemStatus.SKIPPED))
        br.finalize()

        assert br.total_items == 3
        assert br.success_count == 1
        assert br.error_count == 1
        assert br.skipped_count == 1
        assert br.status == BatchStatus.PARTIAL

    def test_batch_result_all_failed(self):
        br = BatchResult()
        br.add_result(BatchItemResult(request_id="1", status=BatchItemStatus.ERROR))
        br.add_result(BatchItemResult(request_id="2", status=BatchItemStatus.ERROR))
        br.finalize()
        assert br.status == BatchStatus.FAILED

    def test_batch_result_all_succeeded(self):
        br = BatchResult()
        br.add_result(BatchItemResult(request_id="1", status=BatchItemStatus.SUCCESS))
        br.finalize()
        assert br.status == BatchStatus.COMPLETED

    def test_create_batch_requests(self):
        items = [{"field_id": "F1"}, {"field_id": "F2"}]
        reqs = create_batch_requests(items)
        assert len(reqs) == 2
        assert reqs[0].id == "F1"

    def test_format_batch_result(self):
        br = BatchResult()
        br.add_result(BatchItemResult(request_id="r1", status=BatchItemStatus.SUCCESS, result="ok"))
        br.finalize()
        formatted = format_batch_result(br, include_all_results=True)
        assert "results" in formatted
        assert formatted["summary"]["success_count"] == 1

    def test_format_batch_result_errors_only(self):
        br = BatchResult()
        br.add_result(BatchItemResult(request_id="r1", status=BatchItemStatus.SUCCESS, result="ok"))
        br.add_result(
            BatchItemResult(request_id="r2", status=BatchItemStatus.ERROR, error="bad")
        )
        br.finalize()
        formatted = format_batch_result(br, include_all_results=False)
        assert "errors" in formatted
        assert len(formatted["errors"]) == 1


@pytest.mark.unit
class TestBatchProcessor:
    """Tests for async BatchProcessor and process_batch."""

    @pytest.mark.asyncio
    async def test_process_batch_success(self):
        async def handler(item: int) -> int:
            return item * 2

        result = await process_batch([1, 2, 3], handler, max_concurrent=2)
        assert result.status == BatchStatus.COMPLETED
        assert result.success_count == 3
        values = sorted([r.result for r in result.results])
        assert values == [2, 4, 6]

    @pytest.mark.asyncio
    async def test_process_batch_empty(self):
        async def handler(item):
            return item

        result = await process_batch([], handler)
        # Empty batch: finalize sees error_count==total_items==0 so marks FAILED
        # but the processor explicitly sets COMPLETED before finalize for empty input
        assert result.total_items == 0
        assert result.success_count == 0
        assert result.error_count == 0

    @pytest.mark.asyncio
    async def test_process_batch_with_error(self):
        async def handler(item: int) -> int:
            if item == 2:
                raise ValueError("bad value")
            return item

        result = await process_batch([1, 2, 3], handler, max_concurrent=2)
        assert result.error_count == 1
        assert result.success_count == 2
        assert result.status == BatchStatus.PARTIAL

    @pytest.mark.asyncio
    async def test_process_batch_skips_none_data(self):
        processor = BatchProcessor(max_concurrent=2)
        requests = [BatchRequest(id="1", data=None)]

        async def handler(item):
            return item

        result = await processor.process(requests, handler)
        assert result.skipped_count == 1

    @pytest.mark.asyncio
    async def test_process_batch_respects_priority(self):
        order = []

        async def handler(item: str) -> str:
            order.append(item)
            return item

        processor = BatchProcessor(max_concurrent=1)
        requests = [
            BatchRequest(id="low", data="low", priority=1),
            BatchRequest(id="high", data="high", priority=10),
        ]
        await processor.process(requests, handler)
        # High priority should be processed first
        assert order[0] == "high"

    @pytest.mark.asyncio
    async def test_process_batch_timeout(self):
        async def handler(item):
            await asyncio.sleep(10)
            return item

        result = await process_batch([1], handler, max_concurrent=1, timeout_seconds=0.01)
        assert result.results[0].status == BatchItemStatus.TIMEOUT
        assert "انتهت" in result.results[0].error_ar


# =============================================================================
# 7. Module-Level Tests
# =============================================================================


@pytest.mark.unit
class TestModuleInit:
    """Tests for the shared.terrain module itself."""

    def test_module_version(self):
        import shared.terrain as terrain_mod

        assert terrain_mod.__version__ == "16.0.0"

    def test_module_exports(self):
        import shared.terrain as terrain_mod

        assert hasattr(terrain_mod, "validators")
        assert hasattr(terrain_mod, "geojson_utils")
        assert hasattr(terrain_mod, "cache")
        assert hasattr(terrain_mod, "responses")
        assert hasattr(terrain_mod, "batch")

    def test_constants_present(self):
        assert ELEVATION_MIN_M < 0
        assert ELEVATION_MAX_M > 0
        assert AGRICULTURAL_ELEVATION_MIN_M >= 0
        assert MAX_GRADE_PERCENT > 0
        assert MIN_GRADE_PERCENT < 0
        assert EARTH_RADIUS_M > 6_000_000
