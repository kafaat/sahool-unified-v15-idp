# Irrigation Cycle Engine

**Type:** Python / FastAPI
**Port:** 8250
**Version:** 16.0.0
**Layer:** Decision (Event Architecture)

## Overview

The Irrigation Cycle Engine implements FAO-56 standard irrigation scheduling with Yemen-specific adaptations. It calculates reference evapotranspiration (ET0) using the Penman-Monteith equation, crop evapotranspiration (ETc) using dual crop coefficients (Kcb + Ke), optimal irrigation cycle periods, and complete multi-day irrigation schedules. The service includes a database of 25+ Yemen crops with regional growth stages and Kc values, six Yemen soil profiles, four climate zones, and salinity management with leaching requirement calculations and yield reduction estimation under salt stress.

## Architecture

```
FastAPI Application (port 8250)
├── ET0 Calculator (Penman-Monteith FAO-56 method)
├── ETc Calculator (ET0 × Kc, dual crop coefficient support)
├── Irrigation Cycle Formula Engine
│   └── T = ((θfc - θmin) × Zr × β) / (ETc × α × γ)
├── Multi-Day Schedule Generator
│   ├── Daily soil water balance
│   ├── Growth stage progression
│   └── Irrigation event detection (depletion threshold)
├── Yemen Data Module
│   ├── 25+ crops (Kc values, growth stages, salinity tolerance)
│   ├── 4 climate zones (ET0 ranges, groundwater data)
│   └── 6 soil profiles (θfc, θwp, bulk density)
└── Salinity Assessment Module
    ├── EC-based leaching requirement
    ├── SAR calculation
    └── Yield reduction estimation (Maas & Hoffman 1977)
    ↓
NATS Publisher (sahool.{tenant_id}.irrigation.cycle_calculated)
```

## API Endpoints

### Health
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Readiness probe (checks Yemen data loading) |

### ET0 Calculation
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/irrigation/et0` | POST | Calculate ET0 using FAO-56 Penman-Monteith |

### Irrigation Cycle
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/irrigation/cycle` | POST | Calculate optimal cycle period and water requirement |
| `/api/v1/irrigation/schedule` | POST | Generate multi-day irrigation schedule |
| `/api/v1/irrigation/salinity-assessment` | POST | Assess salinity impact on irrigation and yield |

### Yemen Reference Data
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/yemen/crops` | GET | List Yemen crops (filter by type and region) |
| `/api/v1/yemen/crops/{crop_name}` | GET | Detailed crop parameters and growth stages |
| `/api/v1/yemen/climate-zones` | GET | Yemen climate zones with ET0 ranges |
| `/api/v1/yemen/soils` | GET | Yemen soil profiles with hydraulic properties |

## Core Formulas

### ET0 (Penman-Monteith FAO-56)
```
ET0 = (0.408 × Δ × (Rn - G) + γ × (900/(T+273)) × u₂ × (eₛ - eₐ))
      / (Δ + γ × (1 + 0.34 × u₂))
```
Where Δ = slope of saturation vapor pressure curve, Rn = net radiation, γ = psychrometric constant, u₂ = wind speed at 2 m height.

### ETc
```
ETc = ET0 × Kc
```

### Irrigation Cycle
```
T = ((θfc - θmin) × Zr × β) / (ETc × α × γ)

T    = Irrigation cycle (days)
θfc  = Field capacity (cm³/cm³)
θmin = Minimum soil moisture threshold
Zr   = Effective root depth (mm)
β    = Soil correction factor (0.8–1.2)
α    = ET correction factor (0.7–1.3)
γ    = Stress/management correction factor (0.8–1.0)
```

## Yemen Crops Database (25+)

Key crops: wheat (القمح), barley (الشعير), sorghum (الذرة الرفيعة), date palm (النخيل), maize, tomato, cucumber, potato, cotton, coffee arabica (القهوة العربية), qat (القات), alfalfa.

Wheat example: root depth 1.0 m, depletion fraction 0.5, salinity threshold 6.0 dS/m, four growth stages (Germination Kc=0.3, Tillering Kc=0.7, Heading Kc=1.0, Grain Filling Kc=0.85).

## Yemen Climate Zones

| Zone | ET0 Range | Annual Rainfall | Key Crops |
|------|-----------|-----------------|-----------|
| High Rainfall | 3.0–5.0 mm/day | 600 mm | wheat, barley, maize |
| Moderate Rainfall | 4.0–6.0 mm/day | 250 mm | sorghum, vegetables |
| Arid | 5.0–8.0 mm/day | 50 mm | date palm, alfalfa |
| Coastal | 4.5–7.0 mm/day | 100 mm | vegetables, rice |

## Yemen Soil Profiles (6)

| Soil Type | θfc | θwp | Bulk Density | Available Water |
|-----------|-----|-----|--------------|----------------|
| Sandy Loam | 0.28 | 0.12 | 1.4 g/cm³ | 160 mm/m |
| Clay Loam | 0.36 | 0.18 | 1.3 g/cm³ | 180 mm/m |
| Calcareous | 0.32 | 0.14 | 1.45 g/cm³ | 180 mm/m |
| Silty Clay | 0.40 | 0.22 | 1.25 g/cm³ | 180 mm/m |
| Sandy | 0.18 | 0.06 | 1.6 g/cm³ | 120 mm/m |
| Wadi Alluvial | 0.30 | 0.13 | 1.35 g/cm³ | 170 mm/m |

## Salinity Assessment

- Leaching fraction: `LF = EC_water / (5 × EC_threshold - EC_water)`
- Yield reduction: Maas & Hoffman (1977) piecewise linear model
- SAR calculation: `SAR = Na / √((Ca + Mg) / 2)` (meq/L)
- Risk classification: low, moderate, high, severe

## NATS Events

### Publishes
| Subject | Trigger |
|---------|---------|
| `sahool.{tenant_id}.irrigation.cycle_calculated` | Successful cycle calculation |

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8250` | No | Service port |
| `NATS_URL` | — | No | NATS server (optional) |
| `TENANT_ID` | `default` | No | Tenant for NATS event scoping |
| `LOG_LEVEL` | `INFO` | No | Logging level |
| `ENVIRONMENT` | `dev` | No | Deployment environment |
| `DATABASE_URL` | — | No | PostgreSQL (optional, for schedule persistence) |

No database is required for ET0/cycle calculations. The service starts without NATS (graceful degradation).

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pyfao56 | >= 1.4.0 | FAO-56 ET calculations |
| numpy | >= 1.26.0 | Numerical computations |
| FastAPI | 0.128.5 | Web framework |
| Pydantic | 2.12.5 | Data validation |
| nats-py | 2.13.1 | NATS messaging |
| structlog | >= 24.1.0 | Structured logging |
| prometheus-client | >= 0.21.0 | Metrics |

## Service Integrations

| Service | Data Exchanged |
|---------|---------------|
| weather-service (8092) | Weather data for ET0 calculations |
| field-management-service (3000) | Field and crop information |
| vegetation-analysis-service (8090) | NDVI for crop stress factor |
| notification-service (8110) | Irrigation schedule alerts |
| irrigation-smart (8094) | Receives cycle recommendations |

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "irrigation-cycle-engine"}
GET /readyz   → {"status": "ok", "yemen_crops_loaded": 25, "climate_zones_loaded": 4}
```

## Admin Integration Notes

- The admin portal's irrigation planning module should call `POST /api/v1/irrigation/schedule` with crop, soil profile, and climate zone to generate a season-long irrigation calendar.
- The salinity assessment endpoint (`POST /api/v1/irrigation/salinity-assessment`) should be surfaced in the water quality management section to alert farmers of yield reduction risk.
- Yemen crop data (`GET /api/v1/yemen/crops`) should populate the crop selection dropdowns throughout the admin irrigation planning interface.
- Climate zone data (`GET /api/v1/yemen/climate-zones`) with groundwater decline rates informs the admin regional water resource management dashboard.
- All formulas comply with FAO-56 (Allen et al., 1998) and Ayers & Westcot (1985) standards — cite these references in any admin documentation or farmer-facing reports.
