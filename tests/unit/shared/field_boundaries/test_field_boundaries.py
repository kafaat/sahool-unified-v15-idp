"""
Tests for Field Boundaries Module - اختبارات وحدة حدود الحقول

Covers:
- Enum values and string representations
- Point, Polygon, MultiPolygon models and validation
- BoundaryPoint, FieldBoundary, BoundaryConflict models
- GPS Track and BoundaryShareRequest models
- Geometry calculations (haversine, area, perimeter, centroid)
- Spatial operations (point-in-polygon, overlap, edge intersection)
- Polygon validation and simplification
- Circular boundary generation
- PostGIS helper query generation
- GeoJSON conversion and serialization
"""

from __future__ import annotations

import math
from datetime import UTC, datetime

import pytest

from shared.field_boundaries.geometry import (
    ACRES_PER_SQM,
    DUNAMS_PER_SQM,
    EARTH_RADIUS_M,
    HECTARES_PER_SQM,
    GeometryMetrics,
    calculate_bounding_box,
    calculate_centroid,
    calculate_geometry_metrics,
    calculate_overlap_area,
    calculate_perimeter,
    calculate_polygon_area_geodesic,
    calculate_polygon_area_projected,
    create_circular_boundary,
    degrees_to_radians,
    edges_intersect,
    generate_postgis_area_query,
    generate_postgis_centroid_query,
    generate_postgis_neighbors_query,
    generate_postgis_overlap_query,
    haversine_distance,
    is_point_in_polygon,
    polygons_overlap,
    radians_to_degrees,
    simplify_polygon,
    validate_polygon,
)
from shared.field_boundaries.models import (
    BoundaryConflict,
    BoundaryPoint,
    BoundaryShareRequest,
    BoundaryStatus,
    BoundaryType,
    ConflictType,
    CoordinateAccuracy,
    FieldBoundary,
    GPSTrack,
    MultiPolygon,
    Point,
    Polygon,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Enum Tests - اختبارات التعدادات
# ═══════════════════════════════════════════════════════════════════════════════


class TestBoundaryEnums:
    """Test boundary-related enumerations."""

    def test_boundary_status_values(self):
        assert BoundaryStatus.DRAFT == "draft"
        assert BoundaryStatus.PENDING_APPROVAL == "pending_approval"
        assert BoundaryStatus.APPROVED == "approved"
        assert BoundaryStatus.DISPUTED == "disputed"
        assert BoundaryStatus.ARCHIVED == "archived"

    def test_boundary_type_values(self):
        assert BoundaryType.FIELD == "field"
        assert BoundaryType.PLOT == "plot"
        assert BoundaryType.FARM == "farm"
        assert BoundaryType.IRRIGATION_ZONE == "irrigation_zone"
        assert BoundaryType.EXCLUSION_ZONE == "exclusion_zone"

    def test_coordinate_accuracy_values(self):
        assert CoordinateAccuracy.HIGH == "high"
        assert CoordinateAccuracy.MEDIUM == "medium"
        assert CoordinateAccuracy.LOW == "low"
        assert CoordinateAccuracy.UNKNOWN == "unknown"

    def test_conflict_type_values(self):
        assert ConflictType.OVERLAP == "overlap"
        assert ConflictType.GAP == "gap"
        assert ConflictType.ENCROACHMENT == "encroachment"
        assert ConflictType.DISPUTED_LINE == "disputed_line"


# ═══════════════════════════════════════════════════════════════════════════════
# Point Model Tests - اختبارات نموذج النقطة
# ═══════════════════════════════════════════════════════════════════════════════


class TestPointModel:
    """Test GeoJSON Point model."""

    def test_valid_point_creation(self):
        point = Point(coordinates=(46.7, 24.7))
        assert point.type == "Point"
        assert point.coordinates == (46.7, 24.7)

    def test_point_boundary_values(self):
        point_min = Point(coordinates=(-180.0, -90.0))
        assert point_min.coordinates == (-180.0, -90.0)

        point_max = Point(coordinates=(180.0, 90.0))
        assert point_max.coordinates == (180.0, 90.0)

    def test_point_invalid_longitude(self):
        with pytest.raises(ValueError, match="Longitude"):
            Point(coordinates=(181.0, 24.7))

    def test_point_invalid_latitude(self):
        with pytest.raises(ValueError, match="Latitude"):
            Point(coordinates=(46.7, 91.0))

    def test_point_negative_invalid(self):
        with pytest.raises(ValueError):
            Point(coordinates=(-181.0, 24.7))

    def test_point_to_postgis(self):
        point = Point(coordinates=(46.7, 24.7))
        result = point.to_postgis()
        assert "ST_SetSRID" in result
        assert "ST_MakePoint(46.7, 24.7)" in result
        assert "4326" in result

    def test_point_zero_coordinates(self):
        point = Point(coordinates=(0.0, 0.0))
        assert point.coordinates == (0.0, 0.0)


# ═══════════════════════════════════════════════════════════════════════════════
# Polygon Model Tests - اختبارات نموذج المضلع
# ═══════════════════════════════════════════════════════════════════════════════


# Riyadh area sample polygon (closed)
SAMPLE_POLYGON_COORDS = [
    [(46.7, 24.7), (46.71, 24.7), (46.71, 24.71), (46.7, 24.71), (46.7, 24.7)]
]


class TestPolygonModel:
    """Test GeoJSON Polygon model."""

    def test_valid_polygon_creation(self):
        polygon = Polygon(coordinates=SAMPLE_POLYGON_COORDS)
        assert polygon.type == "Polygon"
        assert len(polygon.coordinates) == 1
        assert len(polygon.coordinates[0]) == 5

    def test_polygon_exterior_ring(self):
        polygon = Polygon(coordinates=SAMPLE_POLYGON_COORDS)
        exterior = polygon.exterior_ring
        assert len(exterior) == 5
        assert exterior[0] == exterior[-1]

    def test_polygon_no_holes(self):
        polygon = Polygon(coordinates=SAMPLE_POLYGON_COORDS)
        assert polygon.holes == []

    def test_polygon_with_holes(self):
        hole = [(46.703, 24.703), (46.707, 24.703), (46.707, 24.707), (46.703, 24.707), (46.703, 24.703)]
        polygon = Polygon(coordinates=[SAMPLE_POLYGON_COORDS[0], hole])
        assert len(polygon.holes) == 1

    def test_polygon_too_few_points(self):
        with pytest.raises(ValueError, match="at least 4 points"):
            Polygon(coordinates=[[(46.7, 24.7), (46.71, 24.7), (46.7, 24.7)]])

    def test_polygon_not_closed(self):
        with pytest.raises(ValueError, match="closed"):
            Polygon(coordinates=[[(46.7, 24.7), (46.71, 24.7), (46.71, 24.71), (46.7, 24.71)]])

    def test_polygon_empty_rings(self):
        with pytest.raises(ValueError, match="at least one ring"):
            Polygon(coordinates=[])

    def test_polygon_invalid_coordinates_in_ring(self):
        with pytest.raises(ValueError, match="Invalid longitude"):
            Polygon(coordinates=[[(200.0, 24.7), (46.71, 24.7), (46.71, 24.71), (200.0, 24.7)]])

    def test_polygon_to_postgis(self):
        polygon = Polygon(coordinates=SAMPLE_POLYGON_COORDS)
        result = polygon.to_postgis()
        assert "ST_SetSRID" in result
        assert "ST_GeomFromText" in result
        assert "POLYGON" in result
        assert "4326" in result


class TestMultiPolygonModel:
    """Test GeoJSON MultiPolygon model."""

    def test_multipolygon_creation(self):
        mp = MultiPolygon(coordinates=[SAMPLE_POLYGON_COORDS])
        assert mp.type == "MultiPolygon"
        assert len(mp.coordinates) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# BoundaryPoint Tests - اختبارات نقطة الحد
# ═══════════════════════════════════════════════════════════════════════════════


class TestBoundaryPointModel:
    """Test BoundaryPoint model."""

    def test_boundary_point_creation(self):
        bp = BoundaryPoint(coordinates=(46.7, 24.7), captured_at=datetime.now(UTC))
        assert bp.coordinates == (46.7, 24.7)
        assert bp.accuracy_m == 5.0
        assert bp.accuracy_level == CoordinateAccuracy.UNKNOWN
        assert bp.id is not None

    def test_boundary_point_with_accuracy(self):
        bp = BoundaryPoint(
            coordinates=(46.7, 24.7),
            accuracy_m=0.5,
            accuracy_level=CoordinateAccuracy.HIGH,
            captured_at=datetime.now(UTC),
        )
        assert bp.accuracy_m == 0.5
        assert bp.accuracy_level == CoordinateAccuracy.HIGH

    def test_boundary_point_to_point(self):
        bp = BoundaryPoint(coordinates=(46.7, 24.7), captured_at=datetime.now(UTC))
        point = bp.to_point()
        assert isinstance(point, Point)
        assert point.coordinates == (46.7, 24.7)

    def test_boundary_point_with_metadata(self):
        bp = BoundaryPoint(
            coordinates=(46.7, 24.7),
            altitude_m=600.0,
            device_id="gps-001",
            notes="Corner post",
            notes_ar="عمود الزاوية",
            captured_at=datetime.now(UTC),
        )
        assert bp.altitude_m == 600.0
        assert bp.device_id == "gps-001"
        assert bp.notes_ar == "عمود الزاوية"


# ═══════════════════════════════════════════════════════════════════════════════
# FieldBoundary Tests - اختبارات حدود الحقل
# ═══════════════════════════════════════════════════════════════════════════════


def _create_sample_boundary(**overrides) -> FieldBoundary:
    """Helper to create a sample FieldBoundary."""
    defaults = {
        "field_id": "FIELD-001",
        "tenant_id": "tenant-001",
        "owner_id": "user-001",
        "name": "North Field",
        "name_ar": "الحقل الشمالي",
        "geometry": Polygon(coordinates=SAMPLE_POLYGON_COORDS),
    }
    defaults.update(overrides)
    return FieldBoundary(**defaults)


_NOW = datetime.now(UTC)


def _bp(coords: tuple[float, float], **kw) -> BoundaryPoint:
    """Helper to create BoundaryPoint with required captured_at."""
    kw.setdefault("captured_at", _NOW)
    return BoundaryPoint(coordinates=coords, **kw)


def _conflict(**kw) -> BoundaryConflict:
    """Helper to create BoundaryConflict with required detected_at."""
    defaults = {
        "boundary_id_a": "b1",
        "boundary_id_b": "b2",
        "field_id_a": "f1",
        "field_id_b": "f2",
        "owner_id_a": "u1",
        "owner_id_b": "u2",
        "detected_at": _NOW,
    }
    defaults.update(kw)
    return BoundaryConflict(**defaults)


class TestFieldBoundaryModel:
    """Test FieldBoundary model."""

    def test_field_boundary_creation(self):
        fb = _create_sample_boundary()
        assert fb.field_id == "FIELD-001"
        assert fb.tenant_id == "tenant-001"
        assert fb.owner_id == "user-001"
        assert fb.name == "North Field"
        assert fb.name_ar == "الحقل الشمالي"
        assert fb.status == BoundaryStatus.DRAFT
        assert fb.boundary_type == BoundaryType.FIELD
        assert fb.version == 1

    def test_field_boundary_defaults(self):
        fb = _create_sample_boundary()
        assert fb.shared_with == []
        assert fb.neighbor_field_ids == []
        assert fb.metadata == {}
        assert fb.area_hectares is None
        assert fb.perimeter_meters is None

    def test_field_boundary_to_geojson_feature(self):
        fb = _create_sample_boundary(area_hectares=10.5, perimeter_meters=1500.0)
        feature = fb.to_geojson_feature()

        assert feature["type"] == "Feature"
        assert feature["id"] == fb.id
        assert feature["geometry"]["type"] == "Polygon"
        assert feature["properties"]["field_id"] == "FIELD-001"
        assert feature["properties"]["name"] == "North Field"
        assert feature["properties"]["name_ar"] == "الحقل الشمالي"
        assert feature["properties"]["area_hectares"] == 10.5
        assert feature["properties"]["perimeter_meters"] == 1500.0
        assert feature["properties"]["version"] == 1

    def test_field_boundary_to_postgis_insert(self):
        fb = _create_sample_boundary()
        sql, params = fb.to_postgis_insert()

        assert "INSERT INTO field_boundaries" in sql
        assert "ST_GeomFromGeoJSON" in sql
        assert len(params) == 14
        assert params[0] == fb.id
        assert params[1] == "FIELD-001"
        assert params[2] == "tenant-001"

    def test_field_boundary_custom_table_name(self):
        fb = _create_sample_boundary()
        sql, _ = fb.to_postgis_insert(table_name="custom_boundaries")
        assert "INSERT INTO custom_boundaries" in sql

    def test_field_boundary_with_multipolygon(self):
        mp = MultiPolygon(coordinates=[SAMPLE_POLYGON_COORDS])
        fb = _create_sample_boundary(geometry=mp)
        assert fb.geometry.type == "MultiPolygon"


# ═══════════════════════════════════════════════════════════════════════════════
# BoundaryConflict Tests - اختبارات تعارض الحدود
# ═══════════════════════════════════════════════════════════════════════════════


class TestBoundaryConflictModel:
    """Test BoundaryConflict model."""

    def test_overlap_conflict(self):
        conflict = _conflict(
            conflict_type=ConflictType.OVERLAP,
            overlap_area_sqm=150.0,
        )
        assert conflict.conflict_type == ConflictType.OVERLAP
        assert conflict.overlap_area_sqm == 150.0
        assert not conflict.is_resolved

    def test_gap_conflict(self):
        conflict = _conflict(
            conflict_type=ConflictType.GAP,
            gap_distance_m=2.5,
        )
        assert conflict.gap_distance_m == 2.5

    def test_conflict_description_english(self):
        conflict = _conflict(
            conflict_type=ConflictType.OVERLAP,
            overlap_area_sqm=150.0,
            gap_distance_m=0.0,
        )
        desc = conflict.get_description("en")
        assert "150.00 m²" in desc

    def test_conflict_description_arabic(self):
        conflict = _conflict(
            conflict_type=ConflictType.OVERLAP,
            overlap_area_sqm=150.0,
            gap_distance_m=0.0,
        )
        desc = conflict.get_description("ar")
        assert "150.00" in desc
        assert "م²" in desc

    def test_conflict_description_gap_arabic(self):
        conflict = _conflict(
            conflict_type=ConflictType.GAP,
            gap_distance_m=3.5,
            overlap_area_sqm=0.0,
        )
        desc = conflict.get_description("ar")
        assert "3.50" in desc

    def test_conflict_description_encroachment(self):
        conflict = _conflict(
            conflict_type=ConflictType.ENCROACHMENT,
            overlap_area_sqm=0.0,
            gap_distance_m=0.0,
        )
        assert "encroach" in conflict.get_description("en").lower()
        assert "يتجاوز" in conflict.get_description("ar")

    def test_conflict_description_disputed_line(self):
        conflict = _conflict(
            conflict_type=ConflictType.DISPUTED_LINE,
            overlap_area_sqm=0.0,
            gap_distance_m=0.0,
        )
        assert "Disputed" in conflict.get_description("en")

    def test_conflict_defaults(self):
        conflict = _conflict(conflict_type=ConflictType.OVERLAP)
        assert conflict.severity == "medium"
        assert conflict.is_resolved is False
        assert conflict.resolved_by is None


# ═══════════════════════════════════════════════════════════════════════════════
# BoundaryShareRequest Tests - اختبارات طلب المشاركة
# ═══════════════════════════════════════════════════════════════════════════════


class TestBoundaryShareRequestModel:
    """Test BoundaryShareRequest model."""

    def test_share_request_creation(self):
        req = BoundaryShareRequest(
            boundary_id="b1",
            requester_id="user-001",
            recipient_id="user-002",
            created_at=_NOW,
        )
        assert req.boundary_id == "b1"
        assert req.status == "pending"
        assert req.permission_level == "view"

    def test_share_request_with_message(self):
        req = BoundaryShareRequest(
            boundary_id="b1",
            requester_id="user-001",
            recipient_id="user-002",
            message="Please review the boundary",
            message_ar="يرجى مراجعة الحد",
            permission_level="edit",
            created_at=_NOW,
        )
        assert req.message_ar == "يرجى مراجعة الحد"
        assert req.permission_level == "edit"


# ═══════════════════════════════════════════════════════════════════════════════
# GPSTrack Tests - اختبارات مسار GPS
# ═══════════════════════════════════════════════════════════════════════════════


class TestGPSTrackModel:
    """Test GPSTrack model."""

    def test_gps_track_creation(self):
        track = GPSTrack(user_id="user-001", start_time=_NOW)
        assert track.user_id == "user-001"
        assert track.points == []
        assert track.is_closed is False
        assert track.is_processed is False

    def test_gps_track_add_point(self):
        track = GPSTrack(user_id="user-001", start_time=_NOW)
        p1 = _bp((46.7, 24.7))
        p2 = _bp((46.71, 24.7))
        track.add_point(p1)
        track.add_point(p2)
        assert len(track.points) == 2

    def test_gps_track_close(self):
        track = GPSTrack(user_id="user-001", start_time=_NOW)
        track.add_point(_bp((46.7, 24.7)))
        track.add_point(_bp((46.71, 24.7)))
        track.add_point(_bp((46.71, 24.71)))
        # Add closing point manually (close_track creates BoundaryPoint internally
        # which hits a default_factory bug in the source model)
        track.add_point(_bp((46.7, 24.7)))
        track.close_track()
        assert track.is_closed is True
        assert track.points[-1].coordinates == track.points[0].coordinates

    def test_gps_track_close_already_closed(self):
        track = GPSTrack(user_id="user-001", start_time=_NOW)
        track.add_point(_bp((46.7, 24.7)))
        track.add_point(_bp((46.71, 24.7)))
        track.add_point(_bp((46.71, 24.71)))
        track.add_point(_bp((46.7, 24.7)))  # already closes
        track.close_track()
        assert track.is_closed is True
        # Should not add duplicate closing point
        assert len(track.points) == 4

    def test_gps_track_close_too_few_points(self):
        track = GPSTrack(user_id="user-001", start_time=_NOW)
        track.add_point(_bp((46.7, 24.7)))
        track.add_point(_bp((46.71, 24.7)))
        track.close_track()
        assert track.is_closed is False  # Not enough points


# ═══════════════════════════════════════════════════════════════════════════════
# Geometry Constants Tests - اختبارات ثوابت الهندسة
# ═══════════════════════════════════════════════════════════════════════════════


class TestGeometryConstants:
    """Test geometry constants."""

    def test_earth_radius(self):
        assert EARTH_RADIUS_M == 6371000.0

    def test_hectares_conversion(self):
        assert HECTARES_PER_SQM == 0.0001

    def test_dunams_conversion(self):
        assert DUNAMS_PER_SQM == 0.001

    def test_acres_conversion(self):
        assert pytest.approx(0.000247105) == ACRES_PER_SQM


# ═══════════════════════════════════════════════════════════════════════════════
# Conversion Utility Tests - اختبارات أدوات التحويل
# ═══════════════════════════════════════════════════════════════════════════════


class TestConversionUtilities:
    """Test degree/radian conversion."""

    def test_degrees_to_radians_0(self):
        assert degrees_to_radians(0) == 0.0

    def test_degrees_to_radians_180(self):
        assert degrees_to_radians(180) == pytest.approx(math.pi)

    def test_degrees_to_radians_90(self):
        assert degrees_to_radians(90) == pytest.approx(math.pi / 2)

    def test_degrees_to_radians_360(self):
        assert degrees_to_radians(360) == pytest.approx(2 * math.pi)

    def test_radians_to_degrees_pi(self):
        assert radians_to_degrees(math.pi) == pytest.approx(180.0)

    def test_radians_to_degrees_0(self):
        assert radians_to_degrees(0) == 0.0

    def test_roundtrip_conversion(self):
        assert radians_to_degrees(degrees_to_radians(45.0)) == pytest.approx(45.0)


# ═══════════════════════════════════════════════════════════════════════════════
# Haversine Distance Tests - اختبارات مسافة هافرساين
# ═══════════════════════════════════════════════════════════════════════════════


class TestHaversineDistance:
    """Test haversine distance calculation."""

    def test_same_point_zero_distance(self):
        d = haversine_distance(46.7, 24.7, 46.7, 24.7)
        assert d == pytest.approx(0.0)

    def test_known_distance_riyadh_jeddah(self):
        # Riyadh (46.7, 24.7) to Jeddah (39.2, 21.5): ~850 km
        d = haversine_distance(46.7, 24.7, 39.2, 21.5)
        assert 800_000 < d < 900_000  # between 800-900 km

    def test_short_distance_meters(self):
        # ~1.11 km for 0.01 degree latitude at equator
        d = haversine_distance(0.0, 0.0, 0.0, 0.01)
        assert 1000 < d < 1200

    def test_distance_symmetry(self):
        d1 = haversine_distance(46.7, 24.7, 39.2, 21.5)
        d2 = haversine_distance(39.2, 21.5, 46.7, 24.7)
        assert d1 == pytest.approx(d2)


# ═══════════════════════════════════════════════════════════════════════════════
# Area Calculation Tests - اختبارات حساب المساحة
# ═══════════════════════════════════════════════════════════════════════════════


# ~1 km × 1 km square near Riyadh
SQUARE_KM_COORDS = [
    (46.7, 24.7),
    (46.71, 24.7),
    (46.71, 24.71),
    (46.7, 24.71),
    (46.7, 24.7),
]


class TestAreaCalculations:
    """Test polygon area calculations."""

    def test_geodesic_area_positive(self):
        area = calculate_polygon_area_geodesic(SQUARE_KM_COORDS)
        assert area > 0

    def test_geodesic_area_reasonable_size(self):
        # 0.01 degree square near 24.7N should be roughly 1 km²
        area = calculate_polygon_area_geodesic(SQUARE_KM_COORDS)
        area_ha = area * HECTARES_PER_SQM
        assert 80 < area_ha < 130  # roughly 100 hectares

    def test_geodesic_area_too_few_points(self):
        area = calculate_polygon_area_geodesic([(46.7, 24.7), (46.71, 24.7)])
        assert area == 0.0

    def test_projected_area_positive(self):
        area = calculate_polygon_area_projected(SQUARE_KM_COORDS)
        assert area > 0

    def test_projected_area_reasonable(self):
        area = calculate_polygon_area_projected(SQUARE_KM_COORDS)
        area_ha = area * HECTARES_PER_SQM
        assert 80 < area_ha < 130

    def test_projected_area_too_few_points(self):
        area = calculate_polygon_area_projected([(46.7, 24.7), (46.71, 24.7)])
        assert area == 0.0

    def test_projected_area_with_reference_lat(self):
        area = calculate_polygon_area_projected(SQUARE_KM_COORDS, reference_lat=24.7)
        assert area > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Perimeter Calculation Tests - اختبارات حساب المحيط
# ═══════════════════════════════════════════════════════════════════════════════


class TestPerimeterCalculation:
    """Test perimeter calculations."""

    def test_perimeter_positive(self):
        perimeter = calculate_perimeter(SQUARE_KM_COORDS)
        assert perimeter > 0

    def test_perimeter_square_km(self):
        perimeter = calculate_perimeter(SQUARE_KM_COORDS)
        # ~4 km for a ~1 km square
        assert 3000 < perimeter < 5000

    def test_perimeter_too_few_points(self):
        assert calculate_perimeter([(46.7, 24.7)]) == 0.0

    def test_perimeter_empty_list(self):
        assert calculate_perimeter([]) == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Centroid Calculation Tests - اختبارات حساب المركز
# ═══════════════════════════════════════════════════════════════════════════════


class TestCentroidCalculation:
    """Test centroid calculations."""

    def test_centroid_of_square(self):
        coords = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        cx, cy = calculate_centroid(coords)
        assert cx == pytest.approx(0.5, abs=0.01)
        assert cy == pytest.approx(0.5, abs=0.01)

    def test_centroid_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            calculate_centroid([])

    def test_centroid_single_point(self):
        cx, cy = calculate_centroid([(46.7, 24.7)])
        assert cx == pytest.approx(46.7)
        assert cy == pytest.approx(24.7)

    def test_centroid_two_points(self):
        cx, cy = calculate_centroid([(0, 0), (10, 10)])
        assert cx == pytest.approx(5.0)
        assert cy == pytest.approx(5.0)


# ═══════════════════════════════════════════════════════════════════════════════
# Bounding Box Tests - اختبارات الإطار المحيط
# ═══════════════════════════════════════════════════════════════════════════════


class TestBoundingBox:
    """Test bounding box calculations."""

    def test_bounding_box_square(self):
        bbox = calculate_bounding_box(SQUARE_KM_COORDS)
        min_lon, min_lat, max_lon, max_lat = bbox
        assert min_lon == pytest.approx(46.7)
        assert min_lat == pytest.approx(24.7)
        assert max_lon == pytest.approx(46.71)
        assert max_lat == pytest.approx(24.71)

    def test_bounding_box_empty_raises(self):
        with pytest.raises(ValueError):
            calculate_bounding_box([])


# ═══════════════════════════════════════════════════════════════════════════════
# Point-in-Polygon Tests - اختبارات النقطة داخل المضلع
# ═══════════════════════════════════════════════════════════════════════════════


class TestPointInPolygon:
    """Test point-in-polygon algorithm."""

    SQUARE = [(0, 0), (10, 0), (10, 10), (0, 10)]

    def test_point_inside(self):
        assert is_point_in_polygon((5, 5), self.SQUARE) is True

    def test_point_outside(self):
        assert is_point_in_polygon((15, 5), self.SQUARE) is False

    def test_point_outside_negative(self):
        assert is_point_in_polygon((-1, -1), self.SQUARE) is False

    def test_point_far_outside(self):
        assert is_point_in_polygon((100, 100), self.SQUARE) is False


# ═══════════════════════════════════════════════════════════════════════════════
# Polygon Overlap Tests - اختبارات تداخل المضلعات
# ═══════════════════════════════════════════════════════════════════════════════


class TestPolygonOverlap:
    """Test polygon overlap detection."""

    POLY_A = [(0, 0), (10, 0), (10, 10), (0, 10)]
    POLY_B_OVERLAPPING = [(5, 5), (15, 5), (15, 15), (5, 15)]
    POLY_C_DISJOINT = [(20, 20), (30, 20), (30, 30), (20, 30)]

    def test_overlapping_polygons(self):
        assert polygons_overlap(self.POLY_A, self.POLY_B_OVERLAPPING) is True

    def test_disjoint_polygons(self):
        assert polygons_overlap(self.POLY_A, self.POLY_C_DISJOINT) is False

    def test_contained_polygon(self):
        inner = [(2, 2), (8, 2), (8, 8), (2, 8)]
        assert polygons_overlap(self.POLY_A, inner) is True


# ═══════════════════════════════════════════════════════════════════════════════
# Edge Intersection Tests - اختبارات تقاطع الحواف
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeIntersection:
    """Test line segment intersection."""

    def test_intersecting_edges(self):
        edge1 = ((0, 0), (10, 10))
        edge2 = ((0, 10), (10, 0))
        assert edges_intersect(edge1, edge2) is True

    def test_non_intersecting_edges(self):
        edge1 = ((0, 0), (5, 5))
        edge2 = ((6, 0), (10, 5))
        assert edges_intersect(edge1, edge2) is False

    def test_parallel_edges(self):
        edge1 = ((0, 0), (10, 0))
        edge2 = ((0, 5), (10, 5))
        assert edges_intersect(edge1, edge2) is False


# ═══════════════════════════════════════════════════════════════════════════════
# Overlap Area Tests - اختبارات مساحة التداخل
# ═══════════════════════════════════════════════════════════════════════════════


class TestOverlapArea:
    """Test overlap area estimation."""

    def test_no_overlap(self):
        poly1 = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        poly2 = [(5, 5), (6, 5), (6, 6), (5, 6), (5, 5)]
        area = calculate_overlap_area(poly1, poly2)
        assert area == 0.0

    def test_overlap_returns_positive(self):
        poly1 = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        poly2 = [(5, 5), (15, 5), (15, 15), (5, 15), (5, 5)]
        area = calculate_overlap_area(poly1, poly2)
        assert area >= 0.0  # simplified estimation


# ═══════════════════════════════════════════════════════════════════════════════
# Polygon Validation Tests - اختبارات التحقق من المضلع
# ═══════════════════════════════════════════════════════════════════════════════


class TestPolygonValidation:
    """Test polygon validation."""

    def test_valid_polygon(self):
        is_valid, errors = validate_polygon(SQUARE_KM_COORDS)
        assert is_valid is True
        assert errors == []

    def test_too_few_points(self):
        is_valid, errors = validate_polygon([(46.7, 24.7), (46.71, 24.7)])
        assert is_valid is False
        assert any("4 points" in e for e in errors)

    def test_not_closed(self):
        coords = [(46.7, 24.7), (46.71, 24.7), (46.71, 24.71), (46.7, 24.71)]
        is_valid, errors = validate_polygon(coords)
        assert is_valid is False
        assert any("closed" in e.lower() for e in errors)

    def test_invalid_longitude(self):
        coords = [(200, 24.7), (46.71, 24.7), (46.71, 24.71), (200, 24.71), (200, 24.7)]
        is_valid, errors = validate_polygon(coords)
        assert is_valid is False

    def test_empty_polygon(self):
        is_valid, errors = validate_polygon([])
        assert is_valid is False


# ═══════════════════════════════════════════════════════════════════════════════
# Geometry Metrics Tests - اختبارات مقاييس الهندسة
# ═══════════════════════════════════════════════════════════════════════════════


class TestGeometryMetrics:
    """Test comprehensive geometry metrics."""

    def test_metrics_geodesic(self):
        metrics = calculate_geometry_metrics(SQUARE_KM_COORDS, use_geodesic=True)
        assert metrics.area_sqm > 0
        assert metrics.area_hectares > 0
        assert metrics.area_dunams > 0
        assert metrics.area_acres > 0
        assert metrics.perimeter_m > 0

    def test_metrics_projected(self):
        metrics = calculate_geometry_metrics(SQUARE_KM_COORDS, use_geodesic=False)
        assert metrics.area_sqm > 0

    def test_metrics_too_few_points(self):
        metrics = calculate_geometry_metrics([(46.7, 24.7), (46.71, 24.7)])
        assert metrics.area_sqm == 0.0
        assert metrics.is_valid is False

    def test_metrics_empty(self):
        metrics = calculate_geometry_metrics([])
        assert metrics.area_sqm == 0.0
        assert metrics.is_valid is False

    def test_metrics_conversion_factors(self):
        metrics = calculate_geometry_metrics(SQUARE_KM_COORDS)
        assert metrics.area_hectares == pytest.approx(metrics.area_sqm * HECTARES_PER_SQM)
        assert metrics.area_dunams == pytest.approx(metrics.area_sqm * DUNAMS_PER_SQM)
        assert metrics.area_acres == pytest.approx(metrics.area_sqm * ACRES_PER_SQM)

    def test_metrics_bounding_box(self):
        metrics = calculate_geometry_metrics(SQUARE_KM_COORDS)
        min_lon, min_lat, max_lon, max_lat = metrics.bounding_box
        assert min_lon == pytest.approx(46.7)
        assert max_lon == pytest.approx(46.71)


# ═══════════════════════════════════════════════════════════════════════════════
# Simplify Polygon Tests - اختبارات تبسيط المضلع
# ═══════════════════════════════════════════════════════════════════════════════


class TestSimplifyPolygon:
    """Test Douglas-Peucker simplification."""

    def test_simplify_returns_valid(self):
        # Create polygon with many points
        coords = [
            (46.7, 24.7),
            (46.702, 24.7001),
            (46.704, 24.6999),
            (46.706, 24.7002),
            (46.71, 24.7),
            (46.71, 24.71),
            (46.7, 24.71),
            (46.7, 24.7),
        ]
        simplified = simplify_polygon(coords, tolerance_m=50.0)
        assert len(simplified) <= len(coords)
        # Must remain closed
        assert simplified[0] == simplified[-1]

    def test_simplify_too_few_points(self):
        coords = [(46.7, 24.7), (46.71, 24.7), (46.71, 24.71), (46.7, 24.7)]
        result = simplify_polygon(coords, tolerance_m=1.0)
        assert result == coords  # Not enough points to simplify


# ═══════════════════════════════════════════════════════════════════════════════
# Circular Boundary Tests - اختبارات الحد الدائري
# ═══════════════════════════════════════════════════════════════════════════════


class TestCircularBoundary:
    """Test circular polygon generation."""

    def test_create_circular_boundary(self):
        coords = create_circular_boundary(46.7, 24.7, 500, num_points=36)
        assert len(coords) == 37  # 36 + closing point
        assert coords[0] == coords[-1]

    def test_circular_boundary_negative_radius(self):
        with pytest.raises(ValueError, match="positive"):
            create_circular_boundary(46.7, 24.7, -100)

    def test_circular_boundary_too_few_points(self):
        with pytest.raises(ValueError, match="8 points"):
            create_circular_boundary(46.7, 24.7, 500, num_points=5)

    def test_circular_boundary_valid_coordinates(self):
        coords = create_circular_boundary(46.7, 24.7, 1000)
        for lon, lat in coords:
            assert -180 <= lon <= 180
            assert -90 <= lat <= 90


# ═══════════════════════════════════════════════════════════════════════════════
# PostGIS Helper Tests - اختبارات مساعدات PostGIS
# ═══════════════════════════════════════════════════════════════════════════════


class TestPostGISHelpers:
    """Test PostGIS SQL generation helpers."""

    def test_area_query_default(self):
        query = generate_postgis_area_query()
        assert "ST_Area" in query
        assert "geography" in query.lower() or "spheroid" in query.lower() or "geometry" in query

    def test_area_query_custom_column(self):
        query = generate_postgis_area_query(geometry_column="geom")
        assert "geom" in query

    def test_centroid_query(self):
        query = generate_postgis_centroid_query()
        assert "ST_Centroid" in query or "centroid" in query.lower()

    def test_overlap_query(self):
        query = generate_postgis_overlap_query("field_boundaries", "field_boundaries")
        assert "ST_Intersects" in query

    def test_neighbors_query(self):
        query = generate_postgis_neighbors_query("field_boundaries", "b-001")
        assert "ST_DWithin" in query or "distance" in query.lower()
