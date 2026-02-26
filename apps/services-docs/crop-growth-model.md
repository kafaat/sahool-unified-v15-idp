# Crop Growth Model Service

**Port**: 3023 | **Type**: Node.js (NestJS, TypeScript) | **Version**: 16.0.0

Mechanistic, intelligent, and integrated crop growth simulation service. Models phenology, photosynthesis, biomass accumulation, water balance, and root dynamics to support precision agricultural planning and digital twin integration.

---

## Overview

`crop-growth-model` is a scientific NestJS service implementing concepts from WOFOST, DSSAT, and APSIM mechanistic crop growth models. It simulates crop development from sowing to harvest using thermal time (GDD), Farquhar-based photosynthesis, source-sink biomass partitioning, and multi-stress response functions. It integrates satellite data, GIS boundaries, multi-agent advisory, and voice guidance, and it feeds the digital twin engine.

---

## Architecture

```
NestJS Application (Port 3023)
    ├── PhenologyModule        - DVS tracking, GDD accumulation, growth stage transitions
    ├── PhotosynthesisModule   - LUE model, CO2 assimilation, radiation interception
    ├── BiomassModule          - Source-sink-flow partitioning, organ allocation
    ├── SimulationModule       - Full season growth simulation
    ├── RootGrowthModule       - Root depth and distribution dynamics
    ├── WaterBalanceModule     - Soil-crop water balance (FAO-56)
    ├── SatelliteDataModule    - Satellite NDVI / LAI data ingestion
    ├── IrrigationDecisionModule - Model-based irrigation scheduling
    ├── MultiAgentAdvisorModule - CrewAI agent integration for advisory
    ├── VoiceGuidanceModule    - Arabic/English voice synthesis for advisory
    ├── WebDataCollectorModule - Live weather and crop parameter ingestion
    ├── DigitalTwinCoreModule  - Digital twin state management
    ├── RSWorldModelModule     - Remote sensing world model updates
    ├── PlantingStrategyModule - Planting date and variety optimization
    └── GISIntegrationModule   - Field boundary and geospatial operations
```

Global pipes: `ValidationPipe` (whitelist + transform). Global filters: `HttpExceptionFilter`. Global interceptors: `RequestLoggingInterceptor` with correlation IDs.

---

## API Endpoints

### Health

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Kubernetes liveness and readiness probe |

### Phenology

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/phenology/simulate` | Simulate crop phenology with GDD inputs |
| GET | `/api/v1/phenology/stages/{crop}` | List growth stages for a crop type |
| GET | `/api/v1/phenology/gdd-requirements/{crop}` | GDD requirements by stage |

### Photosynthesis

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/photosynthesis/daily` | Calculate daily CO2 assimilation rate |
| POST | `/api/v1/photosynthesis/stress-factors` | Compute temperature and water stress |

### Biomass

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/biomass/distribute` | Source-sink partitioning across organs |
| GET | `/api/v1/biomass/allocation/{crop}/{stage}` | Allocation fractions by crop and stage |

### Growth Simulation

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/simulation/season` | Full-season simulation from sowing to harvest |
| POST | `/api/v1/simulation/scenario` | Multi-scenario comparison simulation |

### Water Balance

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/water-balance/daily` | Daily soil water balance computation |
| POST | `/api/v1/water-balance/irrigation-schedule` | Generate irrigation schedule |

### Irrigation Decision

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/irrigation/decision` | Model-based irrigation decision |
| POST | `/api/v1/irrigation/deficit` | Compute water deficit |

### Satellite Data

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/satellite/assimilate` | Assimilate satellite NDVI/LAI into model state |
| GET | `/api/v1/satellite/lai/{field_id}` | Get LAI estimate for a field |

### Planting Strategy

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/planting-strategy/optimize` | Optimal planting date and variety selection |

### GIS Integration

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/gis/field-analysis` | Spatial crop modeling over field geometry |

### Multi-Agent Advisory

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/advisor/query` | Route query to specialist agents (Arabic/English) |

### Voice Guidance

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/voice/synthesize` | Generate voice guidance for advisory output |

---

## Core Scientific Models

| Module | Scientific Basis | Description |
|--------|-----------------|-------------|
| Phenology | Thermal time (GDD) | DVS 0 → 2 tracking, vernalization |
| Photosynthesis | Farquhar + LUE | Gross/net assimilation, radiation interception |
| Biomass | Source-sink theory | Root, stem, leaf, grain partitioning |
| Water Balance | FAO-56 (Allen et al.) | ET0, Kc, soil water depletion |
| Root Growth | Exponential front descent | Root depth, density distribution |

---

## Rate Limiting

| Window | Limit |
|--------|-------|
| 1 second | 10 requests |
| 1 minute | 100 requests |
| 1 hour | 1,000 requests |

---

## Authentication

JWT Bearer token via `@sahool/nestjs-auth` (`AuthModule.forRoot`). User validation and token revocation are disabled for internal service-to-service calls.

---

## NATS Events

This service does not publish NATS events directly. Results are consumed synchronously by calling services (advisory-service, digital-twin-engine).

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `3023` | HTTP listen port |
| `ENVIRONMENT` | `development` | Deployment environment |
| `DATABASE_URL` | - | PostgreSQL connection string (optional) |
| `CORS_ALLOWED_ORIGINS` | `https://sahool.com,http://localhost:3000` | CORS allowed origins |
| `JWT_SECRET_KEY` | - | Inherited from auth module |

---

## Dependencies

- NestJS 10.x, TypeScript 5.9.x
- `@sahool/nestjs-auth` for JWT authentication
- `@nestjs/throttler` for rate limiting
- `@nestjs/swagger` for API documentation at `/docs`

---

## Health Endpoints

```
GET /health → {"status": "ok", "service": "crop-growth-model", "version": "16.0.0"}
```

---

## Related Services

- **advisory-service** (8093) - consumes growth model recommendations
- **irrigation-smart** (8094) - irrigation scheduling consumer
- **digital-twin-engine** (8253) - uses simulation output for twin state
- **satellite-data / vegetation-analysis-service** (8090) - LAI/NDVI data source
