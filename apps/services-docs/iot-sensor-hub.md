# IoT Sensor Hub

**Type:** Python / FastAPI
**Port:** 8251
**Version:** 16.0.0
**Layer:** Acquisition (Event Architecture)

## Overview

The IoT Sensor Hub is the primary agricultural sensor data aggregation gateway. It ingests data from LoRaWAN nodes (15 km suburban range, 45 km rural), MQTT brokers, and direct HTTP REST sensors. The hub applies 1D Kalman filtering for noise reduction (>92% accuracy), validates readings against 15 sensor type range definitions, generates threshold-based alerts at four severity levels, calculates Weighted Decision Index (WDI) for irrigation decisions, and maintains a 72-hour offline cache with 100 000-entry capacity for Yemen's intermittent connectivity environment.

Hardware cost for a field node: < $15 USD (TTGO LoRa32 / ESP32 + LoRa module).

## Architecture

```
FastAPI Application (port 8251)
├── Node Registry (auto-registration, status, battery, RSSI)
├── Data Ingest Layer
│   ├── LoRaWAN (15–45 km range, ESP32/Arduino nodes)
│   ├── MQTT (TLS/SSL broker, topic: sahool/sensors/#)
│   └── Direct HTTP REST (SensorReading POST)
├── Kalman Filter Engine (1D, process_var=0.01, measurement_var=0.1)
├── Threshold Alerter (CRITICAL / WARNING / ADVISORY / INFO)
├── WDI Calculator (Sahu & Tripathi 2025 formula)
├── 72-Hour Offline Cache (deque, 100 000 entries, auto-cleanup)
└── NATS Publisher (sensor readings, alerts, WDI decisions)
```

## Supported Sensor Types (15)

| Type | Arabic | Unit | Alert Thresholds |
|------|--------|------|-----------------|
| SOIL_MOISTURE | رطوبة التربة | % | Critical < 15%, Warning < 25% |
| SOIL_TEMPERATURE | درجة حرارة التربة | °C | Warning > 48°C, Critical > 50°C |
| SOIL_EC | التوصيل الكهربائي | dS/m | Warning > 4 dS/m |
| AIR_TEMPERATURE | درجة حرارة الهواء | °C | Warning > 42°C, Warning < 5°C |
| AIR_HUMIDITY | رطوبة الهواء | % | Warning < 20%, Warning > 90% |
| WIND_SPEED | سرعة الرياح | m/s | — |
| SOLAR_RADIATION | الإشعاع الشمسي | W/m² | — |
| RAINFALL | الأمطار | mm | — |
| WATER_FLOW | تدفق الماء | L/min | — |
| WATER_LEVEL | مستوى الماء | m | — |
| WATER_EC | توصيل الماء | dS/m | Warning > 3 dS/m |
| WATER_PH | درجة حموضة الماء | pH | — |
| LEAF_WETNESS | رطوبة الأوراق | % | — |
| NDVI_SENSOR | مؤشر الغطاء النباتي | index | — |
| PRESSURE | الضغط | kPa | — |

## API Endpoints

### Health
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Readiness probe with node count and cache size |

### Node Management
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/iot/nodes` | POST | Register new sensor node |
| `/api/v1/iot/nodes` | GET | List nodes (filter by field_id) |
| `/api/v1/iot/nodes/{node_id}` | GET | Node status and recent 20 readings |

### Sensor Data Ingestion
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/iot/readings` | POST | Ingest single sensor reading |
| `/api/v1/iot/readings/batch` | POST | Batch ingest (optimized for 1 000+ readings) |

### Irrigation Decision Support
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/iot/wdi` | POST | Calculate Weighted Decision Index |

### Alerts
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/iot/alerts` | GET | Recent alerts (filter by severity, field_id, limit) |

### Offline Cache
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/iot/cache/status` | GET | Cache size, age, sync status |
| `/api/v1/iot/cache/sync` | POST | Two-phase sync: preview then confirm clear |

### Statistics
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/iot/stats` | GET | Platform stats (nodes, readings, alerts, Kalman) |
| `/api/v1/iot/sensor-types` | GET | All sensor types with ranges and thresholds |

## NATS Events

### Publishes
| Subject | Trigger |
|---------|---------|
| `sahool.{tenant_id}.iot.reading.{sensor_type}` | Every accepted reading (filtered value) |
| `sahool.{tenant_id}.iot.alert.{severity}` | Threshold breach (CRITICAL/WARNING/ADVISORY/INFO) |
| `sahool.{tenant_id}.iot.wdi_calculated` | WDI calculation result |

Example: `sahool.farm_001.iot.reading.soil_moisture`, `sahool.farm_001.iot.alert.critical`

## Alert Severity Levels

| Level | Arabic | Response Window | Example Trigger |
|-------|--------|----------------|----------------|
| CRITICAL | حرج | < 6 hours | Soil moisture < 15% |
| WARNING | تحذير | 24–48 hours | Air temperature < 5°C |
| ADVISORY | استشارة | 1 week | Salinity trend increase |
| INFO | معلومات | Awareness | Battery level 30% |

## WDI (Weighted Decision Index) Formula

```
WDI = 0.35 × soil_moisture_stress
    + 0.25 × temperature_stress
    + 0.15 × humidity_stress
    + 0.10 × wind_stress
    + 0.15 × radiation_stress

Decision:
  WDI ≥ 0.70 → Irrigate immediately (confidence 95%)
  WDI 0.50–0.70 → Schedule within 24 h (confidence 80%)
  WDI 0.30–0.50 → Monitor closely (confidence 70%)
  WDI < 0.30 → No irrigation needed (confidence 90%)
```

Impact: 25% water reduction, 18% yield increase (Sahu & Tripathi, 2025).

## Kalman Filter Configuration

- Process variance: 0.01 (system noise)
- Measurement variance: 0.1 (sensor noise)
- Achieves >92% accuracy (DT Orchestration, ACS 2024)
- Latency: < 0.5 s per filtered reading

## 72-Hour Offline Cache

Queue capacity: 100 000 readings. Auto-cleanup removes entries older than 72 hours. Two-phase sync protocol: first call with `confirm_clear=false` to preview, then `confirm_clear=true` to flush synced entries.

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8251` | No | Service port |
| `ENVIRONMENT` | — | Yes | production / staging / development |
| `TENANT_ID` | `default` | No | Tenant for NATS event scoping |
| `NATS_URL` | — | No | NATS server |
| `MQTT_BROKER_URL` | — | No | MQTT broker URL |
| `MQTT_USERNAME` | — | No | MQTT username |
| `MQTT_PASSWORD` | — | No | MQTT password |
| `MQTT_TOPIC` | `sahool/sensors/#` | No | MQTT subscription topic |
| `LOG_LEVEL` | `INFO` | No | Logging level |

## Performance Benchmarks

| Operation | Latency | Throughput |
|-----------|---------|-----------|
| Single reading ingest | < 5 ms | 200 readings/s |
| Batch ingest (1 000) | < 50 ms | 20 000 readings/s |
| WDI calculation | < 2 ms | 500 WDI/s |
| Cache sync (100 K entries) | < 500 ms | — |

## Integration Points

**Upstream:** iot-gateway (MQTT/LoRaWAN), edge-orchestrator-service (Jetson), weather-service, virtual-sensors

**Downstream:** irrigation-smart (WDI decisions), advisory-service, alert-service, field-intelligence, crop-intelligence-service

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "iot-sensor-hub", "version": "16.0.0"}
GET /readyz   → {"status": "ok", "nodes_registered": 12, "offline_cache_size": 450, "nats": true}
```

## Admin Integration Notes

- The admin portal's live sensor dashboard should subscribe to `sahool.{tenant_id}.iot.reading.*` via the WebSocket gateway to display real-time sensor values.
- CRITICAL alerts (`sahool.{tenant_id}.iot.alert.critical`) must be forwarded to the notification service and displayed as banners in the admin dashboard.
- The two-phase cache sync protocol (`confirm_clear=false` preview, then `confirm_clear=true`) should be exposed in the admin field device panel to let operators manually trigger field data recovery after connectivity outages.
- The WDI endpoint can be invoked by the irrigation management module to provide a data-driven irrigation trigger alongside schedule-based rules.
- Node battery level tracking (visible in node status) should surface low-battery warnings in the admin device management panel.
