"""
SAHOOL Equipment Service - Unit Tests
اختبارات خدمة إدارة المعدات
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app, equipment_db, EquipmentType, EquipmentStatus


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


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

    def test_list_equipment(self, client):
        """Test listing all equipment"""
        response = client.get("/api/v1/equipment")
        assert response.status_code == 200
        data = response.json()
        assert "equipment" in data
        assert "total" in data
        assert isinstance(data["equipment"], list)

    def test_list_equipment_with_type_filter(self, client):
        """Test filtering equipment by type"""
        response = client.get("/api/v1/equipment?equipment_type=tractor")
        assert response.status_code == 200
        data = response.json()
        for eq in data["equipment"]:
            assert eq["equipment_type"] == "tractor"

    def test_list_equipment_with_status_filter(self, client):
        """Test filtering equipment by status"""
        response = client.get("/api/v1/equipment?status=operational")
        assert response.status_code == 200
        data = response.json()
        for eq in data["equipment"]:
            assert eq["status"] == "operational"

    def test_list_equipment_pagination(self, client):
        """Test equipment list pagination"""
        response = client.get("/api/v1/equipment?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 2
        assert data["offset"] == 0


class TestEquipmentStats:
    """Equipment statistics tests"""

    def test_get_stats(self, client):
        """Test getting equipment statistics"""
        response = client.get("/api/v1/equipment/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_type" in data
        assert "by_status" in data
        assert "operational" in data


class TestEquipmentAlerts:
    """Maintenance alerts tests"""

    def test_get_alerts(self, client):
        """Test getting maintenance alerts"""
        response = client.get("/api/v1/equipment/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "count" in data
        assert "overdue_count" in data

    def test_get_alerts_by_priority(self, client):
        """Test filtering alerts by priority"""
        response = client.get("/api/v1/equipment/alerts?priority=high")
        assert response.status_code == 200
        data = response.json()
        for alert in data["alerts"]:
            assert alert["priority"] == "high"

    def test_get_overdue_alerts(self, client):
        """Test filtering overdue alerts"""
        response = client.get("/api/v1/equipment/alerts?overdue_only=true")
        assert response.status_code == 200
        data = response.json()
        for alert in data["alerts"]:
            assert alert["is_overdue"] is True


class TestEquipmentCRUD:
    """Equipment CRUD operations tests"""

    def test_create_equipment(self, client, sample_equipment):
        """Test creating new equipment"""
        response = client.post("/api/v1/equipment", json=sample_equipment)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_equipment["name"]
        assert data["equipment_type"] == sample_equipment["equipment_type"]
        assert data["status"] == "operational"
        assert "qr_code" in data
        assert data["equipment_id"] is not None

    def test_get_equipment_by_id(self, client):
        """Test getting equipment by ID"""
        # Use demo data
        response = client.get("/api/v1/equipment/eq_001")
        assert response.status_code == 200
        data = response.json()
        assert data["equipment_id"] == "eq_001"

    def test_get_equipment_not_found(self, client):
        """Test getting non-existent equipment"""
        response = client.get("/api/v1/equipment/nonexistent_id")
        assert response.status_code == 404

    def test_get_equipment_by_qr(self, client):
        """Test getting equipment by QR code"""
        response = client.get("/api/v1/equipment/qr/QR_EQ001_JD8R410")
        assert response.status_code == 200
        data = response.json()
        assert data["qr_code"] == "QR_EQ001_JD8R410"

    def test_update_equipment(self, client):
        """Test updating equipment"""
        update_data = {
            "name": "Updated Name",
            "status": "maintenance",
        }
        response = client.put("/api/v1/equipment/eq_001", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["status"] == "maintenance"

    def test_update_equipment_status(self, client):
        """Test updating equipment status"""
        response = client.post("/api/v1/equipment/eq_001/status?status=operational")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"


class TestEquipmentLocation:
    """Equipment location tracking tests"""

    def test_update_location(self, client):
        """Test updating equipment GPS location"""
        response = client.post(
            "/api/v1/equipment/eq_001/location?lat=15.5&lon=44.2&location_name=New%20Location"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["current_lat"] == 15.5
        assert data["current_lon"] == 44.2
        assert data["location_name"] == "New Location"


class TestEquipmentTelemetry:
    """Equipment telemetry tests"""

    def test_update_telemetry(self, client):
        """Test updating equipment telemetry data"""
        response = client.post(
            "/api/v1/equipment/eq_001/telemetry?fuel_percent=80&hours=1300"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["current_fuel_percent"] == 80
        assert data["current_hours"] == 1300


class TestEquipmentMaintenance:
    """Equipment maintenance tests"""

    def test_get_maintenance_history(self, client):
        """Test getting maintenance history"""
        response = client.get("/api/v1/equipment/eq_001/maintenance")
        assert response.status_code == 200
        data = response.json()
        assert "equipment_id" in data
        assert "records" in data
        assert "count" in data

    def test_add_maintenance_record(self, client):
        """Test adding a maintenance record"""
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

    def test_delete_equipment(self, client, sample_equipment):
        """Test deleting equipment"""
        # First create
        create_response = client.post("/api/v1/equipment", json=sample_equipment)
        equipment_id = create_response.json()["equipment_id"]

        # Then delete
        response = client.delete(f"/api/v1/equipment/{equipment_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api/v1/equipment/{equipment_id}")
        assert get_response.status_code == 404


class TestEquipmentTypes:
    """Equipment type enum tests"""

    def test_all_equipment_types_valid(self, client):
        """Test that all equipment types are accepted"""
        types = ["tractor", "pump", "drone", "harvester", "sprayer", "pivot", "sensor", "vehicle", "other"]
        for eq_type in types:
            data = {
                "name": f"Test {eq_type}",
                "equipment_type": eq_type,
            }
            response = client.post("/api/v1/equipment", json=data)
            assert response.status_code == 201, f"Failed for type: {eq_type}"


class TestMaintenanceTypes:
    """Maintenance type enum tests"""

    def test_all_maintenance_types_valid(self, client):
        """Test that all maintenance types are accepted"""
        types = [
            "oil_change", "filter_change", "tire_check",
            "battery_check", "calibration", "general_service", "repair", "other"
        ]
        for m_type in types:
            response = client.post(
                f"/api/v1/equipment/eq_001/maintenance"
                f"?maintenance_type={m_type}"
                f"&description=Test%20{m_type}"
            )
            assert response.status_code == 201, f"Failed for type: {m_type}"
