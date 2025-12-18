"""
SAHOOL Spatial Hierarchy Integration Tests
Tests for GIS hierarchy: Farm → Field → Zone → SubZone

Note: These tests require PostGIS. They are marked with pytest.mark.postgis
and will be skipped if PostGIS is not available.
"""

from __future__ import annotations

import pytest
from uuid import uuid4

from field_suite.zones.models import Zone, SubZone, ZoneBoundary, ZoneType


# ---------------------------------------------------------------------------
# ZoneBoundary Tests (No PostGIS required)
# ---------------------------------------------------------------------------


class TestZoneBoundary:
    """Test ZoneBoundary model"""

    def test_from_coordinates(self):
        """Create boundary from coordinates calculates center"""
        coords = [
            (30.0, 31.0),  # (lat, lon)
            (30.0, 32.0),
            (31.0, 32.0),
            (31.0, 31.0),
        ]
        boundary = ZoneBoundary.from_coordinates(coords)

        assert boundary.center_latitude == 30.5
        assert boundary.center_longitude == 31.5
        assert len(boundary.coordinates) == 4

    def test_from_coordinates_empty_raises(self):
        """Empty coordinates raises ValueError"""
        with pytest.raises(ValueError, match="cannot be empty"):
            ZoneBoundary.from_coordinates([])

    def test_to_wkt(self):
        """Boundary converts to WKT POLYGON format"""
        coords = [
            (30.0, 31.0),
            (30.0, 32.0),
            (31.0, 32.0),
            (31.0, 31.0),
        ]
        boundary = ZoneBoundary.from_coordinates(coords)
        wkt = boundary.to_wkt()

        assert wkt.startswith("POLYGON((")
        # Check lon lat format (handles both integer and decimal formats)
        assert ("31 30" in wkt or "31.0 30.0" in wkt)  # lon lat format
        assert wkt.endswith("))")

    def test_to_wkt_closes_polygon(self):
        """WKT ensures polygon is closed"""
        coords = [
            (30.0, 31.0),
            (30.0, 32.0),
            (31.0, 32.0),
            (31.0, 31.0),
        ]
        boundary = ZoneBoundary.from_coordinates(coords)
        wkt = boundary.to_wkt()

        # First and last coordinate should be the same
        # POLYGON((31 30, 32 30, 32 31, 31 31, 31 30))
        coord_part = wkt.replace("POLYGON((", "").replace("))", "")
        points = coord_part.split(", ")
        assert points[0] == points[-1]

    def test_from_wkt_parses_polygon(self):
        """Parse WKT POLYGON to ZoneBoundary"""
        wkt = "POLYGON((31 30, 32 30, 32 31, 31 31, 31 30))"
        boundary = ZoneBoundary.from_wkt(wkt)

        assert len(boundary.coordinates) == 5  # Including closing point
        assert boundary.center_latitude == pytest.approx(30.4, abs=0.1)
        assert boundary.center_longitude == pytest.approx(31.4, abs=0.1)

    def test_from_wkt_invalid_raises(self):
        """Invalid WKT raises ValueError"""
        with pytest.raises(ValueError, match="Invalid WKT"):
            ZoneBoundary.from_wkt("NOT A POLYGON")

    def test_to_dict(self):
        """Boundary serializes to dictionary"""
        coords = [(30.0, 31.0), (30.0, 32.0), (31.0, 32.0)]
        boundary = ZoneBoundary.from_coordinates(coords)
        data = boundary.to_dict()

        assert "coordinates" in data
        assert "center_latitude" in data
        assert "center_longitude" in data


# ---------------------------------------------------------------------------
# Zone Model Tests
# ---------------------------------------------------------------------------


class TestZoneModel:
    """Test Zone domain model"""

    def test_create_zone(self):
        """Create zone with factory method"""
        tenant_id = str(uuid4())
        field_id = str(uuid4())

        coords = [(30.0, 31.0), (30.0, 32.0), (31.0, 32.0), (31.0, 31.0)]
        boundary = ZoneBoundary.from_coordinates(coords)

        zone = Zone.create(
            tenant_id=tenant_id,
            field_id=field_id,
            name="North Irrigation Zone",
            zone_type=ZoneType.IRRIGATION,
            boundary=boundary,
            area_hectares=10.5,
            properties={"irrigation_schedule": "daily"},
        )

        assert zone.id is not None
        assert zone.tenant_id == tenant_id
        assert zone.field_id == field_id
        assert zone.name == "North Irrigation Zone"
        assert zone.zone_type == ZoneType.IRRIGATION
        assert zone.area_hectares == 10.5
        assert zone.properties["irrigation_schedule"] == "daily"
        assert zone.created_at is not None

    def test_zone_to_dict(self):
        """Zone serializes to dictionary"""
        coords = [(30.0, 31.0), (30.0, 32.0), (31.0, 32.0)]
        boundary = ZoneBoundary.from_coordinates(coords)

        zone = Zone.create(
            tenant_id=str(uuid4()),
            field_id=str(uuid4()),
            name="Test Zone",
            zone_type=ZoneType.NDVI_CLUSTER,
            boundary=boundary,
            area_hectares=5.0,
        )

        data = zone.to_dict()

        assert data["name"] == "Test Zone"
        assert data["zone_type"] == "ndvi_cluster"
        assert data["area_hectares"] == 5.0
        assert "boundary" in data
        assert "created_at" in data

    def test_zone_types(self):
        """All zone types are valid"""
        valid_types = [
            ZoneType.IRRIGATION,
            ZoneType.SOIL_TYPE,
            ZoneType.NDVI_CLUSTER,
            ZoneType.YIELD_ZONE,
            ZoneType.MANAGEMENT,
            ZoneType.CUSTOM,
        ]

        for zt in valid_types:
            assert zt.value in [
                "irrigation",
                "soil_type",
                "ndvi_cluster",
                "yield_zone",
                "management",
                "custom",
            ]


# ---------------------------------------------------------------------------
# SubZone Model Tests
# ---------------------------------------------------------------------------


class TestSubZoneModel:
    """Test SubZone domain model"""

    def test_create_subzone(self):
        """Create sub-zone with factory method"""
        tenant_id = str(uuid4())
        zone_id = str(uuid4())

        coords = [(30.0, 31.0), (30.0, 31.5), (30.5, 31.5), (30.5, 31.0)]
        boundary = ZoneBoundary.from_coordinates(coords)

        subzone = SubZone.create(
            tenant_id=tenant_id,
            zone_id=zone_id,
            name="VRA Block A1",
            boundary=boundary,
            area_hectares=2.5,
            properties={"sensor_ids": ["sensor-001", "sensor-002"]},
        )

        assert subzone.id is not None
        assert subzone.tenant_id == tenant_id
        assert subzone.zone_id == zone_id
        assert subzone.name == "VRA Block A1"
        assert subzone.area_hectares == 2.5
        assert "sensor_ids" in subzone.properties

    def test_subzone_to_dict(self):
        """SubZone serializes to dictionary"""
        coords = [(30.0, 31.0), (30.0, 31.5), (30.5, 31.5)]
        boundary = ZoneBoundary.from_coordinates(coords)

        subzone = SubZone.create(
            tenant_id=str(uuid4()),
            zone_id=str(uuid4()),
            name="Test SubZone",
            boundary=boundary,
            area_hectares=1.0,
        )

        data = subzone.to_dict()

        assert data["name"] == "Test SubZone"
        assert "zone_id" in data
        assert "boundary" in data


# ---------------------------------------------------------------------------
# Geometry Validation Tests (Unit level, no DB required)
# ---------------------------------------------------------------------------


class TestGeometryValidation:
    """Test geometry validation utilities"""

    def test_geometry_validation_report_default_values(self):
        """GeometryValidationReport has correct defaults"""
        from field_suite.spatial.validation import GeometryValidationReport

        report = GeometryValidationReport()

        assert report.fields_checked == 0
        assert report.fields_fixed == 0
        assert report.zones_checked == 0
        assert report.zones_fixed == 0
        assert report.subzones_checked == 0
        assert report.subzones_fixed == 0
        assert report.total_checked == 0
        assert report.total_fixed == 0
        assert report.success is True
        assert len(report.errors) == 0

    def test_geometry_validation_report_totals(self):
        """Report calculates totals correctly"""
        from field_suite.spatial.validation import GeometryValidationReport

        report = GeometryValidationReport()
        report.fields_checked = 100
        report.fields_invalid = 5
        report.fields_fixed = 5
        report.zones_checked = 50
        report.zones_invalid = 2
        report.zones_fixed = 2
        report.subzones_checked = 25
        report.subzones_invalid = 1
        report.subzones_fixed = 1

        assert report.total_checked == 175
        assert report.total_invalid == 8
        assert report.total_fixed == 8

    def test_geometry_validation_report_to_dict(self):
        """Report serializes to dictionary"""
        from field_suite.spatial.validation import GeometryValidationReport

        report = GeometryValidationReport()
        report.fields_checked = 10
        report.fields_fixed = 2

        data = report.to_dict()

        assert "fields" in data
        assert data["fields"]["checked"] == 10
        assert data["fields"]["fixed"] == 2
        assert "totals" in data
        assert "success" in data


# ---------------------------------------------------------------------------
# PostGIS Integration Tests (require PostGIS)
# ---------------------------------------------------------------------------


@pytest.mark.skip(reason="Enable when PostGIS test DB is configured")
class TestPostGISIntegration:
    """Integration tests requiring PostGIS database"""

    def test_fields_in_bbox_uses_spatial_index(self, db_session):
        """fields_in_bbox query uses GIST index"""
        from field_suite.spatial.queries import fields_in_bbox

        tenant_id = uuid4()

        # Query should work even with empty results
        results = fields_in_bbox(
            db_session,
            tenant_id=tenant_id,
            xmin=30.0,
            ymin=30.0,
            xmax=32.0,
            ymax=32.0,
        )

        assert isinstance(results, list)

    def test_calculate_area_hectares(self, db_session):
        """Area calculation returns correct value"""
        from field_suite.spatial.queries import calculate_area_hectares

        # Simple 1-degree square at equator
        wkt = "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"

        area = calculate_area_hectares(db_session, geometry_wkt=wkt)

        # ~12,365 km² = ~1,236,500 hectares for 1° square at equator
        assert area > 1_000_000  # Should be > 1M hectares

    def test_find_containing_field(self, db_session):
        """Point-in-polygon query works"""
        from field_suite.spatial.queries import find_containing_field

        tenant_id = uuid4()

        # Should return None for point in empty DB
        result = find_containing_field(
            db_session,
            tenant_id=tenant_id,
            latitude=30.5,
            longitude=31.5,
        )

        assert result is None

    def test_validate_and_fix_geometries_dry_run(self, db_session):
        """Validation job dry run reports without modifying"""
        from field_suite.spatial.validation import validate_and_fix_geometries

        report = validate_and_fix_geometries(db_session, dry_run=True)

        assert report.success is True
        assert report.completed_at is not None


# ---------------------------------------------------------------------------
# Spatial ORM Model Tests
# ---------------------------------------------------------------------------


class TestSpatialORMModels:
    """Test spatial ORM model definitions"""

    def test_field_orm_has_required_columns(self):
        """FieldORM model has all required columns"""
        from field_suite.spatial.orm_models import FieldORM

        # Check column names exist
        columns = {c.name for c in FieldORM.__table__.columns}

        assert "id" in columns
        assert "tenant_id" in columns
        assert "farm_id" in columns
        assert "name" in columns
        assert "geometry_wkt" in columns
        assert "area_hectares" in columns

    def test_zone_orm_has_required_columns(self):
        """ZoneORM model has all required columns"""
        from field_suite.spatial.orm_models import ZoneORM

        columns = {c.name for c in ZoneORM.__table__.columns}

        assert "id" in columns
        assert "tenant_id" in columns
        assert "field_id" in columns
        assert "zone_type" in columns
        assert "geometry_wkt" in columns
        assert "properties" in columns

    def test_subzone_orm_has_required_columns(self):
        """SubZoneORM model has all required columns"""
        from field_suite.spatial.orm_models import SubZoneORM

        columns = {c.name for c in SubZoneORM.__table__.columns}

        assert "id" in columns
        assert "tenant_id" in columns
        assert "zone_id" in columns
        assert "geometry_wkt" in columns
        assert "properties" in columns

    def test_farm_to_field_relationship(self):
        """Farm→Field relationship is defined"""
        from field_suite.spatial.orm_models import FarmORM, FieldORM

        # Check relationship exists
        assert hasattr(FarmORM, "fields")
        assert hasattr(FieldORM, "farm")

    def test_field_to_zone_relationship(self):
        """Field→Zone relationship is defined"""
        from field_suite.spatial.orm_models import FieldORM, ZoneORM

        assert hasattr(FieldORM, "zones")
        assert hasattr(ZoneORM, "field")

    def test_zone_to_subzone_relationship(self):
        """Zone→SubZone relationship is defined"""
        from field_suite.spatial.orm_models import ZoneORM, SubZoneORM

        assert hasattr(ZoneORM, "sub_zones")
        assert hasattr(SubZoneORM, "zone")
