# IoT Gateway - Microservice Analysis Document

> **Service Name**: iot-gateway
> **Type**: Python (FastAPI)
> **Port**: 8106
> **Version**: 16.0.0
> **Description**: MQTT to NATS bridge for sensor data ingestion

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [MQTT Integration](#mqtt-integration)
5. [NATS Events](#nats-events)
6. [Data Models](#data-models)
7. [Data Normalization](#data-normalization)
8. [Device Registry](#device-registry)
9. [Sensor Aggregation](#sensor-aggregation)
10. [Dependencies](#dependencies)
11. [Environment Variables](#environment-variables)
12. [Security](#security)
13. [Bugs and Issues](#bugs-and-issues)
14. [Recommended Fixes](#recommended-fixes)

---

## Overview

The IoT Gateway is the primary entry point for sensor data into the SAHOOL platform. It acts as a bridge between MQTT-enabled IoT devices and the NATS event system, providing:

- **MQTT Bridge**: Subscribes to MQTT topics and forwards normalized data to NATS
- **HTTP API**: Alternative REST API for devices that support HTTP
- **Data Normalization**: Converts various sensor payload formats to standard format
- **Device Registry**: In-memory device registration and status tracking
- **Sensor Aggregation**: Advanced analytics, statistics, and anomaly detection
- **Value Range Validation**: Validates sensor readings against predefined ranges
- **Offline Detection**: Monitors device connectivity and publishes alerts

### Key Features

| Feature | Description (EN) | Description (AR) |
|---------|------------------|------------------|
| MQTT Bridge | MQTT to NATS protocol bridging | جسر بروتوكول MQTT إلى NATS |
| Data Normalization | Standardize sensor payload formats | توحيد صيغ بيانات المستشعرات |
| Device Registry | Track device status and metadata | تتبع حالة الأجهزة وبياناتها |
| Value Validation | Validate sensor value ranges | التحقق من نطاقات قيم المستشعرات |
| Offline Detection | Alert when devices go offline | تنبيه عند انقطاع اتصال الأجهزة |
| Batch Processing | Handle multiple readings at once | معالجة قراءات متعددة دفعة واحدة |
| Sensor Aggregation | Statistical analysis and anomaly detection | تحليل إحصائي واكتشاف الشذوذات |

### Downstream Services

The following services depend on iot-gateway:

| Service | Purpose |
|---------|---------|
| `irrigation-smart` | Receives sensor data for irrigation decisions |

---

## Architecture

```
                    +------------------+
                    |   Kong Gateway   |
                    | /api/v1/iot-gw/* |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   IoT Gateway    |
                    |    (FastAPI)     |
                    |    Port: 8106    |
                    +--------+---------+
                             |
        +--------------------+--------------------+
        |                    |                    |
+-------v-------+    +-------v-------+    +-------v-------+
|  MQTT Broker  |    |     NATS      |    |  PostgreSQL   |
| (Mosquitto)   |    |  Port: 4222   |    | (via pgbouncer)|
|  Port: 1883   |    +---------------+    +---------------+
+-------+-------+
        |
+-------v-------+
|  IoT Devices  |
|  (Sensors,    |
|   Gateways)   |
+---------------+
```

### Component Responsibilities

| Component | File | Purpose |
|-----------|------|---------|
| `main.py` | `src/main.py` | FastAPI app, API endpoints, MQTT message handling |
| `MqttClient` | `src/mqtt_client.py` | Async MQTT client with auto-reconnection |
| `IoTPublisher` | `src/events/publish.py` | NATS event publishing |
| `DeviceRegistry` | `src/registry.py` | In-memory device management |
| `normalize()` | `src/normalizer.py` | Data format normalization |
| `SensorAggregator` | `src/sensor_aggregator.py` | Statistics and anomaly detection |

---

## API Endpoints

### Kong Gateway Routes

| Route | Strip Path | Target |
|-------|------------|--------|
| `/api/v1/iot-gateway` | true | `http://iot-gateway:8106` |
| `/iot-gateway` | true | `http://iot-gateway:8106` |

### Health Endpoints (No Authentication Required)

#### GET /health
Simple health check endpoint.

**Response (200 OK)**:
```json
{
  "status": "ok",
  "service": "iot-gateway"
}
```

#### GET /healthz
Kubernetes liveness probe - always returns OK if service is running.

**Response (200 OK)**:
```json
{
  "status": "ok",
  "service": "iot-gateway"
}
```

#### GET /readyz
Kubernetes readiness probe.

**Response (200 OK)**:
```json
{
  "status": "ready",
  "service": "iot-gateway",
  "version": "16.0.0",
  "checks": {
    "service": "ready"
  }
}
```

---

### Sensor Data Endpoints

#### POST /sensor/reading
Submit a single sensor reading via HTTP.

**Security Features**:
- Device must be registered first
- Validates tenant isolation
- Validates field association
- Validates sensor value ranges
- Logs all operations for audit

**Request Body**:
```json
{
  "device_id": "sensor_001",
  "tenant_id": "tenant_001",
  "field_id": "field_001",
  "sensor_type": "soil_moisture",
  "value": 45.5,
  "unit": "%",
  "timestamp": "2026-01-25T10:30:00Z",
  "metadata": {
    "battery": 85,
    "rssi": -65
  }
}
```

**Request Schema**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `device_id` | string | yes | 1-100 chars | Device identifier |
| `tenant_id` | string | yes | 1-100 chars | Tenant identifier |
| `field_id` | string | yes | 1-100 chars | Field identifier |
| `sensor_type` | string | yes | 1-50 chars | Sensor type |
| `value` | float | yes | Validated against ranges | Sensor value |
| `unit` | string | no | max 20 chars | Measurement unit |
| `timestamp` | string | no | ISO 8601 | Reading timestamp |
| `metadata` | object | no | - | Additional metadata |

**Response (200 OK)**:
```json
{
  "status": "ok",
  "event_id": "uuid-here",
  "device_id": "sensor_001",
  "sensor_type": "soil_moisture",
  "value": 45.5
}
```

**Error Responses**:
- `404`: Device not registered
- `403`: Device not authorized for tenant/field
- `422`: Validation error (value out of range)
- `503`: Publisher not available

---

#### POST /sensor/batch
Submit multiple sensor readings at once.

**Request Body**:
```json
{
  "device_id": "weather_station_001",
  "tenant_id": "tenant_001",
  "field_id": "field_001",
  "readings": [
    {"type": "air_temperature", "value": 25.5, "unit": "°C"},
    {"type": "air_humidity", "value": 65.0, "unit": "%"},
    {"type": "wind_speed", "value": 12.3, "unit": "km/h"}
  ]
}
```

**Request Schema**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `device_id` | string | yes | 1-100 chars | Device identifier |
| `tenant_id` | string | yes | 1-100 chars | Tenant identifier |
| `field_id` | string | yes | 1-100 chars | Field identifier |
| `readings` | array | yes | 1-100 items | Array of readings |

**Reading Object Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` or `sensor_type` | string | yes | Sensor type |
| `value` or `v` | float | yes | Sensor value |
| `unit` or `u` | string | no | Measurement unit |

**Response (200 OK)**:
```json
{
  "status": "ok",
  "count": 3,
  "validated_count": 3,
  "event_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

---

### Device Management Endpoints

#### POST /device/register
Register a new IoT device.

**Request Body**:
```json
{
  "device_id": "sensor_001",
  "tenant_id": "tenant_001",
  "field_id": "field_001",
  "device_type": "soil_sensor",
  "name_ar": "حساس تربة 1",
  "name_en": "Soil Sensor 1",
  "location": {"lat": 24.7136, "lng": 46.6753},
  "metadata": {"firmware_version": "1.2.3"}
}
```

**Request Schema**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `device_id` | string | yes | 1-100 chars | Unique device identifier |
| `tenant_id` | string | yes | 1-100 chars | Tenant identifier |
| `field_id` | string | yes | 1-100 chars | Field identifier |
| `device_type` | string | yes | 1-50 chars | Device type |
| `name_ar` | string | yes | 1-200 chars | Arabic name |
| `name_en` | string | yes | 1-200 chars | English name |
| `location` | object | no | - | GPS coordinates |
| `metadata` | object | no | - | Additional metadata |

**Response (200 OK)**:
```json
{
  "status": "ok",
  "device": {
    "device_id": "sensor_001",
    "tenant_id": "tenant_001",
    "field_id": "field_001",
    "device_type": "soil_sensor",
    "name_ar": "حساس تربة 1",
    "name_en": "Soil Sensor 1",
    "status": "unknown",
    "created_at": "2026-01-25T10:30:00Z",
    "updated_at": "2026-01-25T10:30:00Z"
  }
}
```

---

#### GET /device/{device_id}
Get device information.

**Response (200 OK)**:
```json
{
  "device_id": "sensor_001",
  "tenant_id": "tenant_001",
  "field_id": "field_001",
  "device_type": "soil_sensor",
  "name_ar": "حساس تربة 1",
  "name_en": "Soil Sensor 1",
  "status": "online",
  "last_seen": "2026-01-25T10:30:00Z",
  "last_reading": {
    "sensor_type": "soil_moisture",
    "value": 45.5,
    "unit": "%"
  },
  "battery_level": 85,
  "signal_strength": -65
}
```

**Error Response (404)**:
```json
{
  "detail": "Device not found"
}
```

---

#### GET /device/{device_id}/status
Get device status and health.

**Response (200 OK)**:
```json
{
  "device_id": "sensor_001",
  "status": "online",
  "is_online": true,
  "last_seen": "2026-01-25T10:30:00Z",
  "last_reading": {
    "sensor_type": "soil_moisture",
    "value": 45.5,
    "unit": "%"
  },
  "battery_level": 85,
  "signal_strength": -65
}
```

---

#### GET /devices
List registered devices with pagination and filtering.

**Query Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `field_id` | string | - | Filter by field ID |
| `device_type` | string | - | Filter by device type |
| `limit` | int | 50 | Max devices to return (1-100) |
| `offset` | int | 0 | Number of devices to skip |

**Response (200 OK)**:
```json
{
  "devices": [
    {
      "device_id": "sensor_001",
      "tenant_id": "tenant_001",
      "field_id": "field_001",
      "device_type": "soil_sensor",
      "status": "online"
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

---

#### DELETE /device/{device_id}
Remove device from registry.

**Response (200 OK)**:
```json
{
  "status": "ok",
  "device_id": "sensor_001"
}
```

---

### Field Endpoints

#### GET /field/{field_id}/devices
Get all devices for a field.

**Response (200 OK)**:
```json
{
  "field_id": "field_001",
  "devices": [
    {
      "device_id": "sensor_001",
      "device_type": "soil_sensor",
      "status": "online"
    }
  ],
  "count": 5
}
```

---

#### GET /field/{field_id}/latest
Get latest readings from all devices in a field.

**Response (200 OK)**:
```json
{
  "field_id": "field_001",
  "readings": [
    {
      "device_id": "sensor_001",
      "device_type": "soil_sensor",
      "sensor_type": "soil_moisture",
      "value": 45.5,
      "unit": "%",
      "last_seen": "2026-01-25T10:30:00Z"
    }
  ],
  "count": 5
}
```

---

### Statistics Endpoint

#### GET /stats
Get gateway statistics.

**Response (200 OK)**:
```json
{
  "publisher": {
    "readings_published": 1250,
    "status_published": 50,
    "alerts_published": 10,
    "connected": true
  },
  "registry": {
    "total": 25,
    "online": 20,
    "offline": 3,
    "warning": 2,
    "by_type": {
      "soil_sensor": 10,
      "weather_station": 5,
      "flow_meter": 10
    }
  },
  "mqtt": {
    "broker": "mqtt",
    "topic": "sahool/sensors/#"
  }
}
```

---

## MQTT Integration

### MQTT Client

The IoT Gateway uses the `aiomqtt` library (formerly `asyncio-mqtt`) for asynchronous MQTT communication.

**Client Features**:
- Auto-reconnection with configurable interval (default: 5 seconds)
- Username/password authentication support
- Wildcard topic subscription
- QoS handling (0, 1, 2)
- Retained message support

### MQTT Topics

#### Subscribed Topics

| Pattern | Description |
|---------|-------------|
| `sahool/sensors/#` | All sensor data (default topic) |
| `sahool/sensors/{device_id}/{field_id}/{type}` | Device-specific readings |

#### MQTT Topic Format

```
sahool/sensors/{device_id}/{field_id}/{sensor_type}
```

Example: `sahool/sensors/sensor_001/field_001/soil_moisture`

### MQTT Payload Formats

The normalizer supports multiple input formats:

#### Standard Format
```json
{
  "device_id": "sensor_001",
  "field_id": "field_001",
  "type": "soil_moisture",
  "value": 45.5,
  "unit": "%",
  "timestamp": "2026-01-25T10:30:00Z",
  "battery": 85,
  "rssi": -65
}
```

#### Compact Format
```json
{
  "d": "sensor_001",
  "f": "field_001",
  "t": "soil_moisture",
  "v": 45.5,
  "u": "%"
}
```

#### Batch Format
```json
{
  "device_id": "sensor_001",
  "field_id": "field_001",
  "readings": [
    {"type": "temperature", "value": 25.5, "unit": "°C"},
    {"type": "humidity", "value": 65.0, "unit": "%"}
  ]
}
```

### MQTT Message Processing Flow

```
1. MQTT Message Received
       |
       v
2. Normalize Payload (normalizer.py)
       |
       v
3. Check Device Registration
       |
   [Not Registered]
       |
       v
   Auto-register if IOT_AUTO_REGISTER=true
   OR reject message
       |
       v
4. Validate Sensor Value Range
       |
       v
5. Update Device Status in Registry
       |
       v
6. Publish to NATS (sensor_reading event)
       |
       v
7. Publish to sensor-specific NATS subject
```

---

## NATS Events

### Event Envelope Structure

All events are wrapped in a standard envelope:

```json
{
  "event_id": "uuid",
  "event_type": "sensor_reading",
  "version": 1,
  "aggregate_id": "field_001",
  "tenant_id": "tenant_001",
  "correlation_id": "uuid",
  "timestamp": "2026-01-25T10:30:00Z",
  "payload": { }
}
```

### Published Events

#### sensor_reading (v1)
Published when a sensor reading is received.

**Subject**: `sahool.iot.sensor_reading`

**Payload**:
```json
{
  "device_id": "sensor_001",
  "field_id": "field_001",
  "sensor_type": "soil_moisture",
  "value": 45.5,
  "unit": "%",
  "timestamp": "2026-01-25T10:30:00Z",
  "metadata": {
    "battery": 85,
    "rssi": -65
  }
}
```

**Also published to sensor-specific subject**: `sahool.iot.sensor.{sensor_type}`

---

#### device_status (v1)
Published when device status changes (online/offline).

**Subject**: `sahool.iot.device_status`

**Payload**:
```json
{
  "device_id": "sensor_001",
  "field_id": "field_001",
  "status": "offline",
  "last_seen": "2026-01-25T10:30:00Z",
  "battery_level": 85,
  "signal_strength": -65
}
```

---

#### device_registered (v1)
Published when a new device is registered.

**Subject**: `sahool.iot.device_registered`

**Payload**:
```json
{
  "device_id": "sensor_001",
  "field_id": "field_001",
  "device_type": "soil_sensor",
  "name_ar": "حساس تربة 1",
  "name_en": "Soil Sensor 1"
}
```

---

#### device_alert (v1)
Published for device alerts (offline, low battery, etc).

**Subject**: `sahool.iot.device_alert`

**Payload**:
```json
{
  "device_id": "sensor_001",
  "field_id": "field_001",
  "alert_type": "device_offline",
  "message_ar": "الجهاز sensor_001 غير متصل",
  "message_en": "Device sensor_001 is offline",
  "severity": "warning"
}
```

**Alert Types**:

| Type | Arabic | Description |
|------|--------|-------------|
| `device_offline` | جهاز غير متصل | Device went offline |
| `low_battery` | بطارية منخفضة | Battery level < 20% |
| `sensor_error` | خطأ في الحساس | Sensor reporting errors |
| `out_of_range` | قراءة خارج النطاق | Value outside valid range |
| `communication_error` | خطأ في الاتصال | Communication failure |

### NATS Subjects Summary

| Subject | Event Type | Description |
|---------|------------|-------------|
| `sahool.iot.sensor_reading` | sensor_reading | Sensor data received |
| `sahool.iot.device_status` | device_status | Device status change |
| `sahool.iot.device_registered` | device_registered | New device registered |
| `sahool.iot.device_alert` | device_alert | Device alert |
| `sahool.iot.sensor.soil_moisture` | - | Soil moisture readings |
| `sahool.iot.sensor.soil_temperature` | - | Soil temperature readings |
| `sahool.iot.sensor.soil_ec` | - | Soil EC readings |
| `sahool.iot.sensor.air_temperature` | - | Air temperature readings |
| `sahool.iot.sensor.air_humidity` | - | Air humidity readings |
| `sahool.iot.sensor.water_flow` | - | Water flow readings |
| `sahool.iot.sensor.water_level` | - | Water level readings |

---

## Data Models

### SensorReading

```python
@dataclass
class SensorReading:
    device_id: str        # معرف الجهاز
    field_id: str         # معرف الحقل
    sensor_type: str      # نوع المستشعر
    value: float          # القيمة
    unit: str             # الوحدة
    timestamp: str        # وقت القراءة
    metadata: dict | None # بيانات إضافية
    quality_score: float | None  # نقاط الجودة (0-100)
    is_outlier: bool      # هل هي قيمة شاذة
```

### Device

```python
@dataclass
class Device:
    device_id: str
    tenant_id: str
    field_id: str
    device_type: str       # soil_sensor, weather_station, etc.
    name_ar: str
    name_en: str
    status: str            # online, offline, warning, error, unknown
    last_seen: str | None
    last_reading: dict | None
    firmware_version: str | None
    battery_level: float | None
    signal_strength: int | None  # RSSI in dBm
    location: dict | None  # {"lat": ..., "lng": ...}
    metadata: dict
    created_at: str
    updated_at: str
```

### NormalizedReading

```python
@dataclass
class NormalizedReading:
    device_id: str
    field_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: str
    raw_topic: str | None
    metadata: dict | None
```

### AggregatedData

```python
@dataclass
class AggregatedData:
    field_id: str
    sensor_type: str
    time_range_start: str
    time_range_end: str
    granularity: TimeGranularity  # hourly, daily, weekly, monthly

    # Statistics
    mean: float | None
    median: float | None
    min: float | None
    max: float | None
    std: float | None
    count: int

    # Percentiles
    percentile_10: float | None
    percentile_25: float | None
    percentile_75: float | None
    percentile_90: float | None

    # Advanced metrics
    rate_of_change: float | None  # units/hour
    cumulative_sum: float | None  # for rainfall

    # Quality metrics
    data_quality_score: float | None
    outlier_count: int
    missing_count: int

    devices: list[str]
```

### SensorHealth

```python
@dataclass
class SensorHealth:
    device_id: str
    field_id: str
    sensor_type: str
    status: SensorStatus  # healthy, warning, critical, offline, drift_detected
    timestamp: str

    # Health metrics
    data_quality_score: float  # 0-100
    uptime_percentage: float   # 0-100
    battery_level: float | None
    signal_strength: float | None  # dBm

    # Issue detection
    drift_detected: bool
    drift_magnitude: float | None
    consecutive_errors: int
    last_successful_reading: str | None

    # Statistics
    readings_count_24h: int
    expected_readings_24h: int
    outlier_percentage: float

    # Alerts and recommendations
    alerts: list[str]
    recommendations_ar: list[str]
    recommendations_en: list[str]
```

---

## Data Normalization

### Sensor Type Aliases

The normalizer maps various sensor type names to standard types:

| Standard Type | Aliases |
|---------------|---------|
| `soil_moisture` | sm, moisture, soil_moist, vwc |
| `soil_temperature` | soil_temp, st, ground_temp |
| `soil_ec` | ec, conductivity, electrical_conductivity, salinity |
| `soil_ph` | ph, acidity |
| `air_temperature` | temp, temperature, air_temp, at |
| `air_humidity` | humidity, rh, relative_humidity |
| `wind_speed` | wind, ws, wind_velocity |
| `wind_direction` | wind_dir, wd |
| `rainfall` | rain, precipitation, precip |
| `solar_radiation` | solar, radiation, sr, light |
| `atmospheric_pressure` | pressure, atm, baro |
| `water_level` | level, wl, tank_level |
| `water_flow` | flow, flow_rate, wf |
| `water_quality` | wq, tds |
| `leaf_wetness` | lw, leaf_wet, wetness |
| `canopy_temperature` | canopy_temp, ct |

### Unit Aliases

| Standard Unit | Aliases |
|---------------|---------|
| `%` | percent, pct |
| `°C` | celsius, c, deg_c, degc |
| `°F` | fahrenheit, f, deg_f |
| `mm` | millimeter, millimeters |
| `m/s` | meters_per_second, mps |
| `km/h` | kilometers_per_hour, kph |
| `mS/cm` | millisiemens, ms_cm, ec_unit |
| `dS/m` | decisiemens, ds_m |
| `lux` | lx, illuminance |
| `W/m2` | watts_per_m2, solar_unit |
| `hPa` | hectopascal, mbar |
| `L/min` | liters_per_minute, lpm |
| `m3/h` | cubic_meters_per_hour, cmh |

### Value Range Validation

Sensor readings are validated against predefined ranges:

| Sensor Type | Min | Max | Unit |
|-------------|-----|-----|------|
| `temperature` | -50 | 80 | °C |
| `humidity` | 0 | 100 | % |
| `soil_moisture` | 0 | 100 | % |
| `soil_temperature` | -20 | 60 | °C |
| `ph` | 0 | 14 | - |
| `ec` | 0 | 10 | dS/m |
| `nitrogen` | 0 | 1000 | ppm |
| `phosphorus` | 0 | 1000 | ppm |
| `potassium` | 0 | 1000 | ppm |
| `light` | 0 | 200000 | lux |
| `rainfall` | 0 | 500 | mm |
| `wind_speed` | 0 | 150 | km/h |
| `pressure` | 800 | 1200 | hPa |
| `battery` | 0 | 100 | % |

---

## Device Registry

### Device Types

```python
class DeviceType(Enum):
    SOIL_SENSOR = "soil_sensor"
    WEATHER_STATION = "weather_station"
    WATER_SENSOR = "water_sensor"
    FLOW_METER = "flow_meter"
    VALVE_CONTROLLER = "valve_controller"
    GATEWAY = "gateway"
    CAMERA = "camera"
    UNKNOWN = "unknown"
```

### Device Status

```python
class DeviceStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"
```

### Offline Detection

- Default offline threshold: 15 minutes
- Background task checks every 60 seconds
- Publishes `device_status` and `device_alert` events when device goes offline

### Auto-Registration

When `IOT_AUTO_REGISTER=true`:
- Unknown devices are automatically registered on first reading
- Device type is inferred from sensor type
- Creates minimal registration with auto-generated names

---

## Sensor Aggregation

The `SensorAggregator` class provides advanced analytics:

### Aggregation Methods

- **By Field**: Aggregate all sensors for a specific field
- **By Sensor Type**: Aggregate across fields for a sensor type
- **Time-based**: Hourly, daily, weekly, monthly aggregations

### Statistical Calculations

- Mean, Median, Min, Max
- Standard Deviation
- Percentiles (10th, 25th, 75th, 90th)
- Rate of Change (units/hour)
- Cumulative Sum (for rainfall)

### Outlier Detection Methods

| Method | Description |
|--------|-------------|
| Z-Score | Statistical outlier detection (default threshold: 3 sigma) |
| IQR | Interquartile Range method |
| Threshold | Yemen-specific climate thresholds |

### Sensor Health Monitoring

- Data quality scoring (0-100)
- Uptime percentage calculation
- Drift detection (gradual sensor degradation)
- Alerts and bilingual recommendations

### Yemen Climate Thresholds

| Sensor | Warning Min | Warning Max | Critical Min | Critical Max | Unit |
|--------|-------------|-------------|--------------|--------------|------|
| Soil Moisture | 20 | 80 | 10 | 90 | % |
| Air Temperature | 5 | 45 | 0 | 50 | °C |
| Soil Temperature | 10 | 35 | 5 | 40 | °C |
| Air Humidity | 10 | 95 | 5 | 98 | % |
| Soil EC | 0 | 4 | 0 | 6 | dS/m |
| Soil pH | 5.5 | 8.5 | 4.5 | 9.5 | - |
| Rainfall | 0 | 100 | 0 | 200 | mm/day |
| Wind Speed | 0 | 15 | 0 | 25 | m/s |

---

## Dependencies

### Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | 0.126.0 | Web framework |
| `uvicorn[standard]` | >=0.30.0 | ASGI server |
| `pydantic` | 2.9.2 | Data validation |
| `nats-py` | 2.9.0 | NATS client |
| `aiomqtt` | 2.3.0 | Async MQTT client |
| `httpx` | 0.28.1 | HTTP client |
| `structlog` | >=24.1.0 | Structured logging |
| `python-dotenv` | 1.0.1 | Environment variables |

### Testing Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | 8.3.4 | Testing framework |
| `pytest-asyncio` | 0.24.0 | Async test support |
| `pytest-cov` | 4.1.0 | Coverage reporting |
| `pytest-mock` | 3.12.0 | Mocking |

### External Services

| Service | Purpose | Connection |
|---------|---------|------------|
| PostgreSQL | Not directly used | Via DATABASE_URL |
| NATS | Event publishing | nats://nats:4222 |
| MQTT Broker | Sensor data ingestion | mqtt://mqtt:1883 |

---

## Environment Variables

### Required Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NATS_URL` | NATS server URL | nats://nats:4222 | Yes |
| `MQTT_BROKER` | MQTT broker hostname | mqtt | Yes |
| `MQTT_PORT` | MQTT broker port | 1883 | Yes |
| `MQTT_PASSWORD` | MQTT password | - | Yes (production) |
| `JWT_SECRET_KEY` | JWT signing key | - | Yes |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | 8106 |
| `MQTT_TOPIC` | MQTT subscription topic | sahool/sensors/# |
| `MQTT_USER` | MQTT username | - |
| `MQTT_USERNAME` | MQTT username (legacy) | - |
| `DEFAULT_TENANT` | Default tenant ID | default |
| `IOT_AUTO_REGISTER` | Auto-register unknown devices | false |
| `REDIS_URL` | Redis URL for rate limiting | - |
| `JWT_ALGORITHM` | JWT algorithm | RS256 |
| `LOG_LEVEL` | Logging level | INFO |
| `ENVIRONMENT` | Environment name | development |
| `DATABASE_URL` | PostgreSQL connection string | - |

### Missing Environment Variables (Identified)

The following variables are referenced in code but not fully documented or may be missing:

| Variable | Used In | Issue |
|----------|---------|-------|
| `REDIS_URL` | Rate limiter | Optional but needed for distributed rate limiting |
| `DATABASE_URL` | docker-compose | Passed but not used in current implementation |

---

## Security

### Authentication

- JWT Bearer token authentication available via shared middleware
- Rate limiting tiers based on endpoint and request headers

### Rate Limiting Tiers

| Tier | Requests/min | Endpoints |
|------|--------------|-----------|
| STANDARD | 60 | /sensor/reading |
| PREMIUM | 120 | /sensor/batch, /device/* |
| INTERNAL | 1000 | X-Internal-Service header |

### Tenant Isolation

- Device authorization validates tenant and field association
- Sensor readings rejected if tenant/field mismatch
- All violations logged for audit

### Device Security

- Devices must be registered before accepting data (unless IOT_AUTO_REGISTER=true)
- Value range validation prevents malicious data injection
- All operations logged with device_id and tenant_id

---

## Bugs and Issues

### Critical Issues

#### 1. In-Memory Device Registry - No Persistence
**File**: `src/registry.py`
**Line**: 70-78
**Issue**: Device registry is stored in memory and lost on service restart.
```python
class DeviceRegistry:
    def __init__(self):
        self._devices: dict[str, Device] = {}  # In-memory only!
```
**Impact**: All device registrations lost after restart; devices must re-register.

#### 2. No Database Connection Used
**File**: `src/main.py`
**Issue**: DATABASE_URL is passed in docker-compose but not used.
**Impact**: No persistent storage for device state or readings.

### High Priority Issues

#### 3. Port Mismatch in README
**File**: `README.md`
**Line**: 12-14
**Issue**: README says port 8096, but actual port is 8106.
```markdown
## Port
8096  <-- Wrong!
```
**Fix**: Change to 8106.

#### 4. Global State Without Proper Lock
**File**: `src/main.py`
**Lines**: 62-66
**Issue**: Global variables modified without thread safety.
```python
mqtt_client: MqttClient | None = None
publisher: IoTPublisher | None = None
registry: DeviceRegistry | None = None
```
**Impact**: Potential race conditions in concurrent requests.

#### 5. Timestamp Conflict in Normalizer
**File**: `src/normalizer.py`
**Lines**: 189
**Issue**: Uses both `t` and `timestamp` fields, but `t` is also used for sensor_type.
```python
timestamp_raw = raw.get("timestamp") or raw.get("ts") or raw.get("time") or raw.get("t")
```
**Impact**: If compact format uses `t` for sensor type, timestamp parsing could conflict.

### Medium Priority Issues

#### 6. Silent Exception Swallowing
**File**: `src/main.py`
**Lines**: 211-248
**Issue**: Startup exceptions are caught and logged but not propagated.
```python
try:
    registry = get_registry()
except Exception as e:
    print(f"Warning: Registry initialization failed: {e}")
    registry = None  # Service continues with None!
```
**Impact**: Service may run in degraded state without alerting.

#### 7. Inconsistent API Response Structure
**File**: `src/main.py`
**Issue**: Some endpoints return `count`, others return `total` for pagination.
```python
# /devices returns both count and total
return {"devices": [...], "total": total, ...}
# /field/{field_id}/devices returns only count
return {"devices": [...], "count": len(devices)}
```
**Impact**: API inconsistency for clients.

#### 8. Missing Input Sanitization
**File**: `src/main.py`
**Issue**: Device IDs and field IDs are not sanitized for special characters.
**Impact**: Potential injection in logs or downstream systems.

### Low Priority Issues

#### 9. Unused Import in Normalizer
**File**: `src/normalizer.py`
**Line**: 8
**Issue**: `datetime` imported but `UTC` used separately.
```python
from datetime import timezone, datetime, UTC
```
**Note**: Minor cleanup item.

#### 10. Missing Type Hints
**File**: `src/mqtt_client.py`
**Lines**: 43-49
**Issue**: Function parameters use `None` as default type hint.
```python
def __init__(
    self,
    broker: str = None,  # Should be: str | None = None
    port: int = None,
```

#### 11. Statistics Call Missing Length
**File**: `src/sensor_aggregator.py`
**Line**: 227
**Issue**: `len(sorted_readings)` called but result not assigned.
```python
sorted_readings = sorted(readings)
len(sorted_readings)  # Result discarded
```
**Impact**: No functional impact, but unnecessary operation.

---

## Recommended Fixes

### High Priority

1. **Add Database Persistence for Device Registry**
   - Implement PostgreSQL or Redis backing store
   - Add async database operations
   - Migrate in-memory registry to persistent storage

2. **Fix Port in README**
   ```markdown
   ## Port
   8106
   ```

3. **Add Thread Safety to Global State**
   ```python
   import asyncio
   _registry_lock = asyncio.Lock()
   ```

4. **Fix Timestamp Field Conflict**
   - Remove `t` from timestamp aliases since it's used for sensor_type
   - Document field priority order

### Medium Priority

5. **Standardize API Responses**
   - Use consistent field names (`total` vs `count`)
   - Add pagination metadata to all list endpoints

6. **Add Input Sanitization**
   ```python
   import re
   def sanitize_id(value: str) -> str:
       return re.sub(r'[^a-zA-Z0-9_-]', '', value)
   ```

7. **Improve Error Handling**
   - Add health check degradation reporting
   - Return proper status when components fail

### Low Priority

8. **Clean Up Imports**
   - Remove unused imports
   - Fix type hints for optional parameters

9. **Add Sensor Accuracy Validation**
   - Use `SensorAccuracySpec` definitions in validation
   - Add accuracy-based quality scoring

10. **Implement Missing REST API Endpoints**
    - Add `/api/v1/readings/latest` (documented in README but not implemented)
    - Add `/api/v1/devices/{id}/command` (documented but not implemented)
    - Add `/api/v1/fields/{field_id}/readings` (documented but not implemented)

---

## Testing

### Running Tests

```bash
# Run all tests
cd /home/user/sahool-unified-v15-idp
pytest apps/services/iot-gateway/tests/ -v

# Run with coverage
pytest apps/services/iot-gateway/tests/ --cov=apps.services.iot_gateway -v

# Run specific test file
pytest apps/services/iot-gateway/tests/test_iot_api.py -v
```

### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| Health endpoints | 2 | Good |
| Sensor endpoints | 5 | Good |
| Device endpoints | 8 | Good |
| Field endpoints | 2 | Good |
| Validation | 4 | Good |
| Async behavior | 2 | Good |

---

## Appendix: Sensor Accuracy Specifications

Based on ISO standards and agricultural sensing requirements:

| Sensor | Accuracy | Range | Unit | Calibration Interval |
|--------|----------|-------|------|---------------------|
| Soil Moisture | +/-2% | 0-100 | % vol | 12 months |
| Soil EC | +/-0.01 | 0-10 | mS/cm | 6 months |
| Soil pH | +/-0.02 | 4-8 | pH | 6 months |
| Air Temperature | +/-0.2 | -40 to 85 | °C | 12 months |
| Soil Temperature | +/-0.2 | -20 to 60 | °C | 12 months |
| Air Humidity | +/-2% | 0-100 | % RH | 12 months |
| Light Intensity | +/-5% | 0-200000 | lux | 12 months |
| CO2 | +/-50ppm | 0-5000 | ppm | 12 months |
| Water Flow | +/-1% FS | 0-50 | m3/h | 12 months |
| Wind Speed | +/-0.3 | 0-60 | m/s | 12 months |
| Rainfall | +/-0.2 | 0-500 | mm | 12 months |

---

**Document Generated**: 2026-01-25
**Service Version**: 16.0.0
**Analysis Scope**: Full source code review
