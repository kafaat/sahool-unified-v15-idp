# Leveling Optimizer Service

**Type:** Python / FastAPI
**Port:** 8170
**Version:** 16.0.0
**Layer:** Decision (Event Architecture)

## Overview

The Leveling Optimizer Service calculates agricultural field leveling plans from survey elevation data. It computes cut/fill volumes using design plane equations, estimates earthwork and equipment costs in SAR, recommends the optimal equipment mix, and generates bilingual (Arabic/English) leveling summaries. The service supports four leveling methods (single plane, dual plane, contour, bench) and four optimization priorities (minimize cost, minimize earthwork, optimal drainage, irrigation efficiency).

## Architecture

```
FastAPI Application (port 8170)
├── Survey Input Processor (elevation points → grid)
├── Cut/Fill Calculator
│   ├── Design Plane: z = a*x + b*y + c (single/dual plane methods)
│   ├── Volume Calculation (per-cell depth × area × soil factor)
│   └── Balance Optimizer (minimize net volume or user priority)
├── Cost Estimator
│   ├── Equipment cost (hourly rate × hours required)
│   ├── Labor cost (operator rate × hours)
│   ├── Fuel cost (consumption × SAR/L)
│   ├── Surveying cost (SAR/ha)
│   └── Contingency (10%)
└── Equipment Recommender (productivity-based selection)
    ↓
PostgreSQL (plan persistence) + NATS (plan events)
```

## API Endpoints

### Health
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/metrics` | GET | Prometheus metrics |

### Leveling Analysis
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/leveling/analyze` | POST | Full leveling analysis with cost estimate |
| `/api/v1/leveling/simulate` | POST | Simulate a leveling scenario |
| `/api/v1/leveling/compare` | POST | Compare multiple leveling scenarios |
| `/api/v1/leveling/plan/{field_id}` | GET | Retrieve optimal leveling plan for field |
| `/api/v1/leveling/cost/{field_id}` | GET | Retrieve cost estimation for field |
| `/api/v1/leveling/equipment/{field_id}` | GET | Equipment recommendations for field |

### Cut/Fill Calculation
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cutfill/calculate` | POST | Calculate cut/fill volumes from elevation points |
| `/api/v1/cutfill/optimize` | POST | Find optimal design elevation |
| `/api/v1/cutfill/balance` | POST | Calculate cut/fill balance point |

### Cost Estimation
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/cost/estimate` | POST | Detailed cost breakdown |
| `/api/v1/cost/equipment` | GET | Equipment hourly rates |
| `/api/v1/cost/update-rates` | PUT | Update cost rate parameters |

### Equipment
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/equipment/recommend` | POST | Equipment selection for volume and soil type |
| `/api/v1/equipment/list` | GET | All available equipment types |
| `/api/v1/equipment/productivity` | GET | Productivity rates (m³/hour) |

## Leveling Methods

| Method | Arabic | Best Use |
|--------|--------|----------|
| Single Plane | مستوى واحد | Uniform fields, surface irrigation |
| Dual Plane | مستويين | Fields with multiple grade requirements |
| Contour | كنتوري | Sloped terrain, erosion control |
| Bench | مصاطب | Steep slopes, terraced farming |

## Optimization Priorities

| Priority | Arabic | Objective |
|----------|--------|-----------|
| `minimize_cost` | تقليل التكلفة | Lowest total project cost |
| `minimize_earthwork` | تقليل الحفر والردم | Least volume moved |
| `optimal_drainage` | تصريف مثالي | Best drainage grades |
| `irrigation_efficiency` | كفاءة الري | Optimal for surface irrigation |

## Equipment Types and Rates

| Equipment | Arabic | SAR/hour | Productivity (m³/h) |
|-----------|--------|----------|---------------------|
| Bulldozer | جرافة | 350 | 80 |
| Scraper | كاشطة | 400 | 120 |
| Grader | ممهدة | 300 | 60 |
| Laser Leveler | مسوي ليزر | 450 | 40 |
| Excavator | حفارة | 380 | 100 |
| Dump Truck | شاحنة قلابة | 200 | — |

## Soil Types and Factors

| Soil | Arabic | Expansion Factor | Compaction Factor |
|------|--------|------------------|-------------------|
| Sandy | رملية | 1.20 | 0.95 |
| Loamy | طفالية | 1.25 | 0.90 |
| Clay | طينية | 1.35 | 0.85 |
| Silty | طميية | 1.30 | 0.88 |
| Rocky | صخرية | 1.50 | 0.98 |

## Cut/Fill Methodology

1. Design plane: `z = a*x + b*y + c` (a = grade_x/100, b = grade_y/100, c = centroid elevation)
2. Per-point depth: `cut_depth = max(0, original - design)`, `fill_depth = max(0, design - original)`
3. Volume: `depth × cell_area × soil_expansion_factor`
4. Balance optimization: iterate centroid elevation to minimize net volume or satisfy priority
5. Haul distance: centroid-to-centroid between cut and fill zones × haul factor (1.2)

## NATS Events

### Publishes
| Event | Trigger |
|-------|---------|
| `LevelingPlanCreated.v1` | New leveling plan generated |
| `CostEstimateReady.v1` | Cost estimation completed |
| `LevelingSimulationCompleted.v1` | Simulation completed |

### Consumes
| Event | Action |
|-------|--------|
| `SurveyDataUploaded.v1` | Process new survey data |
| `FieldBoundaryUpdated.v1` | Recalculate with new boundary |
| `TerrainAnalysisCompleted.v1` | Use terrain data for leveling input |

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8170` | No | Service port |
| `DATABASE_URL` | — | Yes | PostgreSQL connection |
| `NATS_URL` | — | Yes | NATS server |
| `REDIS_URL` | — | Yes | Redis for caching |
| `JWT_SECRET_KEY` | — | Yes | JWT secret (32+ chars) |
| `BULLDOZER_COST_PER_HOUR` | `350.0` | No | Bulldozer hourly rate (SAR) |
| `SCRAPER_COST_PER_HOUR` | `400.0` | No | Scraper hourly rate (SAR) |
| `LASER_LEVELER_COST_PER_HOUR` | `450.0` | No | Laser leveler rate (SAR) |
| `SOIL_EXPANSION_FACTOR` | `1.25` | No | Default soil expansion |
| `SOIL_COMPACTION_FACTOR` | `0.90` | No | Default soil compaction |
| `FUEL_COST_PER_LITER` | `2.18` | No | Fuel cost (SAR/L) |
| `OPERATOR_COST_PER_HOUR` | `50.0` | No | Operator cost (SAR/h) |
| `SURVEYING_COST_PER_HECTARE` | `500.0` | No | Survey cost (SAR/ha) |
| `MIN_DRAINAGE_GRADE` | `0.1` | No | Minimum drainage grade (%) |
| `MAX_IRRIGATION_GRADE` | `0.5` | No | Maximum irrigation grade (%) |

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "leveling-optimizer-service"}
GET /readyz   → {"status": "ok", "database": true, "nats": true}
GET /metrics  → Prometheus: plans_created_total, cost_estimate_duration_seconds
```

## Admin Integration Notes

- The admin portal's field preparation module should call `POST /api/v1/leveling/analyze` after uploading survey points to generate the leveling plan.
- A minimum of 4 well-distributed elevation points is required; the admin UI should enforce this constraint before submission.
- Use `GET /api/v1/cost/equipment` to populate equipment rate reference tables in the admin configuration panel (allow administrators to update regional rates via `PUT /api/v1/cost/update-rates`).
- The `LevelingPlanCreated.v1` NATS event can trigger automatic notifications to field engineers with cost estimates and duration.
- The scenario comparison endpoint (`POST /api/v1/leveling/compare`) is ideal for the pre-season planning wizard where agronomists evaluate multiple grade options.
