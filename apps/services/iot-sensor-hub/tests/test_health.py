"""Tests for iot-sensor-hub health and core endpoints."""
import os
import sys

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from src.main import app

TENANT_HEADER = {"X-Tenant-ID": "00000000-0000-0000-0000-000000000001"}
@pytest.fixture
def client():
    return TestClient(app, headers=TENANT_HEADER)
@pytest.mark.unit
class TestHealthEndpoints:
    def test_healthz(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "iot-sensor-hub"

    def test_readyz(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
@pytest.mark.unit
class TestNodeManagement:
    def test_register_node(self, client):
        response = client.post(
            "/api/v1/iot/nodes",
            json={
                "node_id": "NODE-001",
                "node_type": "esp32_lora",
                "name": "Field Sensor 1",
                "field_id": "FIELD-001",
                "sensors": ["soil_moisture", "soil_temperature"],
                "latitude": 15.35,
                "longitude": 44.20,
            },
        )
        assert response.status_code == 201
        assert response.json()["status"] == "registered"

    def test_list_nodes(self, client):
        # Register first
        client.post(
            "/api/v1/iot/nodes",
            json={
                "node_id": "NODE-002",
                "node_type": "esp32_lora",
                "name": "Field Sensor 2",
                "field_id": "FIELD-001",
                "sensors": ["soil_moisture"],
                "latitude": 15.35,
                "longitude": 44.20,
            },
        )
        response = client.get("/api/v1/iot/nodes")
        assert response.status_code == 200
        assert response.json()["total"] > 0
@pytest.mark.unit
class TestSensorIngestion:
    def test_ingest_valid_reading(self, client):
        # Register node first
        client.post(
            "/api/v1/iot/nodes",
            json={
                "node_id": "NODE-003",
                "node_type": "esp32_lora",
                "name": "Test Sensor",
                "field_id": "FIELD-001",
                "sensors": ["soil_moisture"],
                "latitude": 15.35,
                "longitude": 44.20,
            },
        )

        response = client.post(
            "/api/v1/iot/readings",
            json={
                "node_id": "NODE-003",
                "sensor_type": "soil_moisture",
                "value": 45.0,
                "unit": "%",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert "filtered_value" in data

    def test_reject_out_of_range(self, client):
        response = client.post(
            "/api/v1/iot/readings",
            json={
                "node_id": "NODE-003",
                "sensor_type": "soil_moisture",
                "value": 150.0,  # Out of range (0-100)
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "rejected"

    def test_batch_ingestion(self, client):
        response = client.post(
            "/api/v1/iot/readings/batch",
            json={
                "readings": [
                    {"node_id": "NODE-003", "sensor_type": "soil_moisture", "value": 40.0},
                    {"node_id": "NODE-003", "sensor_type": "soil_temperature", "value": 22.0},
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["accepted"] == 2
@pytest.mark.unit
class TestWDI:
    def test_wdi_high_stress(self, client):
        response = client.post(
            "/api/v1/iot/wdi",
            json={
                "field_id": "FIELD-001",
                "soil_moisture": 15.0,
                "temperature": 42.0,
                "humidity": 20.0,
                "wind_speed": 5.0,
                "solar_radiation": 28.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["wdi"] > 0.5
        assert data["irrigate"] is True

    def test_wdi_low_stress(self, client):
        response = client.post(
            "/api/v1/iot/wdi",
            json={
                "field_id": "FIELD-001",
                "soil_moisture": 60.0,
                "temperature": 25.0,
                "humidity": 65.0,
                "wind_speed": 1.0,
                "solar_radiation": 15.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["wdi"] < 0.5
        assert data["irrigate"] is False
@pytest.mark.unit
class TestAlerts:
    def test_critical_alert_generated(self, client):
        """Test that critical low soil moisture triggers alert."""
        client.post(
            "/api/v1/iot/nodes",
            json={
                "node_id": "ALERT-NODE",
                "node_type": "esp32_lora",
                "name": "Alert Test",
                "field_id": "FIELD-002",
                "sensors": ["soil_moisture"],
                "latitude": 15.35,
                "longitude": 44.20,
            },
        )
        response = client.post(
            "/api/v1/iot/readings",
            json={
                "node_id": "ALERT-NODE",
                "sensor_type": "soil_moisture",
                "value": 10.0,  # Below critical threshold (15)
            },
        )
        data = response.json()
        assert data["status"] == "accepted"
        assert len(data["alerts"]) > 0
        assert data["alerts"][0]["severity"] == "critical"

    def test_get_alerts(self, client):
        response = client.get("/api/v1/iot/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert isinstance(data["alerts"], list)

    def test_get_alerts_filtered(self, client):
        """Test alert filtering by severity."""
        response = client.get("/api/v1/iot/alerts", params={"severity": "critical"})
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert all(a["severity"] == "critical" for a in data["alerts"])
@pytest.mark.unit
class TestNodeDetail:
    def test_get_node_by_id(self, client):
        """Test getting a single node by ID."""
        client.post(
            "/api/v1/iot/nodes",
            json={
                "node_id": "DETAIL-NODE",
                "node_type": "esp32_lora",
                "name": "Detail Test",
                "field_id": "FIELD-003",
                "sensors": ["soil_moisture"],
                "latitude": 15.35,
                "longitude": 44.20,
            },
        )
        response = client.get("/api/v1/iot/nodes/DETAIL-NODE")
        assert response.status_code == 200
        data = response.json()
        assert "node" in data
        assert data["node"]["node_id"] == "DETAIL-NODE"
        assert "recent_readings" in data

    def test_get_nonexistent_node(self, client):
        """Test 404 for nonexistent node."""
        response = client.get("/api/v1/iot/nodes/DOES-NOT-EXIST")
        assert response.status_code == 404
@pytest.mark.unit
class TestCacheAndStats:
    def test_cache_status(self, client):
        response = client.get("/api/v1/iot/cache/status")
        assert response.status_code == 200
        assert "cache_size" in response.json()

    def test_cache_sync_preview(self, client):
        """Test cache sync preview (no clear)."""
        response = client.post("/api/v1/iot/cache/sync", params={"confirm_clear": False})
        assert response.status_code == 200
        data = response.json()
        assert data["cleared"] is False

    def test_cache_sync_with_clear(self, client):
        """Test cache sync with clear."""
        response = client.post("/api/v1/iot/cache/sync", params={"confirm_clear": True})
        assert response.status_code == 200
        data = response.json()
        assert data["cleared"] is True

    def test_reject_negative_value(self, client):
        """Test rejection of negative soil moisture."""
        response = client.post(
            "/api/v1/iot/readings",
            json={
                "node_id": "NODE-003",
                "sensor_type": "soil_moisture",
                "value": -5.0,
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "rejected"

    def test_stats(self, client):
        response = client.get("/api/v1/iot/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_readings" in data
        assert "nodes_registered" in data

    def test_sensor_types(self, client):
        response = client.get("/api/v1/iot/sensor-types")
        assert response.status_code == 200
        assert len(response.json()["sensor_types"]) > 0
