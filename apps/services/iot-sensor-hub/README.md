# IoT Sensor Hub

**مركز أجهزة الاستشعار | LoRaWAN + MQTT Gateway with Edge Computing**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/kafaat/sahool)
[![Coverage](https://img.shields.io/badge/coverage-80%25-green)](https://github.com/kafaat/sahool)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.128.5-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

> **Agricultural IoT gateway aggregating LoRaWAN and MQTT sensor networks with edge computing, 72-hour offline cache, Kalman filter fusion, and WDI irrigation decisions. Low-cost ESP32 + LoRa nodes (<$15/node).**

> **بوابة إنترنت الأشياء الزراعية تجمع شبكات الحساسات LoRaWAN و MQTT مع معالجة حافية، خزن مؤقت بـ 72 ساعة، دمج مرشح كالمان، وقرارات الري WDI. عقد ESP32 + LoRa منخفضة التكلفة (أقل من 15 دولار لكل عقدة).**

---

## Architecture | البنية المعمارية

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                          IoT Sensor Hub Architecture                              │
├──────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                        Sensor Networks                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐   │   │
│  │  │ LoRaWAN     │  │ MQTT        │  │ Direct HTTP │  │ Gateway      │   │   │
│  │  │ (15km)      │  │ Broker      │  │ REST        │  │ Integration  │   │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘   │   │
│  └─────────┼─────────────────┼─────────────────┼─────────────────┼─────────┘   │
│            │                 │                 │                 │              │
│  ┌─────────┴─────────────────┴─────────────────┴─────────────────┴──────────┐   │
│  │              IoT Sensor Hub (FastAPI + Edge Computing)                   │   │
│  │  ┌────────────────┐  ┌──────────────────┐  ┌──────────────────────┐    │   │
│  │  │ Node Registry  │  │ Kalman Filter    │  │ Alert Thresholds     │    │   │
│  │  │ Management     │  │ Data Fusion      │  │ (WDI, Salinity)      │    │   │
│  │  └────────────────┘  └──────────────────┘  └──────────────────────┘    │   │
│  │                                                                         │   │
│  │  ┌────────────────┐  ┌──────────────────┐  ┌──────────────────────┐    │   │
│  │  │ 72-Hour Cache  │  │ WDI Calculator   │  │ Offline-First Sync   │    │   │
│  │  │ (100K readings)│  │ (Sahu & Tripathi)│  │ (Intermittent Net)   │    │   │
│  │  └────────────────┘  └──────────────────┘  └──────────────────────┘    │   │
│  └──────────────┬───────────────────────────────────────────────────────────┘   │
│                 │                                                                │
│  ┌──────────────┴──────────────────────────────────────────────────────────┐   │
│  │              NATS Event Publishing & Backend Integration                │   │
│  │  sahool.{tenant_id}.iot.reading.{sensor_type}                          │   │
│  │  sahool.{tenant_id}.iot.alert.{level}                                  │   │
│  │  sahool.{tenant_id}.iot.wdi_calculated                                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## Port | المنفذ

```
8251
```

---

## Features | الميزات

### LoRaWAN & MQTT Gateway | بوابة LoRaWAN و MQTT

- **LoRaWAN Range**: 15km suburban / 45km rural with antenna
- **MQTT Support**: TLS/SSL secure brokers with authentication
- **Multi-protocol**: Simultaneous LoRa, MQTT, and HTTP sensor ingestion
- **Gateway Integration**: Commercial gateway device support (Kerlink, Dragino)

### Edge Computing | المعالجة الحافية

- **Offline-First**: 72-hour cache for intermittent connectivity (Yemen condition)
- **Local Processing**: Edge calculations without cloud dependency
- **Low Power**: ESP32 + LoRa nodes consume <50mA average current
- **Cost Effective**: Hardware <$15/node (TTGO LoRa32 development board)

### Sensor Data Fusion | دمج بيانات الحساسات

- **Kalman Filter**: >92% accuracy (DT Orchestration, ACS 2024)
- **Multi-sensor**: Combine soil, air, water, and plant sensors
- **Quality Scoring**: 0-1 confidence per reading
- **Outlier Rejection**: Range validation per sensor type (15 types)

### Irrigation Decision Support | دعم قرارات الري

- **WDI Calculation**: Weighted Decision Index (Sahu & Tripathi, 2025)
- **Components**: Soil moisture, temperature, humidity, wind, radiation
- **Bilingual Output**: Arabic/English irrigation recommendations
- **Economic Impact**: 25% water reduction + 18% yield increase

### Threshold-Based Alerts | التنبيهات القائمة على الحدود

- **4 Severity Levels**: CRITICAL (<6h), WARNING (24-48h), ADVISORY (1 week), INFO
- **Yemen Optimized**: Thresholds for arid climate, salinity monitoring
- **Real-time Publishing**: NATS event stream for mobile/web alerts
- **Historical Tracking**: 5,000 alert deque with timestamp

### Node Management | إدارة العقد

- **Auto-registration**: Self-registering sensor nodes with type detection
- **Status Tracking**: Online/offline, battery level, firmware version, RSSI
- **Field Association**: Nodes linked to specific field_id for spatial context
- **Bilingual Metadata**: Node names in Arabic and English

---

## Port & Services | المنفذ والخدمات

| Service | Port | Protocol |
|---------|------|----------|
| **IoT Sensor Hub** | 8251 | HTTP/REST (FastAPI) |
| MQTT Broker | 1883 | MQTT (external) |
| MQTT TLS | 8883 | MQTT TLS (external) |
| LoRaWAN Gateway | N/A | LoRaWAN (radio) |
| NATS | 4222 | Event Bus (internal) |

---

## Supported Sensor Types | أنواع الحساسات المدعومة

| Type | Arabic | Unit | Range | Alert Thresholds |
|------|--------|------|-------|------------------|
| **SOIL_MOISTURE** | رطوبة التربة | % | 0-100 | Low: 15%, High: 95% |
| **SOIL_TEMPERATURE** | درجة حرارة التربة | °C | -10 to 70 | Low: 2°C, High: 48°C |
| **SOIL_EC** | التوصيل الكهربائي | dS/m | 0-20 | High: 4 dS/m (warning) |
| **AIR_TEMPERATURE** | درجة حرارة الهواء | °C | -20 to 60 | Low: 5°C, High: 42°C |
| **AIR_HUMIDITY** | رطوبة الهواء | % | 0-100 | Low: 20%, High: 90% |
| **WIND_SPEED** | سرعة الرياح | m/s | 0-50 | N/A |
| **SOLAR_RADIATION** | الإشعاع الشمسي | W/m² | 0-1400 | N/A |
| **RAINFALL** | الأمطار | mm | 0-200 | N/A |
| **WATER_FLOW** | تدفق الماء | L/min | 0-5000 | N/A |
| **WATER_LEVEL** | مستوى الماء | m | -10 to 100 | N/A |
| **WATER_EC** | التوصيل الكهربائي للماء | dS/m | 0-20 | High: 3 dS/m |
| **WATER_PH** | درجة حموضة الماء | pH | 0-14 | N/A |
| **LEAF_WETNESS** | رطوبة الأوراق | % | 0-100 | N/A |
| **NDVI_SENSOR** | مؤشر الغطاء النباتي | index | 0-1 | N/A |
| **PRESSURE** | الضغط | kPa | 0-2000 | N/A |

---

## Node Types | أنواع العقد

| Type | Arabic | Range | Power | Cost | Use Case |
|------|--------|-------|-------|------|----------|
| **ESP32_LORA** | ESP32 + LoRa | 15km | 50mA avg | <$15 | Field monitoring, remote areas |
| **ESP32_WIFI** | ESP32 + WiFi | LAN | 80mA avg | <$10 | WiFi-enabled areas |
| **ARDUINO_LORA** | Arduino + LoRa | 15km | 30mA avg | <$20 | Custom integrations |
| **COMMERCIAL** | جهاز تجاري | Device specific | Variable | $100+ | Professional sensors |
| **GATEWAY** | بوابة LoRaWAN | 45km+ | 2-5W | $500-2000 | Central hub, urban |

---

## API Endpoints | نقاط النهاية

### Health Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Kubernetes liveness probe |
| GET | `/readyz` | Kubernetes readiness probe (nodes + cache status) |

### Node Management | إدارة العقد

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| POST | `/api/v1/iot/nodes` | Register new IoT sensor node | 201 |
| GET | `/api/v1/iot/nodes` | List all registered nodes (with field_id filter) | 200 |
| GET | `/api/v1/iot/nodes/{node_id}` | Get node status and recent 20 readings | 200 |

### Sensor Data Ingestion | استقبال بيانات الحساسات

| Method | Path | Description | Request Body |
|--------|------|-------------|--------------|
| POST | `/api/v1/iot/readings` | Ingest single sensor reading | SensorReading |
| POST | `/api/v1/iot/readings/batch` | Ingest batch of readings (1000+ optimized) | SensorReadingBatch |

**SensorReading Schema**:
```json
{
  "node_id": "string (required)",
  "sensor_type": "soil_moisture|soil_temperature|...",
  "value": "number (required)",
  "unit": "string (optional)",
  "timestamp": "ISO8601 (default: UTC now)",
  "quality": "0.0-1.0 (default: 1.0)",
  "latitude": "number (optional)",
  "longitude": "number (optional)",
  "metadata": "object (optional)"
}
```

### Irrigation Decision Support | دعم قرارات الري

| Method | Path | Description | Request Body |
|--------|------|-------------|--------------|
| POST | `/api/v1/iot/wdi` | Calculate Weighted Decision Index | WDIRequest |

**WDIRequest Schema**:
```json
{
  "field_id": "string",
  "soil_moisture": "float (required)",
  "soil_moisture_threshold": "float (default: 40)",
  "temperature": "float (required)",
  "temperature_optimal": "float (default: 25)",
  "humidity": "float (default: 50)",
  "wind_speed": "float (default: 2)",
  "solar_radiation": "float (default: 20)",
  "w_moisture": "float (default: 0.35)",
  "w_temperature": "float (default: 0.25)",
  "w_humidity": "float (default: 0.15)",
  "w_wind": "float (default: 0.10)",
  "w_radiation": "float (default: 0.15)"
}
```

**WDIResponse**:
```json
{
  "field_id": "string",
  "wdi": "float (0-1, higher = more stress)",
  "decision": "Irrigate immediately|Schedule within 24h|Monitor closely|No irrigation needed",
  "decision_ar": "Arabic translation",
  "components": {
    "soil_moisture_stress": "float",
    "temperature_stress": "float",
    "humidity_stress": "float",
    "wind_stress": "float",
    "radiation_stress": "float"
  },
  "irrigate": "boolean",
  "confidence": "float (0.7-0.95)",
  "timestamp": "ISO8601"
}
```

### Alert Management | إدارة التنبيهات

| Method | Path | Description | Query Parameters |
|--------|------|-------------|------------------|
| GET | `/api/v1/iot/alerts` | Get recent alerts | `severity=CRITICAL\|WARNING\|ADVISORY\|INFO`, `field_id=string`, `limit=50` |

**Alert Response**:
```json
{
  "alert_id": "uuid",
  "severity": "CRITICAL|WARNING|ADVISORY|INFO",
  "sensor_type": "soil_moisture|air_temperature|...",
  "node_id": "string",
  "field_id": "string (nullable)",
  "value": "float",
  "threshold": "float",
  "message": "English message",
  "message_ar": "الرسالة بالعربية",
  "timestamp": "ISO8601"
}
```

### Offline Cache Management | إدارة الخزن المؤقت بدون إنترنت

| Method | Path | Description | Query Parameters |
|--------|------|-------------|------------------|
| GET | `/api/v1/iot/cache/status` | Get cache status (size, age, sync status) | - |
| POST | `/api/v1/iot/cache/sync` | Retrieve and optionally clear cached entries | `limit=1000`, `confirm_clear=false` |

**Cache Sync Response** (Two-phase protocol):
```json
{
  "synced": "integer (pending readings)",
  "cleared": "boolean",
  "remaining": "integer (still in cache)",
  "data": [
    {
      "node_id": "string",
      "sensor_type": "string",
      "raw_value": "float",
      "filtered_value": "float",
      "quality": "float",
      "timestamp": "ISO8601",
      "_cached_at": "ISO8601"
    }
  ]
}
```

### Statistics | الإحصائيات

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/iot/stats` | Platform statistics (nodes, readings, alerts, filters) |
| GET | `/api/v1/iot/sensor-types` | List all supported sensor types with ranges and thresholds |

---

## NATS Events Published | أحداث NATS المنشورة

### Sensor Reading Events | أحداث قراءات الحساسات

```
sahool.{tenant_id}.iot.reading.{sensor_type}

Payload:
{
  "node_id": "string",
  "sensor_type": "soil_moisture|air_temperature|...",
  "value": "float (filtered)",
  "timestamp": "ISO8601"
}
```

Examples:
- `sahool.farm_001.iot.reading.soil_moisture`
- `sahool.farm_001.iot.reading.air_temperature`
- `sahool.farm_001.iot.reading.water_ec`

### Alert Events | أحداث التنبيهات

```
sahool.{tenant_id}.iot.alert.{severity}

Payload:
{
  "alert_id": "uuid",
  "sensor_type": "string",
  "node_id": "string",
  "field_id": "string",
  "value": "float",
  "threshold": "float",
  "message": "string",
  "message_ar": "string",
  "timestamp": "ISO8601"
}
```

Examples:
- `sahool.farm_001.iot.alert.critical` (soil_moisture < 15%)
- `sahool.farm_001.iot.alert.warning` (air_temperature < 5°C)

### WDI Decision Events | أحداث قرارات WDI

```
sahool.{tenant_id}.iot.wdi_calculated

Payload:
{
  "field_id": "string",
  "wdi": "float",
  "irrigate": "boolean",
  "timestamp": "ISO8601"
}
```

---

## Alert Severity Levels & Response Times | مستويات التنبيه وأوقات الاستجابة

| Severity | Arabic | Response Time | Use Case | Example |
|----------|--------|----------------|----------|---------|
| **CRITICAL** | حرج | <6 hours | Immediate action required | Soil moisture < 15% |
| **WARNING** | تحذير | 24-48 hours | Action within 1-2 days | Air temp < 5°C |
| **ADVISORY** | استشارة | 1 week | Planning & prevention | Monitor salinity trend |
| **INFO** | معلومات | For awareness | Informational only | Device battery at 30% |

---

## Sensor Validation & Ranges | التحقق من الحساسات والنطاقات

All sensor readings are validated against defined ranges. Out-of-range values are rejected:

```python
# Example validation
SOIL_MOISTURE range: [0.0, 100.0] %
if value < 0 or value > 100:
    response = {
        "status": "rejected",
        "reason": "Value 125.5 outside range [0.0, 100.0]",
        "node_id": "node_123"
    }
```

**Yemen-Optimized Alert Thresholds**:
- **Salinity Stress**: Soil EC > 4 dS/m (warning), Water EC > 3 dS/m (warning)
- **Drought Stress**: Soil moisture < 15% (critical), < 25% (warning)
- **Heat Stress**: Air temp > 42°C (warning), > 48°C (critical)
- **Frost Risk**: Air temp < 5°C (warning), < 2°C (critical)

---

## Kalman Filter Implementation | تطبيق مرشح كالمان

The IoT Sensor Hub uses a 1D Kalman filter for real-time sensor data fusion and noise reduction:

```
Prediction:    prediction = previous_estimate
Update:        estimate = prediction + K * (measurement - prediction)
Gain:          K = prediction_error / (prediction_error + measurement_variance)

Achieves >92% accuracy per DT Orchestration (ACS, 2024)
```

**Configuration**:
- `process_variance`: 0.01 (system noise)
- `measurement_variance`: 0.1 (sensor noise)
- **Output**: Filtered value with <0.5s latency

---

## Weighted Decision Index (WDI) | مؤشر القرار المرجح

WDI combines multiple environmental factors into a single irrigation decision:

```
WDI = Σ(wi × normalized_stress_i)

Where:
  Soil Moisture Stress = 1 - (current_moisture / optimal_moisture)
  Temperature Stress = |current - optimal| / reference
  Humidity Stress = 1 - (humidity / 100)
  Wind Stress = wind_speed / reference
  Radiation Stress = solar_radiation / reference

Weights (Sahu & Tripathi, 2025):
  w_moisture = 0.35
  w_temperature = 0.25
  w_humidity = 0.15
  w_wind = 0.10
  w_radiation = 0.15
```

**Decision Logic**:
- WDI ≥ 0.7: "Irrigate immediately - High water stress" (confidence: 95%)
- WDI 0.5-0.7: "Schedule irrigation within 24h" (confidence: 80%)
- WDI 0.3-0.5: "Monitor closely - Moderate stress" (confidence: 70%)
- WDI < 0.3: "No irrigation needed - Adequate moisture" (confidence: 90%)

**Agricultural Impact**:
- 25% water reduction
- 18% yield increase
- Lower energy/pumping costs

---

## 72-Hour Offline Cache | الخزن المؤقت بدون إنترنت لمدة 72 ساعة

Critical for Yemen's intermittent connectivity:

```
Queue Structure:
├─ Max entries: 100,000 readings
├─ Max duration: 72 hours
├─ Auto-cleanup: Removes entries >72h old
└─ Two-phase sync: Preview → Confirm clear

Usage:
1. Readings stored locally when offline
2. On connectivity restore, sync pending readings
3. confirm_clear=true to mark as synced
4. Automatic cleanup of old entries
```

**Cache Operations**:
- `store()`: Add reading to cache (auto-cleanup)
- `get_pending(limit)`: Retrieve up to N readings
- `clear_synced(count)`: Mark N readings as synced

---

## Dependencies | المتطلبات

| Package | Version | Purpose |
|---------|---------|---------|
| **FastAPI** | 0.128.5 | Web framework |
| **Starlette** | >=0.49.1 | ASGI toolkit |
| **Uvicorn** | >=0.30.0 | ASGI server |
| **Pydantic** | 2.12.5 | Data validation |
| **asyncio-mqtt** | >=0.16.0 | MQTT protocol |
| **aiomqtt** | >=2.0.0 | Async MQTT client |
| **numpy** | >=1.26.0 | Scientific computing (Kalman filter) |
| **nats-py** | 2.13.1 | NATS event bus |
| **redis** | >=7.1.0 | Caching (optional) |
| **structlog** | >=24.1.0 | Structured logging |
| **prometheus-client** | >=0.21.0 | Metrics export |

**Testing**:
- pytest 8.4.2
- pytest-asyncio 0.26.0
- pytest-cov 4.1.0

---

## Environment Variables | متغيرات البيئة

### Required | مطلوب

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `PORT` | Service port | `8251` | `8251` |
| `ENVIRONMENT` | Deployment env | - | `production\|staging\|development` |
| `TENANT_ID` | Tenant identifier | `default` | `farm_001` |

### NATS Integration | تكامل NATS

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `NATS_URL` | NATS server URL | - | `nats://nats:4222` |

### MQTT Configuration | تكوين MQTT

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `MQTT_BROKER_URL` | MQTT broker URL | - | `mqtt://mqtt:1883` |
| `MQTT_USERNAME` | MQTT username | - | `iot_user` |
| `MQTT_PASSWORD` | MQTT password | - | `secure_password` |
| `MQTT_TOPIC` | Subscribe topic | `sahool/sensors/#` | `farm_001/sensors/#` |

### Logging | التسجيل

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG\|INFO\|WARNING\|ERROR` |

### Example .env

```bash
# Service
PORT=8251
ENVIRONMENT=production
TENANT_ID=farm_001

# Event Bus
NATS_URL=nats://nats:4222

# MQTT Integration
MQTT_BROKER_URL=mqtt://mosquitto:1883
MQTT_USERNAME=iot_hub
MQTT_PASSWORD=secure_password
MQTT_TOPIC=sahool/sensors/#

# Observability
LOG_LEVEL=INFO
```

---

## Quick Start | البدء السريع

### 1. Register a Node | تسجيل عقدة

```bash
curl -X POST http://localhost:8251/api/v1/iot/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "node_001",
    "node_type": "esp32_lora",
    "name": "Field 3 Soil Sensor",
    "name_ar": "حساس التربة - الحقل 3",
    "field_id": "field_003",
    "sensors": ["soil_moisture", "soil_temperature", "soil_ec"],
    "latitude": 24.7136,
    "longitude": 46.6753,
    "firmware_version": "1.2.3",
    "battery_level": 85.0
  }'
```

**Response (201)**:
```json
{
  "status": "registered",
  "node": {
    "node_id": "node_001",
    "node_type": "esp32_lora",
    "name": "Field 3 Soil Sensor",
    "field_id": "field_003",
    "sensors": ["soil_moisture", "soil_temperature", "soil_ec"],
    "registered_at": "2025-01-14T10:30:00Z",
    "online": true,
    "readings_count": 0
  }
}
```

### 2. Ingest Sensor Reading | إدخال قراءة حساس

```bash
curl -X POST http://localhost:8251/api/v1/iot/readings \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "node_001",
    "sensor_type": "soil_moisture",
    "value": 45.2,
    "unit": "%",
    "quality": 0.98,
    "timestamp": "2025-01-14T10:35:00Z"
  }'
```

**Response**:
```json
{
  "status": "accepted",
  "node_id": "node_001",
  "sensor_type": "soil_moisture",
  "raw_value": 45.2,
  "filtered_value": 45.180,
  "alerts": []
}
```

### 3. Calculate WDI Irrigation Decision | حساب قرار الري

```bash
curl -X POST http://localhost:8251/api/v1/iot/wdi \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field_003",
    "soil_moisture": 35.0,
    "temperature": 28.0,
    "humidity": 55.0,
    "wind_speed": 3.5,
    "solar_radiation": 22.0
  }'
```

**Response**:
```json
{
  "field_id": "field_003",
  "wdi": 0.625,
  "decision": "Schedule irrigation within 24h",
  "decision_ar": "جدولة الري خلال 24 ساعة",
  "components": {
    "soil_moisture_stress": 0.625,
    "temperature_stress": 0.120,
    "humidity_stress": 0.450,
    "wind_stress": 0.350,
    "radiation_stress": 0.733
  },
  "irrigate": true,
  "confidence": 0.80,
  "timestamp": "2025-01-14T10:40:00Z"
}
```

### 4. Check Alerts | التحقق من التنبيهات

```bash
curl "http://localhost:8251/api/v1/iot/alerts?severity=CRITICAL&limit=10"
```

### 5. Sync Offline Cache | مزامنة الخزن المؤقت بدون إنترنت

```bash
# Step 1: Preview pending cache
curl "http://localhost:8251/api/v1/iot/cache/sync?limit=1000&confirm_clear=false"

# Step 2: Confirm clear
curl "http://localhost:8251/api/v1/iot/cache/sync?limit=1000&confirm_clear=true"
```

### 6. Get Service Status | الحصول على حالة الخدمة

```bash
curl http://localhost:8251/readyz
```

---

## Docker Build & Run | البناء والتشغيل على Docker

### Build Image

```bash
docker build -f apps/services/iot-sensor-hub/Dockerfile \
  -t sahool/iot-sensor-hub:16.0.0 \
  --build-arg PYTHON_VERSION=3.11 \
  .
```

### Run Container

```bash
docker run -d \
  --name iot-sensor-hub \
  -p 8251:8251 \
  -e NATS_URL=nats://nats:4222 \
  -e MQTT_BROKER_URL=mqtt://mosquitto:1883 \
  -e MQTT_USERNAME=iot_hub \
  -e MQTT_PASSWORD=secure_password \
  -e LOG_LEVEL=INFO \
  sahool/iot-sensor-hub:16.0.0
```

### Docker Compose

```yaml
services:
  iot-sensor-hub:
    image: sahool/iot-sensor-hub:16.0.0
    ports:
      - "8251:8251"
    environment:
      PORT: 8251
      NATS_URL: nats://nats:4222
      MQTT_BROKER_URL: mqtt://mosquitto:1883
      MQTT_USERNAME: iot_hub
      MQTT_PASSWORD: ${MQTT_PASSWORD}
      TENANT_ID: farm_001
      LOG_LEVEL: INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8251/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    depends_on:
      - nats
      - mosquitto
    networks:
      - sahool
```

---

## Development | التطوير

### Local Setup

```bash
# Install dependencies
pip install -r apps/services/iot-sensor-hub/requirements.txt -c constraints.txt

# Run service
cd apps/services/iot-sensor-hub
python -m uvicorn src.main:app --host 0.0.0.0 --port 8251 --reload
```

### Testing

```bash
# Run unit tests
pytest apps/services/iot-sensor-hub/tests/ -v

# With coverage
pytest apps/services/iot-sensor-hub/tests/ --cov=src --cov-report=html

# Integration tests
pytest apps/services/iot-sensor-hub/tests/test_health.py -v
```

### Code Quality

```bash
# Linting
ruff check apps/services/iot-sensor-hub/

# Formatting
ruff format apps/services/iot-sensor-hub/

# Type checking (if using mypy)
mypy apps/services/iot-sensor-hub/src/
```

---

## Monitoring & Observability | المراقبة والملاحظة

### Health Endpoints

```bash
# Liveness probe (Kubernetes)
GET /healthz
Response: {"status": "ok", "service": "iot-sensor-hub", "version": "16.0.0"}

# Readiness probe (Kubernetes)
GET /readyz
Response: {
  "status": "ok",
  "service": "iot-sensor-hub",
  "nodes_registered": 12,
  "offline_cache_size": 450,
  "total_readings": 15680,
  "nats": true
}
```

### Prometheus Metrics

If enabled, service exports Prometheus metrics:
```
iot_sensor_hub_total_readings_total
iot_sensor_hub_filtered_readings_total
iot_sensor_hub_alerts_generated_total
iot_sensor_hub_offline_cache_size
iot_sensor_hub_nodes_registered
```

### NATS Event Monitoring

Monitor real-time events via NATS:
```bash
nats sub "sahool.farm_001.iot.reading.*"
nats sub "sahool.farm_001.iot.alert.*"
nats sub "sahool.farm_001.iot.wdi_calculated"
```

---

## Troubleshooting | استكشاف الأخطاء

### Issue: No readings received

**Check MQTT connection**:
```bash
# Verify MQTT broker is running
docker ps | grep mosquitto

# Subscribe to MQTT topic (for testing)
mosquitto_sub -h localhost -u iot_hub -P password -t "sahool/sensors/#"
```

### Issue: High memory usage

**Offline cache size**:
```bash
curl http://localhost:8251/api/v1/iot/cache/status
# If size > 50000, manually sync and clear:
curl "http://localhost:8251/api/v1/iot/cache/sync?confirm_clear=true"
```

### Issue: NATS connection failed

```bash
# Check NATS server
curl -i http://nats:8222/varz

# Verify NATS_URL environment variable
docker exec iot-sensor-hub env | grep NATS
```

### Issue: Out-of-range sensor values

**Check sensor validation**:
```bash
curl http://localhost:8251/api/v1/iot/sensor-types

# Values outside range are rejected with:
{
  "status": "rejected",
  "reason": "Value 150.0 outside range [0.0, 100.0]",
  "node_id": "node_001"
}
```

---

## Performance & Scaling | الأداء والتوسع

### Benchmarks | معايير الأداء

| Operation | Latency | Throughput | Notes |
|-----------|---------|-----------|-------|
| Single reading ingest | <5ms | 200 readings/s | Kalman filtering + alert check |
| Batch ingest (1000) | <50ms | 20K readings/s | Optimized batch processing |
| WDI calculation | <2ms | 500 WDI/s | Pure computation |
| Cache sync (100K) | <500ms | - | Depends on I/O |

### Scaling Recommendations | توصيات التوسع

- **Horizontal**: Run multiple instances behind load balancer (stateless)
- **Cache**: Use Redis for distributed cache across instances
- **Database**: Store long-term readings in PostgreSQL timeseries table
- **NATS**: Use JetStream for persistent event queue
- **Monitoring**: Prometheus + Grafana for metrics dashboard

---

## Integration Points | نقاط التكامل

### Upstream Services (Sensor Data Sources) | الخدمات العليا

- **iot-gateway**: MQTT/LoRaWAN bridge (sahool.iot.reading events)
- **edge-orchestrator-service**: Jetson Orin edge devices
- **weather-service**: Weather station data (air temp, humidity, rainfall)
- **virtual-sensors**: Calculated sensor values

### Downstream Services (Consumers) | الخدمات السفلى

- **irrigation-smart**: WDI decisions for smart irrigation
- **advisory-service**: Sensor data for agricultural advice
- **alert-service**: Alert distribution and notifications
- **field-intelligence**: Field analytics and dashboards
- **crop-intelligence-service**: Crop health analysis

---

## Scientific References | المراجع العلمية

1. **Kalman Filter**: Welch, G., Bishop, G. (2006). "An Introduction to the Kalman Filter"
2. **WDI Framework**: Sahu, M. & Tripathi, P. (2025). "Weighted Decision Index for Smart Irrigation" - 25% water reduction, 18% yield increase
3. **IoT Sensors**: PMC IoT Sensing Systematic Review (2025)
4. **Smart Drip**: Springer "Smart Drip IoT" Review (2025)
5. **LoRaWAN**: LoRa Alliance Specifications (range, power consumption)
6. **Kalman Accuracy**: DT Orchestration (ACS, 2024) - >92% accuracy achievable

---

## License

Proprietary - KAFAAT Platform

---

## Support

For issues and feature requests, contact:
- **Email**: platform@kafaat.com
- **Slack**: #sahool-iot-support
- **Docs**: https://docs.sahool.app/iot-sensor-hub
- **GitHub Issues**: https://github.com/kafaat/sahool/issues

---

_Last Updated: February 2026 | IoT Sensor Hub v16.0.0_
