# shared/soil_sensors

Soil Sensors Module | وحدة مجسات التربة

IoT soil sensor integration for the SAHOOL platform. Handles multi-protocol sensor data ingestion, calibration, aggregation, statistical anomaly detection, and spatial moisture interpolation across field grids. Supports MQTT, LoRaWAN, and HTTP protocols.

## File Structure

```
shared/soil_sensors/
├── __init__.py      # Module exports
├── models.py        # Data models: SoilSensor, SensorReading, SensorAlert, SensorCalibration, etc.
├── adapters.py      # Protocol adapters: MQTTAdapter, LoRaWANAdapter, HTTPAdapter
└── processor.py     # SensorDataProcessor: calibration, threshold alerts, anomaly detection, IDW interpolation
```

## Key Components

### Data Models (`models.py`)

| Model | Purpose |
|-------|---------|
| `SoilSensor` | Sensor device record with location, protocol, thresholds, calibration, network config |
| `SensorReading` | Single measurement with value, unit, quality score, GPS, battery, RSSI |
| `SensorCalibration` | Dry/wet calibration points with linear interpolation and scale/offset factors |
| `SensorAlert` | Threshold or anomaly alert with severity, bilingual messages, acknowledgment state |
| `FieldMoistureMap` | IDW-interpolated grid of field moisture with dry/wet zone lists |
| `SensorAggregation` | Time-period statistics: avg, min, max, std, trend, trend rate |

Enums:
- `SensorType`: MOISTURE / TEMPERATURE / EC / PH / NPK / SALINITY / WATER_LEVEL / MULTI
- `SensorProtocol`: MQTT / LORAWAN / HTTP / ZIGBEE / NBIOT / CELLULAR
- `SensorStatus`: ACTIVE / OFFLINE / LOW_BATTERY / MAINTENANCE / ERROR / CALIBRATING
- `AlertSeverity`: INFO / LOW / MEDIUM / HIGH / CRITICAL

### Protocol Adapters (`adapters.py`)

`SensorAdapter` is the base class for all protocol adapters. The `get_adapter(protocol)` factory returns the appropriate adapter.

- `MQTTAdapter`: Subscribes to MQTT topics and normalizes payloads to `SensorReading`
- `LoRaWANAdapter`: Handles LoRaWAN uplink decoding (EUI-based addressing, duty cycle management)
- `HTTPAdapter`: Polls or receives webhook data from HTTP-enabled sensors

### Sensor Data Processor (`processor.py`)

`SensorDataProcessor` is the main processing engine for a field. Key capabilities:

**Calibration application**: When a `SoilSensor` has an attached `SensorCalibration`, raw values are automatically linearized between dry and wet calibration points with scale and offset correction.

**Threshold alerting**: Four alert types are generated automatically:
- `critical_low` / `critical_high` (CRITICAL severity)
- `low_moisture` / `high_moisture` (HIGH / MEDIUM severity)

**Anomaly detection**: Z-score analysis on the last 24 hours of readings. Readings beyond 3 standard deviations trigger a MEDIUM-severity `anomaly_detected` alert.

**Field interpolation**: `interpolate_field_moisture()` uses Inverse Distance Weighting (IDW, power=2) to build a spatial moisture grid from sensor point readings. Identifies dry zones (< 30%) and wet zones (> 70%) for targeted irrigation.

Standalone functions:
- `aggregate_readings(readings, interval_minutes)` - time-bucket aggregation with trend analysis
- `detect_anomalies(readings, threshold_std)` - batch anomaly detection
- `interpolate_field_moisture(sensors, readings, field_bounds, resolution_m)` - IDW grid

## Usage Example

```python
from datetime import datetime, UTC
from shared.soil_sensors import (
    SoilSensor,
    SensorReading,
    SensorType,
    SensorProtocol,
    SensorCalibration,
    SensorDataProcessor,
    aggregate_readings,
    detect_anomalies,
    interpolate_field_moisture,
    get_adapter,
)

# Define a sensor
sensor = SoilSensor(
    id="SMS-001",
    tenant_id="TENANT-001",
    field_id="FIELD-003",
    name="Zone A Soil Moisture",
    name_ar="رطوبة التربة - المنطقة أ",
    sensor_type=SensorType.MOISTURE,
    protocol=SensorProtocol.MQTT,
    model="CropX-100",
    manufacturer="CropX",
    lat=24.7135,
    lng=46.6752,
    depth_cm=30,
    min_threshold=30.0,    # Alert below 30%
    max_threshold=75.0,    # Alert above 75%
    critical_min=20.0,
    critical_max=85.0,
    mqtt_topic="sahool/field/FIELD-003/sensor/SMS-001",
)

# Attach calibration
sensor.calibration = SensorCalibration(
    sensor_id="SMS-001",
    calibrated_at=datetime.now(UTC),
    calibrated_by="technician-001",
    dry_value=200.0,
    wet_value=800.0,
    known_dry_percent=5.0,
    known_wet_percent=95.0,
    soil_type="loamy",
    soil_type_ar="طينية رملية",
)

# Process incoming readings
processor = SensorDataProcessor(field_id="FIELD-003", tenant_id="TENANT-001")
processor.register_sensor(sensor)

reading = SensorReading(
    sensor_id="SMS-001",
    timestamp=datetime.now(UTC),
    reading_type=SensorType.MOISTURE,
    value=22.0,    # Will trigger critical_low alert
    unit="%",
    raw_value=250.0,
    battery_percent=85.0,
)

alerts = processor.add_reading(reading)
for alert in alerts:
    print(f"[{alert.severity.value}] {alert.title_en}")
    print(f"  {alert.title_ar}")
    print(f"  {alert.message_en}")

# Time-period aggregation
aggregation = processor.get_aggregation("SMS-001", period_hours=24)
if aggregation:
    print(f"24h avg: {aggregation.avg_value:.1f}% | Trend: {aggregation.trend}")

# Field moisture map via IDW interpolation
sensors = [sensor]
latest_readings = processor.get_latest_readings()
moisture_map = interpolate_field_moisture(
    sensors=sensors,
    readings=latest_readings,
    field_bounds=(24.71, 24.72, 46.67, 46.68),  # min_lat, max_lat, min_lng, max_lng
    resolution_m=10.0,
)
print(f"Field avg moisture: {moisture_map.avg_moisture:.1f}%")
print(f"Dry zones: {len(moisture_map.dry_zones)}")
print(f"Wet zones: {len(moisture_map.wet_zones)}")
```

## Version

1.0.0 | Author: SAHOOL Platform Team
