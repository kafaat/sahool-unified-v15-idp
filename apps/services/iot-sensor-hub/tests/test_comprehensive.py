"""
Comprehensive unit tests for IoT Sensor Hub Service.
Tests cover: KalmanFilter, OfflineCache, IoTSensorEngine, WDI, alerts, models, API endpoints.
Target: >60% code coverage.
"""

import os
import sys
from collections import deque
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add service directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from src.main import (
    ALERT_THRESHOLDS,
    SENSOR_RANGES,
    Alert,
    AlertSeverity,
    IoTSensorEngine,
    KalmanFilter,
    NodeRegistration,
    NodeStatus,
    NodeType,
    OfflineCache,
    SensorReading,
    SensorReadingBatch,
    SensorType,
    WDIRequest,
    WDIResponse,
    app,
    iot_engine,
)

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_engine():
    """Reset engine state before each test."""
    iot_engine.nodes.clear()
    iot_engine.kalman_filters.clear()
    iot_engine.offline_cache._cache.clear()
    iot_engine.readings_buffer.clear()
    iot_engine.alerts.clear()
    iot_engine.stats["total_readings"] = 0
    iot_engine.stats["filtered_readings"] = 0
    iot_engine.stats["alerts_generated"] = 0
    yield


class _TenantClient:
    """Wrapper that adds X-Tenant-ID header to all requests."""

    def __init__(self, client):
        self._client = client

    def get(self, url, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.setdefault("X-Tenant-ID", "00000000-0000-0000-0000-000000000001")
        return self._client.get(url, headers=headers, **kwargs)

    def post(self, url, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.setdefault("X-Tenant-ID", "00000000-0000-0000-0000-000000000001")
        return self._client.post(url, headers=headers, **kwargs)


@pytest.fixture
def client():
    return _TenantClient(TestClient(app))


@pytest.fixture
def sample_node_reg() -> NodeRegistration:
    return NodeRegistration(
        node_id="TEST-NODE-001",
        node_type=NodeType.ESP32_LORA,
        name="Test Sensor Node",
        name_ar="عقدة اختبار",
        field_id="FIELD-TEST",
        sensors=[SensorType.SOIL_MOISTURE, SensorType.SOIL_TEMPERATURE],
        latitude=15.35,
        longitude=44.20,
        firmware_version="1.0.0",
        battery_level=95.0,
    )


@pytest.fixture
def sample_reading() -> SensorReading:
    return SensorReading(
        node_id="TEST-NODE-001",
        sensor_type=SensorType.SOIL_MOISTURE,
        value=45.0,
        unit="%",
        quality=0.9,
    )


# ---------------------------------------------------------------------------
# Test Enums
# ---------------------------------------------------------------------------

class TestEnums:
    def test_sensor_type_values(self):
        assert SensorType.SOIL_MOISTURE == "soil_moisture"
        assert SensorType.WATER_PH == "water_ph"
        assert len(list(SensorType)) == 15

    def test_node_type_values(self):
        assert NodeType.ESP32_LORA == "esp32_lora"
        assert NodeType.COMMERCIAL == "commercial"

    def test_alert_severity_values(self):
        assert AlertSeverity.CRITICAL == "critical"
        assert AlertSeverity.INFO == "info"


# ---------------------------------------------------------------------------
# Test KalmanFilter
# ---------------------------------------------------------------------------

class TestKalmanFilter:
    def test_first_measurement_returns_input(self):
        kf = KalmanFilter()
        result = kf.update(42.0)
        assert result == 42.0
        assert kf.initialized is True

    def test_second_measurement_filtered(self):
        kf = KalmanFilter()
        kf.update(40.0)
        result = kf.update(50.0)
        # Should be between 40 and 50 (filtered)
        assert 40.0 < result < 50.0

    def test_convergence_to_stable_signal(self):
        kf = KalmanFilter()
        for _ in range(20):
            result = kf.update(100.0)
        # Should converge very close to 100
        assert abs(result - 100.0) < 1.0

    def test_filters_noise(self):
        """Noisy readings around 50 should be smoothed."""
        kf = KalmanFilter(process_variance=0.01, measurement_variance=0.5)
        import random
        random.seed(42)
        readings = [50.0 + random.gauss(0, 5) for _ in range(50)]
        results = [kf.update(r) for r in readings]
        # Filtered variance should be less than input variance
        input_var = sum((r - 50) ** 2 for r in readings) / len(readings)
        output_var = sum((r - 50) ** 2 for r in results[10:]) / len(results[10:])
        assert output_var < input_var

    def test_custom_variance_parameters(self):
        kf = KalmanFilter(process_variance=0.1, measurement_variance=1.0)
        assert kf.process_var == 0.1
        assert kf.measurement_var == 1.0
        assert kf.initialized is False


# ---------------------------------------------------------------------------
# Test OfflineCache
# ---------------------------------------------------------------------------

class TestOfflineCache:
    def test_store_and_retrieve(self):
        cache = OfflineCache(max_hours=72)
        cache.store({"value": 42, "_cached_at": datetime.utcnow().isoformat()})
        assert cache.size == 1
        pending = cache.get_pending(10)
        assert len(pending) == 1

    def test_clear_synced(self):
        cache = OfflineCache()
        for i in range(5):
            cache.store({"value": i})
        assert cache.size == 5
        cache.clear_synced(3)
        assert cache.size == 2

    def test_clear_synced_more_than_available(self):
        cache = OfflineCache()
        cache.store({"value": 1})
        cache.clear_synced(100)
        assert cache.size == 0

    def test_maxlen_respected(self):
        cache = OfflineCache()
        # deque maxlen is 100000, just test it works
        assert cache._cache.maxlen == 100000

    def test_get_pending_with_limit(self):
        cache = OfflineCache()
        for i in range(10):
            cache.store({"value": i})
        result = cache.get_pending(3)
        assert len(result) == 3

    def test_size_property(self):
        cache = OfflineCache()
        assert cache.size == 0
        cache.store({"value": 1})
        assert cache.size == 1


# ---------------------------------------------------------------------------
# Test IoTSensorEngine
# ---------------------------------------------------------------------------

class TestIoTSensorEngine:
    def test_register_node(self, sample_node_reg):
        engine = IoTSensorEngine()
        result = engine.register_node(sample_node_reg)
        assert result["node_id"] == "TEST-NODE-001"
        assert result["online"] is True
        assert "TEST-NODE-001" in engine.nodes

    def test_process_valid_reading(self, sample_node_reg, sample_reading):
        engine = IoTSensorEngine()
        engine.register_node(sample_node_reg)
        result = engine.process_reading(sample_reading)
        assert result["status"] == "accepted"
        assert "filtered_value" in result
        assert engine.stats["total_readings"] == 1

    def test_process_out_of_range_reading(self, sample_node_reg):
        engine = IoTSensorEngine()
        engine.register_node(sample_node_reg)
        reading = SensorReading(
            node_id="TEST-NODE-001",
            sensor_type=SensorType.SOIL_MOISTURE,
            value=150.0,  # Out of range (0-100)
        )
        result = engine.process_reading(reading)
        assert result["status"] == "rejected"
        assert "outside range" in result["reason"]

    def test_process_negative_out_of_range(self, sample_node_reg):
        engine = IoTSensorEngine()
        reading = SensorReading(
            node_id="TEST-NODE-001",
            sensor_type=SensorType.SOIL_MOISTURE,
            value=-5.0,
        )
        result = engine.process_reading(reading)
        assert result["status"] == "rejected"

    def test_updates_node_status(self, sample_node_reg, sample_reading):
        engine = IoTSensorEngine()
        engine.register_node(sample_node_reg)
        engine.process_reading(sample_reading)
        node = engine.nodes["TEST-NODE-001"]
        assert node["last_seen"] is not None
        assert node["online"] is True
        assert node["readings_count"] == 1

    def test_stores_in_offline_cache(self, sample_node_reg, sample_reading):
        engine = IoTSensorEngine()
        engine.register_node(sample_node_reg)
        engine.process_reading(sample_reading)
        assert engine.offline_cache.size == 1

    def test_critical_low_alert(self, sample_node_reg):
        engine = IoTSensorEngine()
        engine.register_node(sample_node_reg)
        reading = SensorReading(
            node_id="TEST-NODE-001",
            sensor_type=SensorType.SOIL_MOISTURE,
            value=10.0,  # Below critical_low threshold (15)
        )
        result = engine.process_reading(reading)
        assert result["status"] == "accepted"
        assert len(result["alerts"]) > 0
        assert result["alerts"][0]["severity"] == "critical"

    def test_warning_low_alert(self, sample_node_reg):
        engine = IoTSensorEngine()
        engine.register_node(sample_node_reg)
        reading = SensorReading(
            node_id="TEST-NODE-001",
            sensor_type=SensorType.SOIL_MOISTURE,
            value=20.0,  # Below warning_low (25) but above critical_low (15)
        )
        result = engine.process_reading(reading)
        assert result["status"] == "accepted"
        assert len(result["alerts"]) > 0
        assert result["alerts"][0]["severity"] == "warning"

    def test_critical_high_alert(self, sample_node_reg):
        engine = IoTSensorEngine()
        engine.register_node(sample_node_reg)
        reading = SensorReading(
            node_id="TEST-NODE-001",
            sensor_type=SensorType.SOIL_MOISTURE,
            value=96.0,  # Above critical_high (95)
        )
        result = engine.process_reading(reading)
        assert result["status"] == "accepted"
        assert len(result["alerts"]) > 0
        assert any(a["severity"] == "critical" for a in result["alerts"])

    def test_warning_high_alert(self, sample_node_reg):
        engine = IoTSensorEngine()
        engine.register_node(sample_node_reg)
        reading = SensorReading(
            node_id="TEST-NODE-001",
            sensor_type=SensorType.SOIL_MOISTURE,
            value=92.0,  # Above warning_high (90) but below critical_high (95)
        )
        result = engine.process_reading(reading)
        assert result["status"] == "accepted"
        assert len(result["alerts"]) > 0
        assert any(a["severity"] == "warning" for a in result["alerts"])

    def test_no_alert_normal_reading(self, sample_node_reg, sample_reading):
        engine = IoTSensorEngine()
        engine.register_node(sample_node_reg)
        result = engine.process_reading(sample_reading)
        assert result["status"] == "accepted"
        assert len(result["alerts"]) == 0

    def test_reading_without_registered_node(self, sample_reading):
        """Reading from unregistered node should still be accepted."""
        engine = IoTSensorEngine()
        result = engine.process_reading(sample_reading)
        assert result["status"] == "accepted"


# ---------------------------------------------------------------------------
# Test WDI Calculation
# ---------------------------------------------------------------------------

class TestWDICalculation:
    def test_high_stress_irrigate(self):
        engine = IoTSensorEngine()
        req = WDIRequest(
            field_id="FIELD-001",
            soil_moisture=10.0,
            temperature=45.0,
            humidity=15.0,
            wind_speed=8.0,
            solar_radiation=28.0,
        )
        result = engine.calculate_wdi(req)
        assert result.wdi >= 0.7
        assert result.irrigate is True
        assert result.confidence == 0.95
        assert "immediately" in result.decision.lower()

    def test_moderate_stress_schedule(self):
        engine = IoTSensorEngine()
        req = WDIRequest(
            field_id="FIELD-001",
            soil_moisture=25.0,
            temperature=35.0,
            humidity=30.0,
            wind_speed=4.0,
            solar_radiation=22.0,
        )
        result = engine.calculate_wdi(req)
        assert 0.5 <= result.wdi < 0.7
        assert result.irrigate is True

    def test_low_stress_no_irrigation(self):
        engine = IoTSensorEngine()
        req = WDIRequest(
            field_id="FIELD-001",
            soil_moisture=70.0,
            temperature=25.0,
            humidity=70.0,
            wind_speed=1.0,
            solar_radiation=10.0,
        )
        result = engine.calculate_wdi(req)
        assert result.wdi < 0.3
        assert result.irrigate is False
        assert "No irrigation" in result.decision

    def test_wdi_clamped_to_0_1(self):
        engine = IoTSensorEngine()
        req = WDIRequest(
            field_id="FIELD-001",
            soil_moisture=0.0,
            temperature=60.0,
            humidity=0.0,
            wind_speed=50.0,
            solar_radiation=50.0,
        )
        result = engine.calculate_wdi(req)
        assert 0.0 <= result.wdi <= 1.0

    def test_wdi_components_present(self):
        engine = IoTSensorEngine()
        req = WDIRequest(
            field_id="FIELD-001",
            soil_moisture=40.0,
            temperature=30.0,
        )
        result = engine.calculate_wdi(req)
        assert "soil_moisture_stress" in result.components
        assert "temperature_stress" in result.components
        assert "humidity_stress" in result.components
        assert "wind_stress" in result.components
        assert "radiation_stress" in result.components

    def test_wdi_response_has_bilingual_decision(self):
        engine = IoTSensorEngine()
        req = WDIRequest(
            field_id="FIELD-001",
            soil_moisture=10.0,
            temperature=45.0,
        )
        result = engine.calculate_wdi(req)
        assert len(result.decision) > 0
        assert len(result.decision_ar) > 0


# ---------------------------------------------------------------------------
# Test Pydantic Models
# ---------------------------------------------------------------------------

class TestModels:
    def test_sensor_reading_defaults(self):
        r = SensorReading(
            node_id="N1",
            sensor_type=SensorType.SOIL_MOISTURE,
            value=50.0,
        )
        assert r.quality == 1.0
        assert r.unit == ""
        assert r.latitude is None

    def test_sensor_reading_batch(self):
        batch = SensorReadingBatch(
            readings=[
                SensorReading(node_id="N1", sensor_type=SensorType.SOIL_MOISTURE, value=50.0),
                SensorReading(node_id="N1", sensor_type=SensorType.SOIL_TEMPERATURE, value=22.0),
            ],
            field_id="F1",
            tenant_id="T1",
        )
        assert len(batch.readings) == 2

    def test_node_registration_model(self, sample_node_reg):
        assert sample_node_reg.node_id == "TEST-NODE-001"
        assert sample_node_reg.node_type == NodeType.ESP32_LORA
        assert len(sample_node_reg.sensors) == 2

    def test_wdi_request_defaults(self):
        req = WDIRequest(
            field_id="F1",
            soil_moisture=40.0,
            temperature=25.0,
        )
        assert req.humidity == 50.0
        assert req.w_moisture == 0.35
        assert req.w_temperature == 0.25

    def test_alert_model(self):
        alert = Alert(
            alert_id="test-alert",
            severity=AlertSeverity.WARNING,
            sensor_type="soil_moisture",
            node_id="N1",
            field_id="F1",
            value=20.0,
            threshold=25.0,
            message="Warning test",
            message_ar="تحذير",
            timestamp=datetime.utcnow(),
        )
        assert alert.severity == AlertSeverity.WARNING


# ---------------------------------------------------------------------------
# Test Sensor Ranges & Alert Thresholds Constants
# ---------------------------------------------------------------------------

class TestSensorRangesAndThresholds:
    def test_all_sensor_types_have_ranges(self):
        for st in SensorType:
            assert st in SENSOR_RANGES, f"Missing range for {st}"

    def test_ranges_are_valid(self):
        for st, (lo, hi) in SENSOR_RANGES.items():
            assert lo < hi, f"Invalid range for {st}: {lo} >= {hi}"

    def test_alert_thresholds_subset_of_sensor_types(self):
        for key in ALERT_THRESHOLDS:
            assert key in SENSOR_RANGES


# ---------------------------------------------------------------------------
# Test API Endpoints
# ---------------------------------------------------------------------------

class TestAPIEndpoints:
    def test_healthz(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_readyz(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200

    def test_register_and_list_nodes(self, client):
        client.post(
            "/api/v1/iot/nodes",
            json={
                "node_id": "API-NODE",
                "node_type": "esp32_lora",
                "name": "API Test Node",
                "field_id": "FIELD-API",
                "sensors": ["soil_moisture"],
                "latitude": 15.35,
                "longitude": 44.20,
            },
        )
        response = client.get("/api/v1/iot/nodes")
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_list_nodes_filter_by_field(self, client):
        client.post(
            "/api/v1/iot/nodes",
            json={
                "node_id": "FILTER-NODE",
                "node_type": "esp32_wifi",
                "name": "Filter Test",
                "field_id": "FIELD-FILTER",
                "sensors": ["air_temperature"],
                "latitude": 15.0,
                "longitude": 44.0,
            },
        )
        response = client.get("/api/v1/iot/nodes", params={"field_id": "FIELD-FILTER"})
        assert response.status_code == 200
        nodes = response.json()["nodes"]
        assert all(n["field_id"] == "FIELD-FILTER" for n in nodes)

    def test_get_node_not_found(self, client):
        response = client.get("/api/v1/iot/nodes/NONEXISTENT")
        assert response.status_code == 404

    def test_ingest_and_get_stats(self, client):
        client.post(
            "/api/v1/iot/readings",
            json={
                "node_id": "STAT-NODE",
                "sensor_type": "air_temperature",
                "value": 25.0,
            },
        )
        response = client.get("/api/v1/iot/stats")
        assert response.status_code == 200
        assert response.json()["total_readings"] >= 1

    def test_sensor_types_endpoint(self, client):
        response = client.get("/api/v1/iot/sensor-types")
        assert response.status_code == 200
        types = response.json()["sensor_types"]
        assert len(types) == len(list(SensorType))

    def test_wdi_endpoint(self, client):
        response = client.post(
            "/api/v1/iot/wdi",
            json={
                "field_id": "FIELD-WDI",
                "soil_moisture": 30.0,
                "temperature": 35.0,
                "humidity": 25.0,
                "wind_speed": 3.0,
                "solar_radiation": 20.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "wdi" in data
        assert "decision" in data
        assert "irrigate" in data

    def test_alerts_endpoint(self, client):
        response = client.get("/api/v1/iot/alerts")
        assert response.status_code == 200
        assert "alerts" in response.json()

    def test_cache_status(self, client):
        response = client.get("/api/v1/iot/cache/status")
        assert response.status_code == 200
        assert "cache_size" in response.json()

    def test_batch_ingestion_api(self, client):
        response = client.post(
            "/api/v1/iot/readings/batch",
            json={
                "readings": [
                    {"node_id": "BATCH-N", "sensor_type": "soil_moisture", "value": 40.0},
                    {"node_id": "BATCH-N", "sensor_type": "soil_temperature", "value": 22.0},
                    {"node_id": "BATCH-N", "sensor_type": "soil_moisture", "value": 999.0},
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["accepted"] == 2
        assert data["rejected"] == 1
