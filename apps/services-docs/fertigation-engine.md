# Fertigation Engine

**Type:** Python / FastAPI
**Port:** 8252
**Version:** 16.0.0
**Layer:** Decision (Event Architecture)

## Overview

The Fertigation Engine is an integrated fertilizer-and-irrigation management microservice. It calculates complete fertigation plans — NPK requirements by crop and growth stage, optimal fertilizer selection, electrical conductivity (EC) management, environmental risk assessment, and cost tracking in SAR per hectare. The service covers 8 crops, 8 growth phases, 11 fertilizer types, and performs soil nutrient credit calculations, nutrient balance tracking, and bilingual (Arabic/English) recommendation generation.

## Architecture

```
FastAPI Application (port 8252)
└── FertigationEngine Class
    ├── NPK Database (8 crops × 8 growth phases)
    ├── Fertilizer Database (11 types with EC, solubility, price)
    ├── Soil Nutrient Credit System (30–50% utilization factors)
    ├── Greedy Fertilizer Selector (P → N → K priority)
    ├── EC Management Module (irrigation water + fertilizer contribution)
    ├── Environmental Risk Assessor (N and P leaching risk)
    └── Bilingual Recommendation Generator
    ↓
NATS Event Publisher (plan_created events, optional)
```

No persistent database is required for plan calculations. PostgreSQL is used only if nutrient balance history needs persistence. The service starts and operates without NATS (graceful degradation).

## API Endpoints

### Health
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Liveness probe — `{"status": "ok", "service": "fertigation-engine"}` |
| `/readyz` | GET | Readiness probe — includes crops_with_npk count and NATS status |

### Fertigation Planning
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fertigation/plan` | POST | Calculate complete fertigation plan |
| `/api/v1/fertigation/nutrient-balance` | POST | Calculate cumulative NPK balance |

### Reference Data
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fertigation/fertilizers` | GET | List all 11 fertilizer types with NPK, EC, price |
| `/api/v1/fertigation/crops` | GET | List all 8 crops with total NPK requirements |
| `/api/v1/fertigation/crops/{crop_name}/npk` | GET | NPK by growth phase for a specific crop |
| `/api/v1/fertigation/growth-phases` | GET | List all 8 supported growth phases |

## Supported Crops

| Crop | Arabic | Total N | Total P | Total K |
|------|--------|---------|---------|---------|
| wheat | القمح | 120 kg/ha | 60 kg/ha | 75 kg/ha |
| barley | الشعير | 100 kg/ha | 50 kg/ha | 60 kg/ha |
| date_palm | النخيل | 130 kg/ha | 65 kg/ha | 210 kg/ha |
| tomato | الطماطم | 180 kg/ha | 100 kg/ha | 190 kg/ha |
| sorghum | الذرة الرفيعة | 85 kg/ha | 43 kg/ha | 60 kg/ha |
| qat | القات | 130 kg/ha | 45 kg/ha | 95 kg/ha |
| coffee_arabica | القهوة العربية | 120 kg/ha | 55 kg/ha | 125 kg/ha |
| alfalfa | الجت / البرسيم | 20 kg/ha | 55 kg/ha | 110 kg/ha |

## Fertilizer Database (11 Types)

| Type | N% | P% | K% | Price (SAR/kg) |
|------|----|----|----|----------------|
| urea | 46 | 0 | 0 | 2.50 |
| dap | 18 | 46 | 0 | 3.00 |
| map | 11 | 52 | 0 | 3.50 |
| kcl | 0 | 0 | 60 | 2.80 |
| sop | 0 | 0 | 50 | 4.00 |
| ammonium_nitrate | 34 | 0 | 0 | 2.00 |
| calcium_nitrate | 15.5 | 0 | 0 | 3.50 |
| potassium_nitrate | 13 | 0 | 46 | 5.00 |
| npk_20_20_20 | 20 | 20 | 20 | 6.00 |
| npk_15_15_15 | 15 | 15 | 15 | 5.00 |
| phosphoric_acid | 0 | 52 | 0 | 4.50 |

## Growth Phases

`germination` → `seedling` → `vegetative` → `tillering` → `flowering` → `fruit_development` → `ripening` → `harvest`

## Core Algorithms

**Soil Nutrient Credit:**
- N credit: `soil_n_ppm × 2.0 kg/ha per ppm`, 30% utilized
- P credit: `soil_p_ppm × 1.5 kg/ha per ppm`, 20% utilized
- K credit: `soil_k_ppm × 1.2 kg/ha per ppm`, 20% utilized

**Fertilizer Selection (Greedy):** Phosphorus source first → nitrogen source to cover residual N → potassium source (KCl for normal soils, SOP for saline EC > 1.5 dS/m).

**EC Management:** `EC_total = EC_water + Σ(kg_fertilizer / m³_water × ec_per_gl)`. If total exceeds `max_ec_solution`, service recommends splitting the application.

**N Loss Risk:** Low (< 40 kg/ha), Moderate (40–80 kg/ha), High (> 80 kg/ha). High risk triggers early-morning application advisory.

## NATS Events

### Publishes
| Subject | Trigger |
|---------|---------|
| `sahool.{tenant_id}.fertigation.plan_created` | Successful plan calculation |

Future events (planned): `high_ec_alert`, `n_loss_risk` (when risk is HIGH).

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8252` | No | Service port |
| `ENVIRONMENT` | `development` | No | Deployment environment |
| `LOG_LEVEL` | `INFO` | No | Logging level |
| `NATS_URL` | — | No | NATS server (optional) |
| `TENANT_ID` | `default` | No | Tenant for NATS event scoping |
| `REDIS_URL` | — | No | Redis (future caching use) |

No `DATABASE_URL` is required for plan calculations. The shared module `shared.yemen.crops` is imported if available for extended Yemen variety data.

## Performance

| Operation | Latency | Throughput |
|-----------|---------|-----------|
| Plan calculation | < 50 ms | ~1 000 plans/min (single thread) |
| Nutrient balance | < 20 ms | stateless, horizontally scalable |

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "fertigation-engine", "version": "16.0.0"}
GET /readyz   → {"status": "ok", "crops_with_npk": 8, "fertilizers_available": 11, "nats": true}
```

## Admin Integration Notes

- The admin portal's crop management module should call `POST /api/v1/fertigation/plan` to generate fertigation recommendations after each soil test upload.
- Use `GET /api/v1/fertigation/crops/{crop_name}/npk` to populate the NPK breakdown chart in the field nutrient management view.
- The `GET /api/v1/fertigation/fertilizers` endpoint populates the fertilizer preference selector where farmers can choose locally available products.
- Nutrient balance audits at season end should call `POST /api/v1/fertigation/nutrient-balance` with all applied and removed entries; efficiency scores below 60% should trigger an advisory alert.
- The service integrates with advisory-service, notification-service, and field-intelligence via the `fertigation.plan_created` NATS event.
