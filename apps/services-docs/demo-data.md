# Demo Data Service | خدمة البيانات التجريبية

Realistic agricultural data simulation service that drives the SAHOOL demo environment by continuously sending HTTP requests to platform APIs through the Kong gateway.

**Port:** 8261 | **Type:** Python (standalone script) | **Version:** 16.0.0

---

## Overview

The Demo Data Service generates and injects realistic Saudi Arabian agricultural data into the SAHOOL platform to create a convincing demonstration environment for sales presentations, developer testing, and integration validation. Unlike other services, it has no REST API of its own — it is a worker process that acts as an API client, pumping data into other platform services.

Key capabilities:
- Weather data generation calibrated for Saudi Arabia (temperature 25–45°C, humidity 10–60%)
- IoT sensor simulation: soil sensors (moisture, temperature, pH, EC), weather stations, flow meters
- NDVI vegetation index data with automatic health classification
- Agricultural alert generation (weather, irrigation, pest, harvest)
- Task scheduling for irrigation, fertilization, inspection, harvest, pest control
- Yield prediction request generation
- Inventory transaction simulation (seeds, fertilizer, pesticide, fuel)
- Marketplace product listing creation
- Service health checking across 7 platform endpoints
- Three run modes: continuous (default), once, batch

---

## Architecture

```
Demo Data Service (8261)
└── DemoDataGenerator (single class, no web server)
    ├── generate_weather_data()    → POST /api/v1/weather/readings
    ├── generate_sensor_data()     → POST /api/v1/iot/readings
    ├── generate_ndvi_data()       → POST /api/v1/ndvi/records
    ├── generate_alert_data()      → POST /api/v1/alerts
    ├── generate_task_data()       → POST /api/v1/tasks
    ├── generate_inventory_update()→ POST /api/v1/inventory/transactions
    ├── generate_marketplace_listing() → POST /api/v1/marketplace/products
    ├── request_yield_prediction() → POST /api/v1/yield-prediction/predict
    └── check_field_health()       → GET /api/v1/fields/{id}/health

All requests routed through:
    Kong Gateway (default: http://kong:8000)
    Headers: X-API-Key, X-Tenant-ID, X-User-ID
```

This service does **not** expose its own HTTP server. It is a pure data generator script (`main.py`) launched directly with `python main.py`.

---

## Run Modes

| Mode | Behavior |
|------|---------|
| `continuous` | Default. Runs indefinitely, selecting 3–5 random operations per interval. Reports stats every 10 iterations. |
| `once` | Runs all generators once, prints summary, exits. Useful for seeding. |
| `batch` | Runs `BATCH_COUNT` iterations of weather, sensor, and NDVI data in rapid succession (100ms delay between iterations). |

---

## Generated Data

### Demo Fields (3 fixed UUIDs)
- `d0000000-0000-0000-0000-000000000001`
- `d0000000-0000-0000-0000-000000000002`
- `d0000000-0000-0000-0000-000000000003`

### Demo Devices (5 fixed IDs)
- `SOIL-001`, `SOIL-002` — Soil sensors (moisture, temperature, pH, EC)
- `WEATHER-001` — Weather station (temperature, humidity, wind, solar radiation)
- `WATER-001` — Flow meter (flow rate, total volume, pressure)
- `CAM-001` — Camera (referenced but no image generation in current version)

### Saudi Arabia Governorates
Riyadh, Makkah, Madinah, Eastern Province, Qassim, Asir

### Supported Crops
wheat, barley, dates, tomatoes, alfalfa, cucumbers, grapes

### NDVI Health Classification

| NDVI Range | Classification |
|------------|---------------|
| ≥ 0.8 | excellent |
| 0.6 – 0.8 | good |
| 0.4 – 0.6 | moderate |
| 0.2 – 0.4 | poor |
| < 0.2 | critical |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8261` | Nominal port (not used by the HTTP server, reserved for container) |
| `KONG_URL` | `http://kong:8000` | Kong API gateway URL for all requests |
| `API_KEY` | `demo-api-key` | API key injected as `X-API-Key` header |
| `TENANT_ID` | `a0000000-0000-0000-0000-000000000001` | Demo tenant UUID |
| `USER_ID` | `b0000000-0000-0000-0000-000000000001` | Demo user UUID |
| `INTERVAL_SECONDS` | `30` | Seconds between iterations in continuous mode |
| `DEMO_MODE` | `continuous` | Run mode: `continuous`, `once`, `batch` |
| `BATCH_COUNT` | `100` | Number of batch iterations when `DEMO_MODE=batch` |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Running the Service

```bash
# Docker Compose
docker compose up demo-data

# Direct Python execution
cd apps/services/demo-data
python main.py

# One-shot seeding
DEMO_MODE=once python main.py

# Batch seeding (1000 records)
DEMO_MODE=batch BATCH_COUNT=1000 python main.py
```

---

## Statistics Output

The service prints a statistics summary every 10 continuous iterations and on exit:

```
==================================================
Demo Data Statistics:
  Total requests: 150
  Successful:     143
  Failed:         7
  Success rate:   95.3%
==================================================
```

---

## Dependencies

- **httpx** — Async HTTP client for all API calls
- **asyncio** — Async execution framework
- Python standard library only (no FastAPI, no database, no NATS)

---

## Health Checks Monitored

The service checks health of these endpoints on startup and periodically:

| Service | Endpoint |
|---------|---------|
| Weather | `/api/v1/weather/health` |
| IoT Gateway | `/api/v1/iot/health` |
| NDVI Engine | `/api/v1/ndvi/health` |
| Field Service | `/api/v1/fields/health` |
| Task Service | `/api/v1/tasks/health` |
| Alert Service | `/api/v1/alerts/health` |
| Marketplace | `/api/v1/marketplace/health` |

---

## Related Services

- **weather-service** (8092) — Receives weather readings
- **iot-gateway** (8106) — Receives sensor readings
- **ndvi-processor** (8118) — Receives NDVI records
- **alert-service** (8113) — Receives generated alerts
- **task-service** (8103) — Receives scheduled tasks
- **inventory-service** (8116) — Receives inventory transactions
- **marketplace-service** (3010) — Receives product listings
