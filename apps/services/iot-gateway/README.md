# IoT Gateway Service

**بوابة إنترنت الأشياء - جسر MQTT إلى NATS**

## Overview | نظرة عامة

MQTT to NATS bridge service for sensor data ingestion. Receives sensor readings from IoT devices via MQTT, normalizes the data, and publishes to NATS for platform-wide consumption.

خدمة جسر من MQTT إلى NATS لاستقبال بيانات الحساسات. تستقبل قراءات الحساسات من أجهزة IoT عبر MQTT، وتعمل على تطبيع البيانات، ونشرها إلى NATS للاستهلاك على مستوى المنصة.

## Port

```
8096
```

## Features | الميزات

### MQTT Bridge | جسر MQTT

- Subscribe to sensor topics
- Multi-device support
- QoS handling

### Data Normalization | تطبيع البيانات

- Unified reading format
- Unit conversion
- Timestamp standardization

### Device Registry | سجل الأجهزة

- Auto-registration
- Device status tracking
- Battery monitoring
- Signal strength logging

### Event Publishing | نشر الأحداث

- NATS integration
- Tenant-scoped events
- Real-time streaming

## MQTT Topics

### Sensor Data

```
sahool/sensors/{tenant_id}/{field_id}/{device_id}
```

### Device Status

```
sahool/devices/{tenant_id}/{device_id}/status
```

## API Endpoints

### Health

| Method | Path       | Description             |
| ------ | ---------- | ----------------------- |
| GET    | `/healthz` | Health check            |
| GET    | `/readyz`  | Readiness (MQTT + NATS) |

### Devices

| Method | Path                           | Description             |
| ------ | ------------------------------ | ----------------------- |
| GET    | `/api/v1/devices`              | List registered devices |
| GET    | `/api/v1/devices/{id}`         | Get device status       |
| POST   | `/api/v1/devices/{id}/command` | Send command to device  |

### Readings

| Method | Path                                 | Description         |
| ------ | ------------------------------------ | ------------------- |
| GET    | `/api/v1/readings/latest`            | Get latest readings |
| GET    | `/api/v1/fields/{field_id}/readings` | Field readings      |

## Sensor Reading Format

### Input (MQTT)

```json
{
  "device_id": "sensor_001",
  "type": "soil_moisture",
  "value": 45.2,
  "unit": "%",
  "battery": 85,
  "rssi": -65,
  "timestamp": "2025-12-23T10:00:00Z"
}
```

### Normalized Output (NATS)

```json
{
  "tenant_id": "tenant_001",
  "field_id": "field_001",
  "device_id": "sensor_001",
  "sensor_type": "soil_moisture",
  "value": 45.2,
  "unit": "%",
  "quality": "good",
  "timestamp": "2025-12-23T10:00:00Z",
  "metadata": {
    "battery": 85,
    "rssi": -65
  }
}
```

## Supported Sensor Types

| Type               | Arabic            | Unit  |
| ------------------ | ----------------- | ----- |
| `soil_moisture`    | رطوبة التربة      | %     |
| `soil_temperature` | حرارة التربة      | °C    |
| `air_temperature`  | حرارة الهواء      | °C    |
| `air_humidity`     | رطوبة الهواء      | %     |
| `light_intensity`  | شدة الإضاءة       | lux   |
| `water_level`      | مستوى الماء       | cm    |
| `water_flow`       | تدفق الماء        | L/min |
| `ph_level`         | مستوى pH          | pH    |
| `ec_level`         | التوصيل الكهربائي | mS/cm |

## Device Status

| Status        | Arabic        | Description             |
| ------------- | ------------- | ----------------------- |
| `online`      | متصل          | Active and sending data |
| `offline`     | غير متصل      | No data for > 5 minutes |
| `error`       | خطأ           | Device reporting errors |
| `low_battery` | بطارية منخفضة | Battery < 20%           |

## Dependencies

- FastAPI
- paho-mqtt
- NATS

## Environment Variables

| Variable         | Description       | Default            |
| ---------------- | ----------------- | ------------------ |
| `PORT`           | Service port      | `8096`             |
| `MQTT_BROKER`    | MQTT broker host  | `localhost`        |
| `MQTT_PORT`      | MQTT broker port  | `1883`             |
| `MQTT_TOPIC`     | Subscribe topic   | `sahool/sensors/#` |
| `NATS_URL`       | NATS server URL   | -                  |
| `DEFAULT_TENANT` | Default tenant ID | `default`          |

## Events Published

- `iot.reading` - Sensor reading received
- `iot.device.online` - Device came online
- `iot.device.offline` - Device went offline
- `iot.alert.low_battery` - Low battery alert
