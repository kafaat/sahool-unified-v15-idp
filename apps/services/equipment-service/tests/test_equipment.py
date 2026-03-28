"""
SAHOOL Equipment Service - Unit Tests
اختبارات خدمة إدارة المعدات

These tests mock the repository layer and database dependency so they can
run without a live PostgreSQL instance (offline-first CI).
"""

import os
import sys
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from fastapi.testclient import TestClient
    from src.main import app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    pytest.skip("equipment-service dependencies not installed", allow_module_level=True)


TEST_TENANT_ID = "00000000-0000-0000-0000-000000000001"
NOW = datetime.now(UTC)


def _fake_current_user():
    # The User class resolved via apps/services/shared/auth/models.py requires
    # hashed_password; the top-level shared/auth/models.py does not.  We supply
    # both optional-style kwargs so construction succeeds regardless of which
    # variant is on sys.path.
    kwargs = {
        "id": "test-user-001",
        "email": "test@sahool.sa",
        "tenant_id": TEST_TENANT_ID,
    }
    import inspect

    sig = inspect.signature(User)
    if "hashed_password" in sig.parameters:
        kwargs["hashed_password"] = "fake-hash-for-test"
    if "roles" in sig.parameters:
        kwargs["roles"] = ["farmer"]
    return User(**kwargs)


def _fake_tenant_id():
    return TEST_TENANT_ID


def _fake_get_db():
    """Yield a mock DB session so endpoints never touch a real database."""
    yield MagicMock()


def _make_equipment_row(**overrides):
    """Create a mock equipment DB row with sensible defaults."""
    defaults = {
        "equipment_id": "eq_001",
        "tenant_id": TEST_TENANT_ID,
        "name": "John Deere 8R 410",
        "name_ar": "جون ديري 8R 410",
        "equipment_type": "tractor",
        "status": "operational",
        "brand": "John Deere",
        "model": "8R 410",
        "serial_number": "JD8R410-2023-001",
        "year": 2023,
        "purchase_date": None,
        "purchase_price": None,
        "field_id": "field_north",
        "location_name": "الحقل الشمالي",
        "horsepower": 410,
        "fuel_capacity_liters": 800,
        "current_fuel_percent": 75,
        "current_hours": 1250,
        "current_lat": 15.3694,
        "current_lon": 44.1910,
        "last_maintenance_at": NOW - timedelta(days=30),
        "next_maintenance_at": NOW + timedelta(days=60),
        "next_maintenance_hours": 1500,
        "created_at": NOW - timedelta(days=365),
        "updated_at": NOW - timedelta(hours=2),
        "qr_code": "QR_EQ001_JD8R410",
        "extra_metadata": None,
    }
    defaults.update(overrides)
    row = MagicMock()
    for k, v in defaults.items():
        setattr(row, k, v)
    return row


@pytest.fixture
def mock_repo():
    """Patch the repository module used by main.py endpoints."""
    with patch("src.main.repository") as repo:
        yield repo


@pytest.fixture
def client(mock_repo):
    """Test client fixture with auth, tenant, DB, and repository mocked."""
    from src.database import get_db
    from src.main import get_tenant_id

    app.dependency_overrides[get_current_user] = _fake_current_user
    app.dependency_overrides[get_tenant_id] = _fake_tenant_id
    app.dependency_overrides[get_db] = _fake_get_db
    yield TestClient(app, headers={"X-Tenant-ID": TEST_TENANT_ID})
    app.dependency_overrides.clear()


@pytest.fixture
def sample_equipment():
    """Sample equipment data for testing"""
    return {
        "name": "Test Tractor",
        "name_ar": "جرار اختبار",
        "equipment_type": "tractor",
        "brand": "TestBrand",
        "model": "T-100",
        "serial_number": "TEST-001",
        "year": 2024,
        "horsepower": 150,
        "fuel_capacity_liters": 200,
        "field_id": "field_test",
        "location_name": "Test Location",
    }


class TestHealthEndpoint:
    """Health check endpoint tests"""

    def test_health_check(self, client):
        """Test health check returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "sahool-equipment-service" in data["service"]


class TestEquipmentList:
    """Equipment listing tests"""

    def test_list_equipment(self, mock_repo, client):
        """Test listing all equipment"""
        mock_repo.list_equipment.return_value = ([], 0)
        response = client.get("/api/v1/equipment")
        assert response.status_code == 200
        data = response.json()
        assert "equipment" in data
        assert "total" in data
        assert isinstance(data["equipment"], list)

    def test_list_equipment_with_type_filter(self, mock_repo, client):
        """Test filtering equipment by type"""
        row = _make_equipment_row(equipment_type="tractor")
        mock_repo.list_equipment.return_value = ([row], 1)
        response = client.get("/api/v1/equipment?equipment_type=tractor")
        assert response.status_code == 200
        data = response.json()
        for eq in data["equipment"]:
            assert eq["equipment_type"] == "tractor"

    def test_list_equipment_with_status_filter(self, mock_repo, client):
        """Test filtering equipment by status"""
        row = _make_equipment_row(status="operational")
        mock_repo.list_equipment.return_value = ([row], 1)
        response = client.get("/api/v1/equipment?status=operational")
        assert response.status_code == 200
        data = response.json()
        for eq in data["equipment"]:
            assert eq["status"] == "operational"

    def test_list_equipment_pagination(self, mock_repo, client):
        """Test equipment list pagination"""
        mock_repo.list_equipment.return_value = ([], 0)
        response = client.get("/api/v1/equipment?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 2
        assert data["offset"] == 0


class TestEquipmentStats:
    """Equipment statistics tests"""

    def test_get_stats(self, mock_repo, client):
        """Test getting equipment statistics"""
        mock_repo.get_equipment_stats.return_value = {
            "total": 5,
            "by_type": {"tractor": 3, "pump": 1, "drone": 1},
            "by_status": {"operational": 3, "maintenance": 1, "inactive": 1},
            "operational": 3,
            "maintenance": 1,
            "inactive": 1,
        }
        response = client.get("/api/v1/equipment/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_type" in data
        assert "by_status" in data
        assert "operational" in data


class TestEquipmentAlerts:
    """Maintenance alerts tests"""

    def test_get_alerts(self, mock_repo, client):
        """Test getting maintenance alerts"""
        mock_repo.get_maintenance_alerts.return_value = []
        response = client.get("/api/v1/equipment/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "count" in data
        assert "overdue_count" in data

    def test_get_alerts_by_priority(self, mock_repo, client):
        """Test filtering alerts by priority"""
        alert = MagicMock(
            alert_id="alert_001",
            equipment_id="eq_001",
            equipment_name="Test",
            maintenance_type="oil_change",
            description="Test",
            description_ar=None,
            priority="high",
            due_at=None,
            due_hours=None,
            is_overdue=False,
            created_at=NOW,
        )
        mock_repo.get_maintenance_alerts.return_value = [alert]
        response = client.get("/api/v1/equipment/alerts?priority=high")
        assert response.status_code == 200
        data = response.json()
        for a in data["alerts"]:
            assert a["priority"] == "high"

    def test_get_overdue_alerts(self, mock_repo, client):
        """Test filtering overdue alerts"""
        alert = MagicMock(
            alert_id="alert_002",
            equipment_id="eq_002",
            equipment_name="Test",
            maintenance_type="battery_check",
            description="Overdue",
            description_ar=None,
            priority="high",
            due_at=NOW - timedelta(days=2),
            due_hours=None,
            is_overdue=True,
            created_at=NOW,
        )
        mock_repo.get_maintenance_alerts.return_value = [alert]
        response = client.get("/api/v1/equipment/alerts?overdue_only=true")
        assert response.status_code == 200
        data = response.json()
        for a in data["alerts"]:
            assert a["is_overdue"] is True


class TestEquipmentCRUD:
    """Equipment CRUD operations tests"""

    def test_create_equipment(self, mock_repo, client, sample_equipment):
        """Test creating new equipment"""
        mock_repo.create_equipment.side_effect = lambda db, eq: eq
        response = client.post("/api/v1/equipment", json=sample_equipment)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_equipment["name"]
        assert data["equipment_type"] == sample_equipment["equipment_type"]
        assert data["status"] == "operational"
        assert "qr_code" in data
        assert data["equipment_id"] is not None

    def test_get_equipment_by_id(self, mock_repo, client):
        """Test getting equipment by ID"""
        mock_repo.get_equipment.return_value = _make_equipment_row()
        response = client.get("/api/v1/equipment/eq_001")
        assert response.status_code == 200
        data = response.json()
        assert data["equipment_id"] == "eq_001"

    def test_get_equipment_not_found(self, mock_repo, client):
        """Test getting non-existent equipment"""
        mock_repo.get_equipment.return_value = None
        response = client.get("/api/v1/equipment/nonexistent_id")
        assert response.status_code == 404

    def test_get_equipment_by_qr(self, mock_repo, client):
        """Test getting equipment by QR code"""
        mock_repo.get_equipment_by_qr.return_value = _make_equipment_row(qr_code="QR_EQ001_JD8R410")
        response = client.get("/api/v1/equipment/qr/QR_EQ001_JD8R410")
        assert response.status_code == 200
        data = response.json()
        assert data["qr_code"] == "QR_EQ001_JD8R410"

    def test_update_equipment(self, mock_repo, client):
        """Test updating equipment"""
        updated_row = _make_equipment_row(name="Updated Name", status="maintenance")
        mock_repo.update_equipment.return_value = updated_row
        update_data = {
            "name": "Updated Name",
            "status": "maintenance",
        }
        response = client.put("/api/v1/equipment/eq_001", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["status"] == "maintenance"

    def test_update_equipment_status(self, mock_repo, client):
        """Test updating equipment status"""
        mock_repo.update_equipment.return_value = _make_equipment_row(status="operational")
        response = client.post("/api/v1/equipment/eq_001/status?status=operational")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"


class TestEquipmentLocation:
    """Equipment location tracking tests"""

    def test_update_location(self, mock_repo, client):
        """Test updating equipment GPS location"""
        mock_repo.update_equipment.return_value = _make_equipment_row(
            current_lat=15.5,
            current_lon=44.2,
            location_name="New Location",
        )
        response = client.post("/api/v1/equipment/eq_001/location?lat=15.5&lon=44.2&location_name=New%20Location")
        assert response.status_code == 200
        data = response.json()
        assert data["current_lat"] == 15.5
        assert data["current_lon"] == 44.2
        assert data["location_name"] == "New Location"


class TestEquipmentTelemetry:
    """Equipment telemetry tests"""

    def test_update_telemetry(self, mock_repo, client):
        """Test updating equipment telemetry data"""
        mock_repo.update_equipment.return_value = _make_equipment_row(
            current_fuel_percent=80,
            current_hours=1300,
        )
        response = client.post("/api/v1/equipment/eq_001/telemetry?fuel_percent=80&hours=1300")
        assert response.status_code == 200
        data = response.json()
        assert data["current_fuel_percent"] == 80
        assert data["current_hours"] == 1300


class TestEquipmentMaintenance:
    """Equipment maintenance tests"""

    def test_get_maintenance_history(self, mock_repo, client):
        """Test getting maintenance history"""
        mock_repo.get_equipment.return_value = _make_equipment_row()
        mock_repo.get_maintenance_history.return_value = []
        response = client.get("/api/v1/equipment/eq_001/maintenance")
        assert response.status_code == 200
        data = response.json()
        assert "equipment_id" in data
        assert "records" in data
        assert "count" in data

    def test_add_maintenance_record(self, mock_repo, client):
        """Test adding a maintenance record"""
        mock_repo.get_equipment.return_value = _make_equipment_row()
        mock_repo.create_maintenance_record.side_effect = lambda db, rec: rec
        mock_repo.update_equipment.return_value = _make_equipment_row()
        response = client.post(
            "/api/v1/equipment/eq_001/maintenance"
            "?maintenance_type=oil_change"
            "&description=Regular%20oil%20change"
            "&performed_by=technician_1"
            "&cost=150"
        )
        assert response.status_code == 201
        data = response.json()
        assert data["maintenance_type"] == "oil_change"
        assert data["description"] == "Regular oil change"
        assert data["cost"] == 150


class TestEquipmentDelete:
    """Equipment deletion tests"""

    def test_delete_equipment(self, mock_repo, client, sample_equipment):
        """Test deleting equipment"""
        # Mock create
        mock_repo.create_equipment.side_effect = lambda db, eq: eq

        # First create
        create_response = client.post("/api/v1/equipment", json=sample_equipment)
        equipment_id = create_response.json()["equipment_id"]

        # Mock delete
        mock_repo.delete_equipment.return_value = True

        # Then delete
        response = client.delete(f"/api/v1/equipment/{equipment_id}")
        assert response.status_code == 204

        # Mock not found for verify
        mock_repo.get_equipment.return_value = None

        # Verify deleted
        get_response = client.get(f"/api/v1/equipment/{equipment_id}")
        assert get_response.status_code == 404


class TestEquipmentTypes:
    """Equipment type enum tests"""

    def test_all_equipment_types_valid(self, mock_repo, client):
        """Test that all equipment types are accepted"""
        mock_repo.create_equipment.side_effect = lambda db, eq: eq
        types = [
            "tractor",
            "pump",
            "drone",
            "harvester",
            "sprayer",
            "pivot",
            "sensor",
            "vehicle",
            "other",
        ]
        for eq_type in types:
            data = {
                "name": f"Test {eq_type}",
                "equipment_type": eq_type,
            }
            response = client.post("/api/v1/equipment", json=data)
            assert response.status_code == 201, f"Failed for type: {eq_type}"


class TestMaintenanceTypes:
    """Maintenance type enum tests"""

    def test_all_maintenance_types_valid(self, mock_repo, client):
        """Test that all maintenance types are accepted"""
        mock_repo.get_equipment.return_value = _make_equipment_row()
        mock_repo.create_maintenance_record.side_effect = lambda db, rec: rec
        mock_repo.update_equipment.return_value = _make_equipment_row()
        types = [
            "oil_change",
            "filter_change",
            "tire_check",
            "battery_check",
            "calibration",
            "general_service",
            "repair",
            "other",
        ]
        for m_type in types:
            response = client.post(
                f"/api/v1/equipment/eq_001/maintenance?maintenance_type={m_type}&description=Test%20{m_type}"
            )
            assert response.status_code == 201, f"Failed for type: {m_type}"
