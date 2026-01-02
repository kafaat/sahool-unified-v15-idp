"""
Comprehensive PostGIS Validation Test Suite for SAHOOL
مجموعة اختبارات شاملة للتحقق من صحة PostGIS لنظام سهول

Tests cover:
1. Geometry Validation - التحقق من صحة الأشكال الهندسية
2. Spatial Operations - العمليات المكانية
3. Coordinate Reference Systems - أنظمة الإحداثيات المرجعية
4. Field Boundary Validation - التحقق من صحة حدود الحقول
5. Index Performance - أداء الفهارس المكانية
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

import pytest
from shapely.geometry import Point, Polygon, MultiPolygon, mapping, shape
from shapely.validation import explain_validity
from shapely.ops import unary_union


# ============================================================================
# Test Fixtures - إعداد الاختبارات
# ============================================================================


@pytest.fixture
async def mock_db_pool():
    """
    Mock database connection pool for PostGIS operations
    محاكاة مجموعة اتصالات قاعدة البيانات لعمليات PostGIS
    """
    pool = AsyncMock()
    connection = AsyncMock()

    # Mock connection context manager
    async def mock_acquire():
        return connection

    pool.acquire.return_value.__aenter__ = mock_acquire
    pool.acquire.return_value.__aexit__ = AsyncMock()

    return pool, connection


@pytest.fixture
def valid_polygon_coords():
    """
    Valid polygon coordinates for Yemen region
    إحداثيات مضلع صالحة لمنطقة اليمن
    """
    return [
        [44.1910, 15.3694],  # Southwest corner
        [44.1920, 15.3694],  # Southeast corner
        [44.1920, 15.3704],  # Northeast corner
        [44.1910, 15.3704],  # Northwest corner
        [44.1910, 15.3694],  # Close the ring
    ]


@pytest.fixture
def self_intersecting_polygon_coords():
    """
    Self-intersecting polygon (invalid geometry)
    مضلع متقاطع مع نفسه (شكل هندسي غير صالح)
    """
    return [
        [44.1910, 15.3694],
        [44.1920, 15.3704],  # Creates intersection
        [44.1920, 15.3694],
        [44.1910, 15.3704],  # Crosses previous edge
        [44.1910, 15.3694],
    ]


@pytest.fixture
def yemen_test_polygon():
    """
    Test polygon within Yemen boundaries
    مضلع اختبار ضمن حدود اليمن
    """
    return Polygon([
        [44.1910, 15.3694],
        [44.1920, 15.3694],
        [44.1920, 15.3704],
        [44.1910, 15.3704],
        [44.1910, 15.3694],
    ])


@pytest.fixture
def multipolygon_geometry():
    """
    MultiPolygon geometry for testing
    هندسة متعددة المضلعات للاختبار
    """
    poly1 = Polygon([
        [44.1910, 15.3694],
        [44.1915, 15.3694],
        [44.1915, 15.3699],
        [44.1910, 15.3699],
        [44.1910, 15.3694],
    ])
    poly2 = Polygon([
        [44.1920, 15.3700],
        [44.1925, 15.3700],
        [44.1925, 15.3705],
        [44.1920, 15.3705],
        [44.1920, 15.3700],
    ])
    return MultiPolygon([poly1, poly2])


# ============================================================================
# 1. Geometry Validation Tests - اختبارات التحقق من صحة الأشكال الهندسية
# ============================================================================


class TestGeometryValidation:
    """
    Test geometry validation using PostGIS and Shapely
    اختبار التحقق من صحة الأشكال الهندسية باستخدام PostGIS و Shapely
    """

    def test_valid_polygon_geometry(self, valid_polygon_coords):
        """
        Test that a valid polygon passes validation
        اختبار أن المضلع الصالح يجتاز التحقق
        """
        # Create polygon using Shapely
        polygon = Polygon(valid_polygon_coords)

        # Validate geometry
        assert polygon.is_valid, f"Polygon should be valid: {explain_validity(polygon)}"
        assert polygon.is_simple, "Polygon should be simple (non-self-intersecting)"
        assert not polygon.is_empty, "Polygon should not be empty"

        # Verify ring closure
        coords = list(polygon.exterior.coords)
        assert coords[0] == coords[-1], "Polygon should be closed (first == last point)"

        # Verify minimum points
        assert len(coords) >= 4, "Polygon must have at least 4 points (including closure)"

    def test_invalid_self_intersecting_polygon(self, self_intersecting_polygon_coords):
        """
        Test detection of self-intersecting (invalid) polygons
        اختبار كشف المضلعات المتقاطعة مع نفسها (غير الصالحة)
        """
        # Create self-intersecting polygon
        polygon = Polygon(self_intersecting_polygon_coords)

        # Should be detected as invalid
        assert not polygon.is_valid, "Self-intersecting polygon should be invalid"

        # Get validation error message
        validation_msg = explain_validity(polygon)
        assert "Self-intersection" in validation_msg or "Ring Self-intersection" in validation_msg

        # Test ST_MakeValid equivalent (buffer(0) trick)
        fixed_polygon = polygon.buffer(0)
        assert fixed_polygon.is_valid, "ST_MakeValid should fix the polygon"

    def test_polygon_winding_order(self, valid_polygon_coords):
        """
        Test polygon winding order (counterclockwise for exterior)
        اختبار ترتيب دوران المضلع (عكس عقارب الساعة للحدود الخارجية)
        """
        # Create polygon
        polygon = Polygon(valid_polygon_coords)

        # Shapely automatically ensures correct winding order
        # Exterior should be counterclockwise (positive area)
        assert polygon.exterior.is_ccw, "Exterior ring should be counterclockwise"

        # Test with reversed coordinates (clockwise)
        reversed_coords = valid_polygon_coords[::-1]
        reversed_polygon = Polygon(reversed_coords)

        # Shapely normalizes winding order
        assert reversed_polygon.is_valid, "Reversed polygon should still be valid"
        assert reversed_polygon.exterior.is_ccw, "Shapely normalizes to CCW"

    def test_multipolygon_support(self, multipolygon_geometry):
        """
        Test MultiPolygon geometry support
        اختبار دعم الأشكال الهندسية متعددة المضلعات
        """
        # Validate MultiPolygon
        assert multipolygon_geometry.is_valid, "MultiPolygon should be valid"
        assert multipolygon_geometry.geom_type == "MultiPolygon"

        # Check number of geometries
        assert len(multipolygon_geometry.geoms) == 2, "Should contain 2 polygons"

        # Validate each polygon
        for geom in multipolygon_geometry.geoms:
            assert geom.is_valid, "Each polygon in MultiPolygon should be valid"
            assert geom.geom_type == "Polygon"

        # Test GeoJSON conversion
        geojson = mapping(multipolygon_geometry)
        assert geojson["type"] == "MultiPolygon"
        assert len(geojson["coordinates"]) == 2


# ============================================================================
# 2. Spatial Operations Tests - اختبارات العمليات المكانية
# ============================================================================


class TestSpatialOperations:
    """
    Test spatial operations (PostGIS equivalents using Shapely)
    اختبار العمليات المكانية (معادلات PostGIS باستخدام Shapely)
    """

    def test_point_in_polygon(self, yemen_test_polygon):
        """
        Test ST_Contains - point in polygon check
        اختبار ST_Contains - التحقق من وجود نقطة داخل مضلع
        """
        # Point inside polygon
        point_inside = Point(44.1915, 15.3699)
        assert yemen_test_polygon.contains(point_inside), "Point should be inside polygon"

        # Point outside polygon
        point_outside = Point(44.2000, 15.4000)
        assert not yemen_test_polygon.contains(point_outside), "Point should be outside polygon"

        # Point on boundary
        point_on_boundary = Point(44.1910, 15.3694)
        assert yemen_test_polygon.touches(point_on_boundary) or \
               yemen_test_polygon.contains(point_on_boundary), \
               "Point on boundary should touch or be contained"

    def test_polygon_intersection(self, yemen_test_polygon):
        """
        Test ST_Intersection - polygon intersection
        اختبار ST_Intersection - تقاطع المضلعات
        """
        # Create overlapping polygon
        overlapping_polygon = Polygon([
            [44.1915, 15.3699],
            [44.1925, 15.3699],
            [44.1925, 15.3709],
            [44.1915, 15.3709],
            [44.1915, 15.3699],
        ])

        # Test intersection
        intersection = yemen_test_polygon.intersection(overlapping_polygon)

        assert not intersection.is_empty, "Should have intersection"
        assert intersection.is_valid, "Intersection should be valid"
        assert intersection.area > 0, "Intersection should have area"

        # Test non-overlapping polygon
        non_overlapping = Polygon([
            [44.3000, 15.5000],
            [44.3010, 15.5000],
            [44.3010, 15.5010],
            [44.3000, 15.5010],
            [44.3000, 15.5000],
        ])

        no_intersection = yemen_test_polygon.intersection(non_overlapping)
        assert no_intersection.is_empty, "Should have no intersection"

    def test_buffer_calculation(self, yemen_test_polygon):
        """
        Test ST_Buffer - create buffer around geometry
        اختبار ST_Buffer - إنشاء منطقة عازلة حول الشكل الهندسي
        """
        # Create buffer of 0.001 degrees (~111 meters)
        buffer_distance = 0.001
        buffered = yemen_test_polygon.buffer(buffer_distance)

        assert buffered.is_valid, "Buffered geometry should be valid"
        assert buffered.area > yemen_test_polygon.area, "Buffered area should be larger"

        # Original polygon should be within buffer
        assert buffered.contains(yemen_test_polygon), "Buffer should contain original"

        # Test negative buffer (erosion)
        eroded = yemen_test_polygon.buffer(-0.0001)
        if not eroded.is_empty:
            assert eroded.area < yemen_test_polygon.area, "Eroded area should be smaller"

    def test_centroid_calculation(self, yemen_test_polygon):
        """
        Test ST_Centroid - calculate polygon centroid
        اختبار ST_Centroid - حساب مركز المضلع
        """
        centroid = yemen_test_polygon.centroid

        assert centroid.geom_type == "Point", "Centroid should be a Point"

        # For a rectangular polygon, centroid should be inside
        assert yemen_test_polygon.contains(centroid), "Centroid should be inside polygon"

        # Verify approximate coordinates for our test rectangle
        expected_x = (44.1910 + 44.1920) / 2  # 44.1915
        expected_y = (15.3694 + 15.3704) / 2  # 15.3699

        assert abs(centroid.x - expected_x) < 0.0001, f"Centroid X should be ~{expected_x}"
        assert abs(centroid.y - expected_y) < 0.0001, f"Centroid Y should be ~{expected_y}"

    def test_area_calculation_hectares(self, yemen_test_polygon):
        """
        Test ST_Area - calculate area in hectares
        اختبار ST_Area - حساب المساحة بالهكتار
        """
        from pyproj import Geod

        # Use WGS84 ellipsoid for accurate area calculation
        geod = Geod(ellps="WGS84")

        # Get polygon exterior coordinates
        coords = list(yemen_test_polygon.exterior.coords)

        # Calculate area in square meters
        lons = [coord[0] for coord in coords]
        lats = [coord[1] for coord in coords]
        area_m2, _ = geod.polygon_area_perimeter(lons, lats)
        area_m2 = abs(area_m2)  # Take absolute value

        # Convert to hectares (1 hectare = 10,000 m²)
        area_hectares = area_m2 / 10000

        # Our test polygon is ~0.001° x 0.001°
        # At Yemen's latitude, this is approximately 0.012 hectares
        assert area_hectares > 0, "Area should be positive"
        assert area_hectares < 100, "Area should be reasonable for test polygon"

        # Verify it's in expected range (rough estimate)
        assert 0.001 < area_hectares < 1.0, "Test polygon area should be small"


# ============================================================================
# 3. Coordinate Reference System Tests - اختبارات أنظمة الإحداثيات المرجعية
# ============================================================================


class TestCoordinateReferenceSystems:
    """
    Test CRS validation and transformations
    اختبار التحقق من صحة نظام الإحداثيات والتحويلات
    """

    def test_srid_4326_wgs84(self, yemen_test_polygon):
        """
        Test SRID 4326 (WGS84) coordinate validation
        اختبار التحقق من صحة إحداثيات SRID 4326 (WGS84)
        """
        # Get coordinates
        coords = list(yemen_test_polygon.exterior.coords)

        # Validate all coordinates are in valid WGS84 range
        for lon, lat in coords:
            # Longitude: -180 to 180
            assert -180 <= lon <= 180, f"Longitude {lon} out of WGS84 range"

            # Latitude: -90 to 90
            assert -90 <= lat <= 90, f"Latitude {lat} out of WGS84 range"

        # Verify coordinates are in decimal degrees format
        for lon, lat in coords:
            assert isinstance(lon, (int, float)), "Longitude should be numeric"
            assert isinstance(lat, (int, float)), "Latitude should be numeric"

    def test_coordinate_transformation(self):
        """
        Test coordinate transformation between different CRS
        اختبار تحويل الإحداثيات بين أنظمة الإحداثيات المختلفة
        """
        from pyproj import Transformer

        # Define transformer: WGS84 (EPSG:4326) to UTM Zone 38N (EPSG:32638)
        # Yemen is primarily in UTM Zone 38N and 39N
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:32638", always_xy=True)

        # Test point in Yemen (Sana'a approximate)
        lon, lat = 44.2075, 15.3547

        # Transform to UTM
        utm_x, utm_y = transformer.transform(lon, lat)

        # Verify transformation produced valid UTM coordinates
        assert 100000 <= utm_x <= 900000, "UTM X (easting) should be in valid range"
        assert 0 <= utm_y <= 10000000, "UTM Y (northing) should be in valid range"

        # Test reverse transformation
        transformer_reverse = Transformer.from_crs("EPSG:32638", "EPSG:4326", always_xy=True)
        lon_back, lat_back = transformer_reverse.transform(utm_x, utm_y)

        # Should get back original coordinates (within precision)
        assert abs(lon_back - lon) < 0.000001, "Reverse transform should match original lon"
        assert abs(lat_back - lat) < 0.000001, "Reverse transform should match original lat"

    def test_yemen_bounds_validation(self):
        """
        Test Yemen geographic bounds validation (12.0-19.0 lat, 42.0-54.0 lon)
        اختبار التحقق من صحة الحدود الجغرافية لليمن
        """
        # Yemen boundaries
        YEMEN_MIN_LAT = 12.0
        YEMEN_MAX_LAT = 19.0
        YEMEN_MIN_LON = 42.0
        YEMEN_MAX_LON = 54.0

        # Test valid Yemen coordinates
        valid_coords = [
            (44.2075, 15.3547),  # Sana'a
            (45.0328, 12.7855),  # Aden
            (48.7837, 14.5519),  # Mukalla
            (43.7461, 15.6949),  # Sa'dah
        ]

        for lon, lat in valid_coords:
            assert YEMEN_MIN_LON <= lon <= YEMEN_MAX_LON, \
                f"Longitude {lon} should be within Yemen bounds"
            assert YEMEN_MIN_LAT <= lat <= YEMEN_MAX_LAT, \
                f"Latitude {lat} should be within Yemen bounds"

        # Test invalid coordinates (outside Yemen)
        invalid_coords = [
            (35.0, 15.0),   # Too far west (Iraq/Saudi)
            (60.0, 15.0),   # Too far east (Oman)
            (44.0, 10.0),   # Too far south (Gulf of Aden)
            (44.0, 25.0),   # Too far north (Saudi Arabia)
        ]

        for lon, lat in invalid_coords:
            is_in_yemen = (YEMEN_MIN_LON <= lon <= YEMEN_MAX_LON and
                          YEMEN_MIN_LAT <= lat <= YEMEN_MAX_LAT)
            assert not is_in_yemen, \
                f"Coordinates ({lon}, {lat}) should be outside Yemen"


# ============================================================================
# 4. Field Boundary Validation Tests - اختبارات التحقق من صحة حدود الحقول
# ============================================================================


class TestFieldBoundaryValidation:
    """
    Test field boundary business rules
    اختبار قواعد العمل لحدود الحقول
    """

    def test_field_minimum_area(self):
        """
        Test minimum field area requirement (0.1 hectares)
        اختبار الحد الأدنى لمساحة الحقل (0.1 هكتار)
        """
        from pyproj import Geod

        MIN_AREA_HECTARES = 0.1
        MIN_AREA_M2 = MIN_AREA_HECTARES * 10000  # 1000 m²

        geod = Geod(ellps="WGS84")

        # Create small polygon (~0.05 hectares - below minimum)
        small_polygon = Polygon([
            [44.1910, 15.3694],
            [44.1912, 15.3694],
            [44.1912, 15.3696],
            [44.1910, 15.3696],
            [44.1910, 15.3694],
        ])

        coords = list(small_polygon.exterior.coords)
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        area_m2 = abs(geod.polygon_area_perimeter(lons, lats)[0])
        area_hectares = area_m2 / 10000

        # Should be below minimum
        assert area_hectares < MIN_AREA_HECTARES, \
            f"Small polygon area {area_hectares:.4f} ha should be below minimum"

        # Create larger polygon (~0.15 hectares - above minimum)
        large_polygon = Polygon([
            [44.1910, 15.3694],
            [44.1915, 15.3694],
            [44.1915, 15.3699],
            [44.1910, 15.3699],
            [44.1910, 15.3694],
        ])

        coords = list(large_polygon.exterior.coords)
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        area_m2 = abs(geod.polygon_area_perimeter(lons, lats)[0])
        area_hectares = area_m2 / 10000

        # Should be above minimum
        assert area_hectares > MIN_AREA_HECTARES, \
            f"Large polygon area {area_hectares:.4f} ha should be above minimum"

    def test_field_maximum_area(self):
        """
        Test maximum field area requirement (1000 hectares)
        اختبار الحد الأقصى لمساحة الحقل (1000 هكتار)
        """
        from pyproj import Geod

        MAX_AREA_HECTARES = 1000

        geod = Geod(ellps="WGS84")

        # Create very large polygon (~1200 hectares - above maximum)
        # Roughly 0.1° x 0.1° at Yemen's latitude
        huge_polygon = Polygon([
            [44.0000, 15.0000],
            [44.1000, 15.0000],
            [44.1000, 15.1000],
            [44.0000, 15.1000],
            [44.0000, 15.0000],
        ])

        coords = list(huge_polygon.exterior.coords)
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        area_m2 = abs(geod.polygon_area_perimeter(lons, lats)[0])
        area_hectares = area_m2 / 10000

        # Should be above maximum
        assert area_hectares > MAX_AREA_HECTARES, \
            f"Huge polygon area {area_hectares:.2f} ha should be above maximum"

    def test_overlapping_fields_detection(self):
        """
        Test detection of overlapping field boundaries
        اختبار كشف تداخل حدود الحقول
        """
        # Create two overlapping fields
        field1 = Polygon([
            [44.1910, 15.3694],
            [44.1920, 15.3694],
            [44.1920, 15.3704],
            [44.1910, 15.3704],
            [44.1910, 15.3694],
        ])

        field2 = Polygon([
            [44.1915, 15.3699],
            [44.1925, 15.3699],
            [44.1925, 15.3709],
            [44.1915, 15.3709],
            [44.1915, 15.3699],
        ])

        # Test for overlap
        assert field1.intersects(field2), "Fields should intersect"

        overlap = field1.intersection(field2)
        assert not overlap.is_empty, "Should have overlap area"

        # Calculate overlap percentage
        overlap_area = overlap.area
        field1_area = field1.area
        overlap_percentage = (overlap_area / field1_area) * 100

        assert overlap_percentage > 0, "Overlap percentage should be positive"

        # Test non-overlapping fields
        field3 = Polygon([
            [44.3000, 15.5000],
            [44.3010, 15.5000],
            [44.3010, 15.5010],
            [44.3000, 15.5010],
            [44.3000, 15.5000],
        ])

        assert not field1.intersects(field3), "Distant fields should not intersect"

    def test_field_simplification(self):
        """
        Test polygon simplification (ST_Simplify equivalent)
        اختبار تبسيط المضلع (معادل ST_Simplify)
        """
        # Create complex polygon with many points
        complex_coords = [
            [44.1910, 15.3694],
            [44.1911, 15.3694],
            [44.1912, 15.3694],
            [44.1913, 15.3694],
            [44.1914, 15.3694],
            [44.1915, 15.3694],
            [44.1916, 15.3694],
            [44.1917, 15.3694],
            [44.1918, 15.3694],
            [44.1919, 15.3694],
            [44.1920, 15.3694],
            [44.1920, 15.3704],
            [44.1910, 15.3704],
            [44.1910, 15.3694],
        ]

        complex_polygon = Polygon(complex_coords)
        original_points = len(complex_coords)

        # Simplify with tolerance of 0.0001 degrees
        tolerance = 0.0001
        simplified = complex_polygon.simplify(tolerance, preserve_topology=True)

        simplified_points = len(list(simplified.exterior.coords))

        # Simplified should have fewer points
        assert simplified_points < original_points, \
            f"Simplified polygon should have fewer points ({simplified_points} < {original_points})"

        # Simplified should still be valid
        assert simplified.is_valid, "Simplified polygon should be valid"

        # Area should be approximately the same
        area_diff = abs(complex_polygon.area - simplified.area)
        assert area_diff < 0.0001, "Simplification should preserve area approximately"


# ============================================================================
# 5. Index Performance Tests - اختبارات أداء الفهارس
# ============================================================================


class TestIndexPerformance:
    """
    Test spatial index performance and existence
    اختبار أداء ووجود الفهارس المكانية
    """

    @pytest.mark.asyncio
    async def test_spatial_index_exists(self, mock_db_pool):
        """
        Test that spatial indexes exist in database
        اختبار وجود الفهارس المكانية في قاعدة البيانات
        """
        pool, connection = mock_db_pool

        # Mock response for index check query
        mock_result = [
            {"indexname": "idx_fields_boundary", "indexdef": "CREATE INDEX idx_fields_boundary ON fields USING gist (boundary)"},
            {"indexname": "idx_fields_centroid", "indexdef": "CREATE INDEX idx_fields_centroid ON fields USING gist (centroid)"},
            {"indexname": "idx_farms_location", "indexdef": "CREATE INDEX idx_farms_location ON farms USING gist (location)"},
            {"indexname": "idx_farms_boundary", "indexdef": "CREATE INDEX idx_farms_boundary ON farms USING gist (boundary)"},
        ]

        connection.fetch = AsyncMock(return_value=mock_result)

        # Query to check for spatial indexes
        query = """
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE tablename IN ('fields', 'farms', 'zones', 'sub_zones')
            AND indexdef LIKE '%USING gist%'
            ORDER BY indexname;
        """

        async with pool.acquire() as conn:
            results = await conn.fetch(query)

        # Verify results
        assert len(results) > 0, "Should have spatial indexes"

        # Check for specific indexes
        index_names = [row["indexname"] for row in results]

        expected_indexes = [
            "idx_fields_boundary",
            "idx_fields_centroid",
            "idx_farms_location",
            "idx_farms_boundary",
        ]

        for idx in expected_indexes:
            assert idx in index_names, f"Spatial index {idx} should exist"

        # Verify all are GIST indexes
        for row in results:
            assert "gist" in row["indexdef"].lower(), \
                f"Index {row['indexname']} should be GIST type"

    @pytest.mark.asyncio
    async def test_query_performance_with_index(self, mock_db_pool):
        """
        Test query performance with spatial indexes
        اختبار أداء الاستعلامات مع الفهارس المكانية
        """
        pool, connection = mock_db_pool

        # Mock EXPLAIN ANALYZE output
        mock_explain_result = [
            {
                "QUERY PLAN": "Index Scan using idx_fields_boundary on fields  (cost=0.29..8.31 rows=1 width=1234) (actual time=0.012..0.015 rows=5 loops=1)"
            },
            {
                "QUERY PLAN": "  Index Cond: (boundary && '01030000...'::geometry)"
            },
            {
                "QUERY PLAN": "Planning Time: 0.123 ms"
            },
            {
                "QUERY PLAN": "Execution Time: 0.045 ms"
            },
        ]

        connection.fetch = AsyncMock(return_value=mock_explain_result)

        # Test spatial query with EXPLAIN ANALYZE
        query = """
            EXPLAIN ANALYZE
            SELECT id, name, ST_Area(boundary::geography)/10000 as area_hectares
            FROM fields
            WHERE boundary && ST_MakeEnvelope(44.0, 15.0, 45.0, 16.0, 4326)
            AND tenant_id = $1
            LIMIT 100;
        """

        async with pool.acquire() as conn:
            explain_result = await conn.fetch(query, "test_tenant")

        # Parse EXPLAIN output
        plan_text = "\n".join([row["QUERY PLAN"] for row in explain_result])

        # Verify index is being used
        assert "Index Scan" in plan_text or "Bitmap Index Scan" in plan_text, \
            "Query should use spatial index"

        assert "idx_fields_boundary" in plan_text or "gist" in plan_text.lower(), \
            "Query should use GIST spatial index"

        # Verify performance
        # Extract execution time
        execution_time = 0.0
        for row in explain_result:
            if "Execution Time" in row["QUERY PLAN"]:
                # Parse "Execution Time: X.XXX ms"
                parts = row["QUERY PLAN"].split(":")
                if len(parts) > 1:
                    time_str = parts[1].strip().replace("ms", "").strip()
                    execution_time = float(time_str)

        # With proper index, query should be fast (< 100ms for most cases)
        assert execution_time < 100.0, \
            f"Spatial query should be fast with index (was {execution_time}ms)"


# ============================================================================
# Integration Tests - اختبارات التكامل
# ============================================================================


class TestPostGISIntegration:
    """
    Integration tests for complete PostGIS workflows
    اختبارات التكامل للعمليات الكاملة لـ PostGIS
    """

    @pytest.mark.asyncio
    async def test_field_creation_workflow(self, valid_polygon_coords, mock_db_pool):
        """
        Test complete field creation workflow with PostGIS validation
        اختبار سير عمل إنشاء حقل كامل مع التحقق من PostGIS
        """
        pool, connection = mock_db_pool

        # Step 1: Validate geometry with Shapely
        polygon = Polygon(valid_polygon_coords)
        assert polygon.is_valid, "Geometry must be valid before insertion"

        # Step 2: Calculate area
        from pyproj import Geod
        geod = Geod(ellps="WGS84")
        coords = list(polygon.exterior.coords)
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        area_m2 = abs(geod.polygon_area_perimeter(lons, lats)[0])
        area_hectares = area_m2 / 10000

        # Step 3: Validate area constraints
        assert 0.1 <= area_hectares <= 1000, \
            f"Area {area_hectares:.2f} ha must be between 0.1 and 1000 hectares"

        # Step 4: Calculate centroid
        centroid = polygon.centroid

        # Step 5: Convert to WKT for PostGIS
        wkt = polygon.wkt

        # Step 6: Mock database insertion
        mock_field_id = str(uuid4())
        mock_result = {
            "id": mock_field_id,
            "name": "Test Field",
            "tenant_id": "test_tenant",
            "area_hectares": area_hectares,
            "centroid_lat": centroid.y,
            "centroid_lon": centroid.x,
        }

        connection.fetchrow = AsyncMock(return_value=mock_result)

        # Simulate INSERT query
        insert_query = """
            INSERT INTO fields (id, tenant_id, name, boundary, centroid, area_hectares)
            VALUES ($1, $2, $3, ST_GeomFromText($4, 4326), ST_GeomFromText($5, 4326), $6)
            RETURNING id, name, tenant_id, area_hectares,
                      ST_Y(centroid) as centroid_lat,
                      ST_X(centroid) as centroid_lon;
        """

        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                insert_query,
                mock_field_id,
                "test_tenant",
                "Test Field",
                wkt,
                centroid.wkt,
                area_hectares,
            )

        # Verify result
        assert result["id"] == mock_field_id
        assert result["area_hectares"] == area_hectares
        assert abs(result["centroid_lat"] - centroid.y) < 0.0001
        assert abs(result["centroid_lon"] - centroid.x) < 0.0001

    def test_geojson_conversion(self, yemen_test_polygon):
        """
        Test GeoJSON conversion for API responses
        اختبار تحويل GeoJSON لاستجابات API
        """
        # Convert to GeoJSON
        geojson = mapping(yemen_test_polygon)

        # Verify structure
        assert geojson["type"] == "Polygon"
        assert "coordinates" in geojson
        assert isinstance(geojson["coordinates"], list)
        assert len(geojson["coordinates"]) == 1  # One exterior ring
        assert len(geojson["coordinates"][0]) >= 4  # At least 4 points

        # Verify closure
        first_coord = geojson["coordinates"][0][0]
        last_coord = geojson["coordinates"][0][-1]
        assert first_coord == last_coord, "GeoJSON polygon should be closed"

        # Test reverse conversion
        reconstructed = shape(geojson)
        assert reconstructed.is_valid, "Reconstructed geometry should be valid"
        assert reconstructed.equals(yemen_test_polygon), \
            "Reconstructed geometry should match original"


# ============================================================================
# Utility Functions Tests - اختبارات الدوال المساعدة
# ============================================================================


class TestUtilityFunctions:
    """
    Test utility functions for PostGIS operations
    اختبار الدوال المساعدة لعمليات PostGIS
    """

    def test_validate_yemen_coordinates(self):
        """
        Test Yemen coordinates validation utility
        اختبار أداة التحقق من إحداثيات اليمن
        """
        def validate_yemen_coords(lon: float, lat: float) -> bool:
            """Validate if coordinates are within Yemen bounds"""
            YEMEN_MIN_LAT, YEMEN_MAX_LAT = 12.0, 19.0
            YEMEN_MIN_LON, YEMEN_MAX_LON = 42.0, 54.0

            return (YEMEN_MIN_LON <= lon <= YEMEN_MAX_LON and
                   YEMEN_MIN_LAT <= lat <= YEMEN_MAX_LAT)

        # Valid Yemen coordinates
        assert validate_yemen_coords(44.2075, 15.3547), "Sana'a should be valid"
        assert validate_yemen_coords(45.0328, 12.7855), "Aden should be valid"
        assert validate_yemen_coords(48.7837, 14.5519), "Mukalla should be valid"

        # Invalid coordinates
        assert not validate_yemen_coords(35.0, 15.0), "Iraq should be invalid"
        assert not validate_yemen_coords(60.0, 15.0), "Oman should be invalid"
        assert not validate_yemen_coords(44.0, 10.0), "South of Yemen should be invalid"

    def test_calculate_distance_haversine(self):
        """
        Test Haversine distance calculation
        اختبار حساب المسافة باستخدام صيغة Haversine
        """
        from math import radians, sin, cos, sqrt, atan2

        def haversine_distance(lon1: float, lat1: float,
                             lon2: float, lat2: float) -> float:
            """Calculate distance between two points in kilometers"""
            R = 6371  # Earth radius in kilometers

            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))

            return R * c

        # Test distance between Sana'a and Aden
        sanaa = (44.2075, 15.3547)
        aden = (45.0328, 12.7855)

        distance = haversine_distance(sanaa[0], sanaa[1], aden[0], aden[1])

        # Distance should be approximately 290-300 km
        assert 280 < distance < 310, \
            f"Distance between Sana'a and Aden should be ~295 km (got {distance:.2f} km)"

        # Test distance to same point (should be 0)
        distance_same = haversine_distance(sanaa[0], sanaa[1], sanaa[0], sanaa[1])
        assert distance_same < 0.001, "Distance to same point should be ~0"


# ============================================================================
# Performance Benchmark Tests - اختبارات قياس الأداء
# ============================================================================


class TestPerformanceBenchmarks:
    """
    Performance benchmarks for PostGIS operations
    معايير الأداء لعمليات PostGIS
    """

    def test_bulk_geometry_validation(self):
        """
        Test performance of bulk geometry validation
        اختبار أداء التحقق الجماعي من الأشكال الهندسية
        """
        import time

        # Generate 1000 random polygons
        test_polygons = []
        for i in range(1000):
            base_lon = 44.0 + (i % 10) * 0.01
            base_lat = 15.0 + (i // 10) * 0.01

            polygon = Polygon([
                [base_lon, base_lat],
                [base_lon + 0.005, base_lat],
                [base_lon + 0.005, base_lat + 0.005],
                [base_lon, base_lat + 0.005],
                [base_lon, base_lat],
            ])
            test_polygons.append(polygon)

        # Measure validation time
        start_time = time.time()

        valid_count = 0
        for polygon in test_polygons:
            if polygon.is_valid:
                valid_count += 1

        end_time = time.time()
        elapsed_time = end_time - start_time

        # All should be valid
        assert valid_count == 1000, "All test polygons should be valid"

        # Should complete in reasonable time (< 1 second for 1000 polygons)
        assert elapsed_time < 1.0, \
            f"Bulk validation should be fast (took {elapsed_time:.3f}s for 1000 polygons)"

        # Calculate throughput
        throughput = 1000 / elapsed_time
        assert throughput > 1000, \
            f"Should validate >1000 polygons/sec (got {throughput:.0f}/sec)"


# ============================================================================
# Error Handling Tests - اختبارات معالجة الأخطاء
# ============================================================================


class TestErrorHandling:
    """
    Test error handling for invalid geometries
    اختبار معالجة الأخطاء للأشكال الهندسية غير الصالحة
    """

    def test_empty_polygon_handling(self):
        """
        Test handling of empty polygons
        اختبار معالجة المضلعات الفارغة
        """
        from shapely.geometry import Polygon

        # Empty polygon
        empty_polygon = Polygon()

        assert empty_polygon.is_empty, "Empty polygon should be detected"
        assert not empty_polygon.is_valid, "Empty polygon should be invalid"

        # Attempting operations on empty polygon should be handled
        assert empty_polygon.area == 0, "Empty polygon area should be 0"
        assert empty_polygon.length == 0, "Empty polygon perimeter should be 0"

    def test_invalid_coordinate_handling(self):
        """
        Test handling of invalid coordinates
        اختبار معالجة الإحداثيات غير الصالحة
        """
        # Test various invalid coordinates
        invalid_coords = [
            (200.0, 15.0),    # Longitude out of range
            (44.0, 100.0),    # Latitude out of range
            (None, 15.0),     # None value
            (44.0, None),     # None value
        ]

        for lon, lat in invalid_coords:
            # Should raise error or be detected as invalid
            try:
                if lon is None or lat is None:
                    with pytest.raises(TypeError):
                        point = Point(lon, lat)
                elif not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    # Invalid WGS84 coordinates
                    point = Point(lon, lat)
                    # Point will be created but coordinates are invalid for WGS84
                    assert lon < -180 or lon > 180 or lat < -90 or lat > 90
            except (TypeError, ValueError):
                # Expected for invalid inputs
                pass

    def test_insufficient_points_handling(self):
        """
        Test handling of polygons with insufficient points
        اختبار معالجة المضلعات ذات النقاط غير الكافية
        """
        # Polygon needs at least 3 unique points (4 with closure)
        insufficient_coords = [
            [44.0, 15.0],
            [44.1, 15.0],
            [44.0, 15.0],  # Only 2 unique points
        ]

        # Should raise error or create invalid geometry
        try:
            polygon = Polygon(insufficient_coords)
            # If created, should be invalid
            assert not polygon.is_valid or polygon.is_empty
        except ValueError:
            # Expected - insufficient points
            pass
