"""
Unit tests for shared/field_boundaries module.
اختبارات وحدة حدود الحقول.
"""

import math
import pytest

from shared.field_boundaries.models import (
    BoundaryStatus,
    BoundaryType,
    CoordinateAccuracy,
    ConflictType,
    Point,
    Polygon,
    MultiPolygon,
    BoundaryPoint,
    FieldBoundary,
)
from shared.field_boundaries.geometry import (
    EARTH_RADIUS_M,
    HECTARES_PER_SQM,
    DUNAMS_PER_SQM,
    ACRES_PER_SQM,
    GeometryMetrics,
    degrees_to_radians,
    radians_to_degrees,
    haversine_distance,
    calculate_polygon_area_geodesic,
    calculate_polygon_area_projected,
    calculate_perimeter,
    calculate_centroid,
    calculate_bounding_box,
    is_point_in_polygon,
)


# Sample coordinates for a field near Riyadh
RIYADH_SQUARE = [
    (46.7, 24.7),
    (46.71, 24.7),
    (46.71, 24.71),
    (46.7, 24.71),
    (46.7, 24.7),  # closed
]

RIYADH_POLYGON_COORDS = [[RIYADH_SQUARE]]


@pytest.mark.unit
class TestBoundaryStatusEnum:
    def test_all_values(self):
        assert BoundaryStatus.DRAFT == "draft"
        assert BoundaryStatus.PENDING_APPROVAL == "pending_approval"
        assert BoundaryStatus.APPROVED == "approved"
        assert BoundaryStatus.DISPUTED == "disputed"
        assert BoundaryStatus.ARCHIVED == "archived"

    def test_count(self):
        assert len(BoundaryStatus) == 5


@pytest.mark.unit
class TestBoundaryTypeEnum:
    def test_all_values(self):
        assert BoundaryType.FIELD == "field"
        assert BoundaryType.PLOT == "plot"
        assert BoundaryType.FARM == "farm"
        assert BoundaryType.IRRIGATION_ZONE == "irrigation_zone"
        assert BoundaryType.EXCLUSION_ZONE == "exclusion_zone"

    def test_count(self):
        assert len(BoundaryType) == 5


@pytest.mark.unit
class TestCoordinateAccuracyEnum:
    def test_all_values(self):
        assert CoordinateAccuracy.HIGH == "high"
        assert CoordinateAccuracy.MEDIUM == "medium"
        assert CoordinateAccuracy.LOW == "low"
        assert CoordinateAccuracy.UNKNOWN == "unknown"


@pytest.mark.unit
class TestConflictTypeEnum:
    def test_all_values(self):
        assert ConflictType.OVERLAP == "overlap"
        assert ConflictType.GAP == "gap"
        assert ConflictType.ENCROACHMENT == "encroachment"
        assert ConflictType.DISPUTED_LINE == "disputed_line"

    def test_count(self):
        assert len(ConflictType) == 4


@pytest.mark.unit
class TestPointModel:
    def test_valid_point(self):
        p = Point(coordinates=(46.7, 24.7))
        assert p.type == "Point"
        assert p.coordinates == (46.7, 24.7)

    def test_invalid_longitude(self):
        with pytest.raises(Exception):
            Point(coordinates=(200.0, 24.7))

    def test_invalid_latitude(self):
        with pytest.raises(Exception):
            Point(coordinates=(46.7, 100.0))

    def test_boundary_values(self):
        p1 = Point(coordinates=(-180.0, -90.0))
        assert p1.coordinates == (-180.0, -90.0)
        p2 = Point(coordinates=(180.0, 90.0))
        assert p2.coordinates == (180.0, 90.0)

    def test_to_postgis(self):
        p = Point(coordinates=(46.7, 24.7))
        postgis = p.to_postgis()
        assert "ST_SetSRID" in postgis
        assert "ST_MakePoint" in postgis
        assert "46.7" in postgis
        assert "24.7" in postgis
        assert "4326" in postgis


@pytest.mark.unit
class TestPolygonModel:
    def test_valid_polygon(self):
        poly = Polygon(coordinates=[RIYADH_SQUARE])
        assert poly.type == "Polygon"
        assert len(poly.coordinates) == 1

    def test_exterior_ring(self):
        poly = Polygon(coordinates=[RIYADH_SQUARE])
        assert poly.exterior_ring == RIYADH_SQUARE

    def test_no_holes(self):
        poly = Polygon(coordinates=[RIYADH_SQUARE])
        assert poly.holes == []

    def test_too_few_points(self):
        with pytest.raises(Exception):
            Polygon(coordinates=[[(46.7, 24.7), (46.71, 24.7), (46.7, 24.7)]])

    def test_unclosed_ring(self):
        with pytest.raises(Exception):
            Polygon(coordinates=[[(46.7, 24.7), (46.71, 24.7), (46.71, 24.71), (46.7, 24.71)]])

    def test_to_postgis(self):
        poly = Polygon(coordinates=[RIYADH_SQUARE])
        postgis = poly.to_postgis()
        assert "ST_SetSRID" in postgis
        assert "POLYGON" in postgis
        assert "4326" in postgis


@pytest.mark.unit
class TestBoundaryPointModel:
    def test_creation(self):
        from datetime import datetime, UTC
        bp = BoundaryPoint(coordinates=(46.7, 24.7), captured_at=datetime.now(UTC))
        assert bp.coordinates == (46.7, 24.7)
        assert bp.accuracy_m == 5.0
        assert bp.accuracy_level == CoordinateAccuracy.UNKNOWN
        assert bp.id is not None

    def test_bilingual_notes(self):
        from datetime import datetime, UTC
        bp = BoundaryPoint(
            coordinates=(46.7, 24.7),
            captured_at=datetime.now(UTC),
            notes="Corner point",
            notes_ar="نقطة الزاوية",
        )
        assert bp.notes == "Corner point"
        assert bp.notes_ar == "نقطة الزاوية"

    def test_to_point(self):
        from datetime import datetime, UTC
        bp = BoundaryPoint(coordinates=(46.7, 24.7), captured_at=datetime.now(UTC))
        p = bp.to_point()
        assert isinstance(p, Point)
        assert p.coordinates == (46.7, 24.7)


@pytest.mark.unit
class TestFieldBoundaryModel:
    def test_creation(self):
        fb = FieldBoundary(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            owner_id="USER-001",
            name="North Field",
            geometry=Polygon(coordinates=[RIYADH_SQUARE]),
        )
        assert fb.field_id == "FIELD-001"
        assert fb.status == BoundaryStatus.DRAFT
        assert fb.boundary_type == BoundaryType.FIELD
        assert fb.version == 1

    def test_bilingual_name(self):
        fb = FieldBoundary(
            field_id="FIELD-001",
            tenant_id="TENANT-001",
            owner_id="USER-001",
            name="North Field",
            name_ar="الحقل الشمالي",
            description="Main wheat field",
            description_ar="حقل القمح الرئيسي",
            geometry=Polygon(coordinates=[RIYADH_SQUARE]),
        )
        assert fb.name_ar == "الحقل الشمالي"
        assert fb.description_ar == "حقل القمح الرئيسي"

    def test_defaults(self):
        fb = FieldBoundary(
            field_id="F1",
            tenant_id="T1",
            owner_id="U1",
            name="Test",
            geometry=Polygon(coordinates=[RIYADH_SQUARE]),
        )
        assert fb.shared_with == []
        assert fb.neighbor_field_ids == []
        assert fb.boundary_points == []
        assert fb.previous_version_id is None
        assert fb.accuracy_level == CoordinateAccuracy.UNKNOWN


@pytest.mark.unit
class TestDegreesRadians:
    def test_degrees_to_radians(self):
        assert degrees_to_radians(0) == 0.0
        assert abs(degrees_to_radians(180) - math.pi) < 1e-10
        assert abs(degrees_to_radians(90) - math.pi / 2) < 1e-10

    def test_radians_to_degrees(self):
        assert radians_to_degrees(0) == 0.0
        assert abs(radians_to_degrees(math.pi) - 180.0) < 1e-10

    def test_roundtrip(self):
        assert abs(radians_to_degrees(degrees_to_radians(45.0)) - 45.0) < 1e-10


@pytest.mark.unit
class TestHaversineDistance:
    def test_same_point(self):
        d = haversine_distance(46.7, 24.7, 46.7, 24.7)
        assert d == 0.0

    def test_known_distance(self):
        # Riyadh (46.7, 24.7) to Jeddah (39.2, 21.5) ~ 850 km
        d = haversine_distance(46.7, 24.7, 39.2, 21.5)
        assert 800_000 < d < 900_000

    def test_one_degree_latitude(self):
        d = haversine_distance(0.0, 0.0, 0.0, 1.0)
        assert 110_000 < d < 112_000  # ~111.32 km

    def test_symmetry(self):
        d1 = haversine_distance(46.7, 24.7, 39.2, 21.5)
        d2 = haversine_distance(39.2, 21.5, 46.7, 24.7)
        assert abs(d1 - d2) < 0.01


@pytest.mark.unit
class TestPolygonArea:
    def test_geodesic_area_positive(self):
        area = calculate_polygon_area_geodesic(RIYADH_SQUARE)
        assert area > 0

    def test_geodesic_area_too_few_points(self):
        area = calculate_polygon_area_geodesic([(0, 0), (1, 0), (0, 0)])
        assert area == 0.0

    def test_projected_area_positive(self):
        area = calculate_polygon_area_projected(RIYADH_SQUARE)
        assert area > 0

    def test_projected_area_too_few_points(self):
        area = calculate_polygon_area_projected([(0, 0), (1, 0), (0, 0)])
        assert area == 0.0

    def test_geodesic_vs_projected_similar(self):
        area_g = calculate_polygon_area_geodesic(RIYADH_SQUARE)
        area_p = calculate_polygon_area_projected(RIYADH_SQUARE)
        # Should be within 10% for small fields
        ratio = area_g / area_p if area_p > 0 else 0
        assert 0.8 < ratio < 1.2


@pytest.mark.unit
class TestPerimeter:
    def test_empty(self):
        assert calculate_perimeter([]) == 0.0
        assert calculate_perimeter([(0, 0)]) == 0.0

    def test_positive(self):
        perim = calculate_perimeter(RIYADH_SQUARE)
        assert perim > 0

    def test_square_rough(self):
        # ~1 km square should have ~4 km perimeter
        perim = calculate_perimeter(RIYADH_SQUARE)
        assert 2000 < perim < 6000


@pytest.mark.unit
class TestCentroid:
    def test_empty_raises(self):
        with pytest.raises(ValueError):
            calculate_centroid([])

    def test_single_point(self):
        cx, cy = calculate_centroid([(46.7, 24.7)])
        assert cx == 46.7
        assert cy == 24.7

    def test_two_points(self):
        cx, cy = calculate_centroid([(0, 0), (10, 10)])
        assert cx == 5.0
        assert cy == 5.0

    def test_square_centroid(self):
        cx, cy = calculate_centroid(RIYADH_SQUARE)
        assert 46.69 < cx < 46.72
        assert 24.69 < cy < 24.72


@pytest.mark.unit
class TestBoundingBox:
    def test_empty_raises(self):
        with pytest.raises(ValueError):
            calculate_bounding_box([])

    def test_square(self):
        bbox = calculate_bounding_box(RIYADH_SQUARE)
        min_lon, min_lat, max_lon, max_lat = bbox
        assert min_lon == 46.7
        assert min_lat == 24.7
        assert max_lon == 46.71
        assert max_lat == 24.71


@pytest.mark.unit
class TestPointInPolygon:
    def test_inside(self):
        square = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        assert is_point_in_polygon((5, 5), square) is True

    def test_outside(self):
        square = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        assert is_point_in_polygon((15, 15), square) is False

    def test_riyadh_field(self):
        inside_pt = (46.705, 24.705)
        assert is_point_in_polygon(inside_pt, RIYADH_SQUARE) is True

        outside_pt = (46.5, 24.5)
        assert is_point_in_polygon(outside_pt, RIYADH_SQUARE) is False


@pytest.mark.unit
class TestGeometryMetrics:
    def test_creation(self):
        m = GeometryMetrics(
            area_sqm=10000.0,
            area_hectares=1.0,
            area_dunams=10.0,
            area_acres=2.47,
            perimeter_m=400.0,
            centroid_lon=46.7,
            centroid_lat=24.7,
            bounding_box=(46.69, 24.69, 46.71, 24.71),
            is_valid=True,
            validation_errors=[],
        )
        assert m.area_hectares == 1.0
        assert m.is_valid is True
        assert m.validation_errors == []


@pytest.mark.unit
class TestConstants:
    def test_earth_radius(self):
        assert EARTH_RADIUS_M == 6371000.0

    def test_conversion_factors(self):
        assert HECTARES_PER_SQM == 0.0001
        assert DUNAMS_PER_SQM == 0.001
        assert ACRES_PER_SQM == 0.000247105
        # 1 hectare = 10000 sqm
        assert abs(1.0 / HECTARES_PER_SQM - 10000.0) < 0.01
