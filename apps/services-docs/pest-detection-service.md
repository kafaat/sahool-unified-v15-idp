# Pest Detection Service

**Type:** Python / FastAPI
**Port:** 8125
**Version:** 1.0.0
**Layer:** Intelligence (Event Architecture)

## Overview

The Pest Detection Service provides AI-powered pest and crop disease identification with a Middle East-focused pest database of 100+ species. It supports image-based and symptom-based identification, GPS-tagged field scouting report management, economic and action threshold monitoring, yield loss estimation, and bilingual (Arabic/English) treatment recommendations following Integrated Pest Management (IPM) principles. The service uses the shared `pest_scouting` module for core identification and assessment logic.

## Architecture

```
FastAPI Application (port 8125)
├── Pest Identification Module
│   ├── Image-based AI identification (shared.pest_scouting.PestIdentification)
│   ├── Symptom-based diagnosis
│   └── Bilingual pest database (100+ Middle East species)
├── Scouting Management Module
│   ├── Scout report CRUD with GPS tagging
│   └── Infestation level tracking and history
├── Threshold & Alert Engine
│   ├── Economic threshold monitoring
│   ├── Action threshold alerts
│   └── Yield loss estimation + treatment ROI
└── Treatment Recommendation Module
    ├── Chemical control (PHI/REI compliance)
    ├── Biological control alternatives
    ├── Cultural practices
    └── IPM calendar integration
    ↓
PostgreSQL (report persistence) + Redis (caching) + NATS (events)
```

The service delegates core pest identification logic to `shared/pest_scouting/`:
```python
from shared.pest_scouting import (
    PestIdentification, ScoutReport,
    get_pest_by_id, assess_threshold,
    generate_treatment_recommendation,
)
```

## Key Pest Species Covered

| Pest | Arabic | Priority |
|------|--------|----------|
| Red Palm Weevil | سوسة النخيل الحمراء | Critical (quarantine) |
| Dubas Bug | دوباس النخيل | High (date palm) |
| Desert Locust | الجراد الصحراوي | Critical (quarantine) |
| Aphids | المن | Moderate |
| Whiteflies | الذبابة البيضاء | Moderate |
| Spider Mites | العنكبوت الأحمر | Moderate |
| Date Moth | فراشة التمر | High (date palm) |
| Tuta absoluta | حافرة أنفاق الطماطم | High (tomato) |
| Thrips | التربس | Moderate |
| Fruit Flies | ذباب الفاكهة | Moderate |

## API Endpoints

### Health
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/health` | GET | Comprehensive health with dependency status |
| `/metrics` | GET | Prometheus metrics |

### Pest Identification
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/pests` | GET | List all pests in database |
| `/api/v1/pests/{pest_id}` | GET | Detailed pest information |
| `/api/v1/pests/search` | GET | Search pests by name (Arabic or English) |
| `/api/v1/pests/crop/{crop}` | GET | All pests associated with a specific crop |
| `/api/v1/pests/identify` | POST | Identify pest from uploaded image |
| `/api/v1/pests/identify/symptoms` | POST | Identify by symptom description |
| `/api/v1/pests/quarantine` | GET | List quarantine / notifiable pest species |
| `/api/v1/pests/seasonal` | GET | Seasonal pest risk predictions by month |

### Scout Reports
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/scouts/reports` | GET | List scouting reports |
| `/api/v1/scouts/reports` | POST | Create new scouting report |
| `/api/v1/scouts/reports/{report_id}` | GET | Get report details |
| `/api/v1/scouts/reports/{report_id}` | PUT | Update report |
| `/api/v1/scouts/reports/field/{field_id}` | GET | All reports for a field |
| `/api/v1/scouts/observations` | POST | Add observation to a report |

### Thresholds and Alerts
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/thresholds` | GET | List economic thresholds |
| `/api/v1/thresholds/crop/{crop}/pest/{pest}` | GET | Threshold for a crop-pest pair |
| `/api/v1/thresholds/assess` | POST | Assess current infestation against threshold |
| `/api/v1/alerts` | GET | List active pest alerts |
| `/api/v1/alerts/{alert_id}` | GET | Get alert details |
| `/api/v1/alerts/{alert_id}/acknowledge` | POST | Acknowledge an alert |

### Treatment Recommendations
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/treatments/recommend` | POST | Get IPM treatment recommendations |
| `/api/v1/treatments/protocols/{pest_id}` | GET | Full treatment protocol for a pest |
| `/api/v1/treatments/ipm-calendar` | GET | IPM calendar for a crop/season |
| `/api/v1/treatments/rotation` | GET | Pesticide rotation plan (resistance management) |

## NATS Events

### Publishes
| Event | Trigger |
|-------|---------|
| `PestDetected.v1` | Pest identified in field observation |
| `InfestationAlert.v1` | Infestation level exceeds economic threshold |
| `TreatmentRecommended.v1` | Treatment recommendation generated |
| `OutbreakTracked.v1` | Pest outbreak recorded and geo-tagged |

### Consumes
| Event | Action |
|-------|--------|
| `FieldIndicatorsComputed.v1` | Use field health data for pest risk assessment |
| `WeatherForecastReady.v1` | Update weather-based pest risk models |
| `SatelliteSceneIngested.v1` | Use satellite imagery for pest detection |
| `TaskCompleted.v1` | Track treatment application completion |

## Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `PORT` | `8125` | No | Service port (README shows 8171; governance/services.yaml shows 8125) |
| `HOST` | `0.0.0.0` | No | Bind address |
| `ENVIRONMENT` | `development` | No | Deployment environment |
| `DATABASE_URL` | — | Yes | PostgreSQL connection string |
| `REDIS_URL` | — | Yes | Redis connection string |
| `NATS_URL` | — | Yes | NATS server URL |
| `AI_MODEL_PATH` | — | No | Path to pest detection AI model weights |
| `LOG_LEVEL` | `INFO` | No | Logging level |

Note: The service README lists port 8171 in its configuration examples, but `governance/services.yaml` and the CLAUDE.md service registry record port 8125 as the canonical port. Use 8125 for all routing and service discovery configuration.

## IPM Approach

Treatment recommendations follow a four-tier IPM hierarchy:
1. **Cultural practices** — crop rotation, sanitation, resistant varieties
2. **Biological controls** — beneficial insects, parasitoids, biopesticides
3. **Chemical controls** — selective pesticides respecting PHI (pre-harvest interval) and REI (re-entry interval)
4. **Emergency response** — quarantine pest protocols (RPW, locust)

## Health Endpoints

```
GET /healthz  → {"status": "ok", "service": "pest-detection-service"}
GET /readyz   → {"status": "ok", "database": true, "redis": true, "nats": true}
GET /health   → Extended health with pest database size and model status
GET /metrics  → Prometheus: pests_identified_total, alerts_generated_total, threshold_breaches_total
```

## Kubernetes Deployment

Resource requests: 300m CPU / 512 Mi memory. Limits: 800m CPU / 1 Gi memory. Replicas: 2 for high availability.

## Admin Integration Notes

- The admin portal's pest monitoring dashboard should call `GET /api/v1/alerts` filtered by severity to display active pest alerts across all farms.
- The scouting report module (`POST /api/v1/scouts/reports`) should be linked to the mobile app's field scouting feature, with GPS coordinates auto-populated from device location.
- Seasonal pest predictions (`GET /api/v1/pests/seasonal`) should be surfaced in the advisory calendar to proactively notify farmers of upcoming risk periods.
- Quarantine pest identifications (RPW, locust) publish `InfestationAlert.v1` events with critical severity; these must trigger immediate notifications via the notification service and appear as banners in the admin dashboard.
- The IPM calendar (`GET /api/v1/treatments/ipm-calendar`) integrates with the crop calendar module to schedule preventive treatments at optimal growth stage windows.
- Pesticide rotation plans (`GET /api/v1/treatments/rotation`) should be available in the admin input management section to help agronomists prevent resistance development.
