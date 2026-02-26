# Digital Twin Engine

**Type:** Python / FastAPI
**Port:** 8253
**Version:** 16.0.0
**Layer:** Decision (Event Architecture)

## Overview

The Digital Twin Engine provides advanced agricultural field simulation and multi-objective optimization. It models the dynamic state of a field over time using Kalman filtering (Extended and Unscented variants) for sensor fusion with >92% accuracy. Farmers and agronomists can compare multiple management scenarios (irrigation schedules, fertilizer plans), run Genetic Algorithm or Particle Swarm Optimization to find optimal practices, and update the digital twin with live sensor data. The engine includes Yemen-specific crop varieties, salinity-aware modeling, and bilingual outputs (Arabic/English).

## Architecture

```
FastAPI Application (port 8253)
├── Simulation Engine
│   ├── WOFOST-compatible crop growth model interface
│   ├── Soil water balance (daily timestep)
│   └── Daily output: growth stage, biomass, LAI, soil moisture, yield
├── Scenario Comparison Module
│   ├── Parallel simulation of up to N management scenarios
│   └── Ranking by water efficiency, yield, cost, sustainability
├── Multi-Objective Optimizer
│   ├── Genetic Algorithm (GA) — population 50, generations 100
│   ├── Particle Swarm Optimization (PSO)
│   ├── Weighted Sum Scalarization
│   └── Pareto Front Analysis
├── Kalman Filter State Estimator
│   ├── Extended Kalman Filter (EKF)
│   └── Unscented Kalman Filter (UKF)
└── Yemen Data Module
    ├── Crop varieties (wheat Sakha-95, date palm cultivars, sorghum)
    ├── Climate zone data
    └── Salinity tolerance profiles
```

## API Endpoints

### Health
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/health` | GET | Combined health with DB and NATS status |

### Digital Twin Operations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/digital-twin/info` | GET | Service capabilities and supported crops |
| `/api/v1/digital-twin/simulate` | POST | Run field state simulation (up to 365 days) |
| `/api/v1/digital-twin/scenarios` | POST | Compare multiple management scenarios |
| `/api/v1/digital-twin/optimize` | POST | Multi-objective optimization |
| `/api/v1/digital-twin/state/update` | POST | Update state with sensor measurements via Kalman filter |

### Yemen-Specific Data
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/digital-twin/yemen/crops` | GET | Yemen crop varieties with parameters |

## Simulation Features

### State Variables Tracked
| Variable | Unit |
|----------|------|
| Soil moisture | % |
| Soil temperature | °C |
| Soil salinity (EC) | dS/m |
| Available nitrogen | ppm |
| Available phosphorus | ppm |
| Plant height | cm |
| Leaf Area Index (LAI) | — |
| Biomass | kg/ha |
| Water stress index | 0–1 |

### Optimization Objectives
| Objective | Description |
|-----------|-------------|
| `MINIMIZE_WATER` | Reduce total irrigation volume |
| `MAXIMIZE_YIELD` | Maximize predicted crop yield |
| `MINIMIZE_COST` | Reduce total operational costs (SAR/ha) |
| `MINIMIZE_ENVIRONMENTAL_IMPACT` | Minimize leaching and runoff |
| `BALANCED` | Weighted combination of all objectives |

## Supported Crops

wheat, barley, date_palm, sorghum, millet, tomato, cucumber (plus Yemen-specific varieties: Sakha 95/94, Giza 168 wheat; Al-Burhi, Al-Fardous, Al-Zuheydi date palm; local sorghum).

## Performance

| Operation | Typical Time |
|-----------|-------------|
| 120-day simulation | 45–60 s |
| Kalman state update | 150–250 ms |
| Multi-objective optimization (GA, 100 gen) | 120–180 s |
| 5-scenario comparison | 250–350 s |

## NATS Events

The Digital Twin Engine publishes events when simulations and optimizations complete. Consumed events trigger automatic re-simulation when new sensor data or field configuration changes arrive.

Relevant subjects (published): `sahool.{tenant_id}.twin.simulation_completed`, `sahool.{tenant_id}.twin.optimization_completed`

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8253` | No | Service port |
| `DATABASE_URL` | — | Yes | PostgreSQL connection |
| `REDIS_URL` | — | No | Redis for result caching |
| `NATS_URL` | — | No | NATS server |
| `JWT_SECRET_KEY` | — | Yes | JWT secret (32+ chars) |
| `MAX_SIMULATION_DAYS` | `365` | No | Maximum simulation horizon |
| `DEFAULT_SIMULATION_TIMESTEP` | `1` | No | Timestep in days |
| `KALMAN_FILTER_TYPE` | `extended_kalman_filter` | No | EKF or UKF |
| `STATE_ESTIMATION_ACCURACY_TARGET` | `0.92` | No | Target Kalman accuracy |
| `OPTIMIZATION_DEFAULT_ALGORITHM` | `genetic_algorithm` | No | GA or PSO |
| `GENETIC_ALGORITHM_POPULATION_SIZE` | `50` | No | GA population size |
| `GENETIC_ALGORITHM_GENERATIONS` | `100` | No | GA generation count |
| `GENETIC_ALGORITHM_MUTATION_RATE` | `0.15` | No | GA mutation rate |
| `PROMETHEUS_METRICS_ENABLED` | `true` | No | Enable metrics endpoint |
| `TENANT_ID` | `sahool_default` | No | Default tenant identifier |

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "digital-twin-engine", "version": "16.0.0"}
GET /readyz   → {"status": "ok", "database": true, "nats": true}
GET /health   → Extended status with optimization engine readiness
```

## Admin Integration Notes

- The admin portal's scenario planning module should call `POST /api/v1/digital-twin/scenarios` to let agronomists compare 2–5 irrigation/fertilizer strategies before the season.
- The Kalman state update endpoint (`POST /api/v1/digital-twin/state/update`) should be called automatically when new soil sensor readings arrive from the IoT Sensor Hub.
- Optimization results include a Pareto front array that can be visualized as a trade-off chart (water vs. yield vs. cost) in the admin dashboard.
- Yemen-specific crop data is available via `GET /api/v1/digital-twin/yemen/crops` and should be used to pre-populate crop selection dropdowns in the admin UI.
- For long-running optimizations (120–180 s), implement async polling or WebSocket progress updates in the admin portal.
