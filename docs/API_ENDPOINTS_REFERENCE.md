# SAHOOL Platform - API Endpoints Reference

**Version**: 16.0.0
**Last Updated**: 2026-01-25
**Total Services**: 57+
**API Gateway**: Kong

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting Tiers](#rate-limiting-tiers)
4. [Service Categories](#service-categories)
5. [Core Services (Starter Package)](#core-services-starter-package)
6. [Intelligence Services (Professional Package)](#intelligence-services-professional-package)
7. [Decision & Advisory Services](#decision--advisory-services)
8. [Business & Integration Services](#business--integration-services)
9. [IoT & Acquisition Services](#iot--acquisition-services)
10. [AI & Agent Services](#ai--agent-services)
11. [Infrastructure Services](#infrastructure-services)

---

## Overview

The SAHOOL platform exposes its microservices through Kong API Gateway. All API endpoints follow RESTful conventions and are accessible via:

```
https://api.sahool.io/api/v1/{service-path}
```

### Base URL Patterns

| Environment | Base URL |
|-------------|----------|
| Production | `https://api.sahool.io` |
| Staging | `https://staging-api.sahool.io` |
| Development | `http://localhost:8000` |

### Common Headers

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
Accept: application/json
X-Request-ID: <correlation_id>
X-Tenant-ID: <tenant_id>
```

---

## Authentication

All endpoints (except health checks) require JWT authentication.

### Authentication Flow

1. Obtain JWT token via `/api/v1/auth/login`
2. Include token in `Authorization: Bearer <token>` header
3. Token expiry: 24 hours (configurable)

### ACL Groups

| Group | Access Level |
|-------|--------------|
| `starter-users` | Basic features |
| `professional-users` | Advanced features |
| `enterprise-users` | All features |
| `internal-services` | Service-to-service |

---

## Rate Limiting Tiers

| Tier | Requests/Minute | Requests/Hour | Services |
|------|-----------------|---------------|----------|
| **Basic (Starter)** | 100 | 5,000 | Field, Weather, Calendar, Notifications |
| **Standard (Professional)** | 500 | 25,000 | Satellite, NDVI, Crop Intelligence |
| **Premium (Enterprise)** | 1,000 | 50,000 | AI Advisor, Research, Advanced Analytics |
| **Internal** | 5,000 | 100,000 | Service-to-service communication |

---

## Service Categories

### Event Architecture Layers

| Layer | Services | Purpose |
|-------|----------|---------|
| **Acquisition** | IoT Gateway, Weather Service, Satellite Service | Data ingestion |
| **Intelligence** | Vegetation Analysis, Crop Intelligence, NDVI Processor | Feature extraction |
| **Decision** | Advisory Service, Irrigation Smart, Yield Engine | Recommendations |
| **Business** | Notification, Marketplace, Billing, Task | User operations |

---

## Core Services (Starter Package)

### Field Management Service

- **Port**: 3000
- **Base Path**: `/api/v1/fields`
- **Technology**: Node.js (NestJS)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/v1/profitability/crop/{crop_season_id}` | Get crop profitability | Yes |
| `POST` | `/v1/profitability/analyze` | Analyze field profitability | Yes |
| `POST` | `/v1/profitability/season` | Calculate season profitability | Yes |
| `GET` | `/v1/profitability/compare` | Compare profitability | Yes |
| `GET` | `/v1/profitability/break-even` | Get break-even analysis | Yes |
| `GET` | `/v1/profitability/history/{field_id}/{crop_code}` | Get profitability history | Yes |
| `GET` | `/v1/profitability/benchmarks/{crop_code}` | Get crop benchmarks | Yes |
| `GET` | `/v1/profitability/cost-breakdown/{crop_code}` | Get cost breakdown | Yes |
| `GET` | `/v1/crops/list` | List available crops | Yes |
| `GET` | `/v1/costs/categories` | Get cost categories | Yes |

---

### Field Service (Legacy)

- **Port**: 8102
- **Base Path**: `/api/v1/fields`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/fields` | Create new field | Yes |
| `GET` | `/fields/{field_id}` | Get field details | Yes |
| `GET` | `/fields` | List all fields | Yes |
| `PATCH` | `/fields/{field_id}` | Update field | Yes |
| `DELETE` | `/fields/{field_id}` | Delete field | Yes |
| `PUT` | `/fields/{field_id}/boundary` | Update field boundary | Yes |
| `GET` | `/fields/{field_id}/area` | Get area calculation | Yes |
| `POST` | `/fields/check-overlap` | Check field overlap | Yes |
| `GET` | `/fields/{field_id}/export/kml` | Export as KML | Yes |
| `GET` | `/fields/{field_id}/export/geojson` | Export as GeoJSON | Yes |
| `POST` | `/fields/{field_id}/crops` | Add crop season | Yes |
| `GET` | `/fields/{field_id}/crops/history` | Get crop history | Yes |
| `POST` | `/fields/{field_id}/crops/current/close` | Close current season | Yes |
| `POST` | `/fields/{field_id}/zones` | Create zone | Yes |
| `GET` | `/fields/{field_id}/zones` | List zones | Yes |
| `DELETE` | `/zones/{zone_id}` | Delete zone | Yes |
| `GET` | `/fields/{field_id}/ndvi/history` | Get NDVI history | Yes |
| `POST` | `/fields/{field_id}/ndvi` | Add NDVI record | Yes |
| `GET` | `/fields/{field_id}/stats` | Get field statistics | Yes |
| `GET` | `/users/{user_id}/fields/stats` | Get user field stats | Yes |

---

### Weather Service

- **Port**: 8092
- **Base Path**: `/api/v1/weather`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/weather/assess` | Assess weather impact | Yes |
| `POST` | `/weather/current` | Get current weather | Yes |
| `POST` | `/weather/forecast` | Get weather forecast | Yes |
| `POST` | `/weather/irrigation` | Irrigation weather check | Yes |
| `GET` | `/weather/heat-stress/{temp_c}` | Check heat stress | Yes |
| `GET` | `/weather/providers` | List weather providers | Yes |
| `POST` | `/weather/evapotranspiration` | Calculate ET | Yes |
| `POST` | `/weather/gdd` | Calculate Growing Degree Days | Yes |
| `POST` | `/weather/spray-window` | Check spray window | Yes |
| `POST` | `/weather/agricultural-report` | Get agricultural report | Yes |
| `POST` | `/weather/frost-risk` | Assess frost risk | Yes |
| `POST` | `/weather/heat-stress` | Assess heat stress | Yes |
| `POST` | `/weather/chill-hours` | Calculate chill hours | Yes |
| `POST` | `/weather/drought-index` | Calculate drought index | Yes |
| `POST` | `/weather/comprehensive-stress-report` | Get comprehensive stress report | Yes |

---

### Notification Service

- **Port**: 8110
- **Base Path**: `/api/v1/notifications`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/` | Create custom notification | Yes |
| `POST` | `/weather` | Create weather alert | Yes |
| `POST` | `/pest` | Create pest alert | Yes |
| `POST` | `/irrigation` | Create irrigation reminder | Yes |
| `GET` | `/farmer/{farmer_id}` | Get farmer notifications | Yes |
| `PATCH` | `/{notification_id}/read` | Mark notification read | Yes |
| `GET` | `/broadcast` | Get broadcast notifications | Yes |
| `POST` | `/register` | Register farmer for notifications | Yes |
| `PUT` | `/{farmer_id}/preferences` | Update preferences | Yes |
| `GET` | `/stats` | Get notification statistics | Yes |

---

### Astronomical Calendar

- **Port**: 8111
- **Base Path**: `/api/v1/astronomical`, `/api/v1/calendar`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/v1/today` | Get today's astronomical data | Yes |
| `GET` | `/v1/date/{date_str}` | Get data for specific date | Yes |
| `GET` | `/v1/week` | Get weekly forecast | Yes |
| `GET` | `/v1/moon-phase` | Get current moon phase | Yes |
| `GET` | `/v1/lunar-mansion` | Get current lunar mansion | Yes |
| `GET` | `/v1/lunar-mansions` | List all lunar mansions | Yes |
| `GET` | `/v1/hijri` | Get Hijri date | Yes |
| `GET` | `/v1/hijri-months` | List Hijri months | Yes |
| `GET` | `/v1/zodiac` | Get zodiac info | Yes |
| `GET` | `/v1/zodiac-farming` | Get zodiac farming guide | Yes |
| `GET` | `/v1/seasons` | List seasons | Yes |
| `GET` | `/v1/current-season` | Get current season | Yes |
| `GET` | `/v1/crop-calendar/{crop_name}` | Get crop calendar | Yes |
| `GET` | `/v1/crops` | List crops | Yes |
| `GET` | `/v1/regions` | List Yemeni regions | Yes |
| `GET` | `/v1/regions/{region_id}` | Get region details | Yes |
| `GET` | `/v1/regions/{region_id}/crops` | Get region crops | Yes |
| `GET` | `/v1/best-days` | Get best days for activities | Yes |
| `GET` | `/v1/integration/weather` | Weather integration | Yes |
| `GET` | `/v1/crop-details` | Get crop details | Yes |
| `GET` | `/v1/crop-details/{crop_id}` | Get specific crop | Yes |
| `GET` | `/v1/crop-details/{crop_id}/planting-guide` | Get planting guide | Yes |
| `GET` | `/v1/what-to-plant` | What to plant now | Yes |
| `GET` | `/v1/proverbs` | List agricultural proverbs | Yes |
| `GET` | `/v1/proverbs/today` | Get today's proverb | Yes |
| `GET` | `/v1/proverbs/crop/{crop_name}` | Get crop proverbs | Yes |
| `GET` | `/v1/proverbs/mansion/{mansion_name}` | Get mansion proverbs | Yes |
| `GET` | `/v1/stars` | List agricultural stars | Yes |
| `GET` | `/v1/stars/{star_name}` | Get star details | Yes |
| `GET` | `/v1/landmarks` | List heritage landmarks | Yes |
| `GET` | `/v1/landmarks/{category}` | Get landmarks by category | Yes |
| `GET` | `/v1/landmarks/{category}/{landmark_name}` | Get specific landmark | Yes |
| `GET` | `/v1/wisdom/today` | Get today's wisdom | Yes |
| `GET` | `/v1/techniques` | List heritage techniques | Yes |
| `GET` | `/v1/techniques/{category}` | Get techniques by category | Yes |
| `GET` | `/v1/techniques/{category}/{technique_id}` | Get specific technique | Yes |

---

### User Service

- **Port**: 3025
- **Base Path**: `/api/v1/users`, `/api/v1/auth`
- **Technology**: Node.js (NestJS)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health/healthz` | Liveness probe | No |
| `GET` | `/health/readyz` | Readiness probe | No |
| `POST` | `/users` | Create user | Yes |
| `GET` | `/users` | List users | Yes |
| `GET` | `/users/{id}` | Get user by ID | Yes |
| `GET` | `/users/email/{email}` | Get user by email | Yes |
| `PUT` | `/users/{id}` | Update user | Yes |
| `DELETE` | `/users/{id}` | Soft delete user | Yes |
| `DELETE` | `/users/{id}/hard` | Hard delete user | Yes |
| `GET` | `/users/stats/count/{tenantId}` | Get user count | Yes |
| `GET` | `/users/stats/active` | Get active users | Yes |
| `POST` | `/auth/login` | User login | No |
| `POST` | `/auth/register` | User registration | No |
| `POST` | `/auth/forgot-password` | Forgot password | No |
| `POST` | `/auth/reset-password` | Reset password | No |
| `POST` | `/auth/send-otp` | Send OTP | No |
| `POST` | `/auth/verify-otp` | Verify OTP | No |
| `POST` | `/auth/logout` | Logout | Yes |
| `POST` | `/auth/logout-all` | Logout all sessions | Yes |
| `POST` | `/auth/refresh` | Refresh token | Yes |
| `POST` | `/auth/me` | Get current user | Yes |

---

## Intelligence Services (Professional Package)

### Vegetation Analysis Service

- **Port**: 8090
- **Base Path**: `/api/v1/satellite`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/v1/providers` | List satellite providers | Yes |
| `GET` | `/v1/cache/stats` | Get cache statistics | Yes |
| `GET` | `/v1/cache/health` | Cache health check | Yes |
| `GET` | `/v1/eo-status` | Earth observation status | Yes |
| `GET` | `/v1/satellites` | List available satellites | Yes |
| `GET` | `/v1/regions` | List coverage regions | Yes |
| `POST` | `/v1/imagery/request` | Request satellite imagery | Yes |
| `POST` | `/v1/analyze` | Analyze field vegetation | Yes |
| `POST` | `/v1/analyze-with-action` | Analyze with action recommendations | Yes |
| `POST` | `/v1/analyze/real` | Real satellite analysis | Yes |
| `GET` | `/v1/timeseries/{field_id}` | Get vegetation timeseries | Yes |
| `POST` | `/v1/ndvi-timeseries/analyze/{field_id}` | Analyze NDVI timeseries | Yes |
| `POST` | `/v1/ndvi-timeseries/compare/{field_id}` | Compare NDVI periods | Yes |
| `GET` | `/v1/phenology/{field_id}` | Get phenology data | Yes |
| `GET` | `/v1/phenology/{field_id}/timeline` | Get phenology timeline | Yes |
| `GET` | `/v1/phenology/recommendations/{crop_type}/{stage}` | Get stage recommendations | Yes |
| `GET` | `/v1/phenology/crops` | List supported crops | Yes |
| `POST` | `/v1/phenology/{field_id}/analyze-with-action` | Phenology analysis with actions | Yes |
| `GET` | `/v1/soil-moisture/{field_id}` | Get soil moisture data | Yes |
| `GET` | `/v1/irrigation-events/{field_id}` | Get irrigation events | Yes |
| `GET` | `/v1/sar-timeseries/{field_id}` | Get SAR timeseries | Yes |
| `GET` | `/v1/indices/{field_id}` | Get vegetation indices | Yes |
| `GET` | `/v1/indices/{field_id}/{index_name}` | Get specific index | Yes |
| `POST` | `/v1/indices/interpret` | Interpret vegetation indices | Yes |
| `GET` | `/v1/indices/guide` | Get indices guide | Yes |
| `POST` | `/v1/yield-prediction` | Predict yield | Yes |
| `GET` | `/v1/yield-history/{field_id}` | Get yield history | Yes |
| `GET` | `/v1/regional-yields/{governorate}` | Get regional yields | Yes |
| `GET` | `/v1/cloud-cover/{field_id}` | Get cloud cover data | Yes |
| `GET` | `/v1/clear-observations/{field_id}` | Get clear observations | Yes |
| `GET` | `/v1/best-observation/{field_id}` | Get best observation | Yes |
| `POST` | `/v1/interpolate-cloudy` | Interpolate cloudy data | Yes |
| `GET` | `/v1/export/analysis/{field_id}` | Export analysis | Yes |
| `GET` | `/v1/export/timeseries/{field_id}` | Export timeseries | Yes |
| `GET` | `/v1/export/boundaries` | Export boundaries | Yes |
| `GET` | `/v1/export/report/{field_id}` | Export report | Yes |
| `GET` | `/v1/changes/{field_id}` | Get change detection | Yes |
| `GET` | `/v1/changes/{field_id}/compare` | Compare changes | Yes |
| `GET` | `/v1/changes/{field_id}/anomalies` | Get anomalies | Yes |

---

### Crop Intelligence Service

- **Port**: 8095
- **Base Path**: `/api/v1/crop-intelligence`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/` | Service info | No |
| `POST` | `/api/v1/fields/{field_id}/zones` | Create zones | Yes |
| `GET` | `/api/v1/fields/{field_id}/zones` | Get zones | Yes |
| `GET` | `/api/v1/fields/{field_id}/zones.geojson` | Get zones as GeoJSON | Yes |
| `POST` | `/api/v1/fields/{field_id}/zones/{zone_id}/observations` | Add zone observation | Yes |
| `GET` | `/api/v1/fields/{field_id}/zones/{zone_id}/observations` | Get zone observations | Yes |
| `GET` | `/api/v1/fields/{field_id}/diagnosis` | Get field diagnosis | Yes |
| `GET` | `/api/v1/fields/{field_id}/zones/{zone_id}/timeline` | Get zone timeline | Yes |
| `GET` | `/api/v1/fields/{field_id}/vrt` | Get Variable Rate Technology map | Yes |
| `POST` | `/api/v1/diagnose` | Diagnose crop issue | Yes |
| `POST` | `/api/v1/disease/detect` | Detect disease | Yes |
| `POST` | `/api/v1/fields/{field_id}/zones/{zone_id}/disease-analysis` | Zone disease analysis | Yes |
| `GET` | `/api/v1/disease/types` | Get disease types | Yes |
| `POST` | `/api/v1/nutrients/detect` | Detect nutrient deficiency | Yes |
| `POST` | `/api/v1/nutrients/fertilizer-plan` | Generate fertilizer plan | Yes |
| `POST` | `/api/v1/fields/{field_id}/zones/{zone_id}/nutrient-analysis` | Zone nutrient analysis | Yes |
| `GET` | `/api/v1/nutrients/types` | Get nutrient types | Yes |
| `POST` | `/api/v1/yield/predict` | Predict yield | Yes |
| `POST` | `/api/v1/fields/{field_id}/zones/{zone_id}/yield-prediction` | Zone yield prediction | Yes |
| `GET` | `/api/v1/yield/crop-parameters` | Get crop parameters | Yes |
| `POST` | `/api/v1/pests/assess` | Assess pest risk | Yes |
| `POST` | `/api/v1/fields/{field_id}/zones/{zone_id}/pest-assessment` | Zone pest assessment | Yes |
| `GET` | `/api/v1/pests/types` | Get pest types | Yes |
| `POST` | `/api/v1/comprehensive-analysis` | Comprehensive field analysis | Yes |

---

### NDVI Processor

- **Port**: 8118
- **Base Path**: `/api/v1/ndvi`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/process` | Submit NDVI processing job | Yes |
| `GET` | `/process/{job_id}/status` | Get job status | Yes |
| `DELETE` | `/process/{job_id}` | Cancel job | Yes |
| `GET` | `/process` | List jobs | Yes |
| `GET` | `/fields/{field_id}/ndvi` | Get field NDVI | Yes |
| `GET` | `/fields/{field_id}/ndvi/latest` | Get latest NDVI | Yes |
| `GET` | `/fields/{field_id}/ndvi/timeseries` | Get NDVI timeseries | Yes |
| `GET` | `/fields/{field_id}/ndvi/change` | Get NDVI change | Yes |
| `POST` | `/fields/{field_id}/ndvi/change` | Submit change analysis | Yes |
| `GET` | `/fields/{field_id}/ndvi/seasonal` | Get seasonal analysis | Yes |
| `GET` | `/fields/{field_id}/ndvi/anomaly` | Detect anomalies | Yes |
| `GET` | `/fields/{field_id}/ndvi/export` | Export NDVI data | Yes |
| `POST` | `/composites/monthly` | Create monthly composite | Yes |
| `GET` | `/fields/{field_id}/composites` | Get composites | Yes |
| `GET` | `/composites/{composite_id}` | Get composite details | Yes |
| `GET` | `/composites/{composite_id}/download` | Download composite | Yes |

---

### Indicators Service

- **Port**: 8091
- **Base Path**: `/api/v1/indicators`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/v1/indicators/definitions` | Get indicator definitions | Yes |
| `GET` | `/v1/field/{field_id}/indicators` | Get field indicators | Yes |
| `GET` | `/v1/dashboard/{tenant_id}` | Get dashboard summary | Yes |
| `GET` | `/v1/alerts/{tenant_id}` | Get tenant alerts | Yes |
| `GET` | `/v1/trends/{field_id}/{indicator_id}` | Get indicator trends | Yes |

---

### LAI Estimation Service

- **Port**: 3022
- **Base Path**: `/api/v1/lai`
- **Technology**: Node.js (NestJS)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/api/v1/lai/estimate/{fieldId}` | Estimate LAI | Yes |
| `POST` | `/api/v1/lai/calculate` | Calculate LAI | Yes |
| `GET` | `/api/v1/lai/timeseries/{fieldId}` | Get LAI timeseries | Yes |
| `GET` | `/api/v1/lai/compare/{fieldId}` | Compare LAI values | Yes |
| `GET` | `/api/v1/lai/model/info` | Get model info | Yes |
| `GET` | `/api/v1/lai/stress-detection/{fieldId}` | Detect crop stress | Yes |
| `GET` | `/api/v1/lai/anomaly-check/{fieldId}` | Check for anomalies | Yes |
| `POST` | `/api/v1/indices/calculate` | Calculate vegetation indices | Yes |
| `POST` | `/api/v1/indices/calculate/{indexName}` | Calculate specific index | Yes |
| `POST` | `/api/v1/indices/health` | Assess vegetation health | Yes |
| `GET` | `/api/v1/indices/info` | Get indices info | Yes |
| `GET` | `/api/v1/indices/info/{indexName}` | Get specific index info | Yes |
| `GET` | `/api/v1/indices/list` | List available indices | Yes |

---

### Field Intelligence

- **Port**: 8120
- **Base Path**: `/api/v1/intelligence`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/` | Service info | No |
| `POST` | `/dev/seed-demo-rules` | Seed demo rules (dev only) | Yes |

---

## Decision & Advisory Services

### Advisory Service

- **Port**: 8093
- **Base Path**: `/api/v1/advisory`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/disease/assess` | Assess disease | Yes |
| `POST` | `/disease/symptoms` | Analyze symptoms | Yes |
| `GET` | `/disease/search` | Search diseases | Yes |
| `GET` | `/disease/crop/{crop}` | Get diseases by crop | Yes |
| `GET` | `/disease/{disease_id}` | Get disease details | Yes |
| `POST` | `/nutrient/ndvi` | NDVI-based nutrient analysis | Yes |
| `POST` | `/nutrient/visual` | Visual nutrient analysis | Yes |
| `GET` | `/nutrient/{deficiency_id}` | Get deficiency details | Yes |
| `POST` | `/fertilizer/plan` | Create fertilizer plan | Yes |
| `GET` | `/fertilizer/{fertilizer_id}` | Get fertilizer details | Yes |
| `GET` | `/fertilizer/nutrient/{nutrient}` | Get fertilizers by nutrient | Yes |
| `GET` | `/crops/categories` | Get crop categories | Yes |
| `GET` | `/crops/search` | Search crops | Yes |
| `GET` | `/crops` | List crops | Yes |
| `GET` | `/crops/{crop_code}` | Get crop details | Yes |
| `GET` | `/crops/{crop_code}/varieties` | Get crop varieties | Yes |
| `GET` | `/crops/{crop}/stages` | Get growth stages | Yes |
| `GET` | `/crops/{crop}/requirements` | Get crop requirements | Yes |
| `GET` | `/actions/{action_id}` | Get action details | Yes |

---

### Irrigation Smart

- **Port**: 8094
- **Base Path**: `/api/v1/irrigation`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/v1/crops` | List supported crops | Yes |
| `GET` | `/v1/methods` | List irrigation methods | Yes |
| `POST` | `/v1/calculate` | Calculate irrigation plan | Yes |
| `GET` | `/v1/water-balance/{field_id}` | Get water balance | Yes |
| `POST` | `/v1/sensor-reading` | Submit sensor reading | Yes |
| `GET` | `/v1/efficiency-report/{field_id}` | Get efficiency report | Yes |
| `POST` | `/v1/calculate-with-action` | Calculate with action plan | Yes |
| `POST` | `/v1/sensor-reading-with-action` | Sensor reading with action | Yes |

---

### Yield Engine

- **Port**: 8098
- **Base Path**: `/api/v1/yield`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `POST` | `/v1/predict` | Predict yield | Yes |
| `GET` | `/v1/crops` | List supported crops | Yes |
| `GET` | `/v1/price/{crop_type}` | Get crop prices | Yes |

---

### Yield Prediction Service

- **Port**: 3021
- **Base Path**: `/api/v1/yield`
- **Technology**: Node.js (NestJS)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/api/v1/yield/predict/{fieldId}` | Predict yield | Yes |
| `GET` | `/api/v1/yield/growth-stage/{fieldId}` | Get growth stage | Yes |
| `GET` | `/api/v1/yield/harvest-date/{fieldId}` | Predict harvest date | Yes |
| `GET` | `/api/v1/yield/regional/{governorate}` | Get regional yields | Yes |
| `GET` | `/api/v1/yield/history/{fieldId}` | Get yield history | Yes |
| `GET` | `/api/v1/yield/maturity/{fieldId}` | Check maturity | Yes |
| `GET` | `/api/v1/yield/predict-with-action/{fieldId}` | Predict with action | Yes |
| `GET` | `/api/v1/yield/harvest-readiness/{fieldId}` | Check harvest readiness | Yes |

---

### Agro Advisor

- **Port**: 8105
- **Base Path**: `/api/v1/agro`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/disease/assess` | Assess disease | Yes |
| `POST` | `/disease/symptoms` | Analyze symptoms | Yes |
| `GET` | `/disease/search` | Search diseases | Yes |
| `GET` | `/disease/crop/{crop}` | Get diseases by crop | Yes |
| `GET` | `/disease/{disease_id}` | Get disease details | Yes |
| `POST` | `/nutrient/ndvi` | NDVI-based nutrient analysis | Yes |
| `POST` | `/nutrient/visual` | Visual nutrient analysis | Yes |
| `GET` | `/nutrient/{deficiency_id}` | Get deficiency details | Yes |
| `POST` | `/fertilizer/plan` | Create fertilizer plan | Yes |
| `GET` | `/fertilizer/{fertilizer_id}` | Get fertilizer details | Yes |
| `GET` | `/fertilizer/nutrient/{nutrient}` | Get fertilizers by nutrient | Yes |
| `GET` | `/crops/categories` | Get crop categories | Yes |
| `GET` | `/crops/search` | Search crops | Yes |
| `GET` | `/crops` | List crops | Yes |
| `GET` | `/crops/{crop_code}` | Get crop details | Yes |
| `GET` | `/crops/{crop_code}/varieties` | Get crop varieties | Yes |
| `GET` | `/crops/{crop}/stages` | Get growth stages | Yes |
| `GET` | `/crops/{crop}/requirements` | Get crop requirements | Yes |
| `GET` | `/actions/{action_id}` | Get action details | Yes |

---

### Fertilizer Advisor (Deprecated)

- **Port**: 8104
- **Base Path**: `/api/v1/fertilizer`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min
- **Status**: Deprecated - Use Advisory Service

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/v1/crops` | List supported crops | Yes |
| `GET` | `/v1/fertilizers` | List fertilizers | Yes |
| `POST` | `/v1/recommend` | Get recommendation | Yes |
| `POST` | `/v1/soil-analysis/interpret` | Interpret soil analysis | Yes |
| `GET` | `/v1/deficiency-symptoms/{crop}` | Get deficiency symptoms | Yes |
| `POST` | `/v1/recommend-with-action` | Recommend with action | Yes |
| `POST` | `/v1/soil-analysis/interpret-with-action` | Interpret with action | Yes |
| `POST` | `/v1/recommend/evaluate` | Evaluate recommendation | Yes |
| `GET` | `/v1/recommendations/recent` | Get recent recommendations | Yes |
| `POST` | `/v1/soil-analysis/compress` | Compress soil data | Yes |
| `GET` | `/v1/context-engineering/status` | Get context status | Yes |

---

## Business & Integration Services

### Task Service

- **Port**: 8103
- **Base Path**: `/api/v1/tasks`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/api/v1/tasks` | List tasks | Yes |
| `GET` | `/api/v1/tasks/today` | Get today's tasks | Yes |
| `GET` | `/api/v1/tasks/upcoming` | Get upcoming tasks | Yes |
| `GET` | `/api/v1/tasks/stats` | Get task statistics | Yes |
| `GET` | `/api/v1/tasks/{task_id}` | Get task details | Yes |
| `POST` | `/api/v1/tasks` | Create task | Yes |
| `PUT` | `/api/v1/tasks/{task_id}` | Update task | Yes |
| `POST` | `/api/v1/tasks/{task_id}/complete` | Complete task | Yes |
| `POST` | `/api/v1/tasks/{task_id}/start` | Start task | Yes |
| `POST` | `/api/v1/tasks/{task_id}/cancel` | Cancel task | Yes |
| `DELETE` | `/api/v1/tasks/{task_id}` | Delete task | Yes |
| `POST` | `/api/v1/tasks/{task_id}/evidence` | Add evidence | Yes |
| `POST` | `/api/v1/tasks/from-ndvi-alert` | Create from NDVI alert | Yes |
| `GET` | `/api/v1/tasks/suggest-for-field/{field_id}` | Suggest tasks | Yes |
| `GET` | `/api/v1/fields/{field_id}/health` | Get field health | Yes |
| `POST` | `/api/v1/tasks/auto-create` | Auto-create tasks | Yes |
| `GET` | `/api/v1/tasks/best-days/{activity}` | Get best days | Yes |
| `POST` | `/api/v1/tasks/create-from-astronomical` | Create from astronomical | Yes |
| `POST` | `/api/v1/tasks/lunar-recommendations` | Get lunar recommendations | Yes |

---

### Equipment Service

- **Port**: 8101
- **Base Path**: `/api/v1/equipment`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/api/v1/equipment` | List equipment | Yes |
| `GET` | `/api/v1/equipment/stats` | Get equipment statistics | Yes |
| `GET` | `/api/v1/equipment/alerts` | Get maintenance alerts | Yes |
| `GET` | `/api/v1/equipment/{equipment_id}` | Get equipment details | Yes |
| `GET` | `/api/v1/equipment/qr/{qr_code}` | Get by QR code | Yes |
| `POST` | `/api/v1/equipment` | Create equipment | Yes |
| `PUT` | `/api/v1/equipment/{equipment_id}` | Update equipment | Yes |
| `POST` | `/api/v1/equipment/{equipment_id}/status` | Update status | Yes |
| `POST` | `/api/v1/equipment/{equipment_id}/location` | Update location | Yes |
| `POST` | `/api/v1/equipment/{equipment_id}/telemetry` | Update telemetry | Yes |
| `GET` | `/api/v1/equipment/{equipment_id}/maintenance` | Get maintenance history | Yes |
| `POST` | `/api/v1/equipment/{equipment_id}/maintenance` | Add maintenance record | Yes |
| `DELETE` | `/api/v1/equipment/{equipment_id}` | Delete equipment | Yes |

---

### Billing Core

- **Port**: 8089
- **Base Path**: `/api/v1/billing`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/v1/plans` | List subscription plans | Yes |
| `GET` | `/v1/plans/{plan_id}` | Get plan details | Yes |
| `POST` | `/v1/plans` | Create plan | Yes |
| `POST` | `/v1/tenants` | Create tenant | Yes |
| `GET` | `/v1/tenants/{tenant_id}` | Get tenant details | Yes |
| `GET` | `/v1/tenants/{tenant_id}/subscription` | Get subscription | Yes |
| `PATCH` | `/v1/tenants/{tenant_id}/subscription` | Update subscription | Yes |
| `POST` | `/v1/tenants/{tenant_id}/cancel` | Cancel subscription | Yes |
| `POST` | `/v1/tenants/{tenant_id}/usage` | Record usage | Yes |
| `GET` | `/v1/tenants/{tenant_id}/quota` | Get quota | Yes |
| `GET` | `/v1/enforce` | Enforce quota | Yes |
| `GET` | `/v1/tenants/{tenant_id}/invoices` | Get invoices | Yes |
| `GET` | `/v1/invoices/{invoice_id}` | Get invoice details | Yes |
| `POST` | `/v1/tenants/{tenant_id}/invoices/generate` | Generate invoice | Yes |
| `POST` | `/v1/payments` | Process payment | Yes |
| `GET` | `/v1/tenants/{tenant_id}/payments` | Get payments | Yes |
| `POST` | `/v1/webhooks/tharwatt` | Tharwatt webhook | No |
| `POST` | `/v1/webhooks/stripe` | Stripe webhook | No |
| `GET` | `/v1/reports/revenue` | Revenue report | Yes |
| `GET` | `/v1/reports/subscriptions` | Subscriptions report | Yes |

---

### Marketplace Service

- **Port**: 3010
- **Base Path**: `/api/v1/market`
- **Technology**: Node.js (NestJS)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/market/products` | List products | Yes |
| `GET` | `/market/products/{id}` | Get product details | Yes |
| `POST` | `/market/products` | Create product | Yes |
| `POST` | `/market/list-harvest` | List harvest for sale | Yes |
| `POST` | `/market/orders` | Create order | Yes |
| `GET` | `/market/orders/{userId}` | Get user orders | Yes |
| `GET` | `/market/stats` | Get marketplace stats | Yes |
| `GET` | `/fintech/wallet/{userId}` | Get wallet | Yes |
| `POST` | `/fintech/wallet/{walletId}/deposit` | Deposit | Yes |
| `POST` | `/fintech/wallet/{walletId}/withdraw` | Withdraw | Yes |
| `GET` | `/fintech/wallet/{walletId}/transactions` | Get transactions | Yes |
| `POST` | `/fintech/calculate-score` | Calculate credit score | Yes |
| `POST` | `/fintech/calculate-advanced-score` | Advanced credit score | Yes |
| `GET` | `/fintech/credit-factors/{userId}` | Get credit factors | Yes |
| `POST` | `/fintech/credit-history` | Add credit history | Yes |
| `GET` | `/fintech/credit-report/{userId}` | Get credit report | Yes |
| `POST` | `/fintech/loans` | Create loan | Yes |
| `PUT` | `/fintech/loans/{id}/approve` | Approve loan | Yes |
| `POST` | `/fintech/loans/{id}/repay` | Repay loan | Yes |
| `GET` | `/fintech/loans/{walletId}` | Get loans | Yes |
| `GET` | `/fintech/stats` | Get fintech stats | Yes |
| `GET` | `/fintech/wallet/{walletId}/limits` | Get wallet limits | Yes |
| `PUT` | `/fintech/wallet/{walletId}/limits` | Set wallet limits | Yes |
| `POST` | `/fintech/escrow` | Create escrow | Yes |
| `POST` | `/fintech/escrow/{id}/release` | Release escrow | Yes |
| `POST` | `/fintech/escrow/{id}/refund` | Refund escrow | Yes |
| `GET` | `/fintech/escrow/order/{orderId}` | Get order escrow | Yes |
| `GET` | `/fintech/wallet/{walletId}/escrows` | Get wallet escrows | Yes |
| `POST` | `/fintech/wallet/{walletId}/scheduled-payment` | Create scheduled payment | Yes |
| `GET` | `/fintech/wallet/{walletId}/scheduled-payments` | Get scheduled payments | Yes |
| `POST` | `/fintech/scheduled-payment/{id}/cancel` | Cancel scheduled payment | Yes |
| `POST` | `/fintech/scheduled-payment/{id}/execute` | Execute scheduled payment | Yes |
| `GET` | `/fintech/wallet/{walletId}/dashboard` | Get wallet dashboard | Yes |
| `POST` | `/profiles/sellers` | Create seller profile | Yes |
| `GET` | `/profiles/sellers` | List seller profiles | Yes |
| `GET` | `/profiles/sellers/user/{userId}` | Get seller by user | Yes |
| `GET` | `/profiles/sellers/{id}` | Get seller profile | Yes |
| `PUT` | `/profiles/sellers/user/{userId}` | Update seller | Yes |
| `PATCH` | `/profiles/sellers/user/{userId}/verify` | Verify seller | Yes |
| `PATCH` | `/profiles/sellers/user/{userId}/stats` | Update seller stats | Yes |
| `POST` | `/profiles/buyers` | Create buyer profile | Yes |
| `GET` | `/profiles/buyers` | List buyer profiles | Yes |
| `GET` | `/profiles/buyers/user/{userId}` | Get buyer by user | Yes |
| `GET` | `/profiles/buyers/{id}` | Get buyer profile | Yes |
| `PUT` | `/profiles/buyers/user/{userId}` | Update buyer | Yes |
| `POST` | `/profiles/buyers/user/{userId}/addresses` | Add address | Yes |
| `DELETE` | `/profiles/buyers/user/{userId}/addresses/{label}` | Remove address | Yes |
| `PATCH` | `/profiles/buyers/user/{userId}/loyalty-points` | Update loyalty points | Yes |
| `PATCH` | `/profiles/buyers/user/{userId}/stats` | Update buyer stats | Yes |
| `POST` | `/reviews` | Create review | Yes |
| `GET` | `/reviews/product/{productId}/stats` | Get product review stats | Yes |
| `GET` | `/reviews/product/{productId}` | Get product reviews | Yes |
| `GET` | `/reviews/{id}` | Get review | Yes |
| `GET` | `/reviews/buyer/{buyerId}` | Get buyer reviews | Yes |
| `PUT` | `/reviews/{id}/buyer/{buyerId}` | Update review | Yes |
| `DELETE` | `/reviews/{id}/buyer/{buyerId}` | Delete review | Yes |
| `PATCH` | `/reviews/{id}/helpful` | Mark helpful | Yes |
| `POST` | `/reviews/{id}/report` | Report review | Yes |
| `POST` | `/reviews/responses` | Create response | Yes |
| `GET` | `/reviews/responses/seller/{sellerId}` | Get seller responses | Yes |
| `PUT` | `/reviews/responses/{id}/seller/{sellerId}` | Update response | Yes |
| `DELETE` | `/reviews/responses/{id}/seller/{sellerId}` | Delete response | Yes |

---

### Alert Service

- **Port**: 8113
- **Base Path**: `/api/v1/alerts`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/alerts` | Create alert | Yes |
| `GET` | `/alerts/{alert_id}` | Get alert details | Yes |
| `GET` | `/alerts/field/{field_id}` | Get field alerts | Yes |
| `PATCH` | `/alerts/{alert_id}` | Update alert | Yes |
| `DELETE` | `/alerts/{alert_id}` | Delete alert | Yes |
| `POST` | `/alerts/batch` | Create batch alerts | Yes |
| `POST` | `/alerts/{alert_id}/resolve` | Resolve alert | Yes |
| `POST` | `/alerts/{alert_id}/dismiss` | Dismiss alert | Yes |
| `POST` | `/alerts/rules` | Create alert rule | Yes |
| `GET` | `/alerts/rules` | List alert rules | Yes |
| `DELETE` | `/alerts/rules/{rule_id}` | Delete rule | Yes |
| `GET` | `/alerts/stats` | Get alert statistics | Yes |

---

### Research Core

- **Port**: 3015
- **Base Path**: `/api/v1/research`
- **Technology**: Node.js (NestJS)
- **Rate Limit**: 1000/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `POST` | `/experiments` | Create experiment | Yes |
| `GET` | `/experiments` | List experiments | Yes |
| `GET` | `/experiments/{id}` | Get experiment | Yes |
| `GET` | `/experiments/{id}/summary` | Get summary | Yes |
| `PUT` | `/experiments/{id}` | Update experiment | Yes |
| `POST` | `/experiments/{id}/lock` | Lock experiment | Yes |
| `DELETE` | `/experiments/{id}` | Delete experiment | Yes |
| `POST` | `/experiments/{experimentId}/treatments` | Create treatment | Yes |
| `GET` | `/experiments/{experimentId}/treatments` | List treatments | Yes |
| `GET` | `/experiments/{experimentId}/treatments/{id}` | Get treatment | Yes |
| `PUT` | `/experiments/{experimentId}/treatments/{id}` | Update treatment | Yes |
| `DELETE` | `/experiments/{experimentId}/treatments/{id}` | Delete treatment | Yes |
| `POST` | `/experiments/{experimentId}/samples` | Create sample | Yes |
| `GET` | `/experiments/{experimentId}/samples` | List samples | Yes |
| `GET` | `/experiments/{experimentId}/samples/code/{sampleCode}` | Get by code | Yes |
| `GET` | `/experiments/{experimentId}/samples/{id}` | Get sample | Yes |
| `PUT` | `/experiments/{experimentId}/samples/{id}` | Update sample | Yes |
| `PUT` | `/experiments/{experimentId}/samples/{id}/analysis` | Update analysis | Yes |
| `DELETE` | `/experiments/{experimentId}/samples/{id}` | Delete sample | Yes |
| `POST` | `/experiments/{experimentId}/protocols` | Create protocol | Yes |
| `GET` | `/experiments/{experimentId}/protocols` | List protocols | Yes |
| `GET` | `/experiments/{experimentId}/protocols/{id}` | Get protocol | Yes |
| `PUT` | `/experiments/{experimentId}/protocols/{id}` | Update protocol | Yes |
| `POST` | `/experiments/{experimentId}/protocols/{id}/approve` | Approve protocol | Yes |
| `DELETE` | `/experiments/{experimentId}/protocols/{id}` | Delete protocol | Yes |
| `POST` | `/experiments/{experimentId}/logs` | Create log | Yes |
| `GET` | `/experiments/{experimentId}/logs` | List logs | Yes |
| `GET` | `/experiments/{experimentId}/logs/{id}` | Get log | Yes |
| `GET` | `/experiments/{experimentId}/logs/{id}/verify` | Verify log | Yes |
| `PUT` | `/experiments/{experimentId}/logs/{id}` | Update log | Yes |
| `DELETE` | `/experiments/{experimentId}/logs/{id}` | Delete log | Yes |
| `POST` | `/experiments/{experimentId}/logs/sync` | Sync logs | Yes |
| `POST` | `/signatures/sign` | Sign document | Yes |
| `POST` | `/signatures/verify` | Verify signature | Yes |
| `GET` | `/signatures/{entityType}/{entityId}/history` | Get signature history | Yes |
| `POST` | `/signatures/{id}/invalidate` | Invalidate signature | Yes |

---

### Disaster Assessment

- **Port**: 3020
- **Base Path**: `/api/v1/disasters`
- **Technology**: Node.js (NestJS)
- **Rate Limit**: 1000/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/v1/disasters` | List disasters | Yes |
| `GET` | `/api/v1/disasters/{id}` | Get disaster | Yes |
| `POST` | `/api/v1/disasters/report` | Report disaster | Yes |
| `POST` | `/api/v1/disasters/assess/{fieldId}` | Assess field | Yes |
| `GET` | `/api/v1/disasters/risk/flood` | Flood risk | Yes |
| `GET` | `/api/v1/disasters/risk/drought` | Drought risk | Yes |
| `GET` | `/api/v1/disasters/stats/summary` | Get stats summary | Yes |
| `GET` | `/api/v1/disasters/health` | Health check | No |
| `GET` | `/api/v1/alerts` | List alerts | Yes |
| `GET` | `/api/v1/alerts/weather` | Weather alerts | Yes |
| `GET` | `/api/v1/alerts/pest-disease` | Pest/disease alerts | Yes |
| `POST` | `/api/v1/alerts/subscribe` | Subscribe to alerts | Yes |
| `POST` | `/api/v1/alerts/{id}/read` | Mark alert read | Yes |

---

### Inventory Service

- **Port**: 8116
- **Base Path**: `/api/v1/inventory`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/v1/categories` | Create category | Yes |
| `GET` | `/v1/analytics/forecast/{item_id}` | Forecast item | Yes |
| `GET` | `/v1/analytics/forecasts` | Get all forecasts | Yes |
| `GET` | `/v1/analytics/reorder-recommendations` | Reorder recommendations | Yes |
| `GET` | `/v1/analytics/valuation` | Get valuation | Yes |
| `GET` | `/v1/analytics/turnover` | Get turnover | Yes |
| `GET` | `/v1/analytics/slow-moving` | Get slow-moving items | Yes |
| `GET` | `/v1/analytics/dead-stock` | Get dead stock | Yes |
| `GET` | `/v1/analytics/abc-analysis` | ABC analysis | Yes |
| `GET` | `/v1/analytics/seasonal-patterns/{item_id}` | Seasonal patterns | Yes |
| `GET` | `/v1/analytics/cost-analysis` | Cost analysis | Yes |
| `GET` | `/v1/analytics/waste-analysis` | Waste analysis | Yes |
| `GET` | `/v1/analytics/dashboard` | Analytics dashboard | Yes |

---

### Logistics Service

- **Port**: 8115
- **Base Path**: `/api/v1/logistics`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/health` | Health check | No |
| `GET` | `/api/v1/vehicles` | List vehicles | Yes |
| `GET` | `/api/v1/vehicles/{vehicle_id}` | Get vehicle | Yes |
| `POST` | `/api/v1/vehicles` | Create vehicle | Yes |
| `PUT` | `/api/v1/vehicles/{vehicle_id}` | Update vehicle | Yes |
| `POST` | `/api/v1/vehicles/{vehicle_id}/location` | Update location | Yes |
| `GET` | `/api/v1/storage-facilities` | List facilities | Yes |
| `GET` | `/api/v1/storage-facilities/{facility_id}` | Get facility | Yes |
| `POST` | `/api/v1/storage-facilities` | Create facility | Yes |
| `POST` | `/api/v1/storage-facilities/{facility_id}/conditions` | Update conditions | Yes |
| `GET` | `/api/v1/collections` | List collections | Yes |
| `POST` | `/api/v1/collections` | Create collection | Yes |
| `POST` | `/api/v1/collections/{collection_id}/assign` | Assign collection | Yes |
| `POST` | `/api/v1/collections/{collection_id}/status` | Update status | Yes |
| `POST` | `/api/v1/routes/optimize` | Optimize routes | Yes |
| `GET` | `/api/v1/shipments` | List shipments | Yes |
| `POST` | `/api/v1/shipments` | Create shipment | Yes |
| `POST` | `/api/v1/shipments/{shipment_id}/status` | Update status | Yes |
| `GET` | `/api/v1/stats` | Get logistics stats | Yes |

---

### CRM Service

- **Port**: 8114
- **Base Path**: `/api/v1/crm`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 100/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/health` | Health check | No |
| `POST` | `/api/v1/farmers` | Create farmer | Yes |
| `GET` | `/api/v1/farmers` | List farmers | Yes |
| `GET` | `/api/v1/farmers/{farmer_id}` | Get farmer | Yes |
| `PATCH` | `/api/v1/farmers/{farmer_id}` | Update farmer | Yes |
| `POST` | `/api/v1/deals` | Create deal | Yes |
| `GET` | `/api/v1/deals` | List deals | Yes |
| `PATCH` | `/api/v1/deals/{deal_id}/stage` | Update deal stage | Yes |
| `GET` | `/api/v1/deals/pipeline` | Get pipeline stats | Yes |
| `POST` | `/api/v1/interactions` | Create interaction | Yes |
| `GET` | `/api/v1/interactions` | List interactions | Yes |
| `POST` | `/api/v1/query` | Query CRM data | Yes |
| `GET` | `/metrics` | Prometheus metrics | No |

---

## IoT & Acquisition Services

### IoT Gateway

- **Port**: 8106
- **Base Path**: `/api/v1/iot`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 1000/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/sensor/reading` | Submit sensor reading | Yes |
| `POST` | `/sensor/batch` | Submit batch readings | Yes |
| `POST` | `/device/register` | Register device | Yes |
| `GET` | `/device/{device_id}` | Get device | Yes |
| `GET` | `/device/{device_id}/status` | Get device status | Yes |
| `GET` | `/devices` | List devices | Yes |
| `DELETE` | `/device/{device_id}` | Delete device | Yes |
| `GET` | `/field/{field_id}/devices` | Get field devices | Yes |
| `GET` | `/field/{field_id}/latest` | Get latest readings | Yes |
| `GET` | `/stats` | Get gateway stats | Yes |

---

### IoT Service

- **Port**: 8117
- **Base Path**: `/api/v1/iot`
- **Technology**: Node.js (NestJS)
- **Rate Limit**: 1000/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/iot/health` | IoT health check | No |
| `GET` | `/iot/field/{fieldId}/sensors` | Get field sensors | Yes |
| `GET` | `/iot/field/{fieldId}/sensor/{sensorType}` | Get sensor by type | Yes |
| `POST` | `/iot/field/{fieldId}/pump` | Control pump | Yes |
| `POST` | `/iot/field/{fieldId}/valve/{valveId}` | Control valve | Yes |
| `POST` | `/iot/field/{fieldId}/irrigation/schedule` | Schedule irrigation | Yes |
| `GET` | `/iot/field/{fieldId}/actuators` | Get actuators | Yes |
| `GET` | `/iot/devices` | List devices | Yes |
| `GET` | `/iot/dashboard/{fieldId}` | Get IoT dashboard | Yes |

---

### Virtual Sensors

- **Port**: 8119
- **Base Path**: `/api/v1/virtual-sensors`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/v1/info` | Service info | Yes |
| `POST` | `/v1/et0/calculate` | Calculate ET0 | Yes |
| `GET` | `/v1/crops` | List supported crops | Yes |
| `GET` | `/v1/crops/{crop_type}/kc` | Get crop coefficient | Yes |
| `POST` | `/v1/etc/calculate` | Calculate crop ETc | Yes |
| `GET` | `/v1/soils` | List soil types | Yes |
| `POST` | `/v1/soil-moisture/estimate` | Estimate soil moisture | Yes |
| `GET` | `/v1/irrigation-methods` | List irrigation methods | Yes |
| `POST` | `/v1/irrigation/recommend` | Get irrigation recommendation | Yes |
| `GET` | `/v1/irrigation/quick-check` | Quick irrigation check | Yes |
| `POST` | `/v1/irrigation/recommend-with-action` | Recommend with action | Yes |
| `GET` | `/v1/quick-check-with-action` | Quick check with action | Yes |

---

## AI & Agent Services

### AI Advisor

- **Port**: 8112
- **Base Path**: `/api/v1/ai-advisor`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 1000/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/v1/advisor/ask` | Ask advisor | Yes |
| `POST` | `/v1/advisor/diagnose` | Diagnose issue | Yes |
| `POST` | `/v1/advisor/recommend` | Get recommendation | Yes |
| `POST` | `/v1/advisor/analyze-field` | Analyze field | Yes |
| `GET` | `/v1/advisor/agents` | List agents | Yes |
| `GET` | `/v1/advisor/tools` | List tools | Yes |
| `GET` | `/v1/advisor/rag/info` | RAG system info | Yes |
| `GET` | `/v1/advisor/memory/context` | Get memory context | Yes |
| `GET` | `/v1/advisor/evaluation/stats` | Evaluation stats | Yes |
| `GET` | `/v1/advisor/context-engineering/status` | Context status | Yes |
| `GET` | `/v1/advisor/cost/usage` | Cost usage | Yes |

---

### AI Agents Service

- **Port**: 8123
- **Base Path**: `/api/v1/agents`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 1000/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/health` | Health check | No |
| `GET` | `/api/v1/agents` | List agents | Yes |
| `POST` | `/api/v1/agents/execute` | Execute agent | Yes |
| `GET` | `/api/v1/agents/executions/{execution_id}` | Get execution | Yes |
| `GET` | `/api/v1/agents/executions/{execution_id}/status` | Get execution status | Yes |
| `DELETE` | `/api/v1/agents/executions/{execution_id}` | Cancel execution | Yes |
| `GET` | `/api/v1/agents/executions` | List executions | Yes |
| `POST` | `/api/v1/agents/quick/analyze` | Quick analysis | Yes |
| `GET` | `/metrics` | Prometheus metrics | No |

---

### AI Agents Core

- **Port**: 8122
- **Base Path**: `/api/v1/ai-core`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 1000/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/api/v1/analyze` | Analyze data | Yes |
| `POST` | `/api/v1/edge/sensor` | Edge sensor processing | Yes |
| `POST` | `/api/v1/edge/mobile` | Edge mobile processing | Yes |
| `POST` | `/api/v1/feedback` | Submit feedback | Yes |
| `GET` | `/api/v1/system/status` | System status | Yes |
| `GET` | `/api/v1/agents/{agent_id}/metrics` | Agent metrics | Yes |

---

### Agent Registry

- **Port**: 8150
- **Base Path**: `/api/v1/registry`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/v1/registry/stats` | Registry statistics | Yes |
| `POST` | `/v1/registry/agents` | Register agent | Yes |
| `GET` | `/v1/registry/agents/{agent_id}` | Get agent | Yes |
| `GET` | `/v1/registry/agents` | List agents | Yes |
| `DELETE` | `/v1/registry/agents/{agent_id}` | Deregister agent | Yes |
| `GET` | `/v1/registry/discover/capability` | Discover by capability | Yes |
| `GET` | `/v1/registry/discover/skill` | Discover by skill | Yes |
| `POST` | `/v1/registry/discover/tags` | Discover by tags | Yes |
| `GET` | `/v1/registry/agents/{agent_id}/health` | Agent health | Yes |
| `GET` | `/v1/registry/health/all` | All agents health | Yes |

---

### Skills Service

- **Port**: 8121
- **Base Path**: `/api/v1/skills`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/compress` | Compress data | Yes |
| `POST` | `/memory/store` | Store memory | Yes |
| `POST` | `/memory/recall` | Recall memory | Yes |
| `POST` | `/evaluate` | Evaluate advisory | Yes |
| `GET` | `/` | Service info | No |

---

### Code Fix Agent

- **Port**: 8124
- **Base Path**: `/api/v1/code-fix`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/health/live` | Liveness (alias) | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/health/ready` | Readiness (alias) | No |
| `GET` | `/health` | Combined health | No |
| `GET` | `/metrics` | Prometheus metrics | No |
| `POST` | `/api/v1/analyze` | Analyze code | Yes |
| `POST` | `/api/v1/fix` | Fix code issues | Yes |
| `POST` | `/api/v1/review` | Review code | Yes |
| `POST` | `/api/v1/generate-tests` | Generate tests | Yes |
| `POST` | `/api/v1/implement` | Implement feature | Yes |
| `POST` | `/api/v1/feedback` | Submit feedback | Yes |
| `GET` | `/api/v1/agent/info` | Agent info | Yes |

---

### Code Review Service

- **Port**: 8096
- **Base Path**: `/api/v1/code-review`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/models` | List models | Yes |
| `POST` | `/review` | Review code | Yes |
| `POST` | `/review/file` | Review file | Yes |
| `POST` | `/review/pr` | Review pull request | Yes |
| `POST` | `/webhook/github` | GitHub webhook | No |
| `GET` | `/cache/stats` | Cache statistics | Yes |
| `POST` | `/cache/clear` | Clear cache | Yes |

---

### Crop Health AI (Deprecated)

- **Port**: 8097
- **Base Path**: `/api/v1/crop-health-ai`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min
- **Status**: Deprecated - Use Crop Intelligence Service

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `POST` | `/v1/diagnose` | Diagnose crop | Yes |
| `POST` | `/v1/diagnose/batch` | Batch diagnose | Yes |
| `GET` | `/v1/diseases` | List diseases | Yes |
| `GET` | `/v1/crops` | List crops | Yes |
| `GET` | `/v1/treatment/{disease_id}` | Get treatment | Yes |
| `POST` | `/v1/expert-review` | Request expert review | Yes |
| `GET` | `/v1/diagnoses` | List diagnoses | Yes |
| `GET` | `/v1/diagnoses/stats` | Diagnosis stats | Yes |
| `GET` | `/v1/diagnoses/{diagnosis_id}` | Get diagnosis | Yes |
| `PATCH` | `/v1/diagnoses/{diagnosis_id}` | Update diagnosis | Yes |
| `GET` | `/v1/field/{field_id}/health` | Field health | Yes |
| `GET` | `/v1/field/{field_id}/disease-patterns` | Disease patterns | Yes |
| `GET` | `/v1/field/{field_id}/risk-assessment` | Risk assessment | Yes |
| `POST` | `/v1/field/{field_id}/diagnosis/{diagnosis_id}/mark-treated` | Mark treated | Yes |
| `GET` | `/v1/field/{field_id}/treatment-effectiveness` | Treatment effectiveness | Yes |
| `GET` | `/v1/fields/summary` | Fields summary | Yes |
| `POST` | `/v1/evaluation/record-outcome/{diagnosis_id}` | Record outcome | Yes |
| `GET` | `/v1/evaluation/accuracy-metrics` | Accuracy metrics | Yes |
| `GET` | `/v1/evaluation/per-disease-metrics` | Per-disease metrics | Yes |
| `GET` | `/v1/evaluation/model-drift` | Model drift | Yes |
| `GET` | `/v1/evaluation/report` | Evaluation report | Yes |
| `GET` | `/v1/evaluation/statistics` | Evaluation statistics | Yes |
| `POST` | `/v1/diagnose-with-action` | Diagnose with action | Yes |

---

## Infrastructure Services

### Crop Growth Model

- **Port**: 3023
- **Base Path**: `/api/v1/crop-model`
- **Technology**: Node.js (NestJS)
- **Rate Limit**: 1000/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/v1/simulation/run` | Run simulation | Yes |
| `GET` | `/api/v1/simulation/demo` | Demo simulation | Yes |
| `POST` | `/api/v1/simulation/quick-estimate` | Quick estimate | Yes |
| `GET` | `/api/v1/simulation/weather/sample` | Sample weather | Yes |
| `GET` | `/api/v1/simulation/info` | Simulation info | Yes |
| `GET` | `/api/v1/simulation/health` | Health check | No |
| `POST` | `/api/v1/phenology/gdd` | Calculate GDD | Yes |
| `POST` | `/api/v1/phenology/dvs` | Calculate DVS | Yes |
| `POST` | `/api/v1/phenology/simulate` | Simulate phenology | Yes |
| `POST` | `/api/v1/phenology/predict` | Predict stage | Yes |
| `GET` | `/api/v1/phenology/parameters/{cropType}` | Crop parameters | Yes |
| `GET` | `/api/v1/phenology/crops` | List crops | Yes |
| `GET` | `/api/v1/phenology/stages/{cropType}` | Get stages | Yes |
| `GET` | `/api/v1/phenology/health` | Health check | No |
| `POST` | `/api/v1/biomass/production` | Biomass production | Yes |
| `POST` | `/api/v1/biomass/distribute` | Biomass distribution | Yes |
| `POST` | `/api/v1/biomass/simulate` | Simulate biomass | Yes |
| `POST` | `/api/v1/biomass/yield` | Calculate yield | Yes |
| `GET` | `/api/v1/biomass/lai/{cropType}` | Get LAI | Yes |
| `GET` | `/api/v1/biomass/partitioning/{cropType}` | Partitioning | Yes |
| `GET` | `/api/v1/biomass/parameters/{cropType}` | Parameters | Yes |
| `GET` | `/api/v1/biomass/crops` | List crops | Yes |
| `GET` | `/api/v1/biomass/health` | Health check | No |
| `POST` | `/api/v1/water/kc` | Calculate Kc | Yes |
| `POST` | `/api/v1/water/etc` | Calculate ETc | Yes |
| `POST` | `/api/v1/water/balance` | Water balance | Yes |
| `POST` | `/api/v1/water/irrigation/schedule` | Irrigation schedule | Yes |
| `GET` | `/api/v1/water/yield-response/{cropType}` | Yield response | Yes |
| `GET` | `/api/v1/water/parameters/{cropType}` | Parameters | Yes |
| `GET` | `/api/v1/water/crops` | List crops | Yes |
| `GET` | `/api/v1/water/health` | Health check | No |
| `POST` | `/api/v1/photosynthesis/gpp` | Calculate GPP | Yes |
| `POST` | `/api/v1/photosynthesis/farquhar` | Farquhar model | Yes |
| `GET` | `/api/v1/photosynthesis/curve/light/{cropType}` | Light response | Yes |
| `GET` | `/api/v1/photosynthesis/curve/co2/{cropType}` | CO2 response | Yes |
| `GET` | `/api/v1/photosynthesis/curve/temperature/{cropType}` | Temp response | Yes |
| `GET` | `/api/v1/photosynthesis/parameters/{cropType}` | Parameters | Yes |
| `GET` | `/api/v1/photosynthesis/crops` | List crops | Yes |
| `GET` | `/api/v1/photosynthesis/health` | Health check | No |
| `POST` | `/api/v1/roots/depth` | Root depth | Yes |
| `GET` | `/api/v1/roots/rld/{cropType}` | Root length density | Yes |
| `POST` | `/api/v1/roots/water-uptake` | Water uptake | Yes |
| `POST` | `/api/v1/roots/nutrient-uptake` | Nutrient uptake | Yes |
| `POST` | `/api/v1/roots/architecture` | Root architecture | Yes |
| `GET` | `/api/v1/roots/parameters/{cropType}` | Parameters | Yes |
| `GET` | `/api/v1/roots/crops` | List crops | Yes |
| `GET` | `/api/v1/roots/health` | Health check | No |
| `POST` | `/api/v1/irrigation-decision/method-selector` | Select method | Yes |
| `POST` | `/api/v1/irrigation-decision/calculate-etc` | Calculate ETc | Yes |
| `POST` | `/api/v1/irrigation-decision/threshold-control` | Threshold control | Yes |
| `POST` | `/api/v1/irrigation-decision/smart-schedule` | Smart schedule | Yes |
| `GET` | `/api/v1/irrigation-decision/compare-methods` | Compare methods | Yes |
| `GET` | `/api/v1/irrigation-decision/quick-recommend` | Quick recommend | Yes |
| `GET` | `/api/v1/irrigation-decision/crops` | List crops | Yes |
| `GET` | `/api/v1/irrigation-decision/crops/{cropType}` | Crop info | Yes |
| `GET` | `/api/v1/irrigation-decision/soils` | List soils | Yes |
| `GET` | `/api/v1/irrigation-decision/soils/{soilType}` | Soil info | Yes |
| `GET` | `/api/v1/irrigation-decision/health` | Health check | No |
| `POST` | `/api/v1/advisor-council/irrigation` | Irrigation advice | Yes |
| `POST` | `/api/v1/advisor-council/pest` | Pest advice | Yes |
| `GET` | `/api/v1/advisor-council/quick` | Quick advice | Yes |
| `GET` | `/api/v1/advisor-council/agents` | List agents | Yes |
| `GET` | `/api/v1/advisor-council/agents/{id}` | Get agent | Yes |
| `GET` | `/api/v1/advisor-council/demo` | Demo | Yes |
| `GET` | `/api/v1/advisor-council/health` | Health check | No |
| `GET` | `/api/v1/digital-twin/architecture` | Architecture | Yes |
| `GET` | `/api/v1/digital-twin/architecture/{id}` | Get arch by ID | Yes |
| `GET` | `/api/v1/digital-twin/edge-nodes` | Edge nodes | Yes |
| `POST` | `/api/v1/digital-twin/data/satellite` | Satellite data | Yes |
| `POST` | `/api/v1/digital-twin/data/drone` | Drone data | Yes |
| `GET` | `/api/v1/digital-twin/data/ground-sensors` | Ground sensors | Yes |
| `POST` | `/api/v1/digital-twin/data/fuse` | Fuse data | Yes |
| `GET` | `/api/v1/digital-twin/models/crops` | Crop models | Yes |
| `GET` | `/api/v1/digital-twin/models/crops/{cropType}` | Crop model | Yes |
| `POST` | `/api/v1/digital-twin/models/wofost` | WOFOST model | Yes |
| `POST` | `/api/v1/digital-twin/models/ml` | ML model | Yes |
| `POST` | `/api/v1/digital-twin/models/deep-learning` | DL model | Yes |
| `POST` | `/api/v1/digital-twin/models/llm` | LLM model | Yes |
| `POST` | `/api/v1/digital-twin/models/hybrid-ensemble` | Hybrid ensemble | Yes |
| `POST` | `/api/v1/digital-twin/assimilate` | Data assimilation | Yes |
| `POST` | `/api/v1/digital-twin/state` | Twin state | Yes |
| `GET` | `/api/v1/digital-twin/demo` | Demo | Yes |
| `GET` | `/api/v1/digital-twin/health` | Health check | No |
| `GET` | `/api/v1/satellite-data/select` | Select satellite | Yes |
| `GET` | `/api/v1/satellite-data/satellites` | List satellites | Yes |
| `GET` | `/api/v1/satellite-data/satellites/free` | Free satellites | Yes |
| `GET` | `/api/v1/satellite-data/satellites/{id}` | Get satellite | Yes |
| `GET` | `/api/v1/satellite-data/satellites/application/{application}` | By application | Yes |
| `POST` | `/api/v1/satellite-data/compare` | Compare satellites | Yes |
| `GET` | `/api/v1/satellite-data/indices` | List indices | Yes |
| `GET` | `/api/v1/satellite-data/indices/{name}` | Get index | Yes |
| `GET` | `/api/v1/satellite-data/recommend/{module}` | Recommend | Yes |
| `GET` | `/api/v1/satellite-data/quick-recommend` | Quick recommend | Yes |
| `GET` | `/api/v1/satellite-data/health` | Health check | No |
| `GET` | `/api/v1/voice-guidance/voices` | List voices | Yes |
| `GET` | `/api/v1/voice-guidance/voices/{id}` | Get voice | Yes |
| `GET` | `/api/v1/voice-guidance/scripts` | List scripts | Yes |
| `GET` | `/api/v1/voice-guidance/scripts/{id}` | Get script | Yes |
| `GET` | `/api/v1/voice-guidance/categories` | Categories | Yes |
| `POST` | `/api/v1/voice-guidance/briefing` | Generate briefing | Yes |
| `POST` | `/api/v1/voice-guidance/podcast` | Generate podcast | Yes |
| `GET` | `/api/v1/voice-guidance/quick-tip` | Quick tip | Yes |
| `GET` | `/api/v1/voice-guidance/wisdom` | Wisdom | Yes |
| `GET` | `/api/v1/voice-guidance/demo/briefing` | Demo briefing | Yes |
| `GET` | `/api/v1/voice-guidance/demo/podcast` | Demo podcast | Yes |
| `GET` | `/api/v1/voice-guidance/health` | Health check | No |
| `GET` | `/api/v1/data-collector/sources` | List sources | Yes |
| `GET` | `/api/v1/data-collector/sources/{id}` | Get source | Yes |
| `POST` | `/api/v1/data-collector/collect` | Collect data | Yes |
| `GET` | `/api/v1/data-collector/market/prices` | Market prices | Yes |
| `GET` | `/api/v1/data-collector/weather/alerts` | Weather alerts | Yes |
| `GET` | `/api/v1/data-collector/news` | News | Yes |
| `GET` | `/api/v1/data-collector/research` | Research | Yes |
| `GET` | `/api/v1/data-collector/intelligence` | Intelligence | Yes |
| `GET` | `/api/v1/data-collector/statistics` | Statistics | Yes |
| `GET` | `/api/v1/data-collector/demo` | Demo | Yes |
| `GET` | `/api/v1/data-collector/health` | Health check | No |
| `GET` | `/gis` | GIS info | Yes |
| `GET` | `/gis/layers` | GIS layers | Yes |
| `GET` | `/gis/layers/catalog` | Layer catalog | Yes |
| `GET` | `/gis/layers/{layerId}` | Get layer | Yes |
| `GET` | `/gis/wms/capabilities` | WMS capabilities | Yes |
| `POST` | `/gis/wms/map` | WMS map | Yes |
| `POST` | `/gis/wms/feature-info` | Feature info | Yes |
| `GET` | `/gis/wfs/capabilities` | WFS capabilities | Yes |
| `POST` | `/gis/wfs/features` | WFS features | Yes |
| `POST` | `/gis/spatial/query` | Spatial query | Yes |
| `POST` | `/gis/spatial/buffer` | Buffer analysis | Yes |
| `POST` | `/gis/fields` | Field geometry | Yes |
| `POST` | `/gis/fields/area` | Calculate area | Yes |
| `POST` | `/gis/fields/centroid` | Calculate centroid | Yes |
| `POST` | `/gis/analysis/zonal-stats` | Zonal statistics | Yes |
| `POST` | `/gis/routing/route` | Route planning | Yes |
| `POST` | `/gis/projects` | Create project | Yes |
| `GET` | `/gis/basemaps` | List basemaps | Yes |
| `POST` | `/gis/utils/validate` | Validate geometry | Yes |
| `POST` | `/gis/utils/transform` | Transform CRS | Yes |
| `GET` | `/gis/demo/fields` | Demo fields | Yes |
| `GET` | `/gis/demo/wms` | Demo WMS | Yes |
| `GET` | `/gis/demo/routing` | Demo routing | Yes |
| `GET` | `/planting-strategy` | Strategy info | Yes |
| `GET` | `/planting-strategy/methods` | List methods | Yes |
| `GET` | `/planting-strategy/methods/{methodId}` | Get method | Yes |
| `GET` | `/planting-strategy/methods/{methodId}/guidance` | Guidance | Yes |
| `POST` | `/planting-strategy/optimize` | Optimize | Yes |
| `POST` | `/planting-strategy/plan` | Create plan | Yes |
| `POST` | `/planting-strategy/density` | Calculate density | Yes |
| `POST` | `/planting-strategy/fertilizer` | Fertilizer plan | Yes |
| `POST` | `/planting-strategy/irrigation` | Irrigation plan | Yes |
| `POST` | `/planting-strategy/compare` | Compare strategies | Yes |
| `POST` | `/planting-strategy/analyze-field` | Analyze field | Yes |
| `POST` | `/planting-strategy/digital-twin` | Digital twin | Yes |
| `GET` | `/planting-strategy/crops/{cropType}` | Crop info | Yes |
| `GET` | `/api/v1/rs-world-model/architecture` | Architecture | Yes |
| `GET` | `/api/v1/rs-world-model/scenarios` | Scenarios | Yes |
| `GET` | `/api/v1/rs-world-model/benchmarks` | Benchmarks | Yes |
| `GET` | `/api/v1/rs-world-model/capabilities` | Capabilities | Yes |
| `POST` | `/api/v1/rs-world-model/reason` | Reasoning | Yes |
| `POST` | `/api/v1/rs-world-model/expand` | Expansion | Yes |
| `POST` | `/api/v1/rs-world-model/partition` | Partitioning | Yes |
| `POST` | `/api/v1/rs-world-model/evaluate` | Evaluation | Yes |
| `GET` | `/api/v1/rs-world-model/demo/reason` | Demo reasoning | Yes |
| `GET` | `/api/v1/rs-world-model/demo/expand` | Demo expansion | Yes |
| `GET` | `/api/v1/rs-world-model/demo/flood` | Demo flood | Yes |
| `GET` | `/api/v1/rs-world-model/health` | Health check | No |

---

### MCP Server

- **Port**: 8200
- **Base Path**: `/api/v1/mcp`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 1000/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/ready` | Readiness | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/metrics` | Prometheus metrics | No |
| `GET` | `/` | Service info | No |
| `POST` | `/mcp` | MCP endpoint | Yes |
| `GET` | `/mcp/sse` | SSE endpoint | Yes |
| `GET` | `/tools` | List tools | Yes |
| `GET` | `/resources` | List resources | Yes |
| `GET` | `/prompts` | List prompts | Yes |

---

### WebSocket Gateway

- **Port**: 8081
- **Base Path**: `/api/v1/ws`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 1000/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/stats` | Connection stats | Yes |
| `POST` | `/broadcast` | Broadcast message | Yes |

---

### Audit Service

- **Port**: 8157
- **Base Path**: `/api/v1/audit`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/api/v1/audit/logs` | List audit logs | Yes |
| `GET` | `/api/v1/audit/logs/{log_id}` | Get audit log | Yes |
| `GET` | `/api/v1/audit/users/{user_id}/trail` | User audit trail | Yes |
| `GET` | `/api/v1/audit/resources/{resource_type}/{resource_id}/trail` | Resource trail | Yes |
| `GET` | `/api/v1/audit/chain/validate` | Validate hash chain | Yes |
| `GET` | `/api/v1/audit/chain/summary` | Chain summary | Yes |
| `GET` | `/api/v1/audit/compliance/report` | Compliance report | Yes |
| `GET` | `/api/v1/audit/stats` | Audit statistics | Yes |
| `GET` | `/api/v1/audit/security-events` | Security events | Yes |
| `GET` | `/api/v1/audit/failed-logins` | Failed logins | Yes |
| `GET` | `/api/v1/audit/export` | Export audit logs | Yes |

---

### GlobalGAP Compliance

- **Port**: 8153
- **Base Path**: `/api/v1/globalgap`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/health/live` | Liveness | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/health/ready` | Readiness | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/farms/{farm_id}/compliance` | Get compliance | Yes |
| `POST` | `/farms/{farm_id}/compliance` | Create compliance | Yes |
| `GET` | `/farms/{farm_id}/compliance/trends` | Compliance trends | Yes |
| `GET` | `/checklists` | List checklists | Yes |
| `GET` | `/checklists/{checklist_id}/items` | Get checklist items | Yes |
| `POST` | `/farms/{farm_id}/assessments` | Create assessment | Yes |
| `GET` | `/farms/{farm_id}/assessments` | List assessments | Yes |
| `POST` | `/audits` | Create audit | Yes |
| `GET` | `/audits/{audit_id}` | Get audit | Yes |
| `GET` | `/farms/{farm_id}/audits` | List farm audits | Yes |
| `GET` | `/farms/{farm_id}/non-conformities` | Get non-conformities | Yes |
| `POST` | `/non-conformities` | Create non-conformity | Yes |
| `GET` | `/farms/{farm_id}/certificates` | Get certificates | Yes |
| `POST` | `/certificates` | Create certificate | Yes |
| `GET` | `/certificates/{certificate_id}` | Get certificate | Yes |

---

### Provider Config

- **Port**: 8152
- **Base Path**: `/api/v1/providers`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/` | Service info | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/providers` | List all providers | Yes |
| `GET` | `/providers/maps` | Map providers | Yes |
| `GET` | `/providers/weather` | Weather providers | Yes |
| `GET` | `/providers/satellite` | Satellite providers | Yes |
| `GET` | `/providers/payment` | Payment providers | Yes |
| `GET` | `/providers/sms` | SMS providers | Yes |
| `GET` | `/providers/notification` | Notification providers | Yes |
| `GET` | `/providers/select/{provider_type}` | Select provider | Yes |
| `GET` | `/providers/failover-chain/{provider_type}` | Failover chain | Yes |
| `POST` | `/providers/check` | Check provider status | Yes |
| `GET` | `/providers/check/all` | Check all providers | Yes |
| `GET` | `/config/{tenant_id}` | Get tenant config | Yes |
| `POST` | `/config/{tenant_id}` | Set tenant config | Yes |
| `DELETE` | `/config/{tenant_id}` | Delete tenant config | Yes |
| `GET` | `/config/{tenant_id}/history` | Config history | Yes |
| `POST` | `/config/{tenant_id}/rollback` | Rollback config | Yes |
| `GET` | `/providers/recommend` | Recommend providers | Yes |

---

### Lowcode Engine

- **Port**: 8125
- **Base Path**: `/api/v1/lowcode`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/health` | Health check | No |
| `GET` | `/api/v1/components` | List components | Yes |
| `GET` | `/api/v1/components/categories` | Component categories | Yes |
| `GET` | `/api/v1/components/{component_name}` | Get component | Yes |
| `POST` | `/api/v1/models` | Create data model | Yes |
| `GET` | `/api/v1/models` | List models | Yes |
| `GET` | `/api/v1/models/{model_id}` | Get model | Yes |
| `POST` | `/api/v1/pages` | Create page | Yes |
| `GET` | `/api/v1/pages` | List pages | Yes |
| `GET` | `/api/v1/pages/{page_id}` | Get page | Yes |
| `POST` | `/api/v1/pages/{page_id}/publish` | Publish page | Yes |
| `GET` | `/api/v1/pages/{page_id}/render` | Render page | Yes |
| `POST` | `/api/v1/ai/suggest` | AI suggestions | Yes |
| `GET` | `/api/v1/ai/templates` | AI templates | Yes |
| `POST` | `/api/v1/ai/generate-page` | Generate page | Yes |
| `GET` | `/metrics` | Prometheus metrics | No |

---

### Chat Service

- **Port**: 8127
- **Base Path**: `/api/v1/chat`
- **Technology**: Node.js (NestJS)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check | No |
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/livez` | Liveness | No |
| `GET` | `/chat/health` | Chat health | No |
| `POST` | `/chat/conversations` | Create conversation | Yes |
| `GET` | `/chat/conversations/me` | My conversations | Yes |
| `GET` | `/chat/conversations/{id}` | Get conversation | Yes |
| `GET` | `/chat/conversations/{id}/messages` | Get messages | Yes |
| `POST` | `/chat/messages` | Send message | Yes |
| `POST` | `/chat/messages/{messageId}/read` | Mark read | Yes |
| `POST` | `/chat/conversations/{id}/read` | Mark all read | Yes |
| `GET` | `/chat/unread-count` | Unread count | Yes |

---

### USSD Gateway

- **Port**: 8126
- **Base Path**: `/api/v1/ussd`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/health/live` | Liveness | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/health/ready` | Readiness | No |
| `POST` | `/ussd/callback` | USSD callback | No |
| `POST` | `/ussd/simulate` | Simulate USSD | Yes |
| `POST` | `/sms/send` | Send SMS | Yes |
| `POST` | `/sms/receive` | Receive SMS | No |
| `POST` | `/sms/bulk` | Bulk SMS | Yes |
| `POST` | `/whatsapp/webhook` | WhatsApp webhook | No |
| `POST` | `/whatsapp/send` | Send WhatsApp | Yes |

---

### WeChat Service

- **Port**: 8128
- **Base Path**: `/api/v1/wechat`
- **Technology**: Python (FastAPI)
- **Rate Limit**: 500/min

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/healthz` | Liveness probe | No |
| `GET` | `/readyz` | Readiness probe | No |
| `GET` | `/health` | Health check | No |
| `POST` | `/api/v1/messages/fetch` | Fetch messages | Yes |
| `POST` | `/api/v1/messages/send` | Send message | Yes |
| `POST` | `/api/v1/contacts/add` | Add contact | Yes |
| `POST` | `/api/v1/moments/publish` | Publish moment | Yes |
| `POST` | `/api/v1/chat/summarize` | Summarize chat | Yes |
| `POST` | `/api/v1/chat/insights` | Chat insights | Yes |
| `GET` | `/metrics` | Prometheus metrics | No |

---

## Deprecated Services

The following services are deprecated and should be migrated to their replacements:

| Service | Replacement | Deprecation Date |
|---------|-------------|------------------|
| `satellite-service` | `vegetation-analysis-service` | 2026-01-11 |
| `weather-advanced` | `weather-service` | 2026-01-11 |
| `crop-health-ai` | `crop-intelligence-service` | 2026-01-11 |
| `fertilizer-advisor` | `advisory-service` | 2026-01-11 |
| `field-ops` | `field-management-service` | Legacy |
| `field-core` | `field-management-service` | Legacy |
| `field-service` | `field-management-service` | Legacy |

---

## Health Check Endpoints

All services expose standard health check endpoints:

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/healthz` | Kubernetes liveness probe | `{"status": "ok"}` |
| `/readyz` | Kubernetes readiness probe | `{"status": "ok", "database": true, "nats": true}` |
| `/health` | Combined health status | Full health report |
| `/metrics` | Prometheus metrics | Prometheus format |

---

## Error Responses

All endpoints return standardized error responses:

```json
{
  "status_code": 400,
  "message": "Validation error",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "description of the error"
  },
  "request_id": "uuid",
  "timestamp": "2026-01-25T12:00:00Z"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Related Documentation

- [API Gateway Configuration](./API_GATEWAY.md)
- [Authentication](./AUTHENTICATION.md)
- [Rate Limiting](./RATE_LIMITING.md)
- [Error Handling](./ERROR_HANDLING.md)
- [Service Registry](../governance/services.yaml)

---

_Generated: 2026-01-25_
