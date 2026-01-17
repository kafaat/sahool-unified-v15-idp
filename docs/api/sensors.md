# Sensor/IoT APIs

# واجهات برمجة تطبيقات أجهزة الاستشعار

## Overview | نظرة عامة

IoT and Sensor APIs enable integration with agricultural sensors and IoT devices:

- Real-time sensor data ingestion
- Virtual sensors for calculated metrics
- Sensor configuration and management
- Historical sensor data retrieval

تتيح واجهات إنترنت الأشياء والاستشعار التكامل مع أجهزة الاستشعار الزراعية:

- استقبال بيانات الاستشعار في الوقت الفعلي
- أجهزة استشعار افتراضية للمقاييس المحسوبة
- تكوين وإدارة أجهزة الاستشعار
- استرجاع البيانات التاريخية

## Base URLs

**IoT Gateway:** `http://localhost:8081`
**Virtual Sensors:** `http://localhost:8107`

## Sensor Types | أنواع أجهزة الاستشعار

| Type               | Description             | Units |
| ------------------ | ----------------------- | ----- |
| `soil_moisture`    | Soil moisture sensor    | %     |
| `soil_temperature` | Soil temperature        | °C    |
| `air_temperature`  | Air temperature         | °C    |
| `air_humidity`     | Air humidity            | %     |
| `rainfall`         | Rain gauge              | mm    |
| `wind_speed`       | Wind speed              | km/h  |
| `light_intensity`  | Light sensor            | lux   |
| `ph_sensor`        | Soil pH                 | pH    |
| `ec_sensor`        | Electrical conductivity | dS/m  |

## Endpoints | نقاط النهاية

### POST /api/v1/sensor-data

Ingest sensor data from IoT devices.

**Request Body:**

```json
{
  "device_id": "device-123",
  "sensor_type": "soil_moisture",
  "value": 45.5,
  "unit": "%",
  "field_id": "field-456",
  "timestamp": "2024-01-15T12:30:00Z",
  "metadata": {
    "depth_cm": 30,
    "location": "zone-A"
  }
}
```

**Response:**

```json
{
  "id": "reading-789",
  "device_id": "device-123",
  "received_at": "2024-01-15T12:30:01Z",
  "status": "processed"
}
```

### GET /api/v1/sensors/{device_id}/data

Get sensor data for a specific device.

**Query Parameters:**

- `start_date` (string, optional): Start date (ISO 8601)
- `end_date` (string, optional): End date (ISO 8601)
- `limit` (integer, optional): Number of readings (default: 100)

**Response:**

```json
{
  "device_id": "device-123",
  "sensor_type": "soil_moisture",
  "readings": [
    {
      "timestamp": "2024-01-15T12:30:00Z",
      "value": 45.5,
      "unit": "%"
    }
  ],
  "total": 100
}
```

### GET /api/v1/virtual-sensors/et0

Calculate reference evapotranspiration (ET0).

**Query Parameters:**

- `lat` (number, required): Latitude
- `lon` (number, required): Longitude
- `date` (string, optional): Date (ISO 8601)

**Response:**

```json
{
  "et0_mm": 5.2,
  "date": "2024-01-15",
  "location": {
    "lat": 15.3694,
    "lon": 44.191
  },
  "method": "penman_monteith",
  "weather_data": {
    "temp_max_c": 32,
    "temp_min_c": 18,
    "humidity_pct": 45,
    "wind_speed_kmh": 15
  }
}
```

---

_Last updated: 2026-01-02_
