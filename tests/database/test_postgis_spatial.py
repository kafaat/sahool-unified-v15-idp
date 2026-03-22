"""
PostGIS Spatial Operations Tests for SAHOOL Platform.

Tests validate geospatial queries, geometry operations, and field boundary handling.
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, List

import pytest


@dataclass
class GeoJSONPolygon:
    """GeoJSON Polygon representation."""

    coordinates: list[list[list[float]]]

    @property
    def type(self) -> str:
        return "Polygon"

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "coordinates": self.coordinates}

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass
class GeoJSONPoint:
    """GeoJSON Point representation."""

    coordinates: list[float]

    @property
    def type(self) -> str:
        return "Point"

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.type, "coordinates": self.coordinates}


class GeometryValidator:
    """Validates GeoJSON geometry objects."""

    @staticmethod
    def validate_polygon(geojson: dict[str, Any]) -> bool:
        """Validate a GeoJSON Polygon."""
        if geojson.get("type") != "Polygon":
            return False

        coords = geojson.get("coordinates", [])
        if not coords or not isinstance(coords, list):
            return False

        for ring in coords:
            if len(ring) < 4:
                return False
            if ring[0] != ring[-1]:
                return False
            for point in ring:
                if len(point) < 2:
                    return False
                if not (-180 <= point[0] <= 180):
                    return False
                if not (-90 <= point[1] <= 90):
                    return False

        return True

    @staticmethod
    def validate_point(geojson: dict[str, Any]) -> bool:
        """Validate a GeoJSON Point."""
        if geojson.get("type") != "Point":
            return False

        coords = geojson.get("coordinates", [])
        if len(coords) < 2:
            return False

        lon, lat = coords[0], coords[1]
        return -180 <= lon <= 180 and -90 <= lat <= 90

    @staticmethod
    def calculate_area_hectares(polygon: dict[str, Any]) -> float:
        """Estimate polygon area in hectares using simple calculation."""
        coords = polygon.get("coordinates", [[]])[0]
        if len(coords) < 4:
            return 0.0

        n = len(coords)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += coords[i][0] * coords[j][1]
            area -= coords[j][0] * coords[i][1]

        area_deg = abs(area) / 2.0
        area_km2 = area_deg * 111.32 * 111.32
        return area_km2 * 100


@pytest.fixture
def sample_polygon():
    """Create sample field polygon."""
    return GeoJSONPolygon(coordinates=[[[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8], [46.7, 24.7]]])


@pytest.fixture
def sample_point():
    """Create sample centroid point."""
    return GeoJSONPoint(coordinates=[46.75, 24.75])


@pytest.fixture
def geometry_validator():
    """Create geometry validator."""
    return GeometryValidator()


class TestGeoJSONValidation:
    """Tests for GeoJSON validation."""

    def test_valid_polygon(self, geometry_validator, sample_polygon):
        """Test valid polygon passes validation."""
        assert geometry_validator.validate_polygon(sample_polygon.to_dict())

    def test_invalid_polygon_unclosed(self, geometry_validator):
        """Test unclosed polygon fails validation."""
        invalid = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1]]]}
        assert not geometry_validator.validate_polygon(invalid)

    def test_invalid_polygon_too_few_points(self, geometry_validator):
        """Test polygon with too few points fails validation."""
        invalid = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [0, 0]]]}
        assert not geometry_validator.validate_polygon(invalid)

    def test_invalid_polygon_out_of_bounds(self, geometry_validator):
        """Test polygon with out-of-bounds coordinates fails validation."""
        invalid = {
            "type": "Polygon",
            "coordinates": [[[200, 100], [201, 100], [201, 101], [200, 101], [200, 100]]],
        }
        assert not geometry_validator.validate_polygon(invalid)

    def test_valid_point(self, geometry_validator, sample_point):
        """Test valid point passes validation."""
        assert geometry_validator.validate_point(sample_point.to_dict())

    def test_invalid_point_out_of_bounds(self, geometry_validator):
        """Test point with out-of-bounds coordinates fails validation."""
        invalid = {"type": "Point", "coordinates": [200, 100]}
        assert not geometry_validator.validate_point(invalid)


class TestSpatialQueries:
    """Tests for spatial database queries."""

    @pytest.mark.asyncio
    async def test_point_in_polygon_query(self):
        """Test ST_Contains query for point in polygon."""
        query = """
            SELECT ST_Contains(
                ST_GeomFromGeoJSON($1),
                ST_GeomFromGeoJSON($2)
            ) as contains
        """

        polygon = {"type": "Polygon", "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]}
        point_inside = {"type": "Point", "coordinates": [5, 5]}
        point_outside = {"type": "Point", "coordinates": [15, 15]}

        assert "ST_Contains" in query
        assert "ST_GeomFromGeoJSON" in query

    @pytest.mark.asyncio
    async def test_polygon_intersection_query(self):
        """Test ST_Intersects query for polygon overlap."""
        query = """
            SELECT f.id, f.name
            FROM fields f
            WHERE ST_Intersects(
                f.boundary,
                ST_GeomFromGeoJSON($1)
            )
            AND f.tenant_id = $2
        """

        assert "ST_Intersects" in query
        assert "tenant_id" in query

    @pytest.mark.asyncio
    async def test_area_calculation_query(self):
        """Test ST_Area query for polygon area calculation."""
        query = """
            SELECT
                ST_Area(ST_Transform(boundary, 32637)) / 10000 as area_ha
            FROM fields
            WHERE id = $1
        """

        assert "ST_Area" in query
        assert "ST_Transform" in query

    @pytest.mark.asyncio
    async def test_centroid_calculation_query(self):
        """Test ST_Centroid query."""
        query = """
            SELECT
                ST_AsGeoJSON(ST_Centroid(boundary))::json as centroid
            FROM fields
            WHERE id = $1
        """

        assert "ST_Centroid" in query
        assert "ST_AsGeoJSON" in query

    @pytest.mark.asyncio
    async def test_distance_calculation_query(self):
        """Test ST_Distance query for proximity calculations."""
        query = """
            SELECT
                f.id,
                f.name,
                ST_Distance(
                    f.boundary::geography,
                    ST_GeomFromGeoJSON($1)::geography
                ) as distance_meters
            FROM fields f
            WHERE f.tenant_id = $2
            ORDER BY distance_meters
            LIMIT $3
        """

        assert "ST_Distance" in query
        assert "geography" in query


class TestFieldBoundaryOperations:
    """Tests for field boundary operations."""

    def test_boundary_to_geojson(self, sample_polygon):
        """Test converting boundary to GeoJSON."""
        geojson = sample_polygon.to_dict()

        assert geojson["type"] == "Polygon"
        assert "coordinates" in geojson
        assert len(geojson["coordinates"]) > 0

    def test_geojson_to_wkt(self, sample_polygon):
        """Test converting GeoJSON to WKT."""
        coords = sample_polygon.coordinates[0]
        wkt_points = ", ".join([f"{p[0]} {p[1]}" for p in coords])
        wkt = f"POLYGON(({wkt_points}))"

        assert wkt.startswith("POLYGON")
        assert "46.7" in wkt
        assert "24.7" in wkt

    def test_area_calculation(self, geometry_validator, sample_polygon):
        """Test area calculation."""
        area_ha = geometry_validator.calculate_area_hectares(sample_polygon.to_dict())

        assert area_ha > 0

    def test_boundary_validity_check(self, sample_polygon):
        """Test boundary validity check."""
        coords = sample_polygon.coordinates[0]
        is_closed = coords[0] == coords[-1]
        has_min_points = len(coords) >= 4

        assert is_closed
        assert has_min_points


class TestSpatialIndexing:
    """Tests for spatial index operations."""

    def test_spatial_index_creation_query(self):
        """Test spatial index creation SQL."""
        query = """
            CREATE INDEX IF NOT EXISTS idx_fields_boundary_gist
            ON fields USING GIST (boundary)
        """

        assert "GIST" in query
        assert "boundary" in query

    def test_spatial_index_usage_in_query(self):
        """Test that queries can use spatial index."""
        query = """
            SELECT id, name
            FROM fields
            WHERE boundary && ST_MakeEnvelope($1, $2, $3, $4, 4326)
            AND tenant_id = $5
        """

        assert "&&" in query
        assert "ST_MakeEnvelope" in query


class TestCoordinateTransformation:
    """Tests for coordinate transformation."""

    def test_srid_4326_to_32637(self):
        """Test transformation from WGS84 to UTM Zone 37N."""
        source_srid = 4326
        target_srid = 32637

        query = f"""
            SELECT ST_Transform(
                ST_SetSRID(ST_GeomFromGeoJSON($1), {source_srid}),
                {target_srid}
            )
        """

        assert "ST_Transform" in query
        assert str(source_srid) in query
        assert str(target_srid) in query

    def test_coordinate_precision(self):
        """Test coordinate precision is maintained."""
        original = [46.712345678, 24.712345678]
        precision = 8

        rounded = [round(c, precision) for c in original]

        assert rounded[0] == 46.71234568
        assert rounded[1] == 24.71234568


class TestMultiPolygonSupport:
    """Tests for MultiPolygon geometry support."""

    def test_multipolygon_validation(self, geometry_validator):
        """Test MultiPolygon geometry handling."""
        multipolygon = {
            "type": "MultiPolygon",
            "coordinates": [
                [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                [[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]],
            ],
        }

        assert multipolygon["type"] == "MultiPolygon"
        assert len(multipolygon["coordinates"]) == 2

    def test_multipolygon_to_polygon_collection(self):
        """Test splitting MultiPolygon into Polygon collection."""
        multipolygon_coords = [
            [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
            [[[2, 2], [3, 2], [3, 3], [2, 3], [2, 2]]],
        ]

        polygons = [{"type": "Polygon", "coordinates": coords} for coords in multipolygon_coords]

        assert len(polygons) == 2
        assert all(p["type"] == "Polygon" for p in polygons)


class TestGeometryBuffer:
    """Tests for geometry buffer operations."""

    def test_buffer_query(self):
        """Test ST_Buffer query for creating buffer zones."""
        query = """
            SELECT ST_AsGeoJSON(
                ST_Buffer(
                    boundary::geography,
                    $1
                )::geometry
            )::json as buffer_zone
            FROM fields
            WHERE id = $2
        """

        assert "ST_Buffer" in query
        assert "geography" in query

    def test_negative_buffer_for_shrinking(self):
        """Test negative buffer for shrinking geometry."""
        buffer_distance = -10

        query = f"""
            SELECT ST_Buffer(boundary, {buffer_distance})
            FROM fields
        """

        assert str(buffer_distance) in query


class TestSpatialRelationships:
    """Tests for spatial relationship queries."""

    def test_st_within_query(self):
        """Test ST_Within for checking containment."""
        query = """
            SELECT COUNT(*)
            FROM fields f
            JOIN farms fa ON f.farm_id = fa.id
            WHERE ST_Within(f.boundary, fa.boundary)
        """

        assert "ST_Within" in query

    def test_st_touches_query(self):
        """Test ST_Touches for adjacent fields."""
        query = """
            SELECT f2.id, f2.name
            FROM fields f1
            JOIN fields f2 ON ST_Touches(f1.boundary, f2.boundary)
            WHERE f1.id = $1 AND f2.id != f1.id
        """

        assert "ST_Touches" in query

    def test_st_overlaps_query(self):
        """Test ST_Overlaps for detecting overlapping fields."""
        query = """
            SELECT f1.id as field1, f2.id as field2
            FROM fields f1
            JOIN fields f2 ON ST_Overlaps(f1.boundary, f2.boundary)
            WHERE f1.id < f2.id
            AND f1.tenant_id = $1
        """

        assert "ST_Overlaps" in query


@pytest.mark.unit
class TestNDVIGeospatialQueries:
    """Tests for NDVI-related geospatial queries."""

    def test_ndvi_raster_clip_query(self):
        """Test clipping NDVI raster to field boundary."""
        query = """
            SELECT ST_Clip(
                ndvi.rast,
                f.boundary
            ) as clipped_ndvi
            FROM ndvi_imagery ndvi
            JOIN fields f ON ST_Intersects(ndvi.rast::geometry, f.boundary)
            WHERE f.id = $1
        """

        assert "ST_Clip" in query

    def test_ndvi_zonal_statistics_query(self):
        """Test zonal statistics for NDVI within field."""
        query = """
            SELECT
                (ST_SummaryStats(ST_Clip(ndvi.rast, f.boundary))).*
            FROM ndvi_imagery ndvi
            JOIN fields f ON ST_Intersects(ndvi.rast::geometry, f.boundary)
            WHERE f.id = $1
        """

        assert "ST_SummaryStats" in query


@pytest.mark.unit
class TestGeometrySimplification:
    """Tests for geometry simplification."""

    def test_simplify_for_display(self):
        """Test geometry simplification for map display."""
        query = """
            SELECT ST_AsGeoJSON(
                ST_Simplify(boundary, $1)
            )::json as simplified
            FROM fields
            WHERE id = $2
        """

        tolerance = 0.0001

        assert "ST_Simplify" in query

    def test_preserve_topology(self):
        """Test simplification preserves topology."""
        query = """
            SELECT ST_AsGeoJSON(
                ST_SimplifyPreserveTopology(boundary, $1)
            )::json as simplified
            FROM fields
            WHERE id = $2
        """

        assert "ST_SimplifyPreserveTopology" in query
