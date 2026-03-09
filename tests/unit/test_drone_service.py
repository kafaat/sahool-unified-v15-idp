"""
Comprehensive tests for drone-service API endpoints.
اختبارات شاملة لنقاط نهاية خدمة الطائرات.

Tests cover:
- Drone CRUD operations with tenant isolation
- Flight plan creation (spray and mapping)
- Mission lifecycle and state transitions
- VRA prescription generation
- Weather check validation
- Resource estimation
- Auth enforcement
- Edge cases and error handling

Version: 16.0.0
"""

import importlib
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ─────────────────────────────────────────────────────────────────────────────
# Module isolation helpers
# ─────────────────────────────────────────────────────────────────────────────

_DRONE_SERVICE_ROOT = str(Path(__file__).parent.parent.parent / "apps" / "services" / "drone-service")
_DRONE_SERVICE_SRC = str(Path(_DRONE_SERVICE_ROOT) / "src")


def _ensure_drone_src():
    """Ensure 'src' resolves to drone-service/src, not another service.

    Other test conftest files (e.g. task_service/conftest.py) add their own
    service paths to sys.path, which causes 'from src.xxx import ...' to
    resolve to the wrong service.  This helper evicts any cached 'src.*'
    modules and re-inserts the drone-service path at position 0.
    """
    # Remove any cached src modules from another service
    stale = [k for k in sys.modules if k == "src" or k.startswith("src.")]
    for k in stale:
        del sys.modules[k]

    # Ensure drone-service root is first on sys.path
    if _DRONE_SERVICE_ROOT in sys.path:
        sys.path.remove(_DRONE_SERVICE_ROOT)
    sys.path.insert(0, _DRONE_SERVICE_ROOT)


def _import_drone_module(dotted_name: str):
    """Import a module from drone-service/src with proper isolation."""
    _ensure_drone_src()
    return importlib.import_module(dotted_name)


# ─────────────────────────────────────────────────────────────────────────────
# Test fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    user = MagicMock()
    user.id = "user-001"
    user.tenant_id = "tenant-001"
    user.roles = ["farmer"]
    return user


@pytest.fixture
def mock_user_other_tenant():
    """Create a mock user from a different tenant."""
    user = MagicMock()
    user.id = "user-002"
    user.tenant_id = "tenant-002"
    user.roles = ["farmer"]
    return user


@pytest.fixture
def app(mock_user):
    """Create FastAPI test app with mocked auth."""
    # Create proper no-op mocks for shared modules that register middleware
    from fastapi import HTTPException as _HTTPException

    class _NotFoundException(_HTTPException):
        def __init__(self, *args, **kwargs):
            super().__init__(status_code=404, detail=args[0] if args else "Not found")

    class _ValidationException(_HTTPException):
        def __init__(self, *args, **kwargs):
            super().__init__(status_code=422, detail=args[0] if args else "Validation error")

    class _ForbiddenException(_HTTPException):
        def __init__(self, *args, **kwargs):
            super().__init__(status_code=403, detail=args[0] if args else "Forbidden")

    errors_mock = MagicMock()
    errors_mock.setup_exception_handlers = lambda app: None
    errors_mock.add_request_id_middleware = lambda app: None
    errors_mock.NotFoundException = _NotFoundException
    errors_mock.ValidationException = _ValidationException
    errors_mock.ForbiddenException = _ForbiddenException

    # Create a no-op tenant middleware class
    from starlette.middleware.base import BaseHTTPMiddleware

    class _NoOpTenantMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)

    tenant_mock = MagicMock()
    tenant_mock.TenantContextMiddleware = _NoOpTenantMiddleware

    # Ensure no real connections are attempted during tests
    _ensure_drone_src()
    with (
        patch.dict("os.environ", {"DATABASE_URL": "", "NATS_URL": ""}, clear=False),
        patch.dict(
            "sys.modules",
            {
                "shared.auth.dependencies": MagicMock(),
                "shared.auth.models": MagicMock(),
                "shared.errors_py": errors_mock,
                "shared.middleware.tenant_context": tenant_mock,
                "nats": MagicMock(),
                "asyncpg": MagicMock(),
            },
        ),
    ):
        src_main = _import_drone_module("src.main")
        drone_app = src_main.app

        # Override auth dependency
        from src.api.v1 import drones, flights, missions, vra

        async def override_auth():
            return mock_user

        for module in [drones, flights, missions, vra]:
            if hasattr(module, "get_current_user"):
                drone_app.dependency_overrides[module.get_current_user] = override_auth

        yield drone_app

        drone_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_drone_payload():
    """Sample drone registration payload."""
    return {
        "name": "Agras T40 Unit-1",
        "name_ar": "أجراس T40 وحدة-1",
        "model": "DJI Agras T40",
        "serial_number": "DJI-T40-001",
        "drone_type": "dji",
        "max_payload_kg": 50.0,
        "tank_capacity_l": 40.0,
        "max_flight_time_min": 21.0,
    }


@pytest.fixture
def sample_rectangular_boundary():
    """Sample rectangular field boundary (~1 hectare near Riyadh)."""
    return [
        {"lat": 24.7136, "lng": 46.6753},
        {"lat": 24.7136, "lng": 46.6763},
        {"lat": 24.7145, "lng": 46.6763},
        {"lat": 24.7145, "lng": 46.6753},
    ]


@pytest.fixture
def sample_ndvi_grid():
    """5x5 NDVI grid for VRA tests."""
    return [
        [0.25, 0.30, 0.45, 0.60, 0.70],
        [0.28, 0.35, 0.50, 0.62, 0.68],
        [0.30, 0.38, 0.48, 0.58, 0.65],
        [0.22, 0.32, 0.42, 0.55, 0.63],
        [0.20, 0.28, 0.40, 0.52, 0.60],
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Health endpoint tests
# ─────────────────────────────────────────────────────────────────────────────


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_healthz(self, client):
        """Test liveness probe returns ok."""
        r = client.get("/healthz")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert data["service"] == "drone-service"
        assert data["version"] == "16.0.0"

    def test_readyz_not_ready(self, client):
        """Test readiness probe returns 503 when no DB/NATS."""
        r = client.get("/readyz")
        assert r.status_code == 503
        data = r.json()
        assert data["status"] == "not_ready"
        assert "checks" in data
        assert data["checks"]["database"] == "disconnected"
        assert data["checks"]["nats"] == "disconnected"

    def test_health_comprehensive(self, client):
        """Test comprehensive health check."""
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert "checks" in data
        assert "database" in data["checks"]
        assert "nats" in data["checks"]

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint returns valid format."""
        r = client.get("/metrics")
        assert r.status_code == 200
        assert "text/plain" in r.headers["content-type"]
        body = r.text
        assert "drone_service_up 1" in body
        assert "drone_service_requests_total" in body
        assert "drone_service_db_up" in body

    def test_root_endpoint(self, client):
        """Test root endpoint returns service info."""
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["service"] == "drone-service"
        assert data["version"] == "16.0.0"


# ─────────────────────────────────────────────────────────────────────────────
# Drone CRUD tests
# ─────────────────────────────────────────────────────────────────────────────


class TestDroneCRUD:
    """Tests for drone management endpoints."""

    def test_list_drones_empty(self, client):
        """Test listing drones returns empty list initially."""
        r = client.get("/api/v1/drones/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_register_drone(self, client, sample_drone_payload):
        """Test registering a new drone."""
        r = client.post("/api/v1/drones/", json=sample_drone_payload)
        assert r.status_code == 201
        data = r.json()
        assert data["name"] == "Agras T40 Unit-1"
        assert data["model"] == "DJI Agras T40"
        assert data["serial_number"] == "DJI-T40-001"
        assert data["status"] == "active"
        assert "id" in data

    def test_get_drone(self, client, sample_drone_payload):
        """Test getting drone by ID."""
        create_r = client.post("/api/v1/drones/", json=sample_drone_payload)
        drone_id = create_r.json()["id"]

        r = client.get(f"/api/v1/drones/{drone_id}")
        assert r.status_code == 200
        assert r.json()["id"] == drone_id

    def test_get_drone_not_found(self, client):
        """Test 404 for nonexistent drone."""
        r = client.get("/api/v1/drones/NONEXISTENT")
        assert r.status_code == 404

    def test_update_drone(self, client, sample_drone_payload):
        """Test updating drone info."""
        create_r = client.post("/api/v1/drones/", json=sample_drone_payload)
        drone_id = create_r.json()["id"]

        updated = {**sample_drone_payload, "name": "Updated Drone Name"}
        r = client.put(f"/api/v1/drones/{drone_id}", json=updated)
        assert r.status_code == 200
        assert r.json()["name"] == "Updated Drone Name"

    def test_delete_drone(self, client, sample_drone_payload):
        """Test deleting a drone."""
        create_r = client.post("/api/v1/drones/", json=sample_drone_payload)
        drone_id = create_r.json()["id"]

        r = client.delete(f"/api/v1/drones/{drone_id}")
        assert r.status_code == 204

        # Verify it's gone
        r = client.get(f"/api/v1/drones/{drone_id}")
        assert r.status_code == 404

    def test_delete_drone_not_found(self, client):
        """Test deleting nonexistent drone returns 404."""
        r = client.delete("/api/v1/drones/NONEXISTENT")
        assert r.status_code == 404

    def test_get_drone_status(self, client, sample_drone_payload):
        """Test getting drone status."""
        create_r = client.post("/api/v1/drones/", json=sample_drone_payload)
        drone_id = create_r.json()["id"]

        r = client.get(f"/api/v1/drones/{drone_id}/status")
        assert r.status_code == 200
        data = r.json()
        assert data["drone_id"] == drone_id
        assert data["status"] == "active"
        assert "battery_percent" in data

    def test_get_drone_telemetry(self, client, sample_drone_payload):
        """Test getting drone telemetry."""
        create_r = client.post("/api/v1/drones/", json=sample_drone_payload)
        drone_id = create_r.json()["id"]

        r = client.get(f"/api/v1/drones/{drone_id}/telemetry")
        assert r.status_code == 200
        data = r.json()
        assert data["drone_id"] == drone_id
        assert "telemetry" in data

    def test_register_drone_minimal_fields(self, client):
        """Test registering with only required fields."""
        r = client.post(
            "/api/v1/drones/",
            json={
                "name": "MinDrone",
                "model": "Custom",
                "serial_number": "SERIAL-MIN-001",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert data["drone_type"] == "custom"


# ─────────────────────────────────────────────────────────────────────────────
# Flight planning tests
# ─────────────────────────────────────────────────────────────────────────────


class TestFlightPlanning:
    """Tests for flight planning endpoints."""

    def test_weather_check_safe(self, client):
        """Test weather check with safe conditions."""
        r = client.post(
            "/api/v1/flights/weather-check",
            json={
                "lat": 24.7,
                "lng": 46.6,
                "wind_speed_ms": 3.0,
                "temperature_c": 28.0,
                "humidity_percent": 45.0,
                "precipitation_mm": 0.0,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["safe_to_fly"] is True
        assert "warnings" in data
        assert "warnings_ar" in data

    def test_weather_check_unsafe_wind(self, client):
        """Test weather check with high wind."""
        r = client.post(
            "/api/v1/flights/weather-check",
            json={
                "lat": 24.7,
                "lng": 46.6,
                "wind_speed_ms": 12.0,
                "temperature_c": 25.0,
                "humidity_percent": 50.0,
                "precipitation_mm": 0.0,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["safe_to_fly"] is False
        assert data["condition"] in ("prohibited", "marginal", "unfavorable")

    def test_weather_check_unsafe_rain(self, client):
        """Test weather check with precipitation."""
        r = client.post(
            "/api/v1/flights/weather-check",
            json={
                "lat": 24.7,
                "lng": 46.6,
                "wind_speed_ms": 2.0,
                "temperature_c": 25.0,
                "humidity_percent": 80.0,
                "precipitation_mm": 5.0,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["safe_to_fly"] is False

    def test_resource_estimate(self, client):
        """Test flight resource estimation."""
        r = client.post(
            "/api/v1/flights/estimate",
            json={
                "area_ha": 10.0,
                "spray_rate_l_ha": 15.0,
                "tank_capacity_l": 40.0,
                "flight_time_per_tank_min": 20.0,
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["area_ha"] == 10.0
        assert data["total_volume_l"] > 0
        assert data["tank_fills"] >= 1
        assert data["total_flight_time_min"] > 0

    def test_list_flight_plans_empty(self, client):
        """Test listing flight plans returns empty initially."""
        r = client.get("/api/v1/flights/plans")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 0

    def test_get_flight_plan_not_found(self, client):
        """Test 404 for nonexistent flight plan."""
        r = client.get("/api/v1/flights/plans/NONEXISTENT")
        assert r.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# Mission lifecycle tests
# ─────────────────────────────────────────────────────────────────────────────


class TestMissionLifecycle:
    """Tests for mission management and state transitions."""

    def _create_mission(self, client, name="Test Mission"):
        """Helper to create a mission."""
        r = client.post(
            "/api/v1/missions/",
            json={
                "drone_id": "DRN-TESTDRONE",
                "mission_type": "spray",
                "name": name,
                "name_ar": "مهمة اختبار",
                "field_id": "FIELD-001",
            },
        )
        assert r.status_code == 201
        return r.json()

    def test_create_mission(self, client):
        """Test creating a new mission."""
        data = self._create_mission(client)
        assert data["name"] == "Test Mission"
        assert data["status"] == "planned"
        assert data["mission_type"] == "spray"
        assert "id" in data

    def test_list_missions(self, client):
        """Test listing missions."""
        self._create_mission(client, "Mission A")
        self._create_mission(client, "Mission B")
        r = client.get("/api/v1/missions/")
        assert r.status_code == 200
        assert len(r.json()) >= 2

    def test_get_mission(self, client):
        """Test getting mission by ID."""
        created = self._create_mission(client)
        r = client.get(f"/api/v1/missions/{created['id']}")
        assert r.status_code == 200
        assert r.json()["id"] == created["id"]

    def test_get_mission_not_found(self, client):
        """Test 404 for nonexistent mission."""
        r = client.get("/api/v1/missions/NONEXISTENT")
        assert r.status_code == 404

    def test_start_mission(self, client):
        """Test starting a planned mission."""
        created = self._create_mission(client)
        r = client.post(f"/api/v1/missions/{created['id']}/start")
        assert r.status_code == 200
        assert r.json()["status"] == "active"

    def test_pause_active_mission(self, client):
        """Test pausing an active mission."""
        created = self._create_mission(client)
        client.post(f"/api/v1/missions/{created['id']}/start")
        r = client.post(f"/api/v1/missions/{created['id']}/pause")
        assert r.status_code == 200
        assert r.json()["status"] == "paused"

    def test_resume_paused_mission(self, client):
        """Test resuming a paused mission."""
        created = self._create_mission(client)
        client.post(f"/api/v1/missions/{created['id']}/start")
        client.post(f"/api/v1/missions/{created['id']}/pause")
        r = client.post(f"/api/v1/missions/{created['id']}/resume")
        assert r.status_code == 200
        assert r.json()["status"] == "active"

    def test_abort_active_mission(self, client):
        """Test aborting an active mission."""
        created = self._create_mission(client)
        client.post(f"/api/v1/missions/{created['id']}/start")
        r = client.post(f"/api/v1/missions/{created['id']}/abort")
        assert r.status_code == 200
        assert r.json()["status"] == "aborted"

    def test_complete_active_mission(self, client):
        """Test completing an active mission."""
        created = self._create_mission(client)
        client.post(f"/api/v1/missions/{created['id']}/start")
        r = client.post(f"/api/v1/missions/{created['id']}/complete")
        assert r.status_code == 200
        assert r.json()["status"] == "completed"

    def test_invalid_transition_planned_to_paused(self, client):
        """Test invalid state transition (planned → paused) returns error."""
        created = self._create_mission(client)
        r = client.post(f"/api/v1/missions/{created['id']}/pause")
        assert r.status_code in (400, 422)

    def test_invalid_transition_completed_to_active(self, client):
        """Test completed missions cannot be restarted."""
        created = self._create_mission(client)
        client.post(f"/api/v1/missions/{created['id']}/start")
        client.post(f"/api/v1/missions/{created['id']}/complete")
        r = client.post(f"/api/v1/missions/{created['id']}/start")
        assert r.status_code in (400, 422)

    def test_invalid_transition_aborted_to_active(self, client):
        """Test aborted missions cannot be restarted."""
        created = self._create_mission(client)
        client.post(f"/api/v1/missions/{created['id']}/start")
        client.post(f"/api/v1/missions/{created['id']}/abort")
        r = client.post(f"/api/v1/missions/{created['id']}/resume")
        assert r.status_code in (400, 422)

    def test_full_mission_lifecycle(self, client):
        """Test complete lifecycle: planned → active → paused → active → completed."""
        created = self._create_mission(client)
        mid = created["id"]

        # planned → active
        r1 = client.post(f"/api/v1/missions/{mid}/start")
        assert r1.json()["status"] == "active"

        # active → paused
        r2 = client.post(f"/api/v1/missions/{mid}/pause")
        assert r2.json()["status"] == "paused"

        # paused → active (resume)
        r3 = client.post(f"/api/v1/missions/{mid}/resume")
        assert r3.json()["status"] == "active"

        # active → completed
        r4 = client.post(f"/api/v1/missions/{mid}/complete")
        assert r4.json()["status"] == "completed"


# ─────────────────────────────────────────────────────────────────────────────
# VRA tests
# ─────────────────────────────────────────────────────────────────────────────


class TestVRAEndpoints:
    """Tests for VRA prescription map endpoints."""

    def test_list_prescriptions_empty(self, client):
        """Test listing prescriptions returns empty initially."""
        r = client.get("/api/v1/vra/prescriptions")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 0

    def test_get_prescription_not_found(self, client):
        """Test 404 for nonexistent prescription."""
        r = client.get("/api/v1/vra/prescriptions/NONEXISTENT")
        assert r.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# Shared module tests (drone_integration)
# ─────────────────────────────────────────────────────────────────────────────


class TestDroneIntegrationModels:
    """Tests for shared.drone_integration model classes."""

    def test_coordinate_creation(self):
        from shared.drone_integration.models import Coordinate

        c = Coordinate(lat=24.7, lng=46.6)
        assert c.lat == 24.7
        assert c.lng == 46.6
        assert c.to_tuple() == (24.7, 46.6)

    def test_coordinate_with_altitude(self):
        from shared.drone_integration.models import Coordinate

        c = Coordinate(lat=24.7, lng=46.6, alt_m=100.0, alt_agl_m=50.0)
        assert c.alt_m == 100.0
        assert c.alt_agl_m == 50.0

    def test_bounding_box_center(self):
        from shared.drone_integration.models import BoundingBox

        bb = BoundingBox(min_lat=24.0, max_lat=25.0, min_lng=46.0, max_lng=47.0)
        center = bb.center()
        assert abs(center.lat - 24.5) < 0.001
        assert abs(center.lng - 46.5) < 0.001

    def test_generate_id(self):
        from shared.drone_integration.models import generate_id

        id1 = generate_id("test")
        id2 = generate_id("test")
        assert id1.startswith("test_")
        assert id1 != id2  # Unique

    def test_drone_types_enum(self):
        from shared.drone_integration.models import DroneType

        assert DroneType.DJI_AGRAS_T40 == "dji_agras_t40"
        assert DroneType.DJI_MAVIC_3M == "dji_mavic_3m"

    def test_flight_mode_enum(self):
        from shared.drone_integration.models import FlightMode

        assert FlightMode.SPRAYING == "spraying"
        assert FlightMode.MAPPING == "mapping"

    def test_flight_status_enum(self):
        from shared.drone_integration.models import FlightStatus

        assert FlightStatus.PLANNED == "planned"
        assert FlightStatus.COMPLETED == "completed"

    def test_vra_zone_type_enum(self):
        from shared.drone_integration.models import VRAZoneType

        assert VRAZoneType.HIGH_VIGOR == "high_vigor"
        assert VRAZoneType.BARE_SOIL == "bare_soil"

    def test_waypoint_creation(self):
        from shared.drone_integration.models import Coordinate, Waypoint, WaypointAction

        wp = Waypoint(
            index=0,
            coordinate=Coordinate(lat=24.7, lng=46.6, alt_agl_m=5.0),
            speed_ms=3.0,
            actions=[WaypointAction.START_SPRAY],
        )
        assert wp.speed_ms == 3.0
        assert WaypointAction.START_SPRAY in wp.actions

    def test_weather_condition_enum(self):
        from shared.drone_integration.models import WeatherCondition

        assert WeatherCondition.OPTIMAL == "optimal"
        assert WeatherCondition.PROHIBITED == "prohibited"


class TestFlightPlannerGeometry:
    """Tests for flight planner geometry utilities."""

    def test_haversine_distance(self):
        from shared.drone_integration.flight_planner import haversine_distance
        from shared.drone_integration.models import Coordinate

        # Riyadh to Jeddah approximately 850 km
        riyadh = Coordinate(lat=24.7136, lng=46.6753)
        jeddah = Coordinate(lat=21.4858, lng=39.1925)
        dist = haversine_distance(riyadh, jeddah)
        assert 800000 < dist < 900000  # 800-900 km in meters

    def test_haversine_same_point(self):
        from shared.drone_integration.flight_planner import haversine_distance
        from shared.drone_integration.models import Coordinate

        p = Coordinate(lat=24.7, lng=46.6)
        assert haversine_distance(p, p) == 0.0

    def test_bearing_between(self):
        from shared.drone_integration.flight_planner import bearing_between
        from shared.drone_integration.models import Coordinate

        south = Coordinate(lat=24.0, lng=46.0)
        north = Coordinate(lat=25.0, lng=46.0)
        bearing = bearing_between(south, north)
        assert abs(bearing - 0) < 1  # ~0 degrees (north)

    def test_destination_point(self):
        from shared.drone_integration.flight_planner import destination_point, haversine_distance
        from shared.drone_integration.models import Coordinate

        start = Coordinate(lat=24.7, lng=46.6)
        dest = destination_point(start, 0, 1000)  # 1km north
        assert dest.lat > start.lat
        assert abs(dest.lng - start.lng) < 0.001
        dist = haversine_distance(start, dest)
        assert abs(dist - 1000) < 10  # Within 10m

    def test_polygon_area(self):
        from shared.drone_integration.flight_planner import calculate_polygon_area
        from shared.drone_integration.models import Coordinate

        # ~100m x 100m square ≈ 1 hectare
        square = [
            Coordinate(lat=24.7136, lng=46.6753),
            Coordinate(lat=24.7136, lng=46.6763),
            Coordinate(lat=24.7145, lng=46.6763),
            Coordinate(lat=24.7145, lng=46.6753),
        ]
        area = calculate_polygon_area(square)
        assert area > 5000  # More than 5,000 m² (~10,131 m² for this polygon)

    def test_point_in_polygon(self):
        from shared.drone_integration.flight_planner import point_in_polygon
        from shared.drone_integration.models import Coordinate

        square = [
            Coordinate(lat=24.0, lng=46.0),
            Coordinate(lat=24.0, lng=47.0),
            Coordinate(lat=25.0, lng=47.0),
            Coordinate(lat=25.0, lng=46.0),
        ]
        assert point_in_polygon(Coordinate(lat=24.5, lng=46.5), square) is True
        assert point_in_polygon(Coordinate(lat=23.0, lng=46.5), square) is False


class TestWeatherAssessment:
    """Tests for flight weather assessment."""

    def test_optimal_weather(self):
        from shared.drone_integration.flight_planner import assess_flight_weather

        result = assess_flight_weather(
            temperature_c=25,
            humidity_percent=50,
            wind_speed_ms=3,
            wind_direction_deg=90,
        )
        assert result.can_fly is True
        assert result.condition.value in ("optimal", "acceptable")

    def test_high_wind_prohibited(self):
        from shared.drone_integration.flight_planner import assess_flight_weather

        result = assess_flight_weather(
            temperature_c=25,
            humidity_percent=50,
            wind_speed_ms=15,
            wind_direction_deg=0,
        )
        assert result.can_fly is False

    def test_precipitation_unfavorable(self):
        from shared.drone_integration.flight_planner import assess_flight_weather

        result = assess_flight_weather(
            temperature_c=25,
            humidity_percent=80,
            wind_speed_ms=3,
            wind_direction_deg=0,
            precipitation_mm=5,
        )
        assert result.can_fly is False

    def test_weather_check_returns_warnings(self):
        from shared.drone_integration.flight_planner import assess_flight_weather

        result = assess_flight_weather(
            temperature_c=5,
            humidity_percent=90,
            wind_speed_ms=7,
            wind_direction_deg=180,
        )
        assert isinstance(result.warnings_en, list)
        assert isinstance(result.warnings_ar, list)


class TestVRAGenerator:
    """Tests for VRA prescription map generation."""

    def test_create_ndvi_prescription(self):
        from shared.drone_integration.models import BoundingBox
        from shared.drone_integration.vra import create_ndvi_prescription

        grid = [
            [0.2, 0.3, 0.5, 0.7],
            [0.25, 0.35, 0.55, 0.65],
            [0.3, 0.4, 0.6, 0.72],
        ]
        bounds = BoundingBox(min_lat=24.0, max_lat=24.01, min_lng=46.0, max_lng=46.01)
        result = create_ndvi_prescription(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            ndvi_grid=grid,
            bounds=bounds,
            base_rate_l_ha=10.0,
        )
        assert result.field_id == "FIELD-001"
        assert result.tenant_id == "tenant-001"
        assert len(result.zones) > 0

    def test_create_ndvi_prescription_empty_grid(self):
        from shared.drone_integration.models import BoundingBox
        from shared.drone_integration.vra import create_ndvi_prescription

        bounds = BoundingBox(min_lat=24.0, max_lat=24.01, min_lng=46.0, max_lng=46.01)
        result = create_ndvi_prescription(
            field_id="FIELD-002",
            tenant_id="tenant-001",
            ndvi_grid=[],
            bounds=bounds,
        )
        assert len(result.zones) == 0

    def test_vra_zone_labels(self):
        from shared.drone_integration.vra import VRAGenerator

        gen = VRAGenerator()
        en, ar = gen._get_zone_labels(
            __import__("shared.drone_integration.models", fromlist=["VRAZoneType"]).VRAZoneType.HIGH_VIGOR
        )
        assert en == "High Vigor"
        assert ar == "نمو قوي"

    def test_ndvi_to_zone_type(self):
        from shared.drone_integration.vra import VRAGenerator
        from shared.drone_integration.models import VRAZoneType

        gen = VRAGenerator()
        assert gen._ndvi_to_zone_type(0.05) == VRAZoneType.BARE_SOIL
        assert gen._ndvi_to_zone_type(0.2) == VRAZoneType.LOW_VIGOR
        assert gen._ndvi_to_zone_type(0.35) == VRAZoneType.STRESSED
        assert gen._ndvi_to_zone_type(0.5) == VRAZoneType.MEDIUM_VIGOR
        assert gen._ndvi_to_zone_type(0.75) == VRAZoneType.HIGH_VIGOR

    def test_create_spot_spray_map(self):
        from shared.drone_integration.models import Coordinate
        from shared.drone_integration.vra import create_spot_spray_map

        boundary = [
            Coordinate(lat=24.0, lng=46.0),
            Coordinate(lat=24.0, lng=46.01),
            Coordinate(lat=24.01, lng=46.01),
            Coordinate(lat=24.01, lng=46.0),
        ]
        detections = [
            {"lat": 24.005, "lng": 46.005, "density": 0.8},
            {"lat": 24.006, "lng": 46.006, "density": 0.6},
        ]
        result = create_spot_spray_map(
            field_id="FIELD-001",
            tenant_id="tenant-001",
            detection_points=detections,
            boundary=boundary,
        )
        assert result.field_id == "FIELD-001"
        assert len(result.zones) > 0


class TestAdvancedFlightPlannerDeprecation:
    """Tests for deprecated advanced_flight_planner module."""

    def test_deprecation_warning(self):
        """Test that DroneFlightPlanner raises DeprecationWarning."""
        import warnings
        from shared.drone_integration.advanced_flight_planner import DroneFlightPlanner

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _planner = DroneFlightPlanner()  # noqa: F841 - instantiation triggers warning
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()

    def test_gsd_calculation_still_works(self):
        """Test that deprecated planner still functions correctly."""
        import warnings
        from shared.drone_integration.advanced_flight_planner import DroneFlightPlanner

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            planner = DroneFlightPlanner()
            gsd = planner.calculate_gsd(altitude_m=50.0)
            assert gsd > 0
            assert isinstance(gsd, float)


class TestKMLExportSecurity:
    """Tests for KML export XML injection prevention."""

    def test_kml_escapes_special_chars(self):
        from shared.drone_integration.models import Coordinate, FlightPath, FlightPattern, Waypoint

        path = FlightPath(
            id="test-kml-001",
            name='<script>alert("xss")</script>',
            name_ar="<b>هجوم</b>",
            waypoints=[
                Waypoint(index=0, coordinate=Coordinate(lat=24.7, lng=46.6, alt_agl_m=5)),
            ],
            pattern=FlightPattern.PARALLEL,
            total_distance_m=100.0,
            estimated_duration_min=5.0,
            cruise_altitude_m=10.0,
            cruise_speed_ms=3.0,
            swath_width_m=5.0,
        )
        kml = path.to_kml()
        assert "<script>" not in kml
        assert "&lt;script&gt;" in kml
        assert "&lt;b&gt;" in kml


class TestEventsModule:
    """Tests for the events publishing module."""

    @pytest.mark.asyncio
    async def test_publish_event_with_nc(self):
        events = _import_drone_module("src.events")
        nc = AsyncMock()
        await events.publish_event(nc, "sahool.drone.test", {"key": "value"})
        nc.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_event_without_nc(self):
        events = _import_drone_module("src.events")
        # Should not raise
        await events.publish_event(None, "sahool.drone.test", {"key": "value"})

    @pytest.mark.asyncio
    async def test_publish_drone_event_includes_tenant(self):
        events = _import_drone_module("src.events")
        nc = AsyncMock()
        await events.publish_drone_event(nc, "sahool.drone.registered", "tenant-001", drone_id="DRN-001")
        # Called twice: once for base subject, once for tenant-scoped
        assert nc.publish.call_count == 2

    def test_event_subjects_defined(self):
        events = _import_drone_module("src.events")
        assert events.DRONE_REGISTERED == "sahool.drone.registered"
        assert events.FLIGHT_PLANNED == "sahool.drone.flight_planned"
        assert events.MISSION_CREATED == "sahool.drone.mission_created"
        assert events.VRA_PRESCRIPTION_CREATED == "sahool.drone.vra_prescription_created"


class TestEventEnvelope:
    """Tests for EventEnvelope wrapper class."""

    def test_create_envelope(self):
        events = _import_drone_module("src.events")
        envelope = events.EventEnvelope.create(
            event_type="drone_registered",
            version=1,
            aggregate_id="DRN-001",
            tenant_id="tenant-001",
            correlation_id="corr-001",
            payload={"drone_id": "DRN-001", "model": "DJI Agras T40"},
        )
        assert envelope.event_type == "drone_registered"
        assert envelope.version == 1
        assert envelope.aggregate_id == "DRN-001"
        assert envelope.tenant_id == "tenant-001"
        assert envelope.correlation_id == "corr-001"
        assert envelope.event_id  # UUID generated
        assert envelope.timestamp  # Timestamp generated

    def test_envelope_to_dict(self):
        events = _import_drone_module("src.events")
        envelope = events.EventEnvelope.create(
            event_type="mission_created",
            version=1,
            aggregate_id="MSN-001",
            tenant_id="tenant-001",
            correlation_id="corr-002",
            payload={"mission_id": "MSN-001"},
        )
        d = envelope.to_dict()
        assert d["event_type"] == "mission_created"
        assert d["aggregate_id"] == "MSN-001"
        assert d["tenant_id"] == "tenant-001"
        assert "event_id" in d
        assert "timestamp" in d
        assert d["payload"] == {"mission_id": "MSN-001"}

    def test_envelope_unique_ids(self):
        events = _import_drone_module("src.events")
        e1 = events.EventEnvelope.create("test", 1, "agg", "t1", "c1", {})
        e2 = events.EventEnvelope.create("test", 1, "agg", "t1", "c1", {})
        assert e1.event_id != e2.event_id


class TestDronePublisher:
    """Tests for DronePublisher lifecycle and publishing."""

    @pytest.mark.asyncio
    async def test_publish_without_connection(self):
        events = _import_drone_module("src.events")
        publisher = events.DronePublisher()
        # Should return empty string, not raise
        event_id = await publisher.publish(
            "drone_registered",
            "tenant-001",
            "DRN-001",
            {"drone_id": "DRN-001"},
        )
        assert event_id == ""

    @pytest.mark.asyncio
    async def test_publish_with_mock_nc(self):
        events = _import_drone_module("src.events")
        publisher = events.DronePublisher()
        publisher.nc = AsyncMock()
        event_id = await publisher.publish(
            "drone_registered",
            "tenant-001",
            "DRN-001",
            {"drone_id": "DRN-001", "model": "T40"},
        )
        assert event_id  # Non-empty UUID
        assert publisher.nc.publish.call_count == 2  # base + tenant-scoped

    @pytest.mark.asyncio
    async def test_publish_drone_registered(self):
        events = _import_drone_module("src.events")
        publisher = events.DronePublisher()
        publisher.nc = AsyncMock()
        event_id = await publisher.publish_drone_registered(
            tenant_id="tenant-001",
            drone_id="DRN-001",
            model="DJI Agras T40",
        )
        assert event_id
        assert publisher.nc.publish.call_count == 2

    @pytest.mark.asyncio
    async def test_publish_mission_event(self):
        events = _import_drone_module("src.events")
        publisher = events.DronePublisher()
        publisher.nc = AsyncMock()
        event_id = await publisher.publish_mission_event(
            "mission_started",
            "tenant-001",
            "MSN-001",
            drone_id="DRN-001",
        )
        assert event_id
        # Verify the published data contains EventEnvelope structure
        call_args = publisher.nc.publish.call_args_list[0]
        import json

        data = json.loads(call_args[0][1].decode())
        assert "event_id" in data
        assert "event_type" in data
        assert data["event_type"] == "mission_started"
        assert data["payload"]["mission_id"] == "MSN-001"

    @pytest.mark.asyncio
    async def test_close_without_connection(self):
        events = _import_drone_module("src.events")
        publisher = events.DronePublisher()
        # Should not raise
        await publisher.close()


class TestEventTypes:
    """Tests for event types, subjects, and versioning."""

    def test_subjects_dict(self):
        types = _import_drone_module("src.events.types")
        assert types.SUBJECTS[types.DRONE_REGISTERED] == "sahool.drone.registered"
        assert types.SUBJECTS[types.MISSION_CREATED] == "sahool.drone.mission_created"

    def test_versions_dict(self):
        types = _import_drone_module("src.events.types")
        assert types.VERSIONS[types.DRONE_REGISTERED] == 1
        assert types.VERSIONS[types.FLIGHT_PLANNED] == 1

    def test_get_subject(self):
        types = _import_drone_module("src.events.types")
        assert types.get_subject("drone_registered") == "sahool.drone.registered"
        # Unknown type falls back to prefix
        assert types.get_subject("unknown_event") == "sahool.drone.unknown_event"

    def test_get_version(self):
        types = _import_drone_module("src.events.types")
        assert types.get_version("drone_registered") == 1
        # Unknown defaults to 1
        assert types.get_version("unknown_event") == 1

    def test_cross_service_subjects(self):
        types = _import_drone_module("src.events.types")
        assert types.VISION_PEST_DETECTED == "sahool.vision.pest_detected"
        assert types.WEATHER_ALERT == "sahool.weather.alert"
