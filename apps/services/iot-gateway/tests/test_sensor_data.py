"""
Comprehensive Sensor Data Normalization Tests
Tests data normalization, format conversion, validation, and edge cases
"""

import json
from datetime import UTC, datetime

import pytest

from apps.services.iot_gateway.src.normalizer import (
    NormalizedReading,
    normalize,
    normalize_batch,
    _normalize_sensor_type,
    _normalize_unit,
    _get_default_unit,
    _extract_device_from_topic,
    _extract_field_from_topic,
    _extract_type_from_topic,
)


class TestNormalizedReading:
    """Test NormalizedReading dataclass"""

    def test_create_normalized_reading(self):
        """Test creating a normalized reading"""
        reading = NormalizedReading(
            device_id="sensor_001",
            field_id="field_001",
            sensor_type="soil_moisture",
            value=45.5,
            unit="%",
            timestamp=datetime.now(UTC).isoformat(),
        )

        assert reading.device_id == "sensor_001"
        assert reading.field_id == "field_001"
        assert reading.sensor_type == "soil_moisture"
        assert reading.value == 45.5
        assert reading.unit == "%"

    def test_normalized_reading_to_dict(self):
        """Test converting reading to dictionary"""
        reading = NormalizedReading(
            device_id="sensor_001",
            field_id="field_001",
            sensor_type="soil_moisture",
            value=45.5,
            unit="%",
            timestamp=datetime.now(UTC).isoformat(),
            metadata={"battery": 85, "rssi": -65},
        )

        data = reading.to_dict()
        assert isinstance(data, dict)
        assert data["device_id"] == "sensor_001"
        assert data["metadata"]["battery"] == 85

    def test_normalized_reading_without_metadata(self):
        """Test reading without metadata"""
        reading = NormalizedReading(
            device_id="sensor_001",
            field_id="field_001",
            sensor_type="soil_moisture",
            value=45.5,
            unit="%",
            timestamp=datetime.now(UTC).isoformat(),
        )

        data = reading.to_dict()
        assert "metadata" not in data  # None values are filtered out


class TestBasicNormalization:
    """Test basic payload normalization"""

    def test_normalize_standard_payload(self):
        """Test normalization of standard payload"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_123",
                "type": "soil_moisture",
                "value": 45.5,
                "unit": "%",
            }
        )

        result = normalize(payload)

        assert result.device_id == "sensor_001"
        assert result.field_id == "field_123"
        assert result.sensor_type == "soil_moisture"
        assert result.value == 45.5
        assert result.unit == "%"

    def test_normalize_compact_payload(self):
        """Test normalization of compact payload with abbreviated keys"""
        payload = json.dumps(
            {"d": "sensor_002", "f": "field_456", "t": "temperature", "v": 28.3}
        )

        result = normalize(payload)

        assert result.device_id == "sensor_002"
        assert result.field_id == "field_456"
        assert result.sensor_type == "air_temperature"  # Normalized
        assert result.value == 28.3

    def test_normalize_alternative_key_names(self):
        """Test normalization with alternative key names"""
        payload = json.dumps(
            {
                "deviceId": "sensor_003",
                "fieldId": "field_789",
                "sensorType": "soil_ec",
                "val": 2.5,
                "u": "mS/cm",
            }
        )

        result = normalize(payload)

        assert result.device_id == "sensor_003"
        assert result.field_id == "field_789"
        assert result.sensor_type == "soil_ec"
        assert result.value == 2.5
        assert result.unit == "mS/cm"


class TestSensorTypeNormalization:
    """Test sensor type alias mapping"""

    def test_soil_moisture_aliases(self):
        """Test soil moisture type aliases"""
        assert _normalize_sensor_type("soil_moisture") == "soil_moisture"
        assert _normalize_sensor_type("sm") == "soil_moisture"
        assert _normalize_sensor_type("moisture") == "soil_moisture"
        assert _normalize_sensor_type("vwc") == "soil_moisture"

    def test_temperature_aliases(self):
        """Test temperature type aliases"""
        assert _normalize_sensor_type("air_temperature") == "air_temperature"
        assert _normalize_sensor_type("temp") == "air_temperature"
        assert _normalize_sensor_type("temperature") == "air_temperature"
        assert _normalize_sensor_type("at") == "air_temperature"

    def test_ec_aliases(self):
        """Test EC (conductivity) type aliases"""
        assert _normalize_sensor_type("soil_ec") == "soil_ec"
        assert _normalize_sensor_type("ec") == "soil_ec"
        assert _normalize_sensor_type("conductivity") == "soil_ec"
        assert _normalize_sensor_type("salinity") == "soil_ec"

    def test_water_sensor_aliases(self):
        """Test water sensor type aliases"""
        assert _normalize_sensor_type("water_level") == "water_level"
        assert _normalize_sensor_type("level") == "water_level"
        assert _normalize_sensor_type("wl") == "water_level"

        assert _normalize_sensor_type("water_flow") == "water_flow"
        assert _normalize_sensor_type("flow") == "water_flow"
        assert _normalize_sensor_type("flow_rate") == "water_flow"

    def test_weather_sensor_aliases(self):
        """Test weather sensor type aliases"""
        assert _normalize_sensor_type("wind_speed") == "wind_speed"
        assert _normalize_sensor_type("wind") == "wind_speed"
        assert _normalize_sensor_type("ws") == "wind_speed"

        assert _normalize_sensor_type("rainfall") == "rainfall"
        assert _normalize_sensor_type("rain") == "rainfall"
        assert _normalize_sensor_type("precipitation") == "rainfall"

    def test_unknown_sensor_type(self):
        """Test unknown sensor type returns as-is"""
        result = _normalize_sensor_type("custom_sensor_xyz")
        assert result == "custom_sensor_xyz"

    def test_case_insensitive_sensor_type(self):
        """Test sensor type normalization is case-insensitive"""
        assert _normalize_sensor_type("SOIL_MOISTURE") == "soil_moisture"
        assert _normalize_sensor_type("Temperature") == "air_temperature"
        assert _normalize_sensor_type("EC") == "soil_ec"


class TestUnitNormalization:
    """Test unit normalization"""

    def test_percentage_unit(self):
        """Test percentage unit normalization"""
        assert _normalize_unit("%") == "%"
        assert _normalize_unit("percent") == "%"
        assert _normalize_unit("pct") == "%"

    def test_temperature_units(self):
        """Test temperature unit normalization"""
        assert _normalize_unit("celsius") == "°C"
        assert _normalize_unit("c") == "°C"
        assert _normalize_unit("deg_c") == "°C"

        assert _normalize_unit("fahrenheit") == "°F"
        assert _normalize_unit("f") == "°F"

    def test_ec_units(self):
        """Test EC unit normalization"""
        assert _normalize_unit("millisiemens") == "mS/cm"
        assert _normalize_unit("ms_cm") == "mS/cm"
        assert _normalize_unit("decisiemens") == "dS/m"

    def test_speed_units(self):
        """Test speed unit normalization"""
        assert _normalize_unit("meters_per_second") == "m/s"
        assert _normalize_unit("mps") == "m/s"
        assert _normalize_unit("kilometers_per_hour") == "km/h"
        assert _normalize_unit("kph") == "km/h"

    def test_flow_units(self):
        """Test flow unit normalization"""
        assert _normalize_unit("liters_per_minute") == "L/min"
        assert _normalize_unit("lpm") == "L/min"
        assert _normalize_unit("cubic_meters_per_hour") == "m³/h"

    def test_unknown_unit(self):
        """Test unknown unit returns as-is"""
        result = _normalize_unit("custom_unit")
        assert result == "custom_unit"


class TestDefaultUnits:
    """Test default unit assignment"""

    def test_soil_sensor_defaults(self):
        """Test default units for soil sensors"""
        assert _get_default_unit("soil_moisture") == "%"
        assert _get_default_unit("soil_temperature") == "°C"
        assert _get_default_unit("soil_ec") == "mS/cm"
        assert _get_default_unit("soil_ph") == ""

    def test_weather_sensor_defaults(self):
        """Test default units for weather sensors"""
        assert _get_default_unit("air_temperature") == "°C"
        assert _get_default_unit("air_humidity") == "%"
        assert _get_default_unit("wind_speed") == "m/s"
        assert _get_default_unit("wind_direction") == "°"
        assert _get_default_unit("rainfall") == "mm"
        assert _get_default_unit("atmospheric_pressure") == "hPa"

    def test_water_sensor_defaults(self):
        """Test default units for water sensors"""
        assert _get_default_unit("water_level") == "cm"
        assert _get_default_unit("water_flow") == "L/min"

    def test_unknown_sensor_default(self):
        """Test default unit for unknown sensor"""
        assert _get_default_unit("unknown_sensor") == ""


class TestMetadataHandling:
    """Test metadata extraction and handling"""

    def test_normalize_with_battery_metadata(self):
        """Test normalization with battery metadata"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_moisture",
                "value": 45.5,
                "battery": 85,
            }
        )

        result = normalize(payload)

        assert result.metadata is not None
        assert result.metadata["battery"] == 85

    def test_normalize_with_rssi_metadata(self):
        """Test normalization with RSSI metadata"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_moisture",
                "value": 45.5,
                "rssi": -65,
            }
        )

        result = normalize(payload)

        assert result.metadata is not None
        assert result.metadata["rssi"] == -65

    def test_normalize_with_explicit_metadata(self):
        """Test normalization with explicit metadata field"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_moisture",
                "value": 45.5,
                "metadata": {"custom_field": "custom_value", "firmware": "v1.2.3"},
            }
        )

        result = normalize(payload)

        assert result.metadata["custom_field"] == "custom_value"
        assert result.metadata["firmware"] == "v1.2.3"

    def test_normalize_with_mixed_metadata(self):
        """Test normalization with both battery/rssi and explicit metadata"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_moisture",
                "value": 45.5,
                "battery": 85,
                "rssi": -65,
                "metadata": {"location": "zone_1"},
            }
        )

        result = normalize(payload)

        assert result.metadata["battery"] == 85
        assert result.metadata["rssi"] == -65
        assert result.metadata["location"] == "zone_1"


class TestTimestampHandling:
    """Test timestamp extraction and handling"""

    def test_normalize_with_iso_timestamp(self):
        """Test normalization with ISO timestamp"""
        timestamp = datetime.now(UTC).isoformat()
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_moisture",
                "value": 45.5,
                "timestamp": timestamp,
            }
        )

        result = normalize(payload)

        assert result.timestamp == timestamp

    def test_normalize_with_unix_timestamp(self):
        """Test normalization with Unix timestamp"""
        unix_ts = 1672531200  # 2023-01-01 00:00:00 UTC
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_moisture",
                "value": 45.5,
                "timestamp": unix_ts,
            }
        )

        result = normalize(payload)

        assert result.timestamp is not None
        assert "2023-01-01" in result.timestamp

    def test_normalize_without_timestamp(self):
        """Test normalization without timestamp (should use current time)"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_moisture",
                "value": 45.5,
            }
        )

        result = normalize(payload)

        assert result.timestamp is not None
        # Should be recent (within 1 second)
        ts = datetime.fromisoformat(result.timestamp.replace("Z", "+00:00"))
        diff = abs((datetime.now(UTC) - ts).total_seconds())
        assert diff < 2

    def test_normalize_with_alternative_timestamp_keys(self):
        """Test normalization with alternative timestamp key names"""
        timestamp = datetime.now(UTC).isoformat()

        # Test with 'ts' key
        payload1 = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_moisture",
                "value": 45.5,
                "ts": timestamp,
            }
        )
        result1 = normalize(payload1)
        assert result1.timestamp == timestamp

        # Test with 'time' key
        payload2 = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_moisture",
                "value": 45.5,
                "time": timestamp,
            }
        )
        result2 = normalize(payload2)
        assert result2.timestamp == timestamp


class TestTopicExtraction:
    """Test MQTT topic parsing"""

    def test_extract_device_from_topic(self):
        """Test extracting device ID from MQTT topic"""
        topic = "sahool/sensors/sensor_001/field_123/soil_moisture"
        device_id = _extract_device_from_topic(topic)
        assert device_id == "sensor_001"

    def test_extract_field_from_topic(self):
        """Test extracting field ID from MQTT topic"""
        topic = "sahool/sensors/sensor_001/field_123/soil_moisture"
        field_id = _extract_field_from_topic(topic)
        assert field_id == "field_123"

    def test_extract_type_from_topic(self):
        """Test extracting sensor type from MQTT topic"""
        topic = "sahool/sensors/sensor_001/field_123/soil_moisture"
        sensor_type = _extract_type_from_topic(topic)
        assert sensor_type == "soil_moisture"

    def test_extract_from_invalid_topic(self):
        """Test extraction from invalid topic returns None"""
        topic = "invalid/topic/format"
        assert _extract_device_from_topic(topic) is None
        assert _extract_field_from_topic(topic) is None
        assert _extract_type_from_topic(topic) is None

    def test_normalize_from_topic(self):
        """Test normalization using MQTT topic context"""
        payload = json.dumps({"type": "soil_moisture", "value": 40})
        topic = "sahool/sensors/sensor_005/field_abc/soil_moisture"

        result = normalize(payload, topic)

        assert result.device_id == "sensor_005"
        assert result.field_id == "field_abc"
        assert result.sensor_type == "soil_moisture"
        assert result.value == 40
        assert result.raw_topic == topic


class TestBatchNormalization:
    """Test batch payload normalization"""

    def test_normalize_batch_with_readings_key(self):
        """Test batch normalization with 'readings' key"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "readings": [
                    {"type": "soil_moisture", "value": 45.5},
                    {"type": "soil_temperature", "value": 22.3},
                    {"type": "soil_ec", "value": 2.1},
                ],
            }
        )

        results = normalize_batch(payload)

        assert len(results) == 3
        assert results[0].sensor_type == "soil_moisture"
        assert results[1].sensor_type == "soil_temperature"
        assert results[2].sensor_type == "soil_ec"

    def test_normalize_batch_with_data_key(self):
        """Test batch normalization with 'data' key"""
        payload = json.dumps(
            {
                "device_id": "sensor_002",
                "field_id": "field_002",
                "data": [
                    {"type": "air_temperature", "value": 25.5},
                    {"type": "air_humidity", "value": 65.0},
                ],
            }
        )

        results = normalize_batch(payload)

        assert len(results) == 2
        assert results[0].sensor_type == "air_temperature"
        assert results[1].sensor_type == "air_humidity"

    def test_normalize_batch_direct_array(self):
        """Test batch normalization with direct array"""
        payload = json.dumps(
            [
                {
                    "device_id": "sensor_003",
                    "field_id": "field_003",
                    "type": "wind_speed",
                    "value": 12.5,
                },
                {
                    "device_id": "sensor_003",
                    "field_id": "field_003",
                    "type": "rainfall",
                    "value": 5.2,
                },
            ]
        )

        results = normalize_batch(payload)

        assert len(results) == 2
        assert all(r.device_id == "sensor_003" for r in results)

    def test_normalize_batch_inherits_common_fields(self):
        """Test that batch readings inherit common device/field IDs"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "readings": [
                    {"type": "soil_moisture", "value": 45.5},
                    {"type": "soil_temperature", "value": 22.3},
                ],
            }
        )

        results = normalize_batch(payload)

        assert all(r.device_id == "sensor_001" for r in results)
        assert all(r.field_id == "field_001" for r in results)

    def test_normalize_batch_single_reading(self):
        """Test batch normalization with single reading"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_moisture",
                "value": 45.5,
            }
        )

        results = normalize_batch(payload)

        assert len(results) == 1
        assert results[0].sensor_type == "soil_moisture"


class TestErrorHandling:
    """Test error handling in normalization"""

    def test_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError"""
        payload = "this is not valid JSON"

        with pytest.raises(ValueError, match="Invalid JSON"):
            normalize(payload)

    def test_missing_device_id_raises_error(self):
        """Test that missing device_id raises error"""
        payload = json.dumps({"field_id": "field_001", "type": "temp", "value": 25})

        with pytest.raises(ValueError, match="device_id"):
            normalize(payload)

    def test_missing_field_id_raises_error(self):
        """Test that missing field_id raises error"""
        payload = json.dumps({"device_id": "sensor_001", "type": "temp", "value": 25})

        with pytest.raises(ValueError, match="field_id"):
            normalize(payload)

    def test_missing_sensor_type_raises_error(self):
        """Test that missing sensor type raises error"""
        payload = json.dumps(
            {"device_id": "sensor_001", "field_id": "field_001", "value": 25}
        )

        with pytest.raises(ValueError, match="sensor type"):
            normalize(payload)

    def test_missing_value_raises_error(self):
        """Test that missing value raises error"""
        payload = json.dumps(
            {"device_id": "sensor_001", "field_id": "field_001", "type": "temp"}
        )

        with pytest.raises(ValueError, match="value"):
            normalize(payload)

    def test_invalid_value_type_raises_error(self):
        """Test that non-numeric value raises error"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "temp",
                "value": "not a number",
            }
        )

        with pytest.raises(ValueError, match="Invalid value"):
            normalize(payload)


class TestRealWorldPayloads:
    """Test real-world sensor payload formats"""

    def test_lorawanarduino_payload(self):
        """Test LoRaWAN Arduino-style payload"""
        payload = json.dumps(
            {
                "d": "lora_sensor_001",
                "f": "field_north_01",
                "t": "sm",
                "v": 42.3,
                "battery": 78,
                "rssi": -72,
            }
        )

        result = normalize(payload)

        assert result.device_id == "lora_sensor_001"
        assert result.field_id == "field_north_01"
        assert result.sensor_type == "soil_moisture"
        assert result.value == 42.3
        assert result.metadata["battery"] == 78
        assert result.metadata["rssi"] == -72

    def test_weather_station_payload(self):
        """Test weather station multi-sensor payload"""
        payload = json.dumps(
            {
                "device_id": "weather_station_001",
                "field_id": "field_central",
                "readings": [
                    {"type": "temp", "value": 28.5, "unit": "celsius"},
                    {"type": "humidity", "value": 65.2, "unit": "percent"},
                    {"type": "wind", "value": 15.3, "unit": "kph"},
                    {"type": "rain", "value": 2.5, "unit": "mm"},
                ],
            }
        )

        results = normalize_batch(payload)

        assert len(results) == 4
        assert results[0].sensor_type == "air_temperature"
        assert results[0].unit == "°C"
        assert results[1].sensor_type == "air_humidity"
        assert results[1].unit == "%"
        assert results[2].sensor_type == "wind_speed"
        assert results[3].sensor_type == "rainfall"

    def test_soil_probe_payload(self):
        """Test soil probe with multiple depths"""
        payload = json.dumps(
            {
                "device_id": "soil_probe_001",
                "field_id": "field_west",
                "data": [
                    {
                        "type": "soil_moisture",
                        "value": 45.5,
                        "metadata": {"depth": "10cm"},
                    },
                    {
                        "type": "soil_moisture",
                        "value": 52.3,
                        "metadata": {"depth": "20cm"},
                    },
                    {
                        "type": "soil_moisture",
                        "value": 58.7,
                        "metadata": {"depth": "30cm"},
                    },
                ],
            }
        )

        results = normalize_batch(payload)

        assert len(results) == 3
        assert all(r.sensor_type == "soil_moisture" for r in results)
        assert results[0].metadata["depth"] == "10cm"
        assert results[1].metadata["depth"] == "20cm"
        assert results[2].metadata["depth"] == "30cm"

    def test_minimalist_payload(self):
        """Test minimal payload with only essential fields"""
        payload = json.dumps({"d": "s1", "f": "f1", "t": "sm", "v": 50})
        topic = "sahool/sensors/s1/f1/sm"

        result = normalize(payload, topic)

        assert result.device_id == "s1"
        assert result.field_id == "f1"
        assert result.sensor_type == "soil_moisture"
        assert result.value == 50.0
        assert result.unit == "%"  # Default unit


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_zero_value(self):
        """Test normalization with zero value"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "rainfall",
                "value": 0,
            }
        )

        result = normalize(payload)

        assert result.value == 0.0

    def test_negative_value(self):
        """Test normalization with negative value (e.g., temperature)"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "air_temperature",
                "value": -5.5,
            }
        )

        result = normalize(payload)

        assert result.value == -5.5

    def test_very_large_value(self):
        """Test normalization with very large value"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "light",
                "value": 150000.0,
            }
        )

        result = normalize(payload)

        assert result.value == 150000.0

    def test_decimal_precision(self):
        """Test that decimal precision is preserved"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_ec",
                "value": 2.345678,
            }
        )

        result = normalize(payload)

        assert result.value == 2.345678

    def test_empty_unit(self):
        """Test normalization with empty unit string"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_ph",
                "value": 6.5,
                "unit": "",
            }
        )

        result = normalize(payload)

        assert result.unit == ""

    def test_special_characters_in_ids(self):
        """Test normalization with special characters in IDs"""
        payload = json.dumps(
            {
                "device_id": "sensor-001_v2",
                "field_id": "field_north-west_01",
                "type": "soil_moisture",
                "value": 45.5,
            }
        )

        result = normalize(payload)

        assert result.device_id == "sensor-001_v2"
        assert result.field_id == "field_north-west_01"

    def test_unicode_in_metadata(self):
        """Test normalization with Unicode characters in metadata"""
        payload = json.dumps(
            {
                "device_id": "sensor_001",
                "field_id": "field_001",
                "type": "soil_moisture",
                "value": 45.5,
                "metadata": {"location": "المنطقة الشمالية", "notes": "测试"},
            }
        )

        result = normalize(payload)

        assert result.metadata["location"] == "المنطقة الشمالية"
        assert result.metadata["notes"] == "测试"
