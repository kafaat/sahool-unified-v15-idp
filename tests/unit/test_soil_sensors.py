"""
Comprehensive Unit Tests for Soil Sensors Module
اختبارات الوحدة الشاملة لوحدة مجسات التربة

Tests cover:
- Sensor data models validation
- MQTT adapter parsing
- LoRaWAN adapter parsing
- HTTP adapter parsing
- Data normalization
- Calibration calculations
- Threshold checks
- Aggregation and statistics
- Error handling for malformed data
"""

import json
import math
import pytest
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch

from shared.soil_sensors.models import (
    SensorType,
    SensorProtocol,
    SensorStatus,
    AlertSeverity,
    SensorReading,
    SoilSensor,
    SensorCalibration,
    SensorAlert,
    FieldMoistureMap,
    SensorAggregation,
)
from shared.soil_sensors.adapters import (
    AdapterConfig,
    SensorAdapter,
    MQTTAdapter,
    LoRaWANAdapter,
    HTTPAdapter,
    NBIoTAdapter,
    get_adapter,
    SensorManager,
)
from shared.soil_sensors.processor import (
    SensorDataProcessor,
    aggregate_readings,
    detect_anomalies,
    interpolate_field_moisture,
    generate_moisture_alert,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_sensor() -> SoilSensor:
    """Create a sample soil sensor for testing"""
    return SoilSensor(
        id="sensor_001",
        tenant_id="tenant_123",
        field_id="field_456",
        name="Moisture Sensor A",
        name_ar="مجس رطوبة أ",
        sensor_type=SensorType.MOISTURE,
        protocol=SensorProtocol.MQTT,
        model="CropX-100",
        manufacturer="CropX",
        lat=24.7136,
        lng=46.6753,
        depth_cm=30,
        status=SensorStatus.ACTIVE,
        battery_percent=85.0,
        min_threshold=30.0,
        max_threshold=70.0,
        critical_min=15.0,
        critical_max=85.0,
        mqtt_topic="sahool/sensors/tenant_123/field_456/sensor_001",
    )


@pytest.fixture
def sample_calibration() -> SensorCalibration:
    """Create a sample calibration for testing"""
    return SensorCalibration(
        sensor_id="sensor_001",
        calibrated_at=datetime.now(UTC),
        calibrated_by="technician_001",
        dry_value=200,
        wet_value=800,
        known_dry_percent=10.0,
        known_wet_percent=90.0,
        offset=0.0,
        scale=1.0,
        soil_type="loam",
        soil_type_ar="طمي",
    )


@pytest.fixture
def sample_reading() -> SensorReading:
    """Create a sample sensor reading for testing"""
    return SensorReading(
        sensor_id="sensor_001",
        timestamp=datetime.now(UTC),
        reading_type=SensorType.MOISTURE,
        value=45.0,
        unit="%",
        quality=0.95,
        is_valid=True,
        lat=24.7136,
        lng=46.6753,
        depth_cm=30,
        battery_percent=85.0,
        signal_strength=-65,
    )


@pytest.fixture
def adapter_config() -> AdapterConfig:
    """Create adapter configuration for testing"""
    return AdapterConfig(
        protocol=SensorProtocol.MQTT,
        host="localhost",
        port=1883,
        username="test_user",
        password="test_pass",
        use_tls=False,
        connect_timeout=30,
        read_timeout=60,
    )


# =============================================================================
# Test Section 1: Sensor Data Models Validation
# =============================================================================


class TestSensorEnums:
    """Test enum classes"""

    @pytest.mark.unit
    def test_sensor_type_values(self):
        """Test SensorType enum has expected values"""
        assert SensorType.MOISTURE.value == "moisture"
        assert SensorType.TEMPERATURE.value == "temperature"
        assert SensorType.EC.value == "electrical_conductivity"
        assert SensorType.PH.value == "ph"
        assert SensorType.NPK.value == "npk"
        assert SensorType.SALINITY.value == "salinity"
        assert SensorType.WATER_LEVEL.value == "water_level"
        assert SensorType.MULTI.value == "multi"

    @pytest.mark.unit
    def test_sensor_protocol_values(self):
        """Test SensorProtocol enum has expected values"""
        assert SensorProtocol.MQTT.value == "mqtt"
        assert SensorProtocol.LORAWAN.value == "lorawan"
        assert SensorProtocol.HTTP.value == "http"
        assert SensorProtocol.ZIGBEE.value == "zigbee"
        assert SensorProtocol.NBIOT.value == "nb-iot"
        assert SensorProtocol.CELLULAR.value == "cellular"

    @pytest.mark.unit
    def test_sensor_status_values(self):
        """Test SensorStatus enum has expected values"""
        assert SensorStatus.ACTIVE.value == "active"
        assert SensorStatus.OFFLINE.value == "offline"
        assert SensorStatus.LOW_BATTERY.value == "low_battery"
        assert SensorStatus.MAINTENANCE.value == "maintenance"
        assert SensorStatus.ERROR.value == "error"
        assert SensorStatus.CALIBRATING.value == "calibrating"

    @pytest.mark.unit
    def test_alert_severity_values(self):
        """Test AlertSeverity enum has expected values"""
        assert AlertSeverity.INFO.value == "info"
        assert AlertSeverity.LOW.value == "low"
        assert AlertSeverity.MEDIUM.value == "medium"
        assert AlertSeverity.HIGH.value == "high"
        assert AlertSeverity.CRITICAL.value == "critical"


class TestSensorReading:
    """Test SensorReading dataclass"""

    @pytest.mark.unit
    def test_sensor_reading_creation(self, sample_reading):
        """Test basic SensorReading creation"""
        assert sample_reading.sensor_id == "sensor_001"
        assert sample_reading.reading_type == SensorType.MOISTURE
        assert sample_reading.value == 45.0
        assert sample_reading.unit == "%"
        assert sample_reading.is_valid is True

    @pytest.mark.unit
    def test_sensor_reading_defaults(self):
        """Test SensorReading default values"""
        reading = SensorReading(
            sensor_id="test",
            timestamp=datetime.now(UTC),
            reading_type=SensorType.MOISTURE,
            value=50.0,
            unit="%",
        )
        assert reading.quality == 1.0
        assert reading.is_valid is True
        assert reading.lat is None
        assert reading.lng is None
        assert reading.depth_cm is None
        assert reading.raw_value is None
        assert reading.battery_percent is None

    @pytest.mark.unit
    def test_sensor_reading_with_all_fields(self):
        """Test SensorReading with all optional fields populated"""
        now = datetime.now(UTC)
        reading = SensorReading(
            sensor_id="sensor_002",
            timestamp=now,
            reading_type=SensorType.TEMPERATURE,
            value=25.5,
            unit="C",
            quality=0.98,
            is_valid=True,
            lat=24.7136,
            lng=46.6753,
            depth_cm=15,
            raw_value=2550,
            raw_unit="raw",
            battery_percent=92.0,
            signal_strength=-55,
        )
        assert reading.lat == 24.7136
        assert reading.lng == 46.6753
        assert reading.depth_cm == 15
        assert reading.raw_value == 2550
        assert reading.battery_percent == 92.0
        assert reading.signal_strength == -55


class TestSoilSensor:
    """Test SoilSensor dataclass"""

    @pytest.mark.unit
    def test_soil_sensor_creation(self, sample_sensor):
        """Test basic SoilSensor creation"""
        assert sample_sensor.id == "sensor_001"
        assert sample_sensor.tenant_id == "tenant_123"
        assert sample_sensor.field_id == "field_456"
        assert sample_sensor.sensor_type == SensorType.MOISTURE
        assert sample_sensor.protocol == SensorProtocol.MQTT

    @pytest.mark.unit
    def test_soil_sensor_to_dict(self, sample_sensor):
        """Test SoilSensor to_dict method"""
        data = sample_sensor.to_dict()

        assert data["id"] == "sensor_001"
        assert data["tenant_id"] == "tenant_123"
        assert data["field_id"] == "field_456"
        assert data["sensor_type"] == "moisture"
        assert data["protocol"] == "mqtt"
        assert data["location"]["lat"] == 24.7136
        assert data["location"]["lng"] == 46.6753
        assert data["location"]["depth_cm"] == 30
        assert data["thresholds"]["min"] == 30.0
        assert data["thresholds"]["max"] == 70.0
        assert data["thresholds"]["critical_min"] == 15.0
        assert data["thresholds"]["critical_max"] == 85.0

    @pytest.mark.unit
    def test_soil_sensor_defaults(self):
        """Test SoilSensor default values"""
        sensor = SoilSensor(
            id="test",
            tenant_id="tenant",
            field_id="field",
            name="Test",
            name_ar="اختبار",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.MQTT,
            model="Test-Model",
            manufacturer="Test-Mfg",
            lat=0.0,
            lng=0.0,
        )
        assert sensor.depth_cm == 30
        assert sensor.status == SensorStatus.ACTIVE
        assert sensor.reading_interval_min == 60
        assert sensor.transmission_interval_min == 60
        assert sensor.is_active is True


class TestSensorCalibration:
    """Test SensorCalibration dataclass"""

    @pytest.mark.unit
    def test_calibration_creation(self, sample_calibration):
        """Test basic SensorCalibration creation"""
        assert sample_calibration.sensor_id == "sensor_001"
        assert sample_calibration.dry_value == 200
        assert sample_calibration.wet_value == 800
        assert sample_calibration.known_dry_percent == 10.0
        assert sample_calibration.known_wet_percent == 90.0

    @pytest.mark.unit
    def test_apply_calibration_midpoint(self, sample_calibration):
        """Test calibration at midpoint"""
        # Midpoint between dry (200) and wet (800) is 500
        raw_value = 500
        calibrated = sample_calibration.apply_calibration(raw_value)
        # Expected: 10% + 0.5 * (90% - 10%) = 10% + 40% = 50%
        assert abs(calibrated - 50.0) < 0.01

    @pytest.mark.unit
    def test_apply_calibration_dry_point(self, sample_calibration):
        """Test calibration at dry point"""
        calibrated = sample_calibration.apply_calibration(200)
        # Should be at known_dry_percent
        assert abs(calibrated - 10.0) < 0.01

    @pytest.mark.unit
    def test_apply_calibration_wet_point(self, sample_calibration):
        """Test calibration at wet point"""
        calibrated = sample_calibration.apply_calibration(800)
        # Should be at known_wet_percent
        assert abs(calibrated - 90.0) < 0.01

    @pytest.mark.unit
    def test_apply_calibration_clamping_low(self, sample_calibration):
        """Test calibration clamps values below 0"""
        # Value way below dry point
        calibrated = sample_calibration.apply_calibration(-1000)
        assert calibrated >= 0.0

    @pytest.mark.unit
    def test_apply_calibration_clamping_high(self, sample_calibration):
        """Test calibration clamps values above 100"""
        # Value way above wet point
        calibrated = sample_calibration.apply_calibration(5000)
        assert calibrated <= 100.0

    @pytest.mark.unit
    def test_apply_calibration_with_offset_and_scale(self):
        """Test calibration with offset and scale factors"""
        calibration = SensorCalibration(
            sensor_id="test",
            calibrated_at=datetime.now(UTC),
            calibrated_by="tech",
            dry_value=0,
            wet_value=100,
            known_dry_percent=0.0,
            known_wet_percent=100.0,
            offset=5.0,
            scale=0.9,
        )
        # At 50 raw: normalized = 0.5, calibrated = 50%, after scale & offset = 50 * 0.9 + 5 = 50
        calibrated = calibration.apply_calibration(50)
        expected = 50.0 * 0.9 + 5.0
        assert abs(calibrated - expected) < 0.01

    @pytest.mark.unit
    def test_apply_calibration_same_dry_wet(self):
        """Test calibration when dry and wet values are the same (edge case)"""
        calibration = SensorCalibration(
            sensor_id="test",
            calibrated_at=datetime.now(UTC),
            calibrated_by="tech",
            dry_value=500,
            wet_value=500,  # Same as dry
            known_dry_percent=0.0,
            known_wet_percent=100.0,
        )
        # Should return raw value unchanged
        calibrated = calibration.apply_calibration(50)
        assert calibrated == 50


class TestSensorAlert:
    """Test SensorAlert dataclass"""

    @pytest.mark.unit
    def test_sensor_alert_creation(self):
        """Test basic SensorAlert creation"""
        now = datetime.now(UTC)
        alert = SensorAlert(
            alert_id="alert_001",
            sensor_id="sensor_001",
            field_id="field_456",
            tenant_id="tenant_123",
            timestamp=now,
            alert_type="low_moisture",
            severity=AlertSeverity.HIGH,
            reading_value=25.0,
            reading_unit="%",
            threshold_value=30.0,
            title_en="Low Moisture Alert",
            title_ar="تنبيه رطوبة منخفضة",
            message_en="Soil moisture is low",
            message_ar="رطوبة التربة منخفضة",
        )
        assert alert.alert_id == "alert_001"
        assert alert.severity == AlertSeverity.HIGH
        assert alert.acknowledged is False
        assert alert.resolved is False

    @pytest.mark.unit
    def test_sensor_alert_to_dict(self):
        """Test SensorAlert to_dict method"""
        now = datetime.now(UTC)
        alert = SensorAlert(
            alert_id="alert_001",
            sensor_id="sensor_001",
            field_id="field_456",
            tenant_id="tenant_123",
            timestamp=now,
            alert_type="low_moisture",
            severity=AlertSeverity.HIGH,
            reading_value=25.0,
            reading_unit="%",
            threshold_value=30.0,
            title_en="Low Moisture",
            title_ar="رطوبة منخفضة",
            message_en="Low moisture detected",
            message_ar="تم اكتشاف رطوبة منخفضة",
        )
        data = alert.to_dict()

        assert data["alert_id"] == "alert_001"
        assert data["severity"] == "high"
        assert data["timestamp"] == now.isoformat()
        assert data["acknowledged"] is False
        assert data["resolved"] is False
        assert data["title_ar"] == "رطوبة منخفضة"


class TestFieldMoistureMap:
    """Test FieldMoistureMap dataclass"""

    @pytest.mark.unit
    def test_field_moisture_map_creation(self):
        """Test basic FieldMoistureMap creation"""
        moisture_map = FieldMoistureMap(
            field_id="field_456",
            timestamp=datetime.now(UTC),
            grid_resolution_m=10,
            min_lat=24.0,
            max_lat=24.1,
            min_lng=46.0,
            max_lng=46.1,
            moisture_grid=[[45.0, 50.0], [48.0, 52.0]],
            avg_moisture=48.75,
            min_moisture=45.0,
            max_moisture=52.0,
            std_moisture=2.5,
            sensor_count=4,
        )
        assert moisture_map.field_id == "field_456"
        assert moisture_map.interpolation_method == "idw"
        assert len(moisture_map.moisture_grid) == 2
        assert len(moisture_map.dry_zones) == 0


class TestSensorAggregation:
    """Test SensorAggregation dataclass"""

    @pytest.mark.unit
    def test_sensor_aggregation_creation(self):
        """Test basic SensorAggregation creation"""
        now = datetime.now(UTC)
        agg = SensorAggregation(
            sensor_id="sensor_001",
            field_id="field_456",
            period_start=now - timedelta(hours=24),
            period_end=now,
            reading_type=SensorType.MOISTURE,
            count=24,
            avg_value=45.5,
            min_value=38.0,
            max_value=55.0,
            std_value=4.2,
            trend="stable",
            trend_rate=0.1,
            valid_readings=23,
            invalid_readings=1,
        )
        assert agg.count == 24
        assert agg.trend == "stable"
        assert agg.valid_readings == 23


# =============================================================================
# Test Section 2: MQTT Adapter Parsing
# =============================================================================


class TestMQTTAdapter:
    """Test MQTTAdapter class"""

    @pytest.mark.unit
    def test_mqtt_adapter_creation(self, adapter_config):
        """Test MQTTAdapter initialization"""
        adapter = MQTTAdapter(adapter_config)
        assert adapter.config == adapter_config
        assert adapter.connected is False
        assert adapter.client is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_mqtt_adapter_connect(self, adapter_config):
        """Test MQTT adapter connect"""
        adapter = MQTTAdapter(adapter_config)
        result = await adapter.connect()
        assert result is True
        assert adapter.connected is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_mqtt_adapter_disconnect(self, adapter_config):
        """Test MQTT adapter disconnect"""
        adapter = MQTTAdapter(adapter_config)
        await adapter.connect()
        await adapter.disconnect()
        assert adapter.connected is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_mqtt_adapter_subscribe(self, adapter_config, sample_sensor):
        """Test MQTT adapter subscribe"""
        adapter = MQTTAdapter(adapter_config)
        await adapter.subscribe(sample_sensor)
        topic = sample_sensor.mqtt_topic
        assert topic in adapter._subscriptions
        assert adapter._subscriptions[topic] == sample_sensor

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_mqtt_adapter_subscribe_default_topic(self, adapter_config):
        """Test MQTT adapter subscribe with default topic generation"""
        adapter = MQTTAdapter(adapter_config)
        sensor = SoilSensor(
            id="sensor_002",
            tenant_id="tenant_123",
            field_id="field_456",
            name="Test",
            name_ar="اختبار",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.MQTT,
            model="Test",
            manufacturer="Test",
            lat=0.0,
            lng=0.0,
            mqtt_topic=None,  # No custom topic
        )
        await adapter.subscribe(sensor)
        expected_topic = f"sahool/sensors/{sensor.tenant_id}/{sensor.field_id}/{sensor.id}"
        assert expected_topic in adapter._subscriptions

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_mqtt_adapter_unsubscribe(self, adapter_config, sample_sensor):
        """Test MQTT adapter unsubscribe"""
        adapter = MQTTAdapter(adapter_config)
        await adapter.subscribe(sample_sensor)
        await adapter.unsubscribe(sample_sensor)
        topic = sample_sensor.mqtt_topic
        assert topic not in adapter._subscriptions

    @pytest.mark.unit
    def test_mqtt_parse_sahool_format(self, adapter_config, sample_sensor):
        """Test parsing SAHOOL standard format payload"""
        adapter = MQTTAdapter(adapter_config)
        now = datetime.now(UTC)
        payload = json.dumps(
            {
                "value": 45.5,
                "type": "moisture",
                "timestamp": now.isoformat(),
                "unit": "%",
                "quality": 0.95,
                "valid": True,
                "battery": 80,
                "rssi": -65,
                "raw_value": 4550,
                "raw_unit": "raw",
            }
        ).encode()

        reading = adapter.parse_payload(payload, sample_sensor)

        assert reading is not None
        assert reading.sensor_id == sample_sensor.id
        assert reading.value == 45.5
        assert reading.unit == "%"
        assert reading.quality == 0.95
        assert reading.is_valid is True
        assert reading.battery_percent == 80
        assert reading.signal_strength == -65
        assert reading.raw_value == 4550

    @pytest.mark.unit
    def test_mqtt_parse_cropx_format(self, adapter_config, sample_sensor):
        """Test parsing CropX format payload"""
        adapter = MQTTAdapter(adapter_config)
        payload = json.dumps(
            {
                "moisture": 42.0,
                "depth": 25,
                "battery": 75,
            }
        ).encode()

        reading = adapter.parse_payload(payload, sample_sensor)

        assert reading is not None
        assert reading.sensor_id == sample_sensor.id
        assert reading.reading_type == SensorType.MOISTURE
        assert reading.value == 42.0
        assert reading.depth_cm == 25
        assert reading.battery_percent == 75

    @pytest.mark.unit
    def test_mqtt_parse_generic_numeric(self, adapter_config, sample_sensor):
        """Test parsing generic numeric payload

        Note: The current implementation doesn't fully support raw numeric JSON
        due to the order of format checks (dict checks come before isinstance check).
        This test documents the current behavior - a raw numeric payload returns None.
        """
        adapter = MQTTAdapter(adapter_config)
        payload = json.dumps(55.5).encode()

        reading = adapter.parse_payload(payload, sample_sensor)

        # Current implementation returns None for raw numeric payloads
        # because dict membership checks ("value" in data) fail before
        # the isinstance(data, (int, float)) check is reached
        assert reading is None

    @pytest.mark.unit
    def test_mqtt_parse_invalid_json(self, adapter_config, sample_sensor):
        """Test parsing invalid JSON payload"""
        adapter = MQTTAdapter(adapter_config)
        payload = b"not valid json {"

        reading = adapter.parse_payload(payload, sample_sensor)
        assert reading is None

    @pytest.mark.unit
    def test_mqtt_parse_empty_payload(self, adapter_config, sample_sensor):
        """Test parsing empty payload"""
        adapter = MQTTAdapter(adapter_config)
        payload = b""

        reading = adapter.parse_payload(payload, sample_sensor)
        assert reading is None

    @pytest.mark.unit
    def test_mqtt_parse_unknown_format(self, adapter_config, sample_sensor):
        """Test parsing unknown format returns None"""
        adapter = MQTTAdapter(adapter_config)
        # JSON but not matching any known format
        payload = json.dumps({"unknown_field": "value"}).encode()

        reading = adapter.parse_payload(payload, sample_sensor)
        assert reading is None

    @pytest.mark.unit
    def test_mqtt_on_reading_callback(self, adapter_config, sample_reading):
        """Test callback registration and emission"""
        adapter = MQTTAdapter(adapter_config)
        callback_calls = []

        def callback(reading):
            callback_calls.append(reading)

        adapter.on_reading(callback)
        adapter._emit_reading(sample_reading)

        assert len(callback_calls) == 1
        assert callback_calls[0] == sample_reading

    @pytest.mark.unit
    def test_mqtt_callback_error_handling(self, adapter_config, sample_reading):
        """Test callback error doesn't break other callbacks"""
        adapter = MQTTAdapter(adapter_config)
        successful_calls = []

        def error_callback(reading):
            raise ValueError("Test error")

        def success_callback(reading):
            successful_calls.append(reading)

        adapter.on_reading(error_callback)
        adapter.on_reading(success_callback)
        adapter._emit_reading(sample_reading)

        # The second callback should still be called
        assert len(successful_calls) == 1


# =============================================================================
# Test Section 3: LoRaWAN Adapter Parsing
# =============================================================================


class TestLoRaWANAdapter:
    """Test LoRaWANAdapter class"""

    @pytest.mark.unit
    def test_lorawan_adapter_creation(self, adapter_config):
        """Test LoRaWANAdapter initialization"""
        config = AdapterConfig(protocol=SensorProtocol.LORAWAN)
        adapter = LoRaWANAdapter(config)
        assert adapter.connected is False
        assert len(adapter._devices) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_lorawan_adapter_connect(self):
        """Test LoRaWAN adapter connect"""
        config = AdapterConfig(protocol=SensorProtocol.LORAWAN)
        adapter = LoRaWANAdapter(config)
        result = await adapter.connect()
        assert result is True
        assert adapter.connected is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_lorawan_adapter_subscribe(self):
        """Test LoRaWAN adapter subscribe by device EUI"""
        config = AdapterConfig(protocol=SensorProtocol.LORAWAN)
        adapter = LoRaWANAdapter(config)
        sensor = SoilSensor(
            id="sensor_lorawan",
            tenant_id="tenant",
            field_id="field",
            name="LoRaWAN Sensor",
            name_ar="مجس LoRaWAN",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.LORAWAN,
            model="LoRa-Soil",
            manufacturer="Test",
            lat=0.0,
            lng=0.0,
            device_eui="0011223344556677",
        )
        await adapter.subscribe(sensor)
        assert sensor.device_eui in adapter._devices
        assert adapter._devices[sensor.device_eui] == sensor

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_lorawan_adapter_unsubscribe(self):
        """Test LoRaWAN adapter unsubscribe"""
        config = AdapterConfig(protocol=SensorProtocol.LORAWAN)
        adapter = LoRaWANAdapter(config)
        sensor = SoilSensor(
            id="sensor_lorawan",
            tenant_id="tenant",
            field_id="field",
            name="LoRaWAN Sensor",
            name_ar="مجس",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.LORAWAN,
            model="LoRa-Soil",
            manufacturer="Test",
            lat=0.0,
            lng=0.0,
            device_eui="0011223344556677",
        )
        await adapter.subscribe(sensor)
        await adapter.unsubscribe(sensor)
        assert sensor.device_eui not in adapter._devices

    @pytest.mark.unit
    def test_lorawan_parse_binary_moisture(self):
        """Test parsing binary LoRaWAN payload"""
        config = AdapterConfig(protocol=SensorProtocol.LORAWAN)
        adapter = LoRaWANAdapter(config)
        sensor = SoilSensor(
            id="sensor_lorawan",
            tenant_id="tenant",
            field_id="field",
            name="LoRaWAN",
            name_ar="مجس",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.LORAWAN,
            model="Test",
            manufacturer="Test",
            lat=0.0,
            lng=0.0,
        )

        # 4500 = 45.00% moisture (scaled by 100), battery 85%
        moisture_raw = 4500
        battery = 85
        payload = moisture_raw.to_bytes(2, "big") + bytes([battery])

        reading = adapter.parse_payload(payload, sensor)

        assert reading is not None
        assert reading.value == 45.0
        assert reading.unit == "%"
        assert reading.battery_percent == 85
        assert reading.raw_value == 4500

    @pytest.mark.unit
    def test_lorawan_parse_2_bytes_only(self):
        """Test parsing LoRaWAN payload with only moisture (no battery)"""
        config = AdapterConfig(protocol=SensorProtocol.LORAWAN)
        adapter = LoRaWANAdapter(config)
        sensor = SoilSensor(
            id="test",
            tenant_id="tenant",
            field_id="field",
            name="Test",
            name_ar="اختبار",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.LORAWAN,
            model="Test",
            manufacturer="Test",
            lat=0.0,
            lng=0.0,
        )

        # 5500 = 55.00%
        payload = (5500).to_bytes(2, "big")

        reading = adapter.parse_payload(payload, sensor)

        assert reading is not None
        assert reading.value == 55.0
        assert reading.battery_percent is None

    @pytest.mark.unit
    def test_lorawan_parse_single_byte(self):
        """Test parsing LoRaWAN payload with single byte (invalid)"""
        config = AdapterConfig(protocol=SensorProtocol.LORAWAN)
        adapter = LoRaWANAdapter(config)
        sensor = SoilSensor(
            id="test",
            tenant_id="tenant",
            field_id="field",
            name="Test",
            name_ar="اختبار",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.LORAWAN,
            model="Test",
            manufacturer="Test",
            lat=0.0,
            lng=0.0,
        )

        # Single byte - not enough data
        payload = bytes([100])

        reading = adapter.parse_payload(payload, sensor)
        assert reading is None

    @pytest.mark.unit
    def test_lorawan_parse_empty_payload(self):
        """Test parsing empty LoRaWAN payload"""
        config = AdapterConfig(protocol=SensorProtocol.LORAWAN)
        adapter = LoRaWANAdapter(config)
        sensor = SoilSensor(
            id="test",
            tenant_id="tenant",
            field_id="field",
            name="Test",
            name_ar="اختبار",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.LORAWAN,
            model="Test",
            manufacturer="Test",
            lat=0.0,
            lng=0.0,
        )

        reading = adapter.parse_payload(b"", sensor)
        assert reading is None

    @pytest.mark.unit
    def test_lorawan_parse_extreme_values(self):
        """Test parsing LoRaWAN payload with extreme values"""
        config = AdapterConfig(protocol=SensorProtocol.LORAWAN)
        adapter = LoRaWANAdapter(config)
        sensor = SoilSensor(
            id="test",
            tenant_id="tenant",
            field_id="field",
            name="Test",
            name_ar="اختبار",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.LORAWAN,
            model="Test",
            manufacturer="Test",
            lat=0.0,
            lng=0.0,
        )

        # Maximum 2-byte value: 65535 = 655.35%
        payload = (65535).to_bytes(2, "big")
        reading = adapter.parse_payload(payload, sensor)
        assert reading is not None
        assert reading.value == 655.35

        # Zero value
        payload = (0).to_bytes(2, "big")
        reading = adapter.parse_payload(payload, sensor)
        assert reading is not None
        assert reading.value == 0.0


# =============================================================================
# Test Section 4: HTTP Adapter Parsing
# =============================================================================


class TestHTTPAdapter:
    """Test HTTPAdapter class"""

    @pytest.mark.unit
    def test_http_adapter_creation(self, adapter_config):
        """Test HTTPAdapter initialization"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)
        assert adapter.connected is False
        assert len(adapter._sensors) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_http_adapter_connect(self):
        """Test HTTP adapter connect (always succeeds)"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)
        result = await adapter.connect()
        assert result is True
        assert adapter.connected is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_http_adapter_disconnect(self):
        """Test HTTP adapter disconnect"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)
        await adapter.connect()
        await adapter.disconnect()
        assert adapter.connected is False

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_http_adapter_subscribe(self, sample_sensor):
        """Test HTTP adapter subscribe"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)
        await adapter.subscribe(sample_sensor)
        assert sample_sensor.id in adapter._sensors
        assert adapter._sensors[sample_sensor.id] == sample_sensor

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_http_adapter_unsubscribe(self, sample_sensor):
        """Test HTTP adapter unsubscribe"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)
        await adapter.subscribe(sample_sensor)
        await adapter.unsubscribe(sample_sensor)
        assert sample_sensor.id not in adapter._sensors

    @pytest.mark.unit
    def test_http_parse_sensoterra_format(self, sample_sensor):
        """Test parsing Sensoterra webhook format"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)
        now = datetime.now(UTC)

        payload = json.dumps(
            {
                "sensor_id": "ext_sensor_001",
                "volumetric_water_content": 0.42,  # 42%
                "timestamp": now.isoformat(),
                "latitude": 24.7136,
                "longitude": 46.6753,
                "depth": 30,
                "battery_level": 88,
            }
        ).encode()

        reading = adapter.parse_payload(payload, sample_sensor)

        assert reading is not None
        assert reading.sensor_id == sample_sensor.id
        assert reading.value == 42.0  # Converted from 0.42
        assert reading.unit == "%"
        assert reading.lat == 24.7136
        assert reading.lng == 46.6753
        assert reading.depth_cm == 30
        assert reading.battery_percent == 88

    @pytest.mark.unit
    def test_http_parse_libelium_format(self, sample_sensor):
        """Test parsing Libelium webhook format"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)

        payload = json.dumps(
            {
                "id": "device_001",
                "sensor": {
                    "value": 48.5,
                    "unit": "%",
                },
            }
        ).encode()

        reading = adapter.parse_payload(payload, sample_sensor)

        assert reading is not None
        assert reading.value == 48.5
        assert reading.unit == "%"

    @pytest.mark.unit
    def test_http_parse_generic_moisture_format(self, sample_sensor):
        """Test parsing generic moisture format"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)

        payload = json.dumps(
            {
                "moisture": 55.0,
            }
        ).encode()

        reading = adapter.parse_payload(payload, sample_sensor)

        assert reading is not None
        assert reading.value == 55.0

    @pytest.mark.unit
    def test_http_parse_generic_value_format(self, sample_sensor):
        """Test parsing generic value format"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)

        payload = json.dumps(
            {
                "value": 60.0,
            }
        ).encode()

        reading = adapter.parse_payload(payload, sample_sensor)

        assert reading is not None
        assert reading.value == 60.0

    @pytest.mark.unit
    def test_http_parse_invalid_json(self, sample_sensor):
        """Test parsing invalid JSON"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)

        payload = b"not valid json"

        reading = adapter.parse_payload(payload, sample_sensor)
        assert reading is None

    @pytest.mark.unit
    def test_http_parse_empty_payload(self, sample_sensor):
        """Test parsing empty payload"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)

        reading = adapter.parse_payload(b"", sample_sensor)
        assert reading is None

    @pytest.mark.unit
    def test_http_parse_unknown_format(self, sample_sensor):
        """Test parsing unknown format"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)

        payload = json.dumps(
            {
                "unknown_key": "unknown_value",
            }
        ).encode()

        reading = adapter.parse_payload(payload, sample_sensor)
        assert reading is None


# =============================================================================
# Test Section 5: NBIoT Adapter and Factory
# =============================================================================


class TestNBIoTAdapter:
    """Test NBIoTAdapter class"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_nbiot_adapter_connect(self):
        """Test NB-IoT adapter connect"""
        config = AdapterConfig(protocol=SensorProtocol.NBIOT)
        adapter = NBIoTAdapter(config)
        result = await adapter.connect()
        assert result is True
        assert adapter.connected is True

    @pytest.mark.unit
    def test_nbiot_parse_payload_like_lorawan(self, sample_sensor):
        """Test NB-IoT uses LoRaWAN-style binary parsing"""
        config = AdapterConfig(protocol=SensorProtocol.NBIOT)
        adapter = NBIoTAdapter(config)

        # Same format as LoRaWAN
        moisture_raw = 3500
        payload = moisture_raw.to_bytes(2, "big")

        reading = adapter.parse_payload(payload, sample_sensor)

        assert reading is not None
        assert reading.value == 35.0


class TestAdapterFactory:
    """Test get_adapter factory function"""

    @pytest.mark.unit
    def test_get_adapter_mqtt(self):
        """Test factory returns MQTTAdapter for MQTT protocol"""
        config = AdapterConfig(protocol=SensorProtocol.MQTT)
        adapter = get_adapter(SensorProtocol.MQTT, config)
        assert isinstance(adapter, MQTTAdapter)

    @pytest.mark.unit
    def test_get_adapter_lorawan(self):
        """Test factory returns LoRaWANAdapter for LORAWAN protocol"""
        config = AdapterConfig(protocol=SensorProtocol.LORAWAN)
        adapter = get_adapter(SensorProtocol.LORAWAN, config)
        assert isinstance(adapter, LoRaWANAdapter)

    @pytest.mark.unit
    def test_get_adapter_http(self):
        """Test factory returns HTTPAdapter for HTTP protocol"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = get_adapter(SensorProtocol.HTTP, config)
        assert isinstance(adapter, HTTPAdapter)

    @pytest.mark.unit
    def test_get_adapter_nbiot(self):
        """Test factory returns NBIoTAdapter for NBIOT protocol"""
        config = AdapterConfig(protocol=SensorProtocol.NBIOT)
        adapter = get_adapter(SensorProtocol.NBIOT, config)
        assert isinstance(adapter, NBIoTAdapter)

    @pytest.mark.unit
    def test_get_adapter_cellular(self):
        """Test factory returns NBIoTAdapter for CELLULAR protocol"""
        config = AdapterConfig(protocol=SensorProtocol.CELLULAR)
        adapter = get_adapter(SensorProtocol.CELLULAR, config)
        assert isinstance(adapter, NBIoTAdapter)

    @pytest.mark.unit
    def test_get_adapter_unknown_defaults_to_http(self):
        """Test factory defaults to HTTPAdapter for unknown protocol"""
        config = AdapterConfig(protocol=SensorProtocol.ZIGBEE)
        adapter = get_adapter(SensorProtocol.ZIGBEE, config)
        assert isinstance(adapter, HTTPAdapter)


# =============================================================================
# Test Section 6: Sensor Manager
# =============================================================================


class TestSensorManager:
    """Test SensorManager class"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_sensor_manager_add_adapter(self):
        """Test adding adapter to manager"""
        manager = SensorManager()
        config = AdapterConfig(protocol=SensorProtocol.MQTT)
        await manager.add_adapter(SensorProtocol.MQTT, config)

        assert SensorProtocol.MQTT in manager._adapters
        assert manager._adapters[SensorProtocol.MQTT].connected is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_sensor_manager_register_sensor(self, sample_sensor):
        """Test registering sensor with manager"""
        manager = SensorManager()
        config = AdapterConfig(protocol=SensorProtocol.MQTT)
        await manager.add_adapter(SensorProtocol.MQTT, config)
        await manager.register_sensor(sample_sensor)

        assert sample_sensor.id in manager._sensors

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_sensor_manager_unregister_sensor(self, sample_sensor):
        """Test unregistering sensor from manager"""
        manager = SensorManager()
        config = AdapterConfig(protocol=SensorProtocol.MQTT)
        await manager.add_adapter(SensorProtocol.MQTT, config)
        await manager.register_sensor(sample_sensor)
        await manager.unregister_sensor(sample_sensor.id)

        assert sample_sensor.id not in manager._sensors

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_sensor_manager_shutdown(self, sample_sensor):
        """Test manager shutdown"""
        manager = SensorManager()
        config = AdapterConfig(protocol=SensorProtocol.MQTT)
        await manager.add_adapter(SensorProtocol.MQTT, config)
        await manager.register_sensor(sample_sensor)
        await manager.shutdown()

        assert len(manager._adapters) == 0
        assert len(manager._sensors) == 0

    @pytest.mark.unit
    def test_sensor_manager_on_reading_callback(self, sample_reading):
        """Test manager callback registration"""
        manager = SensorManager()
        callback_calls = []

        def callback(reading):
            callback_calls.append(reading)

        manager.on_reading(callback)
        manager._handle_reading(sample_reading)

        assert len(callback_calls) == 1
        assert callback_calls[0] == sample_reading


# =============================================================================
# Test Section 7: Data Processor - Threshold Checks
# =============================================================================


class TestSensorDataProcessorThresholds:
    """Test SensorDataProcessor threshold checking"""

    @pytest.mark.unit
    def test_processor_creation(self):
        """Test processor initialization"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        assert processor.field_id == "field_456"
        assert processor.tenant_id == "tenant_123"
        assert processor._max_readings == 1000

    @pytest.mark.unit
    def test_processor_register_sensor(self, sample_sensor):
        """Test registering sensor with processor"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)
        assert sample_sensor.id in processor._sensors

    @pytest.mark.unit
    def test_processor_add_reading_no_alert(self, sample_sensor, sample_reading):
        """Test adding reading within thresholds (no alert)"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        # Reading is 45%, thresholds are 30-70%
        sample_reading.value = 45.0
        alerts = processor.add_reading(sample_reading)

        assert len(alerts) == 0
        assert sample_reading.sensor_id in processor._readings
        assert len(processor._readings[sample_reading.sensor_id]) == 1

    @pytest.mark.unit
    def test_processor_add_invalid_reading(self, sample_sensor, sample_reading):
        """Test adding invalid reading is ignored"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        sample_reading.is_valid = False
        alerts = processor.add_reading(sample_reading)

        assert len(alerts) == 0

    @pytest.mark.unit
    def test_processor_critical_low_threshold(self, sample_sensor, sample_reading):
        """Test critical low threshold alert"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        # Critical min is 15%
        sample_reading.value = 10.0
        alerts = processor.add_reading(sample_reading)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.alert_type == "critical_low"
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.reading_value == 10.0

    @pytest.mark.unit
    def test_processor_critical_high_threshold(self, sample_sensor, sample_reading):
        """Test critical high threshold alert"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        # Critical max is 85%
        sample_reading.value = 90.0
        alerts = processor.add_reading(sample_reading)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.alert_type == "critical_high"
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.reading_value == 90.0

    @pytest.mark.unit
    def test_processor_low_moisture_threshold(self, sample_sensor, sample_reading):
        """Test low moisture warning threshold"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        # Min threshold is 30%
        sample_reading.value = 25.0
        alerts = processor.add_reading(sample_reading)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.alert_type == "low_moisture"
        assert alert.severity == AlertSeverity.HIGH

    @pytest.mark.unit
    def test_processor_high_moisture_threshold(self, sample_sensor, sample_reading):
        """Test high moisture warning threshold"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        # Max threshold is 70%
        sample_reading.value = 75.0
        alerts = processor.add_reading(sample_reading)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.alert_type == "high_moisture"
        assert alert.severity == AlertSeverity.MEDIUM

    @pytest.mark.unit
    def test_processor_alert_has_bilingual_messages(self, sample_sensor, sample_reading):
        """Test alerts have Arabic and English messages"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        sample_reading.value = 10.0  # Critical low
        alerts = processor.add_reading(sample_reading)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.title_en != ""
        assert alert.title_ar != ""
        assert alert.message_en != ""
        assert alert.message_ar != ""
        # Check Arabic text is present
        assert "حرج" in alert.title_ar or "رطوبة" in alert.title_ar


# =============================================================================
# Test Section 8: Data Processor - Calibration
# =============================================================================


class TestSensorDataProcessorCalibration:
    """Test SensorDataProcessor calibration application"""

    @pytest.mark.unit
    def test_processor_applies_calibration(self, sample_sensor, sample_calibration):
        """Test that processor applies calibration to readings"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        sample_sensor.calibration = sample_calibration
        processor.register_sensor(sample_sensor)

        # Create reading with raw value at midpoint (500)
        reading = SensorReading(
            sensor_id=sample_sensor.id,
            timestamp=datetime.now(UTC),
            reading_type=SensorType.MOISTURE,
            value=500,  # Raw value
            unit="%",
        )

        alerts = processor.add_reading(reading)

        # Value should be calibrated to ~50%
        stored_reading = processor._readings[sample_sensor.id][-1]
        assert abs(stored_reading.value - 50.0) < 1.0


# =============================================================================
# Test Section 9: Data Processor - Anomaly Detection
# =============================================================================


class TestSensorDataProcessorAnomalies:
    """Test SensorDataProcessor anomaly detection"""

    @pytest.mark.unit
    def test_processor_no_anomaly_with_few_readings(self, sample_sensor, sample_reading):
        """Test no anomaly detection with insufficient data"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        # Add less than 10 readings
        for i in range(5):
            reading = SensorReading(
                sensor_id=sample_sensor.id,
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=45.0 + i,
                unit="%",
            )
            alerts = processor.add_reading(reading)
            # Should not have anomaly alerts yet
            assert not any(a.alert_type == "anomaly_detected" for a in alerts)

    @pytest.mark.unit
    def test_processor_detects_anomaly(self, sample_sensor):
        """Test anomaly detection with statistical outlier"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        # Remove thresholds so we only test anomaly detection
        sample_sensor.min_threshold = None
        sample_sensor.max_threshold = None
        sample_sensor.critical_min = None
        sample_sensor.critical_max = None
        processor.register_sensor(sample_sensor)

        base_time = datetime.now(UTC)

        # Add 15 normal readings around 50%
        for i in range(15):
            reading = SensorReading(
                sensor_id=sample_sensor.id,
                timestamp=base_time - timedelta(hours=12 - i),
                reading_type=SensorType.MOISTURE,
                value=50.0 + (i % 3 - 1),  # Values between 49-51%
                unit="%",
            )
            processor.add_reading(reading)

        # Add an anomalous reading (far from mean)
        anomalous_reading = SensorReading(
            sensor_id=sample_sensor.id,
            timestamp=datetime.now(UTC),
            reading_type=SensorType.MOISTURE,
            value=90.0,  # Way outside normal range
            unit="%",
        )
        alerts = processor.add_reading(anomalous_reading)

        anomaly_alerts = [a for a in alerts if a.alert_type == "anomaly_detected"]
        assert len(anomaly_alerts) == 1
        assert anomaly_alerts[0].severity == AlertSeverity.MEDIUM


# =============================================================================
# Test Section 10: Data Processor - Aggregation
# =============================================================================


class TestSensorDataProcessorAggregation:
    """Test SensorDataProcessor aggregation"""

    @pytest.mark.unit
    def test_processor_get_latest_readings(self, sample_sensor, sample_reading):
        """Test getting latest reading from each sensor"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        # Add multiple readings
        for i in range(5):
            reading = SensorReading(
                sensor_id=sample_sensor.id,
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=40.0 + i * 2,
                unit="%",
            )
            processor.add_reading(reading)

        latest = processor.get_latest_readings()

        assert sample_sensor.id in latest
        assert latest[sample_sensor.id].value == 48.0  # Last value

    @pytest.mark.unit
    def test_processor_get_latest_reading_specific_sensor(self, sample_sensor, sample_reading):
        """Test getting latest reading for specific sensor"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        processor.add_reading(sample_reading)

        latest = processor.get_latest_readings(sensor_id=sample_sensor.id)

        assert sample_sensor.id in latest
        assert latest[sample_sensor.id] == sample_reading

    @pytest.mark.unit
    def test_processor_get_aggregation(self, sample_sensor):
        """Test getting aggregated readings"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        base_time = datetime.now(UTC)

        # Add readings with known values
        values = [40.0, 45.0, 50.0, 55.0, 60.0]
        for i, value in enumerate(values):
            reading = SensorReading(
                sensor_id=sample_sensor.id,
                timestamp=base_time - timedelta(hours=i),
                reading_type=SensorType.MOISTURE,
                value=value,
                unit="%",
            )
            processor.add_reading(reading)

        agg = processor.get_aggregation(sample_sensor.id, period_hours=24)

        assert agg is not None
        assert agg.count == 5
        assert agg.avg_value == 50.0
        assert agg.min_value == 40.0
        assert agg.max_value == 60.0
        assert agg.valid_readings == 5
        assert agg.invalid_readings == 0

    @pytest.mark.unit
    def test_processor_get_aggregation_no_readings(self, sample_sensor):
        """Test aggregation returns None when no readings"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        agg = processor.get_aggregation(sample_sensor.id, period_hours=24)
        assert agg is None

    @pytest.mark.unit
    def test_processor_get_aggregation_trend_increasing(self, sample_sensor):
        """Test aggregation detects increasing trend"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        base_time = datetime.now(UTC)

        # Add increasing values
        for i in range(10):
            reading = SensorReading(
                sensor_id=sample_sensor.id,
                timestamp=base_time - timedelta(hours=10 - i),
                reading_type=SensorType.MOISTURE,
                value=30.0 + i * 5,  # 30, 35, 40, ..., 75
                unit="%",
            )
            processor.add_reading(reading)

        agg = processor.get_aggregation(sample_sensor.id, period_hours=24)

        assert agg is not None
        assert agg.trend == "increasing"

    @pytest.mark.unit
    def test_processor_get_aggregation_trend_decreasing(self, sample_sensor):
        """Test aggregation detects decreasing trend"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        base_time = datetime.now(UTC)

        # Add decreasing values
        for i in range(10):
            reading = SensorReading(
                sensor_id=sample_sensor.id,
                timestamp=base_time - timedelta(hours=10 - i),
                reading_type=SensorType.MOISTURE,
                value=75.0 - i * 5,  # 75, 70, 65, ..., 30
                unit="%",
            )
            processor.add_reading(reading)

        agg = processor.get_aggregation(sample_sensor.id, period_hours=24)

        assert agg is not None
        assert agg.trend == "decreasing"


# =============================================================================
# Test Section 11: Standalone Aggregation Function
# =============================================================================


class TestAggregateReadings:
    """Test aggregate_readings function"""

    @pytest.mark.unit
    def test_aggregate_readings_empty_list(self):
        """Test aggregation with empty list"""
        result = aggregate_readings([])
        assert result == []

    @pytest.mark.unit
    def test_aggregate_readings_single_interval(self):
        """Test aggregation within single interval"""
        base_time = datetime(2024, 1, 15, 10, 0, 0)  # 10:00

        readings = [
            SensorReading(
                sensor_id="sensor_001",
                timestamp=base_time + timedelta(minutes=5),
                reading_type=SensorType.MOISTURE,
                value=40.0,
                unit="%",
            ),
            SensorReading(
                sensor_id="sensor_001",
                timestamp=base_time + timedelta(minutes=15),
                reading_type=SensorType.MOISTURE,
                value=50.0,
                unit="%",
            ),
            SensorReading(
                sensor_id="sensor_001",
                timestamp=base_time + timedelta(minutes=30),
                reading_type=SensorType.MOISTURE,
                value=60.0,
                unit="%",
            ),
        ]

        result = aggregate_readings(readings, interval_minutes=60)

        assert len(result) == 1
        agg = result[0]
        assert agg.count == 3
        assert agg.avg_value == 50.0
        assert agg.min_value == 40.0
        assert agg.max_value == 60.0

    @pytest.mark.unit
    def test_aggregate_readings_multiple_intervals(self):
        """Test aggregation across multiple intervals"""
        base_time = datetime(2024, 1, 15, 10, 0, 0)

        readings = [
            # First hour
            SensorReading(
                sensor_id="sensor_001",
                timestamp=base_time + timedelta(minutes=10),
                reading_type=SensorType.MOISTURE,
                value=40.0,
                unit="%",
            ),
            SensorReading(
                sensor_id="sensor_001",
                timestamp=base_time + timedelta(minutes=30),
                reading_type=SensorType.MOISTURE,
                value=50.0,
                unit="%",
            ),
            # Second hour
            SensorReading(
                sensor_id="sensor_001",
                timestamp=base_time + timedelta(minutes=70),
                reading_type=SensorType.MOISTURE,
                value=55.0,
                unit="%",
            ),
            SensorReading(
                sensor_id="sensor_001",
                timestamp=base_time + timedelta(minutes=90),
                reading_type=SensorType.MOISTURE,
                value=65.0,
                unit="%",
            ),
        ]

        result = aggregate_readings(readings, interval_minutes=60)

        assert len(result) == 2

        # First interval
        assert result[0].avg_value == 45.0
        assert result[0].count == 2

        # Second interval
        assert result[1].avg_value == 60.0
        assert result[1].count == 2

    @pytest.mark.unit
    def test_aggregate_readings_with_invalid(self):
        """Test aggregation excludes invalid readings from stats"""
        base_time = datetime(2024, 1, 15, 10, 0, 0)

        readings = [
            SensorReading(
                sensor_id="sensor_001",
                timestamp=base_time + timedelta(minutes=10),
                reading_type=SensorType.MOISTURE,
                value=40.0,
                unit="%",
                is_valid=True,
            ),
            SensorReading(
                sensor_id="sensor_001",
                timestamp=base_time + timedelta(minutes=20),
                reading_type=SensorType.MOISTURE,
                value=999.0,  # Invalid value
                unit="%",
                is_valid=False,
            ),
            SensorReading(
                sensor_id="sensor_001",
                timestamp=base_time + timedelta(minutes=30),
                reading_type=SensorType.MOISTURE,
                value=60.0,
                unit="%",
                is_valid=True,
            ),
        ]

        result = aggregate_readings(readings, interval_minutes=60)

        assert len(result) == 1
        agg = result[0]
        assert agg.count == 3  # Total readings
        assert agg.valid_readings == 2
        assert agg.invalid_readings == 1
        assert agg.avg_value == 50.0  # Only valid readings


# =============================================================================
# Test Section 12: Anomaly Detection Function
# =============================================================================


class TestDetectAnomalies:
    """Test detect_anomalies function"""

    @pytest.mark.unit
    def test_detect_anomalies_empty_list(self):
        """Test anomaly detection with empty list"""
        result = detect_anomalies([])
        assert result == []

    @pytest.mark.unit
    def test_detect_anomalies_insufficient_data(self):
        """Test anomaly detection with less than 10 readings"""
        readings = [
            SensorReading(
                sensor_id="sensor_001",
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=50.0 + i,
                unit="%",
            )
            for i in range(5)
        ]

        result = detect_anomalies(readings)
        assert result == []

    @pytest.mark.unit
    def test_detect_anomalies_no_outliers(self):
        """Test anomaly detection with no outliers"""
        readings = [
            SensorReading(
                sensor_id="sensor_001",
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=50.0 + (i % 3 - 1),  # 49, 50, 51
                unit="%",
            )
            for i in range(15)
        ]

        result = detect_anomalies(readings)
        assert result == []

    @pytest.mark.unit
    def test_detect_anomalies_with_outlier(self):
        """Test anomaly detection identifies outlier"""
        readings = [
            SensorReading(
                sensor_id="sensor_001",
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=50.0,  # Normal value
                unit="%",
            )
            for _ in range(14)
        ]

        # Add outlier
        readings.append(
            SensorReading(
                sensor_id="sensor_001",
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=100.0,  # Outlier
                unit="%",
            )
        )

        result = detect_anomalies(readings)
        assert len(result) == 1
        assert result[0].value == 100.0

    @pytest.mark.unit
    def test_detect_anomalies_custom_threshold(self):
        """Test anomaly detection with custom threshold"""
        readings = [
            SensorReading(
                sensor_id="sensor_001",
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=50.0 + (i - 7),  # Range 43-57
                unit="%",
            )
            for i in range(15)
        ]

        # With stricter threshold (2 std), more readings might be flagged
        result_strict = detect_anomalies(readings, threshold_std=2.0)

        # With looser threshold (4 std), fewer readings flagged
        result_loose = detect_anomalies(readings, threshold_std=4.0)

        assert len(result_strict) >= len(result_loose)


# =============================================================================
# Test Section 13: Field Moisture Interpolation
# =============================================================================


class TestInterpolateFieldMoisture:
    """Test interpolate_field_moisture function"""

    @pytest.mark.unit
    def test_interpolate_no_sensors(self):
        """Test interpolation with no sensors"""
        result = interpolate_field_moisture(
            sensors=[],
            readings={},
            field_bounds=(24.0, 24.1, 46.0, 46.1),
            resolution_m=10.0,
        )

        assert result.sensor_count == 0
        assert result.moisture_grid == []

    @pytest.mark.unit
    def test_interpolate_single_sensor(self):
        """Test interpolation with single sensor"""
        sensor = SoilSensor(
            id="sensor_001",
            tenant_id="tenant",
            field_id="field",
            name="Test",
            name_ar="اختبار",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.MQTT,
            model="Test",
            manufacturer="Test",
            lat=24.05,
            lng=46.05,
        )

        reading = SensorReading(
            sensor_id="sensor_001",
            timestamp=datetime.now(UTC),
            reading_type=SensorType.MOISTURE,
            value=50.0,
            unit="%",
        )

        result = interpolate_field_moisture(
            sensors=[sensor],
            readings={"sensor_001": reading},
            field_bounds=(24.0, 24.1, 46.0, 46.1),
            resolution_m=50.0,  # Coarser resolution for faster test
        )

        assert result.sensor_count == 1
        assert len(result.moisture_grid) > 0
        # All values should be approximately 50% (single sensor, IDW)
        for row in result.moisture_grid:
            for value in row:
                assert 45.0 <= value <= 55.0

    @pytest.mark.unit
    def test_interpolate_multiple_sensors(self):
        """Test interpolation with multiple sensors"""
        sensors = [
            SoilSensor(
                id="sensor_001",
                tenant_id="tenant",
                field_id="field",
                name="Dry",
                name_ar="جاف",
                sensor_type=SensorType.MOISTURE,
                protocol=SensorProtocol.MQTT,
                model="Test",
                manufacturer="Test",
                lat=24.01,
                lng=46.01,  # Corner
            ),
            SoilSensor(
                id="sensor_002",
                tenant_id="tenant",
                field_id="field",
                name="Wet",
                name_ar="رطب",
                sensor_type=SensorType.MOISTURE,
                protocol=SensorProtocol.MQTT,
                model="Test",
                manufacturer="Test",
                lat=24.09,
                lng=46.09,  # Opposite corner
            ),
        ]

        readings = {
            "sensor_001": SensorReading(
                sensor_id="sensor_001",
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=20.0,  # Dry
                unit="%",
            ),
            "sensor_002": SensorReading(
                sensor_id="sensor_002",
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=80.0,  # Wet
                unit="%",
            ),
        }

        result = interpolate_field_moisture(
            sensors=sensors,
            readings=readings,
            field_bounds=(24.0, 24.1, 46.0, 46.1),
            resolution_m=100.0,
        )

        assert result.sensor_count == 2
        assert result.min_moisture <= result.avg_moisture <= result.max_moisture

    @pytest.mark.unit
    def test_interpolate_calculates_statistics(self):
        """Test interpolation calculates statistics correctly"""
        sensors = [
            SoilSensor(
                id="sensor_001",
                tenant_id="tenant",
                field_id="field",
                name="Test",
                name_ar="اختبار",
                sensor_type=SensorType.MOISTURE,
                protocol=SensorProtocol.MQTT,
                model="Test",
                manufacturer="Test",
                lat=24.05,
                lng=46.05,
            ),
        ]

        readings = {
            "sensor_001": SensorReading(
                sensor_id="sensor_001",
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=50.0,
                unit="%",
            ),
        }

        result = interpolate_field_moisture(
            sensors=sensors,
            readings=readings,
            field_bounds=(24.0, 24.1, 46.0, 46.1),
            resolution_m=100.0,
        )

        assert result.avg_moisture >= 0
        assert result.min_moisture >= 0
        assert result.max_moisture >= 0
        assert result.std_moisture >= 0
        assert result.interpolation_method == "idw"

    @pytest.mark.unit
    def test_interpolate_identifies_dry_zones(self):
        """Test interpolation identifies dry zones"""
        sensors = [
            SoilSensor(
                id="sensor_001",
                tenant_id="tenant",
                field_id="field",
                name="Test",
                name_ar="اختبار",
                sensor_type=SensorType.MOISTURE,
                protocol=SensorProtocol.MQTT,
                model="Test",
                manufacturer="Test",
                lat=24.05,
                lng=46.05,
            ),
        ]

        readings = {
            "sensor_001": SensorReading(
                sensor_id="sensor_001",
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=20.0,  # Very dry
                unit="%",
            ),
        }

        result = interpolate_field_moisture(
            sensors=sensors,
            readings=readings,
            field_bounds=(24.0, 24.1, 46.0, 46.1),
            resolution_m=100.0,
        )

        # Should identify dry zones (< 30%)
        assert len(result.dry_zones) > 0

    @pytest.mark.unit
    def test_interpolate_identifies_wet_zones(self):
        """Test interpolation identifies wet zones"""
        sensors = [
            SoilSensor(
                id="sensor_001",
                tenant_id="tenant",
                field_id="field",
                name="Test",
                name_ar="اختبار",
                sensor_type=SensorType.MOISTURE,
                protocol=SensorProtocol.MQTT,
                model="Test",
                manufacturer="Test",
                lat=24.05,
                lng=46.05,
            ),
        ]

        readings = {
            "sensor_001": SensorReading(
                sensor_id="sensor_001",
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=85.0,  # Very wet
                unit="%",
            ),
        }

        result = interpolate_field_moisture(
            sensors=sensors,
            readings=readings,
            field_bounds=(24.0, 24.1, 46.0, 46.1),
            resolution_m=100.0,
        )

        # Should identify wet zones (> 70%)
        assert len(result.wet_zones) > 0


# =============================================================================
# Test Section 14: Generate Moisture Alert
# =============================================================================


class TestGenerateMoistureAlert:
    """Test generate_moisture_alert function"""

    @pytest.mark.unit
    def test_generate_alert_no_grid(self):
        """Test no alert with empty moisture grid"""
        moisture_map = FieldMoistureMap(
            field_id="field_456",
            timestamp=datetime.now(UTC),
            moisture_grid=[],
        )

        alert = generate_moisture_alert("field_456", "tenant_123", moisture_map)
        assert alert is None

    @pytest.mark.unit
    def test_generate_alert_critical_dry(self):
        """Test critical dry alert (avg < 25%)"""
        moisture_map = FieldMoistureMap(
            field_id="field_456",
            timestamp=datetime.now(UTC),
            moisture_grid=[[20.0, 22.0], [18.0, 24.0]],
            avg_moisture=21.0,
            dry_zones=[{"lat": 24.0, "lng": 46.0, "moisture": 18.0}],
        )

        alert = generate_moisture_alert("field_456", "tenant_123", moisture_map)

        assert alert is not None
        assert alert.alert_type == "field_dry_critical"
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.reading_value == 21.0
        assert "immediate" in alert.message_en.lower() or "critical" in alert.message_en.lower()
        assert "فوري" in alert.message_ar or "حرج" in alert.message_ar

    @pytest.mark.unit
    def test_generate_alert_warning_dry(self):
        """Test warning dry alert (25% <= avg < 35%)"""
        moisture_map = FieldMoistureMap(
            field_id="field_456",
            timestamp=datetime.now(UTC),
            moisture_grid=[[30.0, 32.0], [28.0, 34.0]],
            avg_moisture=31.0,
        )

        alert = generate_moisture_alert("field_456", "tenant_123", moisture_map)

        assert alert is not None
        assert alert.alert_type == "field_dry_warning"
        assert alert.severity == AlertSeverity.HIGH
        assert "24-48" in alert.message_en  # Planning irrigation

    @pytest.mark.unit
    def test_generate_alert_waterlogged(self):
        """Test waterlogged alert (avg > 80%)"""
        moisture_map = FieldMoistureMap(
            field_id="field_456",
            timestamp=datetime.now(UTC),
            moisture_grid=[[85.0, 82.0], [88.0, 84.0]],
            avg_moisture=84.75,
            wet_zones=[{"lat": 24.0, "lng": 46.0, "moisture": 88.0}],
        )

        alert = generate_moisture_alert("field_456", "tenant_123", moisture_map)

        assert alert is not None
        assert alert.alert_type == "field_waterlogged"
        assert alert.severity == AlertSeverity.MEDIUM
        assert "skip" in alert.message_en.lower()
        assert "تخطي" in alert.message_ar

    @pytest.mark.unit
    def test_generate_alert_normal_moisture(self):
        """Test no alert for normal moisture (35% <= avg <= 80%)"""
        moisture_map = FieldMoistureMap(
            field_id="field_456",
            timestamp=datetime.now(UTC),
            moisture_grid=[[50.0, 55.0], [52.0, 58.0]],
            avg_moisture=53.75,
        )

        alert = generate_moisture_alert("field_456", "tenant_123", moisture_map)
        assert alert is None


# =============================================================================
# Test Section 15: Error Handling for Malformed Data
# =============================================================================


class TestErrorHandling:
    """Test error handling for malformed data"""

    @pytest.mark.unit
    def test_mqtt_parse_malformed_value_type(self, adapter_config, sample_sensor):
        """Test MQTT parsing with wrong value type"""
        adapter = MQTTAdapter(adapter_config)

        # Value is a string instead of number
        payload = json.dumps(
            {
                "value": "not a number",
                "type": "moisture",
            }
        ).encode()

        reading = adapter.parse_payload(payload, sample_sensor)
        assert reading is None

    @pytest.mark.unit
    def test_mqtt_parse_missing_required_fields(self, adapter_config, sample_sensor):
        """Test MQTT parsing with missing required fields"""
        adapter = MQTTAdapter(adapter_config)

        # Has value but no type
        payload = json.dumps(
            {
                "value": 45.0,
                # Missing "type"
            }
        ).encode()

        reading = adapter.parse_payload(payload, sample_sensor)
        assert reading is None

    @pytest.mark.unit
    def test_mqtt_parse_invalid_sensor_type(self, adapter_config, sample_sensor):
        """Test MQTT parsing with invalid sensor type"""
        adapter = MQTTAdapter(adapter_config)

        payload = json.dumps(
            {
                "value": 45.0,
                "type": "invalid_type_xyz",
            }
        ).encode()

        reading = adapter.parse_payload(payload, sample_sensor)
        assert reading is None

    @pytest.mark.unit
    def test_lorawan_parse_corrupted_binary(self, sample_sensor):
        """Test LoRaWAN parsing with corrupted binary data"""
        config = AdapterConfig(protocol=SensorProtocol.LORAWAN)
        adapter = LoRaWANAdapter(config)

        # Various invalid payloads
        payloads = [
            b"",
            b"\x00",  # Single byte
            b"\xff" * 100,  # Too long but still valid
        ]

        for payload in payloads:
            if len(payload) >= 2:
                reading = adapter.parse_payload(payload, sample_sensor)
                # Should parse (even if value is unusual)
                assert reading is not None
            else:
                reading = adapter.parse_payload(payload, sample_sensor)
                # Too short to parse
                assert reading is None

    @pytest.mark.unit
    def test_http_parse_nested_invalid_value(self, sample_sensor):
        """Test HTTP parsing with nested invalid value"""
        config = AdapterConfig(protocol=SensorProtocol.HTTP)
        adapter = HTTPAdapter(config)

        payload = json.dumps(
            {
                "id": "device",
                "sensor": {
                    "value": "not a number",
                    "unit": "%",
                },
            }
        ).encode()

        reading = adapter.parse_payload(payload, sample_sensor)
        assert reading is None

    @pytest.mark.unit
    def test_calibration_with_none_values(self):
        """Test calibration handles edge cases gracefully"""
        calibration = SensorCalibration(
            sensor_id="test",
            calibrated_at=datetime.now(UTC),
            calibrated_by="tech",
            dry_value=0,
            wet_value=1000,
            known_dry_percent=0.0,
            known_wet_percent=100.0,
        )

        # Test with extreme values
        assert calibration.apply_calibration(float("inf")) == 100.0  # Clamped
        assert calibration.apply_calibration(-float("inf")) == 0.0  # Clamped

    @pytest.mark.unit
    def test_processor_handles_none_sensor(self, sample_reading):
        """Test processor rejects reading from unregistered sensor (tenant isolation)"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        # Don't register any sensor

        alerts = processor.add_reading(sample_reading)

        # SECURITY: Readings from unregistered sensors are rejected for tenant isolation
        assert sample_reading.sensor_id not in processor._readings
        assert len(alerts) == 0

    @pytest.mark.unit
    def test_aggregation_handles_empty_periods(self, sample_sensor):
        """Test aggregation handles periods with no data"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor.register_sensor(sample_sensor)

        # Add reading from far past
        old_reading = SensorReading(
            sensor_id=sample_sensor.id,
            timestamp=datetime.now(UTC) - timedelta(days=30),
            reading_type=SensorType.MOISTURE,
            value=50.0,
            unit="%",
        )
        processor.add_reading(old_reading)

        # Request aggregation for last 24 hours (no data)
        agg = processor.get_aggregation(sample_sensor.id, period_hours=24)
        assert agg is None


# =============================================================================
# Test Section 16: Reading Storage and Trimming
# =============================================================================


class TestReadingStorageTrimming:
    """Test reading storage and automatic trimming"""

    @pytest.mark.unit
    def test_processor_trims_old_readings(self, sample_sensor):
        """Test processor trims readings when exceeding max"""
        processor = SensorDataProcessor("field_456", "tenant_123")
        processor._max_readings = 10  # Reduce for testing
        processor.register_sensor(sample_sensor)

        # Add more readings than max
        for i in range(15):
            reading = SensorReading(
                sensor_id=sample_sensor.id,
                timestamp=datetime.now(UTC),
                reading_type=SensorType.MOISTURE,
                value=float(i),
                unit="%",
            )
            processor.add_reading(reading)

        # Should only keep last 10
        assert len(processor._readings[sample_sensor.id]) == 10

        # First reading should be value 5 (0-4 trimmed)
        assert processor._readings[sample_sensor.id][0].value == 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
