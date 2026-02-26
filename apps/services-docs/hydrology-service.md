# Hydrology Service

**Type:** Python / FastAPI
**Port:** 8165
**Version:** 16.0.0
**Layer:** Intelligence (Event Architecture)

## Overview

The Hydrology Service provides comprehensive agricultural water management analysis by processing terrain data to produce drainage network maps, wetness zone classification, depression detection, stream network delineation, and watershed basin analysis. It depends on the Terrain Core Service for DEM-derived flow data and the Weather Service for rainfall-based waterlogging predictions. Results drive irrigation layout decisions, drainage infrastructure planning, and flood risk assessments.

## Architecture

```
FastAPI Application (port 8165)
├── Drainage Network Analyzer (pattern, density, bifurcation ratio)
├── Wetness Zone Classifier (6 TWI levels, irrigation efficiency score)
├── Depression Detector (volume, depth, risk level)
├── Stream Network Delineator (Strahler ordering, length, upstream area)
└── Basin / Watershed Delineator (pour points, runoff coefficient)
    ↓
External Service Calls
├── terrain-core-service:8185 → DEM, flow direction, TWI, slope
└── weather-service:8092 → Rainfall data for waterlogging prediction
    ↓
PostgreSQL (result persistence) + NATS (analysis events)
```

## API Endpoints

### Health
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/metrics` | GET | Prometheus metrics |

### Full Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/hydrology/analyze` | POST | Complete hydrology analysis (all modules) |
| `/api/v1/hydrology/summary/{field_id}` | GET | Cached analysis summary |

### Drainage
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/drainage/network` | POST | Analyze drainage network |
| `/api/v1/drainage/pattern/{field_id}` | GET | Drainage pattern (dendritic, parallel, etc.) |
| `/api/v1/drainage/density/{field_id}` | GET | Drainage density calculation |

### Wetness
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/wetness/analyze` | POST | Wetness zone analysis from TWI |
| `/api/v1/wetness/predict-waterlogging` | POST | Waterlogging risk given rainfall scenario |
| `/api/v1/wetness/zones/{field_id}` | GET | Classified wetness zones |

### Depressions
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/depressions/detect` | POST | Detect and classify sink depressions |
| `/api/v1/depressions/volume/{field_id}` | GET | Total depression volume |
| `/api/v1/depressions/{field_id}` | GET | Depression list with risk levels |

### Streams
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/streams/detect` | POST | Detect stream network |
| `/api/v1/streams/{field_id}` | GET | Stream network with Strahler orders |
| `/api/v1/streams/order/{field_id}` | GET | Streams grouped by order |

### Basins
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/basins/delineate` | POST | Delineate watersheds and sub-basins |
| `/api/v1/basins/{field_id}` | GET | Basin morphometric parameters |
| `/api/v1/basins/runoff/{field_id}` | GET | Runoff coefficient estimate |

## Wetness Level Classification

| Level | TWI Range | Management |
|-------|-----------|------------|
| Very Dry | < 4 | Increase irrigation |
| Dry | 4–6 | Monitor soil moisture |
| Moderate | 6–9 | Optimal for most crops |
| Wet | 9–12 | Reduce irrigation |
| Very Wet | 12–15 | Improve drainage |
| Waterlogged | > 15 | Critical drainage action |

## Depression Risk Levels

| Level | Depth | Drain Time | Action |
|-------|-------|------------|--------|
| Low | < 20 cm | < 6 h | Monitor |
| Medium | 20–50 cm | 6–24 h | Improve drainage |
| High | 50–100 cm | 24–72 h | Fill or drain |
| Critical | > 100 cm | > 72 h | Immediate action |

## Drainage Patterns

| Pattern | Description |
|---------|-------------|
| Dendritic | Tree-like; uniform geology |
| Parallel | Steep uniform slopes |
| Trellis | Folded sedimentary rock |
| Rectangular | Jointed / fractured rock |
| Radial | Around volcanic cones |
| Centripetal | Toward central depression |

## NATS Events

### Publishes
| Event | Trigger |
|-------|---------|
| `HydrologyAnalysisCompleted.v1` | Full analysis finished |
| `WaterloggingAlert.v1` | High waterlogging risk detected |
| `DepressionDetected.v1` | Critical depression identified |
| `DrainageQualityAssessed.v1` | Drainage quality score calculated |

### Consumes
| Event | Action |
|-------|--------|
| `FieldCreated.v1` | Run hydrology analysis for new field |
| `TerrainAnalysisCompleted.v1` | Trigger hydrology processing with new terrain data |
| `WeatherForecastReady.v1` | Update waterlogging predictions |
| `RainfallRecorded.v1` | Recalculate predictions with actual rainfall |

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8165` | No | Service port |
| `DATABASE_URL` | — | Yes | PostgreSQL connection |
| `NATS_URL` | — | Yes | NATS server |
| `TERRAIN_SERVICE_URL` | `http://terrain-core-service:8185` | No | Terrain Core Service URL |
| `WEATHER_SERVICE_URL` | `http://weather-service:8092` | No | Weather Service URL |
| `DEFAULT_DEM_RESOLUTION` | `30.0` | No | DEM resolution in meters |
| `FLOW_ACCUMULATION_THRESHOLD` | `100` | No | Stream detection threshold |
| `DEPRESSION_FILL_MAX_DEPTH` | `2.0` | No | Max depression fill depth (m) |
| `WETNESS_INDEX_HIGH_THRESHOLD` | `12.0` | No | TWI threshold for high wetness |
| `BASIN_AREA_MIN_HECTARES` | `0.5` | No | Minimum basin area |
| `CACHE_TTL_SECONDS` | `3600` | No | Redis cache TTL |

## Service Dependencies

```
hydrology-service → terrain-core-service
  GET /api/v1/terrain/flow      (flow direction and accumulation)
  GET /api/v1/terrain/twi       (Topographic Wetness Index)
  GET /api/v1/dem/metadata      (DEM source and resolution)

hydrology-service → weather-service
  GET /api/v1/weather/rainfall/{field_id}    (historical rainfall)
  GET /api/v1/weather/forecast/{field_id}    (rainfall forecast)
```

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "hydrology-service"}
GET /readyz   → {"status": "ok", "terrain_service": true, "nats": true}
GET /metrics  → Prometheus: analysis_duration_seconds, waterlogging_alerts_total
```

## Admin Integration Notes

- Hydrology analysis is automatically triggered by the `TerrainAnalysisCompleted.v1` event; no manual invocation is needed.
- The admin portal's field drainage dashboard can display wetness zone maps and depression locations sourced from this service.
- Pre-season waterlogging risk reports use the `predict-waterlogging` endpoint with 50 mm rainfall scenarios for field preparation planning.
- The `WaterloggingAlert.v1` event should be routed to the notification service to warn farmers of high-risk zones before rain events.
- Large fields (> 200 ha) may require 3–8 minutes for full analysis; implement async polling on the NATS event.
