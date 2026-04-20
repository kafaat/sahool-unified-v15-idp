"""
Unit tests for shared/geofencing module.
Tests geofence models, enums, engine logic (point-in-polygon, distance),
alert generation, bilingual labels, and theft detection.
"""

import math
import pytest
from datetime import UTC, datetime, timedelta

from shared.geofencing.models import (
    AlertSeverity,
    AlertType,
    EquipmentZoneStatus,
    Geofence,
    GeofenceAlert,
    GeofenceType,
    LatLng,
    PositionUpdate,
    ZoneStatus,
)
from shared.geofencing.engine import (
    EARTH_RADIUS_M,
    GeofenceEngine,
    calculate_distance_to_boundary,
    check_position_in_geofence,
    create_circular_geofence,
    create_polygon_geofence,
    haversine_distance,
    point_in_polygon,
    distance_to_polygon_boundary,
    point_to_line_distance,
)
from shared.geofencing.alerts import (
    generate_entry_alert,
    generate_exit_alert,
    generate_speed_alert,
    generate_theft_alert,
    generate_daily_summary,
)


# =============================================================================
# Helpers
# =============================================================================

# A simple square polygon around (24.7, 46.7) -- roughly Riyadh area
SQUARE_BOUNDARY = [
    LatLng(lat=24.6, lng=46.6),
    LatLng(lat=24.6, lng=46.8),
    LatLng(lat=24.8, lng=46.8),
    LatLng(lat=24.8, lng=46.6),
]

NOW = datetime.now(UTC)


def _make_circular_geofence(**kwargs) -> Geofence:
    defaults = {
        "id": "geo_circ01",
        "tenant_id": "tenant_001",
        "name": "Main Farm",
        "name_ar": "المزرعة الرئيسية",
        "geofence_type": GeofenceType.ALLOWED,
        "center": LatLng(lat=24.7, lng=46.7),
        "radius_m": 1000.0,
    }
    defaults.update(kwargs)
    return Geofence(**defaults)


def _make_polygon_geofence(**kwargs) -> Geofence:
    defaults = {
        "id": "geo_poly01",
        "tenant_id": "tenant_001",
        "name": "Field A",
        "name_ar": "الحقل أ",
        "geofence_type": GeofenceType.FIELD,
        "boundary": SQUARE_BOUNDARY,
    }
    defaults.update(kwargs)
    return Geofence(**defaults)


def _make_position(
    lat=24.7,
    lng=46.7,
    equipment_id="equip_001",
    tenant_id="tenant_001",
    speed_kmh=None,
    timestamp=None,
    prev_lat=None,
    prev_lng=None,
    prev_timestamp=None,
    engine_on=None,
) -> PositionUpdate:
    return PositionUpdate(
        equipment_id=equipment_id,
        tenant_id=tenant_id,
        timestamp=timestamp or NOW,
        lat=lat,
        lng=lng,
        speed_kmh=speed_kmh,
        prev_lat=prev_lat,
        prev_lng=prev_lng,
        prev_timestamp=prev_timestamp,
        engine_on=engine_on,
    )


# =============================================================================
# Enum Tests
# =============================================================================


@pytest.mark.unit
class TestEnums:
    """Test all geofencing enum types and their string values."""

    def test_geofence_type_values(self):
        assert GeofenceType.ALLOWED == "allowed"
        assert GeofenceType.RESTRICTED == "restricted"
        assert GeofenceType.SENSITIVE == "sensitive"
        assert GeofenceType.PARKING == "parking"
        assert GeofenceType.FIELD == "field"
        assert GeofenceType.FARM_BOUNDARY == "farm_boundary"

    def test_alert_type_values(self):
        assert AlertType.EXIT == "exit"
        assert AlertType.ENTRY == "entry"
        assert AlertType.SPEEDING == "speeding"
        assert AlertType.THEFT == "theft"
        assert AlertType.IDLE == "idle"
        assert AlertType.UNAUTHORIZED_MOVE == "unauthorized_move"

    def test_alert_severity_values(self):
        assert AlertSeverity.LOW == "low"
        assert AlertSeverity.MEDIUM == "medium"
        assert AlertSeverity.HIGH == "high"
        assert AlertSeverity.CRITICAL == "critical"

    def test_zone_status_values(self):
        assert ZoneStatus.INSIDE == "inside"
        assert ZoneStatus.OUTSIDE == "outside"
        assert ZoneStatus.APPROACHING == "approaching"
        assert ZoneStatus.LEAVING == "leaving"


# =============================================================================
# LatLng Tests
# =============================================================================


@pytest.mark.unit
class TestLatLng:
    """Test the LatLng data class."""

    def test_creation(self):
        ll = LatLng(lat=24.7, lng=46.7)
        assert ll.lat == 24.7
        assert ll.lng == 46.7

    def test_to_tuple(self):
        ll = LatLng(lat=24.7, lng=46.7)
        assert ll.to_tuple() == (24.7, 46.7)

    def test_to_dict(self):
        ll = LatLng(lat=24.7, lng=46.7)
        d = ll.to_dict()
        assert d == {"lat": 24.7, "lng": 46.7}


# =============================================================================
# Geofence Model Tests
# =============================================================================


@pytest.mark.unit
class TestGeofenceModel:
    """Test the Geofence dataclass."""

    def test_circular_geofence_creation(self):
        gf = _make_circular_geofence()
        assert gf.id == "geo_circ01"
        assert gf.name == "Main Farm"
        assert gf.name_ar == "المزرعة الرئيسية"
        assert gf.geofence_type == GeofenceType.ALLOWED
        assert gf.center is not None
        assert gf.radius_m == 1000.0
        assert gf.boundary is None

    def test_polygon_geofence_creation(self):
        gf = _make_polygon_geofence()
        assert gf.boundary is not None
        assert len(gf.boundary) == 4
        assert gf.center is None
        assert gf.radius_m is None

    def test_defaults(self):
        gf = _make_circular_geofence()
        assert gf.alert_on_exit is True
        assert gf.alert_on_entry is False
        assert gf.alert_channels == ["push", "sms"]
        assert gf.buffer_distance_m == 50
        assert gf.is_active is True
        assert gf.max_speed_kmh is None

    def test_to_dict_circular(self):
        gf = _make_circular_geofence()
        d = gf.to_dict()
        assert d["id"] == "geo_circ01"
        assert d["geofence_type"] == "allowed"
        assert d["center"] == {"lat": 24.7, "lng": 46.7}
        assert d["radius_m"] == 1000.0
        assert d["boundary"] is None

    def test_to_dict_polygon(self):
        gf = _make_polygon_geofence()
        d = gf.to_dict()
        assert d["boundary"] is not None
        assert len(d["boundary"]) == 4
        assert d["center"] is None


# =============================================================================
# PositionUpdate Tests
# =============================================================================


@pytest.mark.unit
class TestPositionUpdate:
    """Test the PositionUpdate dataclass."""

    def test_creation(self):
        pos = _make_position(lat=24.71, lng=46.71, speed_kmh=25.0)
        assert pos.equipment_id == "equip_001"
        assert pos.lat == 24.71
        assert pos.lng == 46.71
        assert pos.speed_kmh == 25.0

    def test_defaults(self):
        pos = _make_position()
        assert pos.accuracy_m is None
        assert pos.heading_degrees is None
        assert pos.engine_on is None
        assert pos.fuel_percent is None
        assert pos.prev_lat is None


# =============================================================================
# GeofenceAlert Tests
# =============================================================================


@pytest.mark.unit
class TestGeofenceAlertModel:
    """Test the GeofenceAlert dataclass and bilingual labels."""

    def test_creation_and_bilingual(self):
        alert = GeofenceAlert(
            alert_id="alert_001",
            tenant_id="tenant_001",
            equipment_id="equip_001",
            equipment_name="Tractor A",
            equipment_name_ar="الجرار أ",
            alert_type=AlertType.EXIT,
            severity=AlertSeverity.HIGH,
            timestamp=NOW,
            geofence_id="geo_001",
            geofence_name="Main Farm",
            geofence_name_ar="المزرعة الرئيسية",
            lat=24.7,
            lng=46.7,
            title_en="Equipment Left Zone",
            title_ar="المعدة غادرت المنطقة",
            message_en="Tractor A left Main Farm",
            message_ar="الجرار أ غادر المزرعة الرئيسية",
        )
        assert alert.title_en == "Equipment Left Zone"
        assert alert.title_ar == "المعدة غادرت المنطقة"
        assert alert.equipment_name_ar == "الجرار أ"
        assert alert.geofence_name_ar == "المزرعة الرئيسية"

    def test_to_dict(self):
        alert = GeofenceAlert(
            alert_id="alert_002",
            tenant_id="tenant_001",
            equipment_id="equip_001",
            equipment_name="Harvester",
            equipment_name_ar="الحصادة",
            alert_type=AlertType.SPEEDING,
            severity=AlertSeverity.MEDIUM,
            timestamp=NOW,
            geofence_id="geo_001",
            geofence_name="Field B",
            geofence_name_ar="الحقل ب",
            lat=24.72,
            lng=46.72,
            speed_kmh=45.0,
        )
        d = alert.to_dict()
        assert d["alert_type"] == "speeding"
        assert d["severity"] == "medium"
        assert d["position"] == {"lat": 24.72, "lng": 46.72}
        assert d["speed_kmh"] == 45.0
        assert d["acknowledged"] is False

    def test_acknowledge_defaults(self):
        alert = GeofenceAlert(
            alert_id="a1",
            tenant_id="t1",
            equipment_id="e1",
            equipment_name="",
            equipment_name_ar="",
            alert_type=AlertType.EXIT,
            severity=AlertSeverity.HIGH,
            timestamp=NOW,
            geofence_id="g1",
            geofence_name="",
            geofence_name_ar="",
            lat=0,
            lng=0,
        )
        assert alert.acknowledged is False
        assert alert.acknowledged_by is None
        assert alert.acknowledged_at is None


# =============================================================================
# EquipmentZoneStatus Tests
# =============================================================================


@pytest.mark.unit
class TestEquipmentZoneStatus:
    """Test the EquipmentZoneStatus dataclass."""

    def test_defaults(self):
        status = EquipmentZoneStatus(
            equipment_id="equip_001",
            equipment_name="Tractor",
            timestamp=NOW,
            lat=24.7,
            lng=46.7,
        )
        assert status.is_within_allowed_zones is True
        assert status.is_in_restricted_zone is False
        assert status.nearest_boundary_distance_m is None
        assert status.active_alerts == []
        assert status.zones == []


# =============================================================================
# Haversine Distance Tests
# =============================================================================


@pytest.mark.unit
class TestHaversineDistance:
    """Test haversine distance calculations."""

    def test_same_point(self):
        d = haversine_distance(24.7, 46.7, 24.7, 46.7)
        assert d == 0.0

    def test_known_distance(self):
        # Riyadh to Jeddah is approximately 850 km
        d = haversine_distance(24.7136, 46.6753, 21.4858, 39.1925)
        assert 830_000 < d < 870_000

    def test_small_distance(self):
        # Approximately 1 degree lat ~ 111 km
        d = haversine_distance(24.0, 46.0, 25.0, 46.0)
        assert 110_000 < d < 112_000

    def test_symmetric(self):
        d1 = haversine_distance(24.7, 46.7, 25.0, 47.0)
        d2 = haversine_distance(25.0, 47.0, 24.7, 46.7)
        assert abs(d1 - d2) < 0.01


# =============================================================================
# Point-in-Polygon Tests
# =============================================================================


@pytest.mark.unit
class TestPointInPolygon:
    """Test ray-casting point-in-polygon algorithm."""

    def test_point_inside_square(self):
        assert point_in_polygon(24.7, 46.7, SQUARE_BOUNDARY) is True

    def test_point_outside_square(self):
        assert point_in_polygon(25.0, 47.0, SQUARE_BOUNDARY) is False

    def test_point_near_edge_outside(self):
        # Just outside the south edge (lat=24.6)
        assert point_in_polygon(24.5, 46.7, SQUARE_BOUNDARY) is False

    def test_degenerate_polygon_too_few_points(self):
        two_points = [LatLng(lat=0, lng=0), LatLng(lat=1, lng=1)]
        assert point_in_polygon(0.5, 0.5, two_points) is False

    def test_triangle(self):
        triangle = [
            LatLng(lat=0, lng=0),
            LatLng(lat=0, lng=10),
            LatLng(lat=10, lng=5),
        ]
        # Center-ish should be inside
        assert point_in_polygon(3, 5, triangle) is True
        # Clearly outside
        assert point_in_polygon(11, 5, triangle) is False


# =============================================================================
# Distance to Polygon Boundary Tests
# =============================================================================


@pytest.mark.unit
class TestDistanceToPolygonBoundary:
    """Test distance from a point to polygon boundary."""

    def test_returns_inf_for_single_point(self):
        result = distance_to_polygon_boundary(24.7, 46.7, [LatLng(0, 0)])
        assert result == float("inf")

    def test_inside_point_has_positive_distance(self):
        # Point in center of square should have positive distance to boundary
        d = distance_to_polygon_boundary(24.7, 46.7, SQUARE_BOUNDARY)
        assert d > 0

    def test_outside_point_has_positive_distance(self):
        d = distance_to_polygon_boundary(25.0, 47.0, SQUARE_BOUNDARY)
        assert d > 0


# =============================================================================
# Point-to-Line Distance Tests
# =============================================================================


@pytest.mark.unit
class TestPointToLineDistance:
    """Test point-to-line-segment distance."""

    def test_zero_length_segment(self):
        d = point_to_line_distance(1.0, 1.0, 0.0, 0.0, 0.0, 0.0)
        # Should return haversine distance from (1,1) to (0,0)
        expected = haversine_distance(1.0, 1.0, 0.0, 0.0)
        assert abs(d - expected) < 0.01


# =============================================================================
# Check Position in Geofence Tests
# =============================================================================


@pytest.mark.unit
class TestCheckPositionInGeofence:
    """Test combined check_position_in_geofence function."""

    def test_inside_circular(self):
        gf = _make_circular_geofence(radius_m=5000.0)
        is_inside, dist = check_position_in_geofence(24.7, 46.7, gf)
        assert is_inside is True
        # At center, distance to boundary should be ~radius
        assert abs(dist - 5000.0) < 1.0

    def test_outside_circular(self):
        gf = _make_circular_geofence(radius_m=100.0)
        # ~11 km away
        is_inside, dist = check_position_in_geofence(24.8, 46.8, gf)
        assert is_inside is False

    def test_inside_polygon(self):
        gf = _make_polygon_geofence()
        is_inside, dist = check_position_in_geofence(24.7, 46.7, gf)
        assert is_inside is True
        assert dist > 0

    def test_outside_polygon(self):
        gf = _make_polygon_geofence()
        is_inside, dist = check_position_in_geofence(25.0, 47.0, gf)
        assert is_inside is False

    def test_no_geometry_returns_false(self):
        gf = Geofence(
            id="empty",
            tenant_id="t1",
            name="Empty",
            name_ar="فارغ",
            geofence_type=GeofenceType.ALLOWED,
        )
        is_inside, dist = check_position_in_geofence(24.7, 46.7, gf)
        assert is_inside is False
        assert dist == float("inf")


# =============================================================================
# Create Geofence Helper Tests
# =============================================================================


@pytest.mark.unit
class TestCreateGeofenceHelpers:
    """Test create_circular_geofence and create_polygon_geofence."""

    def test_create_circular(self):
        gf = create_circular_geofence(
            tenant_id="t1",
            name="Parking Zone",
            name_ar="منطقة الوقوف",
            center_lat=24.7,
            center_lng=46.7,
            radius_m=200.0,
            geofence_type=GeofenceType.PARKING,
        )
        assert gf.id.startswith("geo_")
        assert gf.tenant_id == "t1"
        assert gf.name == "Parking Zone"
        assert gf.name_ar == "منطقة الوقوف"
        assert gf.center.lat == 24.7
        assert gf.radius_m == 200.0
        assert gf.geofence_type == GeofenceType.PARKING

    def test_create_polygon(self):
        boundary_tuples = [(24.6, 46.6), (24.6, 46.8), (24.8, 46.8), (24.8, 46.6)]
        gf = create_polygon_geofence(
            tenant_id="t1",
            name="Restricted Area",
            name_ar="منطقة مقيدة",
            boundary=boundary_tuples,
            geofence_type=GeofenceType.RESTRICTED,
        )
        assert gf.id.startswith("geo_")
        assert gf.geofence_type == GeofenceType.RESTRICTED
        assert len(gf.boundary) == 4
        assert isinstance(gf.boundary[0], LatLng)

    def test_create_circular_default_type(self):
        gf = create_circular_geofence(
            tenant_id="t1",
            name="Default",
            name_ar="افتراضي",
            center_lat=0,
            center_lng=0,
            radius_m=100,
        )
        assert gf.geofence_type == GeofenceType.ALLOWED


# =============================================================================
# GeofenceEngine Tests
# =============================================================================


@pytest.mark.unit
class TestGeofenceEngine:
    """Test the GeofenceEngine class."""

    def _setup_engine(self) -> GeofenceEngine:
        engine = GeofenceEngine()
        gf = _make_circular_geofence(
            radius_m=5000.0,
            geofence_type=GeofenceType.FARM_BOUNDARY,
            alert_on_exit=True,
            alert_on_entry=False,
        )
        engine.add_geofence(gf)
        return engine

    def test_add_and_get_geofence(self):
        engine = GeofenceEngine()
        gf = _make_circular_geofence()
        gf_id = engine.add_geofence(gf)
        assert gf_id == "geo_circ01"
        assert engine.get_geofence("geo_circ01") is gf

    def test_remove_geofence(self):
        engine = GeofenceEngine()
        gf = _make_circular_geofence()
        engine.add_geofence(gf)
        assert engine.remove_geofence("geo_circ01") is True
        assert engine.get_geofence("geo_circ01") is None

    def test_remove_nonexistent(self):
        engine = GeofenceEngine()
        assert engine.remove_geofence("nonexistent") is False

    def test_get_geofences_for_equipment(self):
        engine = GeofenceEngine()
        gf1 = _make_circular_geofence(id="gf1", equipment_ids=["equip_001"])
        gf2 = _make_circular_geofence(id="gf2", equipment_ids=["equip_002"])
        gf3 = _make_circular_geofence(id="gf3", equipment_ids=[])  # tenant-wide
        engine.add_geofence(gf1)
        engine.add_geofence(gf2)
        engine.add_geofence(gf3)

        result = engine.get_geofences_for_equipment("equip_001")
        ids = [g.id for g in result]
        assert "gf1" in ids
        assert "gf3" in ids  # tenant-wide included
        assert "gf2" not in ids

    def test_update_position_no_alert_when_inside(self):
        engine = self._setup_engine()
        # Position inside the geofence
        pos = _make_position(lat=24.7, lng=46.7)
        alerts = engine.update_position(pos)
        assert len(alerts) == 0

    def test_exit_alert_on_transition(self):
        engine = self._setup_engine()

        # First position: inside
        pos1 = _make_position(lat=24.7, lng=46.7, timestamp=NOW - timedelta(minutes=5))
        engine.update_position(pos1)

        # Second position: outside (far away)
        pos2 = _make_position(lat=25.5, lng=47.5, timestamp=NOW)
        alerts = engine.update_position(pos2)

        exit_alerts = [a for a in alerts if a.alert_type == AlertType.EXIT]
        assert len(exit_alerts) >= 1
        assert exit_alerts[0].severity == AlertSeverity.CRITICAL  # FARM_BOUNDARY => CRITICAL

    def test_entry_alert_on_restricted_zone(self):
        engine = GeofenceEngine()
        gf = _make_circular_geofence(
            id="restricted_01",
            radius_m=5000.0,
            geofence_type=GeofenceType.RESTRICTED,
            alert_on_exit=False,
            alert_on_entry=True,
        )
        engine.add_geofence(gf)

        # First position: outside
        pos1 = _make_position(lat=25.5, lng=47.5, timestamp=NOW - timedelta(minutes=5))
        engine.update_position(pos1)

        # Second position: inside
        pos2 = _make_position(lat=24.7, lng=46.7, timestamp=NOW)
        alerts = engine.update_position(pos2)

        entry_alerts = [a for a in alerts if a.alert_type == AlertType.ENTRY]
        assert len(entry_alerts) >= 1
        assert entry_alerts[0].severity == AlertSeverity.HIGH  # RESTRICTED => HIGH

    def test_entry_alert_sensitive_zone_is_critical(self):
        engine = GeofenceEngine()
        gf = _make_circular_geofence(
            id="sensitive_01",
            radius_m=5000.0,
            geofence_type=GeofenceType.SENSITIVE,
            alert_on_exit=False,
            alert_on_entry=True,
        )
        engine.add_geofence(gf)

        pos1 = _make_position(lat=25.5, lng=47.5, timestamp=NOW - timedelta(minutes=5))
        engine.update_position(pos1)
        pos2 = _make_position(lat=24.7, lng=46.7, timestamp=NOW)
        alerts = engine.update_position(pos2)

        entry_alerts = [a for a in alerts if a.alert_type == AlertType.ENTRY]
        assert len(entry_alerts) >= 1
        assert entry_alerts[0].severity == AlertSeverity.CRITICAL

    def test_speed_alert(self):
        engine = GeofenceEngine()
        gf = _make_circular_geofence(
            radius_m=50000.0,  # large zone
            max_speed_kmh=30.0,
        )
        engine.add_geofence(gf)

        pos = _make_position(lat=24.7, lng=46.7, speed_kmh=60.0)
        alerts = engine.update_position(pos)

        speed_alerts = [a for a in alerts if a.alert_type == AlertType.SPEEDING]
        assert len(speed_alerts) == 1
        assert "60.0" in speed_alerts[0].message_en
        assert "30" in speed_alerts[0].message_en

    def test_speed_alert_bilingual(self):
        engine = GeofenceEngine()
        gf = _make_circular_geofence(
            name="Zone X",
            name_ar="المنطقة س",
            radius_m=50000.0,
            max_speed_kmh=20.0,
        )
        engine.add_geofence(gf)

        pos = _make_position(lat=24.7, lng=46.7, speed_kmh=40.0)
        alerts = engine.update_position(pos)

        speed_alerts = [a for a in alerts if a.alert_type == AlertType.SPEEDING]
        assert len(speed_alerts) == 1
        assert "المنطقة س" in speed_alerts[0].title_ar
        assert "Zone X" in speed_alerts[0].title_en

    def test_acknowledge_alert(self):
        engine = self._setup_engine()

        # Generate an exit alert
        pos1 = _make_position(lat=24.7, lng=46.7, timestamp=NOW - timedelta(minutes=5))
        engine.update_position(pos1)
        pos2 = _make_position(lat=25.5, lng=47.5, timestamp=NOW)
        alerts = engine.update_position(pos2)

        assert len(alerts) > 0
        alert_id = alerts[0].alert_id

        result = engine.acknowledge_alert(alert_id, acknowledged_by="admin_user")
        assert result is True
        assert alerts[0].acknowledged is True
        assert alerts[0].acknowledged_by == "admin_user"
        assert alerts[0].acknowledged_at is not None

    def test_acknowledge_nonexistent_alert(self):
        engine = GeofenceEngine()
        assert engine.acknowledge_alert("fake_id", "admin") is False

    def test_get_unacknowledged_alerts(self):
        engine = self._setup_engine()

        pos1 = _make_position(lat=24.7, lng=46.7, timestamp=NOW - timedelta(minutes=5))
        engine.update_position(pos1)
        pos2 = _make_position(lat=25.5, lng=47.5, timestamp=NOW)
        engine.update_position(pos2)

        unacked = engine.get_unacknowledged_alerts("tenant_001")
        assert len(unacked) > 0

        # Filter by equipment
        unacked_filtered = engine.get_unacknowledged_alerts("tenant_001", equipment_id="equip_001")
        assert len(unacked_filtered) > 0

        # Non-matching equipment
        unacked_none = engine.get_unacknowledged_alerts("tenant_001", equipment_id="equip_999")
        assert len(unacked_none) == 0

    def test_get_equipment_status(self):
        engine = GeofenceEngine()
        gf_allowed = _make_circular_geofence(
            id="allowed_zone",
            radius_m=50000.0,
            geofence_type=GeofenceType.ALLOWED,
        )
        gf_restricted = _make_circular_geofence(
            id="restricted_zone",
            radius_m=50000.0,
            geofence_type=GeofenceType.RESTRICTED,
        )
        engine.add_geofence(gf_allowed)
        engine.add_geofence(gf_restricted)

        pos = _make_position(lat=24.7, lng=46.7)
        engine.update_position(pos)

        status = engine.get_equipment_status("equip_001", "Tractor A")
        assert status is not None
        assert status.equipment_id == "equip_001"
        assert status.is_within_allowed_zones is True
        assert status.is_in_restricted_zone is True  # same center, inside both
        assert len(status.zones) == 2
        assert status.nearest_boundary_distance_m is not None

    def test_get_equipment_status_unknown_equipment(self):
        engine = GeofenceEngine()
        assert engine.get_equipment_status("unknown", "Unknown") is None


# =============================================================================
# Theft Detection Tests
# =============================================================================


@pytest.mark.unit
class TestTheftDetection:
    """Test the theft detection logic in GeofenceEngine."""

    def test_theft_alert_outside_farm_boundary(self):
        engine = GeofenceEngine()
        farm = _make_circular_geofence(
            id="farm_01",
            radius_m=500.0,
            geofence_type=GeofenceType.FARM_BOUNDARY,
            alert_on_exit=False,  # disable normal exit alert for this test
        )
        engine.add_geofence(farm)

        # First position: just inside farm
        t1 = NOW - timedelta(minutes=10)
        pos1 = _make_position(lat=24.7, lng=46.7, timestamp=t1)
        engine.update_position(pos1)

        # Second position: far outside farm with significant movement
        t2 = NOW
        pos2 = _make_position(lat=25.0, lng=47.0, timestamp=t2)
        alerts = engine.update_position(pos2)

        theft_alerts = [a for a in alerts if a.alert_type == AlertType.THEFT]
        assert len(theft_alerts) >= 1
        assert theft_alerts[0].severity == AlertSeverity.CRITICAL
        assert "theft" in theft_alerts[0].title_en.lower()
        assert "سرقة" in theft_alerts[0].title_ar


# =============================================================================
# Alert Helper Function Tests
# =============================================================================


@pytest.mark.unit
class TestAlertHelpers:
    """Test the standalone alert generation functions in alerts.py."""

    def _sample_geofence(self, **kwargs) -> Geofence:
        defaults = {
            "id": "gf_test",
            "tenant_id": "t1",
            "name": "Test Zone",
            "name_ar": "منطقة الاختبار",
            "geofence_type": GeofenceType.ALLOWED,
            "center": LatLng(lat=24.7, lng=46.7),
            "radius_m": 1000.0,
        }
        defaults.update(kwargs)
        return Geofence(**defaults)

    def test_generate_exit_alert(self):
        gf = self._sample_geofence()
        alert = generate_exit_alert(
            equipment_id="eq1",
            equipment_name="Pump A",
            equipment_name_ar="المضخة أ",
            tenant_id="t1",
            geofence=gf,
            position=(24.8, 46.8),
            distance_to_boundary_m=150.0,
        )
        assert alert["alert_type"] == "geofence_exit"
        assert alert["alert_type_ar"] == "خروج من السياج الجغرافي"
        assert alert["priority"] == "high"
        assert "المعدة غادرت المنطقة" in alert["title_ar"]
        assert alert["equipment_name"] == "Pump A"
        assert alert["equipment_name_ar"] == "المضخة أ"
        assert alert["action_required"] is True
        assert len(alert["recommended_actions_en"]) == 3
        assert len(alert["recommended_actions_ar"]) == 3

    def test_generate_exit_alert_farm_boundary_critical(self):
        gf = self._sample_geofence(geofence_type=GeofenceType.FARM_BOUNDARY)
        alert = generate_exit_alert(
            equipment_id="eq1",
            equipment_name="Tractor",
            equipment_name_ar="الجرار",
            tenant_id="t1",
            geofence=gf,
            position=(25.0, 47.0),
            distance_to_boundary_m=500.0,
        )
        assert alert["priority"] == "critical"

    def test_generate_entry_alert(self):
        gf = self._sample_geofence(geofence_type=GeofenceType.RESTRICTED)
        alert = generate_entry_alert(
            equipment_id="eq1",
            equipment_name="Loader",
            equipment_name_ar="اللودر",
            tenant_id="t1",
            geofence=gf,
            position=(24.7, 46.7),
        )
        assert alert["alert_type"] == "geofence_entry"
        assert alert["alert_type_ar"] == "دخول للسياج الجغرافي"
        assert alert["priority"] == "high"
        assert "المعدة دخلت المنطقة" in alert["title_ar"]

    def test_generate_entry_alert_sensitive_critical(self):
        gf = self._sample_geofence(geofence_type=GeofenceType.SENSITIVE)
        alert = generate_entry_alert(
            equipment_id="eq1",
            equipment_name="Truck",
            equipment_name_ar="الشاحنة",
            tenant_id="t1",
            geofence=gf,
            position=(24.7, 46.7),
        )
        assert alert["priority"] == "critical"

    def test_generate_speed_alert(self):
        gf = self._sample_geofence(max_speed_kmh=25.0)
        alert = generate_speed_alert(
            equipment_id="eq1",
            equipment_name="Sprayer",
            equipment_name_ar="الرشاش",
            tenant_id="t1",
            geofence=gf,
            position=(24.7, 46.7),
            current_speed_kmh=55.0,
        )
        assert alert["alert_type"] == "speed_violation"
        assert alert["alert_type_ar"] == "تجاوز حد السرعة"
        assert alert["current_speed_kmh"] == 55.0
        assert alert["max_speed_kmh"] == 25.0
        assert alert["excess_speed_kmh"] == 30.0
        assert "تجاوز حد السرعة" in alert["title_ar"]

    def test_generate_theft_alert(self):
        reasons = ["Outside farm boundary", "Rapid movement outside allowed zones"]
        alert = generate_theft_alert(
            equipment_id="eq1",
            equipment_name="Generator",
            equipment_name_ar="المولد",
            tenant_id="t1",
            position=(25.0, 47.0),
            speed_kmh=80.0,
            reasons=reasons,
            last_known_zone="Main Farm",
        )
        assert alert["alert_type"] == "theft_suspected"
        assert alert["alert_type_ar"] == "اشتباه سرقة"
        assert alert["priority"] == "critical"
        assert alert["requires_acknowledgment"] is True
        assert alert["escalation_timeout_minutes"] == 5
        assert "call" in alert["channels"]
        assert "whatsapp" in alert["channels"]
        assert len(alert["recommended_actions_en"]) == 5
        assert len(alert["recommended_actions_ar"]) == 5
        # Check Arabic reason translations
        assert "خارج حدود المزرعة" in alert["reasons_ar"]
        assert "حركة سريعة خارج المناطق المسموحة" in alert["reasons_ar"]
        assert alert["emergency_contacts"]["police_sa"] == "911"

    def test_generate_daily_summary(self):
        summary = generate_daily_summary(
            tenant_id="t1",
            date=NOW,
            equipment_count=10,
            total_alerts=25,
            exit_alerts=8,
            entry_alerts=5,
            speed_alerts=10,
            theft_alerts=2,
            equipment_outside_zones=[{"equipment_id": "eq1", "zone": "Main Farm"}],
        )
        assert summary["report_type"] == "geofencing_daily_summary"
        assert summary["report_type_ar"] == "ملخص السياج الجغرافي اليومي"
        assert summary["statistics"]["equipment_monitored"] == 10
        assert summary["statistics"]["total_alerts"] == 25
        assert summary["statistics"]["alerts_by_type"]["theft"] == 2
        assert len(summary["equipment_outside_zones"]) == 1
        assert "تقرير السياج الجغرافي اليومي" in summary["title_ar"]
        # Bilingual summary text
        assert "10" in summary["summary_en"]
        assert "10" in summary["summary_ar"]


# =============================================================================
# calculate_distance_to_boundary wrapper test
# =============================================================================


@pytest.mark.unit
class TestCalculateDistanceToBoundary:
    """Test the calculate_distance_to_boundary convenience function."""

    def test_circular_distance(self):
        gf = _make_circular_geofence(radius_m=1000.0)
        # At center, distance to boundary = radius
        d = calculate_distance_to_boundary(24.7, 46.7, gf)
        assert abs(d - 1000.0) < 1.0
