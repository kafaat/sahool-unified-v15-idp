"""Comprehensive tests for logistics-service - models, endpoints, helpers, error handling."""

import math
import os
import sys
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

from src.main import (
    HARVEST_COLLECTIONS,
    PRIORITY_AR,
    SHIPMENT_STATUS_AR,
    SHIPMENTS,
    STORAGE_FACILITIES,
    STORAGE_TYPE_AR,
    VEHICLE_STATUS_AR,
    VEHICLE_TYPE_AR,
    VEHICLES,
    CollectionPriority,
    HarvestCollection,
    HarvestCollectionCreate,
    RouteOptimizationRequest,
    RouteOptimizationResult,
    Shipment,
    ShipmentCreate,
    ShipmentStatus,
    StorageFacility,
    StorageFacilityCreate,
    StorageType,
    Vehicle,
    VehicleCreate,
    VehicleStatus,
    VehicleType,
    VehicleUpdate,
    app,
    calculate_distance,
    get_tenant_id,
    publish_event,
    seed_demo_data,
)

TENANT = "tenant_demo"
# Middleware requires UUID format, but the dependency override returns tenant_demo for business logic
TENANT_UUID = "00000000-0000-0000-0000-000000000001"
HEADERS = {"X-Tenant-Id": TENANT_UUID}


@pytest.fixture(autouse=True)
def reset_stores():
    """Reset in-memory stores before each test and seed demo data."""
    VEHICLES.clear()
    STORAGE_FACILITIES.clear()
    HARVEST_COLLECTIONS.clear()
    SHIPMENTS.clear()
    seed_demo_data()
    yield
    VEHICLES.clear()
    STORAGE_FACILITIES.clear()
    HARVEST_COLLECTIONS.clear()
    SHIPMENTS.clear()


async def _override_tenant_id():
    return TENANT


@pytest.fixture
def client():
    from src.main import get_tenant_id as real_get_tenant_id

    app.dependency_overrides[real_get_tenant_id] = _override_tenant_id
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


# ==========================================================================
# Enum & Translation Tests
# ==========================================================================
class TestEnums:
    def test_vehicle_type_values(self):
        assert VehicleType.TRUCK == "truck"
        assert VehicleType.REFRIGERATED == "refrigerated"
        assert VehicleType.TANKER == "tanker"
        assert VehicleType.TRACTOR_TRAILER == "tractor_trailer"

    def test_vehicle_status_values(self):
        assert VehicleStatus.AVAILABLE == "available"
        assert VehicleStatus.IN_TRANSIT == "in_transit"
        assert VehicleStatus.MAINTENANCE == "maintenance"
        assert VehicleStatus.OUT_OF_SERVICE == "out_of_service"

    def test_shipment_status_values(self):
        assert ShipmentStatus.SCHEDULED == "scheduled"
        assert ShipmentStatus.COLLECTING == "collecting"
        assert ShipmentStatus.DELIVERED == "delivered"
        assert ShipmentStatus.CANCELLED == "cancelled"

    def test_storage_type_values(self):
        assert StorageType.COLD == "cold"
        assert StorageType.GRAIN_SILO == "grain_silo"
        assert StorageType.CONTROLLED_ATMOSPHERE == "controlled_atmosphere"

    def test_collection_priority_values(self):
        assert CollectionPriority.LOW == "low"
        assert CollectionPriority.URGENT == "urgent"

    def test_arabic_translations_complete(self):
        """All enum values should have Arabic translations."""
        for vt in VehicleType:
            assert vt in VEHICLE_TYPE_AR, f"Missing Arabic for VehicleType.{vt.name}"
        for vs in VehicleStatus:
            assert vs in VEHICLE_STATUS_AR, f"Missing Arabic for VehicleStatus.{vs.name}"
        for ss in ShipmentStatus:
            assert ss in SHIPMENT_STATUS_AR, f"Missing Arabic for ShipmentStatus.{ss.name}"
        for st in StorageType:
            assert st in STORAGE_TYPE_AR, f"Missing Arabic for StorageType.{st.name}"
        for cp in CollectionPriority:
            assert cp in PRIORITY_AR, f"Missing Arabic for CollectionPriority.{cp.name}"


# ==========================================================================
# Pydantic Model Tests
# ==========================================================================
class TestModels:
    def test_vehicle_create_validation(self):
        data = VehicleCreate(
            name="Test Truck",
            vehicle_type=VehicleType.TRUCK,
            license_plate="ABC-123",
            capacity_kg=5000.0,
        )
        assert data.name == "Test Truck"
        assert data.capacity_kg == 5000.0

    def test_vehicle_create_capacity_must_be_positive(self):
        with pytest.raises((ValueError, Exception)):
            VehicleCreate(
                name="Bad Truck",
                vehicle_type=VehicleType.TRUCK,
                license_plate="X",
                capacity_kg=-100,
            )

    def test_vehicle_update_partial(self):
        update = VehicleUpdate(status=VehicleStatus.MAINTENANCE)
        dumped = update.model_dump(exclude_unset=True)
        assert "status" in dumped
        assert "name" not in dumped

    def test_storage_facility_create_validation(self):
        data = StorageFacilityCreate(
            name="Cold Store",
            storage_type=StorageType.COLD,
            address="123 Main St",
            lat=15.0,
            lon=44.0,
            total_capacity_kg=10000.0,
        )
        assert data.total_capacity_kg == 10000.0

    def test_harvest_collection_create(self):
        data = HarvestCollectionCreate(
            field_id="f1",
            field_name="Field 1",
            crop_type="wheat",
            estimated_quantity_kg=1000.0,
            scheduled_date=datetime.now(UTC),
            pickup_lat=15.0,
            pickup_lon=44.0,
        )
        assert data.priority == CollectionPriority.MEDIUM  # default

    def test_shipment_create_weight_must_be_positive(self):
        with pytest.raises((ValueError, Exception)):
            ShipmentCreate(
                vehicle_id="v1",
                cargo_description="Test",
                weight_kg=0,
                scheduled_departure=datetime.now(UTC),
            )

    def test_route_optimization_request(self):
        req = RouteOptimizationRequest(
            vehicle_id="v1",
            start_lat=15.0,
            start_lon=44.0,
            collection_ids=["c1", "c2"],
        )
        assert req.return_to_start is True  # default


# ==========================================================================
# Helper Function Tests
# ==========================================================================
class TestHelpers:
    def test_calculate_distance_same_point(self):
        dist = calculate_distance(15.0, 44.0, 15.0, 44.0)
        assert dist == pytest.approx(0.0, abs=0.001)

    def test_calculate_distance_known_points(self):
        # Sanaa to Aden approximately 300+ km
        dist = calculate_distance(15.3694, 44.1910, 12.7855, 45.0187)
        assert dist > 200
        assert dist < 400

    def test_calculate_distance_symmetry(self):
        d1 = calculate_distance(15.0, 44.0, 16.0, 45.0)
        d2 = calculate_distance(16.0, 45.0, 15.0, 44.0)
        assert d1 == pytest.approx(d2, abs=0.001)

    @pytest.mark.asyncio
    async def test_publish_event_no_nats(self):
        """publish_event should not raise when NATS is not connected."""
        await publish_event("sahool.test.event", {"key": "value"})

    def test_seed_demo_data(self):
        """Demo data seeding should create vehicles, facilities, collections."""
        VEHICLES.clear()
        STORAGE_FACILITIES.clear()
        HARVEST_COLLECTIONS.clear()
        seed_demo_data()
        assert len(VEHICLES) == 2
        assert len(STORAGE_FACILITIES) == 2
        assert len(HARVEST_COLLECTIONS) == 2


# ==========================================================================
# Health Endpoint Tests
# ==========================================================================
class TestHealthEndpoints:
    def test_healthz(self, client):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "sahool-logistics-service"
        assert "version" in data

    def test_readyz(self, client):
        resp = client.get("/readyz")
        assert resp.status_code == 200
        data = resp.json()
        assert "vehicles_count" in data
        assert "facilities_count" in data

    def test_combined_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "stats" in data
        assert "vehicles" in data["stats"]


# ==========================================================================
# Fleet / Vehicle Endpoint Tests
# ==========================================================================
class TestVehicleEndpoints:
    def test_list_vehicles(self, client):
        resp = client.get("/api/v1/vehicles", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["vehicles"]) == 2

    def test_list_vehicles_filter_by_type(self, client):
        resp = client.get("/api/v1/vehicles?vehicle_type=refrigerated", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["vehicles"][0]["vehicle_type"] == "refrigerated"

    def test_list_vehicles_filter_by_status(self, client):
        resp = client.get("/api/v1/vehicles?status=available", headers=HEADERS)
        data = resp.json()
        assert all(v["status"] == "available" for v in data["vehicles"])

    def test_list_vehicles_pagination(self, client):
        resp = client.get("/api/v1/vehicles?limit=1&offset=0", headers=HEADERS)
        data = resp.json()
        assert len(data["vehicles"]) == 1
        assert data["total"] == 2

    def test_get_vehicle_by_id(self, client):
        resp = client.get("/api/v1/vehicles/veh_001", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["vehicle_id"] == "veh_001"
        assert data["vehicle_type_ar"] is not None

    def test_get_vehicle_not_found(self, client):
        resp = client.get("/api/v1/vehicles/nonexistent", headers=HEADERS)
        assert resp.status_code == 404

    def test_get_vehicle_wrong_tenant(self, client):
        """Vehicle from a different tenant should not be accessible."""
        VEHICLES["veh_other"] = {
            **VEHICLES["veh_001"],
            "vehicle_id": "veh_other",
            "tenant_id": "other_tenant",
        }
        # Override returns tenant_demo, so veh_other (other_tenant) should not be found
        resp = client.get("/api/v1/vehicles/veh_other", headers=HEADERS)
        assert resp.status_code == 404

    def test_create_vehicle(self, client):
        resp = client.post(
            "/api/v1/vehicles",
            json={
                "name": "New Van",
                "vehicle_type": "van",
                "license_plate": "NEW-001",
                "capacity_kg": 2000,
            },
            headers=HEADERS,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "New Van"
        assert data["status"] == "available"
        assert data["vehicle_type_ar"] is not None

    def test_update_vehicle(self, client):
        resp = client.put(
            "/api/v1/vehicles/veh_001",
            json={"status": "maintenance", "name": "Updated Truck"},
            headers=HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "maintenance"
        assert data["name"] == "Updated Truck"

    def test_update_vehicle_not_found(self, client):
        resp = client.put(
            "/api/v1/vehicles/nonexistent",
            json={"name": "X"},
            headers=HEADERS,
        )
        assert resp.status_code == 404

    def test_update_vehicle_location(self, client):
        resp = client.post(
            "/api/v1/vehicles/veh_001/location?lat=15.5&lon=44.5",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        assert VEHICLES["veh_001"]["current_lat"] == 15.5
        assert VEHICLES["veh_001"]["current_lon"] == 44.5

    def test_update_vehicle_location_with_fuel(self, client):
        resp = client.post(
            "/api/v1/vehicles/veh_001/location?lat=15.5&lon=44.5&fuel_level=75",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        assert VEHICLES["veh_001"]["fuel_level_percent"] == 75

    def test_update_vehicle_location_not_found(self, client):
        resp = client.post(
            "/api/v1/vehicles/nonexistent/location?lat=15.0&lon=44.0",
            headers=HEADERS,
        )
        assert resp.status_code == 404


# ==========================================================================
# Storage Facility Endpoint Tests
# ==========================================================================
class TestStorageFacilityEndpoints:
    def test_list_storage_facilities(self, client):
        resp = client.get("/api/v1/storage-facilities", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2

    def test_list_storage_facilities_filter_type(self, client):
        resp = client.get("/api/v1/storage-facilities?storage_type=cold", headers=HEADERS)
        data = resp.json()
        assert data["total"] == 1

    def test_get_storage_facility(self, client):
        resp = client.get("/api/v1/storage-facilities/fac_001", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["facility_id"] == "fac_001"

    def test_get_storage_facility_not_found(self, client):
        resp = client.get("/api/v1/storage-facilities/nonexistent", headers=HEADERS)
        assert resp.status_code == 404

    def test_create_storage_facility(self, client):
        resp = client.post(
            "/api/v1/storage-facilities",
            json={
                "name": "New Silo",
                "storage_type": "grain_silo",
                "address": "Test Address",
                "lat": 15.0,
                "lon": 44.0,
                "total_capacity_kg": 50000,
            },
            headers=HEADERS,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "New Silo"
        assert data["available_capacity_kg"] == 50000  # starts full

    def test_update_facility_conditions(self, client):
        resp = client.post(
            "/api/v1/storage-facilities/fac_001/conditions?temperature_c=5.0&humidity_percent=88.0",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["alerts"] == []  # 5.0 is within 2-8 range

    def test_update_facility_conditions_temp_alert(self, client):
        resp = client.post(
            "/api/v1/storage-facilities/fac_001/conditions?temperature_c=10.0",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        # 10C > max 8C for fac_001
        assert len(data["alerts"]) > 0
        assert "above maximum" in data["alerts"][0]

    def test_update_facility_conditions_temp_below_min(self, client):
        resp = client.post(
            "/api/v1/storage-facilities/fac_001/conditions?temperature_c=-1.0",
            headers=HEADERS,
        )
        data = resp.json()
        assert len(data["alerts"]) > 0
        assert "below minimum" in data["alerts"][0]

    def test_update_facility_conditions_not_found(self, client):
        resp = client.post(
            "/api/v1/storage-facilities/nonexistent/conditions?temperature_c=5.0",
            headers=HEADERS,
        )
        assert resp.status_code == 404


# ==========================================================================
# Harvest Collection Endpoint Tests
# ==========================================================================
class TestCollectionEndpoints:
    def test_list_collections(self, client):
        resp = client.get("/api/v1/collections", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2

    def test_list_collections_filter_status(self, client):
        resp = client.get("/api/v1/collections?status=scheduled", headers=HEADERS)
        data = resp.json()
        assert all(c["status"] == "scheduled" for c in data["collections"])

    def test_list_collections_filter_priority(self, client):
        resp = client.get("/api/v1/collections?priority=urgent", headers=HEADERS)
        data = resp.json()
        assert data["total"] == 1

    def test_create_collection(self, client):
        resp = client.post(
            "/api/v1/collections",
            json={
                "field_id": "f_new",
                "field_name": "New Field",
                "crop_type": "barley",
                "estimated_quantity_kg": 3000,
                "priority": "high",
                "scheduled_date": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
                "pickup_lat": 15.4,
                "pickup_lon": 44.2,
            },
            headers=HEADERS,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "scheduled"
        assert data["crop_type"] == "barley"

    def test_assign_vehicle_to_collection(self, client):
        resp = client.post(
            "/api/v1/collections/col_001/assign?vehicle_id=veh_001",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        assert HARVEST_COLLECTIONS["col_001"]["assigned_vehicle_id"] == "veh_001"

    def test_assign_vehicle_collection_not_found(self, client):
        resp = client.post(
            "/api/v1/collections/nonexistent/assign?vehicle_id=veh_001",
            headers=HEADERS,
        )
        assert resp.status_code == 404

    def test_assign_vehicle_not_found(self, client):
        resp = client.post(
            "/api/v1/collections/col_001/assign?vehicle_id=nonexistent",
            headers=HEADERS,
        )
        assert resp.status_code == 404

    def test_update_collection_status(self, client):
        resp = client.post(
            "/api/v1/collections/col_001/status?status=collecting",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        assert HARVEST_COLLECTIONS["col_001"]["status"] == "collecting"
        assert HARVEST_COLLECTIONS["col_001"]["actual_collection_date"] is not None

    def test_update_collection_status_with_quantity(self, client):
        resp = client.post(
            "/api/v1/collections/col_001/status?status=delivered&actual_quantity_kg=2400",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        assert HARVEST_COLLECTIONS["col_001"]["actual_quantity_kg"] == 2400

    def test_update_collection_status_not_found(self, client):
        resp = client.post(
            "/api/v1/collections/nonexistent/status?status=delivered",
            headers=HEADERS,
        )
        assert resp.status_code == 404


# ==========================================================================
# Route Optimization Tests
# ==========================================================================
class TestRouteOptimization:
    def test_optimize_route(self, client):
        resp = client.post(
            "/api/v1/routes/optimize",
            json={
                "vehicle_id": "veh_001",
                "start_lat": 15.3694,
                "start_lon": 44.1910,
                "collection_ids": ["col_001", "col_002"],
            },
            headers=HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["optimized_order"]) == 2
        assert data["total_distance_km"] > 0
        assert data["estimated_duration_hours"] > 0
        # Last waypoint should be a return
        assert data["waypoints"][-1].get("type") == "return"

    def test_optimize_route_no_return(self, client):
        resp = client.post(
            "/api/v1/routes/optimize",
            json={
                "vehicle_id": "veh_001",
                "start_lat": 15.3694,
                "start_lon": 44.1910,
                "collection_ids": ["col_001"],
                "return_to_start": False,
            },
            headers=HEADERS,
        )
        assert resp.status_code == 200
        data = resp.json()
        # No return waypoint
        assert all(w.get("type") != "return" for w in data["waypoints"])

    def test_optimize_route_vehicle_not_found(self, client):
        resp = client.post(
            "/api/v1/routes/optimize",
            json={
                "vehicle_id": "nonexistent",
                "start_lat": 15.0,
                "start_lon": 44.0,
                "collection_ids": ["col_001"],
            },
            headers=HEADERS,
        )
        assert resp.status_code == 404

    def test_optimize_route_no_valid_collections(self, client):
        resp = client.post(
            "/api/v1/routes/optimize",
            json={
                "vehicle_id": "veh_001",
                "start_lat": 15.0,
                "start_lon": 44.0,
                "collection_ids": ["nonexistent_1", "nonexistent_2"],
            },
            headers=HEADERS,
        )
        assert resp.status_code == 400


# ==========================================================================
# Shipment Endpoint Tests
# ==========================================================================
class TestShipmentEndpoints:
    def _create_shipment(self, client):
        return client.post(
            "/api/v1/shipments",
            json={
                "vehicle_id": "veh_001",
                "cargo_description": "Wheat harvest",
                "weight_kg": 2500,
                "scheduled_departure": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
            },
            headers=HEADERS,
        )

    def test_create_shipment(self, client):
        resp = self._create_shipment(client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "scheduled"
        assert data["weight_kg"] == 2500

    def test_create_shipment_vehicle_not_found(self, client):
        resp = client.post(
            "/api/v1/shipments",
            json={
                "vehicle_id": "nonexistent",
                "cargo_description": "Test",
                "weight_kg": 100,
                "scheduled_departure": datetime.now(UTC).isoformat(),
            },
            headers=HEADERS,
        )
        assert resp.status_code == 404

    def test_list_shipments(self, client):
        self._create_shipment(client)
        resp = client.get("/api/v1/shipments", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    def test_list_shipments_filter_status(self, client):
        self._create_shipment(client)
        resp = client.get("/api/v1/shipments?status=scheduled", headers=HEADERS)
        data = resp.json()
        assert all(s["status"] == "scheduled" for s in data["shipments"])

    def test_update_shipment_status(self, client):
        create_resp = self._create_shipment(client)
        sid = create_resp.json()["shipment_id"]
        resp = client.post(
            f"/api/v1/shipments/{sid}/status?status=in_transit",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        assert SHIPMENTS[sid]["status"] == "in_transit"
        assert SHIPMENTS[sid]["actual_departure"] is not None

    def test_update_shipment_status_delivered(self, client):
        create_resp = self._create_shipment(client)
        sid = create_resp.json()["shipment_id"]
        # Move to delivered
        client.post(f"/api/v1/shipments/{sid}/status?status=in_transit", headers=HEADERS)
        resp = client.post(f"/api/v1/shipments/{sid}/status?status=delivered", headers=HEADERS)
        assert resp.status_code == 200
        assert SHIPMENTS[sid]["actual_arrival"] is not None

    def test_update_shipment_status_not_found(self, client):
        resp = client.post(
            "/api/v1/shipments/nonexistent/status?status=delivered",
            headers=HEADERS,
        )
        assert resp.status_code == 404

    def test_update_shipment_with_location(self, client):
        create_resp = self._create_shipment(client)
        sid = create_resp.json()["shipment_id"]
        resp = client.post(
            f"/api/v1/shipments/{sid}/status?status=in_transit&lat=15.5&lon=44.5",
            headers=HEADERS,
        )
        assert resp.status_code == 200
        assert SHIPMENTS[sid]["current_lat"] == 15.5


# ==========================================================================
# Statistics Endpoint Tests
# ==========================================================================
class TestStatsEndpoint:
    def test_get_stats(self, client):
        resp = client.get("/api/v1/stats", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert data["tenant_id"] == TENANT
        assert data["fleet"]["total_vehicles"] == 2
        assert data["storage"]["total_facilities"] == 2
        assert data["collections"]["total"] == 2
        assert "utilization_percent" in data["storage"]

    def test_get_stats_storage_utilization(self, client):
        """Stats should include storage utilization percentage."""
        resp = client.get("/api/v1/stats", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert 0 <= data["storage"]["utilization_percent"] <= 100


# ==========================================================================
# Tenant Isolation Tests
# ==========================================================================
class TestTenantIsolation:
    def test_vehicles_filtered_by_tenant(self, client):
        """Vehicles from different tenant should not appear in listing."""
        VEHICLES["veh_other"] = {
            **VEHICLES["veh_001"],
            "vehicle_id": "veh_other",
            "tenant_id": "other_tenant",
        }
        resp = client.get("/api/v1/vehicles", headers=HEADERS)
        data = resp.json()
        # Should only see tenant_demo vehicles (2), not the other_tenant one
        assert data["total"] == 2
        ids = [v["vehicle_id"] for v in data["vehicles"]]
        assert "veh_other" not in ids

    def test_facilities_filtered_by_tenant(self, client):
        """Facilities from different tenant should not appear in listing."""
        STORAGE_FACILITIES["fac_other"] = {
            **STORAGE_FACILITIES["fac_001"],
            "facility_id": "fac_other",
            "tenant_id": "other_tenant",
        }
        resp = client.get("/api/v1/storage-facilities", headers=HEADERS)
        data = resp.json()
        assert data["total"] == 2
        ids = [f["facility_id"] for f in data["facilities"]]
        assert "fac_other" not in ids
