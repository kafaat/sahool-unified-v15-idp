# SAHOOL Legacy Service Migration Guide

This document provides comprehensive migration guidance for all deprecated services in the SAHOOL platform. Follow these instructions to migrate your applications from legacy services to their modern replacements.

---

## Table of Contents

1. [Overview](#overview)
2. [Migration Timeline](#migration-timeline)
3. [Service Migrations](#service-migrations)
   - [satellite-service to vegetation-analysis-service](#1-satellite-service--vegetation-analysis-service)
   - [weather-advanced to weather-service](#2-weather-advanced--weather-service)
   - [crop-health-ai to crop-intelligence-service](#3-crop-health-ai--crop-intelligence-service)
   - [fertilizer-advisor to advisory-service](#4-fertilizer-advisor--advisory-service)
   - [field-ops to field-management-service](#5-field-ops--field-management-service)
   - [field-core to field-management-service](#6-field-core--field-management-service)
   - [field-service to field-management-service](#7-field-service--field-management-service)
4. [Data Migration Steps](#data-migration-steps)
5. [Testing Migration](#testing-migration)
6. [Rollback Procedures](#rollback-procedures)
7. [Support and Resources](#support-and-resources)

---

## Overview

As part of SAHOOL's continuous improvement and service consolidation efforts, several legacy services have been deprecated and replaced with modern, more capable alternatives. This guide provides:

- Detailed API endpoint mappings
- Code migration examples
- Data migration procedures
- Breaking changes documentation
- Timeline and sunset dates

### Deprecation Headers

All deprecated services return the following HTTP headers to help identify deprecation status:

```http
X-API-Deprecated: true
X-API-Deprecation-Date: YYYY-MM-DD
X-API-Deprecation-Info: This service is deprecated. Use [new-service] instead.
X-API-Sunset: YYYY-MM-DD
Link: <http://[new-service]:[port]>; rel="successor-version"
Deprecation: true
```

---

## Migration Timeline

| Deprecated Service   | Replaced By                   | Deprecation Date | Sunset Date  | Status       |
|----------------------|-------------------------------|------------------|--------------|--------------|
| `satellite-service`  | `vegetation-analysis-service` | 2026-01-11       | 2026-07-01   | Deprecated   |
| `weather-advanced`   | `weather-service`             | 2025-01-01       | 2025-06-01   | Deprecated   |
| `crop-health-ai`     | `crop-intelligence-service`   | 2025-01-01       | 2025-06-01   | Deprecated   |
| `fertilizer-advisor` | `advisory-service`            | 2026-01-11       | 2026-07-01   | Deprecated   |
| `field-ops`          | `field-management-service`    | 2024-06-01       | 2025-01-01   | Legacy       |
| `field-core`         | `field-management-service`    | 2024-06-01       | 2025-01-01   | Legacy       |
| `field-service`      | `field-management-service`    | 2024-06-01       | 2025-01-01   | Legacy       |

**Important**: Services will be removed after their sunset date. Plan migrations accordingly.

---

## Service Migrations

### 1. satellite-service -> vegetation-analysis-service

#### Overview

The `satellite-service` provided basic satellite imagery analysis. The new `vegetation-analysis-service` offers enhanced capabilities including multi-source imagery processing, advanced vegetation indices, and improved accuracy.

#### Old Service Details

- **Port**: 8100
- **Base URL**: `http://satellite-service:8100`
- **Technology**: Python/FastAPI

**Old Endpoints**:
```
GET  /healthz
GET  /readyz
GET  /v1/imagery/{field_id}
POST /v1/analyze
GET  /v1/ndvi/{field_id}
GET  /v1/timeseries/{field_id}
```

#### New Service Details

- **Port**: 8090
- **Base URL**: `http://vegetation-analysis-service:8090`
- **Technology**: Python/FastAPI
- **Version**: 16.0.0

**New Endpoints**:
```
GET  /healthz
GET  /readyz
POST /v1/vegetation/analyze
GET  /v1/vegetation/indices/{field_id}
POST /v1/vegetation/timeseries
GET  /v1/vegetation/ndvi/{field_id}
POST /v1/vegetation/multi-index
```

#### API Mapping

| Old Endpoint                    | New Endpoint                           | Notes                    |
|---------------------------------|----------------------------------------|--------------------------|
| `GET /v1/imagery/{field_id}`    | `GET /v1/vegetation/indices/{field_id}`| Enhanced response format |
| `POST /v1/analyze`              | `POST /v1/vegetation/analyze`          | Additional parameters    |
| `GET /v1/ndvi/{field_id}`       | `GET /v1/vegetation/ndvi/{field_id}`   | Same interface           |
| `GET /v1/timeseries/{field_id}` | `POST /v1/vegetation/timeseries`       | Changed to POST          |

#### Code Migration Example

**Before (satellite-service)**:
```python
import httpx

async def get_ndvi_data(field_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://satellite-service:8100/v1/ndvi/{field_id}"
        )
        return response.json()

async def analyze_imagery(field_id: str, lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://satellite-service:8100/v1/analyze",
            json={
                "field_id": field_id,
                "latitude": lat,
                "longitude": lon
            }
        )
        return response.json()
```

**After (vegetation-analysis-service)**:
```python
import httpx

async def get_ndvi_data(field_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://vegetation-analysis-service:8090/v1/vegetation/ndvi/{field_id}"
        )
        return response.json()

async def analyze_imagery(field_id: str, lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://vegetation-analysis-service:8090/v1/vegetation/analyze",
            json={
                "field_id": field_id,
                "location": {"lat": lat, "lon": lon},
                "indices": ["ndvi", "evi", "ndwi", "ndre", "lci", "savi"]  # New: specify indices
            }
        )
        return response.json()
```

#### Breaking Changes

1. **Response Structure**: The new service returns more detailed index data
2. **Timeseries Endpoint**: Changed from GET to POST to support additional parameters
3. **Authentication**: New service requires `X-Tenant-Id` header

---

### 2. weather-advanced -> weather-service

#### Overview

The `weather-advanced` service provided 7-day forecasting with Open-Meteo and OpenWeatherMap integration. The new `weather-service` (Weather Core) offers multi-provider support, advanced agricultural metrics, and comprehensive stress assessments.

#### Old Service Details

- **Port**: 8092
- **Base URL**: `http://weather-advanced:8092`
- **Technology**: Python/FastAPI
- **Version**: 15.4.0

**Old Endpoints**:
```
GET  /healthz
GET  /readyz
GET  /v1/locations
GET  /v1/current/{location_id}
GET  /v1/forecast/{location_id}
GET  /v1/alerts/{location_id}
GET  /v1/agricultural-calendar/{location_id}
```

**Old Data Models**:
```python
class CurrentWeather(BaseModel):
    location_id: str
    location_name_ar: str
    latitude: float
    longitude: float
    timestamp: datetime
    temperature_c: float
    feels_like_c: float
    humidity_percent: float
    pressure_hpa: float
    wind_speed_kmh: float
    wind_direction: str
    wind_gust_kmh: float
    visibility_km: float
    cloud_cover_percent: float
    uv_index: float
    dew_point_c: float
    condition: WeatherCondition
    condition_ar: str
```

#### New Service Details

- **Port**: 8108
- **Base URL**: `http://weather-service:8108`
- **Technology**: Python/FastAPI
- **Version**: 16.0.0

**New Endpoints**:
```
GET  /healthz
GET  /readyz
POST /weather/assess
POST /weather/current
POST /weather/forecast
POST /weather/irrigation
GET  /weather/heat-stress/{temp_c}
GET  /weather/providers
POST /weather/evapotranspiration
POST /weather/gdd
POST /weather/spray-window
POST /weather/agricultural-report
POST /weather/frost-risk
POST /weather/heat-stress
POST /weather/chill-hours
POST /weather/drought-index
POST /weather/comprehensive-stress-report
```

**New Data Models**:
```python
class LocationRequest(BaseModel):
    tenant_id: str
    field_id: str
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    correlation_id: str | None = None
```

#### API Mapping

| Old Endpoint                            | New Endpoint                               | Notes                              |
|-----------------------------------------|--------------------------------------------|------------------------------------|
| `GET /v1/current/{location_id}`         | `POST /weather/current`                    | Changed to POST with body          |
| `GET /v1/forecast/{location_id}`        | `POST /weather/forecast`                   | Changed to POST with body          |
| `GET /v1/alerts/{location_id}`          | `POST /weather/assess`                     | Integrated into assessment         |
| `GET /v1/agricultural-calendar/{loc}`   | `POST /weather/agricultural-report`        | Enhanced with more metrics         |
| N/A                                     | `POST /weather/evapotranspiration`         | New endpoint                       |
| N/A                                     | `POST /weather/frost-risk`                 | New endpoint                       |
| N/A                                     | `POST /weather/comprehensive-stress-report`| New endpoint                       |

#### Code Migration Example

**Before (weather-advanced)**:
```python
import httpx

async def get_current_weather(location_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://weather-advanced:8092/v1/current/{location_id}"
        )
        return response.json()

async def get_forecast(location_id: str, days: int = 7):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://weather-advanced:8092/v1/forecast/{location_id}",
            params={"days": days}
        )
        return response.json()
```

**After (weather-service)**:
```python
import httpx

async def get_current_weather(tenant_id: str, field_id: str, lat: float, lon: float):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://weather-service:8108/weather/current",
            json={
                "tenant_id": tenant_id,
                "field_id": field_id,
                "lat": lat,
                "lon": lon
            }
        )
        return response.json()

async def get_forecast(tenant_id: str, field_id: str, lat: float, lon: float, days: int = 7):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://weather-service:8108/weather/forecast?days={days}",
            json={
                "tenant_id": tenant_id,
                "field_id": field_id,
                "lat": lat,
                "lon": lon
            }
        )
        return response.json()
```

#### Breaking Changes

1. **HTTP Methods**: Most endpoints changed from GET to POST
2. **Required Fields**: `tenant_id` and `field_id` are now required
3. **Location Format**: Changed from `location_id` to explicit `lat`/`lon` coordinates
4. **Response Structure**: Enhanced with provider information and more detailed metrics

---

### 3. crop-health-ai -> crop-intelligence-service

#### Overview

The `crop-health-ai` service (Sahool Vision) provided AI-powered plant disease diagnosis from images. The new `crop-intelligence-service` offers comprehensive crop intelligence including disease detection, nutrient deficiency analysis, yield prediction, and pest risk assessment.

#### Old Service Details

- **Port**: 8095
- **Base URL**: `http://crop-health-ai:8095`
- **Technology**: Python/FastAPI
- **Version**: 2.2.0

**Old Endpoints**:
```
GET  /healthz
GET  /readyz
POST /v1/diagnose
POST /v1/diagnose/batch
GET  /v1/diseases
GET  /v1/crops
GET  /v1/treatment/{disease_id}
POST /v1/expert-review
GET  /v1/diagnoses
GET  /v1/diagnoses/stats
GET  /v1/diagnoses/{diagnosis_id}
PATCH /v1/diagnoses/{diagnosis_id}
GET  /v1/field/{field_id}/health
GET  /v1/field/{field_id}/disease-patterns
GET  /v1/field/{field_id}/risk-assessment
POST /v1/diagnose-with-action
```

**Old Data Models**:
```python
class DiagnosisResult(BaseModel):
    diagnosis_id: str
    disease_id: str
    disease_name: str
    disease_name_ar: str
    confidence: float
    severity: str
    affected_area_percent: float
    treatment_ar: str
    treatment_en: str
```

#### New Service Details

- **Port**: 8095
- **Base URL**: `http://crop-intelligence-service:8095`
- **Technology**: Python/FastAPI
- **Version**: 16.0.0

**New Endpoints**:
```
GET  /healthz
GET  /readyz
POST /api/v1/fields/{field_id}/zones/{zone_id}/observations
GET  /api/v1/fields/{field_id}/zones/{zone_id}/observations
GET  /api/v1/fields/{field_id}/diagnosis
GET  /api/v1/fields/{field_id}/zones/{zone_id}/timeline
GET  /api/v1/fields/{field_id}/vrt
POST /api/v1/diagnose
POST /api/v1/disease/detect
POST /api/v1/fields/{field_id}/zones/{zone_id}/disease-analysis
GET  /api/v1/disease/types
POST /api/v1/nutrients/detect
POST /api/v1/nutrients/fertilizer-plan
POST /api/v1/fields/{field_id}/zones/{zone_id}/nutrient-analysis
GET  /api/v1/nutrients/types
POST /api/v1/yield/predict
POST /api/v1/fields/{field_id}/zones/{zone_id}/yield-prediction
GET  /api/v1/yield/crop-parameters
POST /api/v1/pests/assess
POST /api/v1/fields/{field_id}/zones/{zone_id}/pest-assessment
GET  /api/v1/pests/types
POST /api/v1/comprehensive-analysis
```

**New Data Models**:
```python
class DiseaseDetectionRequest(BaseModel):
    ndvi: float = Field(..., ge=-1, le=1)
    evi: float = Field(..., ge=-1, le=1)
    ndre: float = Field(..., ge=-1, le=1)
    ndwi: float = Field(..., ge=-1, le=1)
    lci: float = Field(..., ge=-1, le=1)
    savi: float = Field(..., ge=-1, le=1)
    crop_type: CropType = Field(default=CropType.UNKNOWN)
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    temp_c: float | None = Field(default=None, ge=-50, le=60)
```

#### API Mapping

| Old Endpoint                     | New Endpoint                                            | Notes                              |
|----------------------------------|--------------------------------------------------------|------------------------------------|
| `POST /v1/diagnose`              | `POST /api/v1/disease/detect`                          | Index-based detection              |
| `POST /v1/diagnose/batch`        | N/A                                                    | Use individual calls               |
| `GET /v1/diseases`               | `GET /api/v1/disease/types`                            | Different format                   |
| `GET /v1/treatment/{disease_id}` | Embedded in detection response                         | Included in recommendations        |
| `GET /v1/field/{id}/health`      | `GET /api/v1/fields/{id}/diagnosis`                    | Enhanced with zones                |
| N/A                              | `POST /api/v1/comprehensive-analysis`                  | New: all-in-one analysis           |
| N/A                              | `POST /api/v1/nutrients/detect`                        | New: nutrient deficiency           |
| N/A                              | `POST /api/v1/yield/predict`                           | New: yield prediction              |
| N/A                              | `POST /api/v1/pests/assess`                            | New: pest risk assessment          |

#### Code Migration Example

**Before (crop-health-ai)**:
```python
import httpx

async def diagnose_disease(image_file: bytes, field_id: str, crop_type: str):
    async with httpx.AsyncClient() as client:
        files = {"image": ("plant.jpg", image_file, "image/jpeg")}
        params = {"field_id": field_id, "crop_type": crop_type}
        response = await client.post(
            "http://crop-health-ai:8095/v1/diagnose",
            files=files,
            params=params
        )
        return response.json()
```

**After (crop-intelligence-service)**:
```python
import httpx

async def detect_disease(
    ndvi: float, evi: float, ndre: float, ndwi: float,
    lci: float, savi: float, crop_type: str = "wheat"
):
    """Detect diseases from vegetation indices"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://crop-intelligence-service:8095/api/v1/disease/detect",
            json={
                "ndvi": ndvi,
                "evi": evi,
                "ndre": ndre,
                "ndwi": ndwi,
                "lci": lci,
                "savi": savi,
                "crop_type": crop_type,
                "humidity_pct": 60.0,
                "temp_c": 25.0
            }
        )
        return response.json()

async def comprehensive_analysis(
    field_id: str, ndvi: float, evi: float, ndre: float,
    ndwi: float, lci: float, savi: float, crop_type: str = "wheat",
    temp_c: float = 25.0, humidity_pct: float = 50.0
):
    """Get comprehensive field analysis including diseases, nutrients, yield, and pests"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://crop-intelligence-service:8095/api/v1/comprehensive-analysis",
            params={
                "ndvi": ndvi,
                "evi": evi,
                "ndre": ndre,
                "ndwi": ndwi,
                "lci": lci,
                "savi": savi,
                "crop_type": crop_type,
                "temp_c": temp_c,
                "humidity_pct": humidity_pct,
                "field_area_hectares": 1.0
            }
        )
        return response.json()
```

#### Breaking Changes

1. **Detection Method**: Changed from image-based to vegetation index-based detection
2. **Zone-Based Architecture**: New service uses field/zone hierarchy
3. **Expanded Capabilities**: Includes nutrient, yield, and pest analysis
4. **API Prefix**: Changed from `/v1/` to `/api/v1/`

---

### 4. fertilizer-advisor -> advisory-service

#### Overview

The `fertilizer-advisor` service provided NPK recommendations and soil analysis. The new `advisory-service` (Agro Advisor) offers comprehensive agricultural advisory including disease diagnosis, nutrient assessment, and complete fertilizer planning.

#### Old Service Details

- **Port**: 8093
- **Base URL**: `http://fertilizer-advisor:8093`
- **Technology**: Python/FastAPI
- **Version**: 15.3.0

**Old Endpoints**:
```
GET  /healthz
GET  /readyz
GET  /v1/crops
GET  /v1/fertilizers
POST /v1/recommend
POST /v1/soil-analysis/interpret
GET  /v1/deficiency-symptoms/{crop}
POST /v1/recommend-with-action
POST /v1/soil-analysis/interpret-with-action
POST /v1/recommend/evaluate
GET  /v1/recommendations/recent
POST /v1/soil-analysis/compress
GET  /v1/context-engineering/status
```

**Old Data Models**:
```python
class FertilizerRequest(BaseModel):
    field_id: str
    crop: CropType
    growth_stage: GrowthStage
    area_hectares: float = Field(..., gt=0)
    soil_type: SoilType = SoilType.LOAMY
    target_yield_kg_ha: float | None = None
    budget_yer: float | None = None
    organic_only: bool = False
    soil_analysis: SoilAnalysis | None = None

class FertilizationPlan(BaseModel):
    plan_id: str
    field_id: str
    crop: CropType
    crop_name_ar: str
    growth_stage: GrowthStage
    growth_stage_ar: str
    area_hectares: float
    soil_analysis: SoilAnalysis | None
    target_yield_kg_ha: float
    recommendations: list[FertilizerRecommendation]
    total_nitrogen_kg: float
    total_phosphorus_kg: float
    total_potassium_kg: float
    total_cost_yer: float
    schedule: list[dict]
    warnings_ar: list[str]
    warnings_en: list[str]
    created_at: datetime
```

#### New Service Details

- **Port**: 8095
- **Base URL**: `http://advisory-service:8095`
- **Technology**: Python/FastAPI
- **Version**: 15.3.3

**New Endpoints**:
```
GET  /healthz
GET  /readyz
POST /disease/assess
POST /disease/symptoms
GET  /disease/search
GET  /disease/crop/{crop}
GET  /disease/{disease_id}
POST /nutrient/ndvi
POST /nutrient/visual
GET  /nutrient/{deficiency_id}
POST /fertilizer/plan
GET  /fertilizer/{fertilizer_id}
GET  /fertilizer/nutrient/{nutrient}
GET  /crops/categories
GET  /crops/search
GET  /crops
GET  /crops/{crop_code}
GET  /crops/{crop_code}/varieties
GET  /crops/{crop}/stages
GET  /crops/{crop}/requirements
GET  /actions/{action_id}
```

**New Data Models**:
```python
class FertilizerPlanRequest(BaseModel):
    tenant_id: str
    field_id: str
    crop: str
    stage: str
    field_size_ha: float = 1.0
    soil_fertility: str = "medium"
    irrigation_type: str = "drip"
    correlation_id: str | None = None
```

#### API Mapping

| Old Endpoint                       | New Endpoint                    | Notes                        |
|------------------------------------|---------------------------------|------------------------------|
| `GET /v1/crops`                    | `GET /crops`                    | Enhanced with categories     |
| `GET /v1/fertilizers`              | `GET /fertilizer/{fertilizer_id}`| Per-fertilizer lookup       |
| `POST /v1/recommend`               | `POST /fertilizer/plan`         | Simplified request model     |
| `POST /v1/soil-analysis/interpret` | `POST /nutrient/visual`         | Different approach           |
| `GET /v1/deficiency-symptoms/{crop}`| `GET /nutrient/{deficiency_id}` | ID-based lookup             |
| N/A                                | `POST /disease/assess`          | New: disease advisory        |
| N/A                                | `GET /crops/{code}/varieties`   | New: Yemen varieties         |

#### Code Migration Example

**Before (fertilizer-advisor)**:
```python
import httpx
from datetime import datetime

async def get_fertilizer_recommendation(
    field_id: str, crop: str, growth_stage: str, area_ha: float
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://fertilizer-advisor:8093/v1/recommend",
            json={
                "field_id": field_id,
                "crop": crop,
                "growth_stage": growth_stage,
                "area_hectares": area_ha,
                "soil_type": "loamy",
                "organic_only": False
            }
        )
        return response.json()
```

**After (advisory-service)**:
```python
import httpx

async def get_fertilizer_plan(
    tenant_id: str, field_id: str, crop: str, stage: str, field_size_ha: float
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://advisory-service:8095/fertilizer/plan",
            json={
                "tenant_id": tenant_id,
                "field_id": field_id,
                "crop": crop,
                "stage": stage,
                "field_size_ha": field_size_ha,
                "soil_fertility": "medium",
                "irrigation_type": "drip"
            }
        )
        return response.json()
```

#### Breaking Changes

1. **Tenant Requirement**: `tenant_id` is now required
2. **Simplified Request**: Removed soil analysis from direct request
3. **Response Structure**: Different format for fertilizer recommendations
4. **Expanded Scope**: Service now includes disease and crop advisory

---

### 5. field-ops -> field-management-service

#### Overview

The `field-ops` service provided basic field management and operations tracking. It has been consolidated into `field-management-service` with enhanced capabilities.

#### Old Service Details

- **Port**: 8080
- **Base URL**: `http://field-ops:8080`
- **Technology**: Python/FastAPI
- **Version**: 15.3.3

**Old Endpoints**:
```
GET  /healthz
GET  /readyz
POST /fields
GET  /fields/{field_id}
GET  /fields
PUT  /fields/{field_id}
DELETE /fields/{field_id}
POST /operations
GET  /operations/{operation_id}
GET  /operations
POST /operations/{operation_id}/complete
GET  /stats/tenant/{tenant_id}
```

**Old Data Models**:
```python
class FieldCreate(BaseModel):
    tenant_id: str
    name: str
    name_ar: str | None = None
    area_hectares: float = Field(gt=0)
    crop_type: str | None = None
    geometry: dict | None = None
    metadata: dict | None = None

class OperationCreate(BaseModel):
    tenant_id: str
    field_id: str
    operation_type: str  # planting, irrigation, fertilizing, harvesting
    scheduled_date: str | None = None
    notes: str | None = None
    metadata: dict | None = None
```

#### New Service Details

- **Port**: 3000
- **Base URL**: `http://field-management-service:3000`
- **Technology**: Node.js/NestJS with Prisma
- **Version**: 16.0.0

**New Endpoints**:
```
GET  /healthz
GET  /readyz
POST /api/v1/fields
GET  /api/v1/fields/{field_id}
GET  /api/v1/fields
PATCH /api/v1/fields/{field_id}
DELETE /api/v1/fields/{field_id}
POST /api/v1/fields/{field_id}/operations
GET  /api/v1/fields/{field_id}/operations
PATCH /api/v1/operations/{operation_id}
GET  /api/v1/stats/tenant
```

#### API Mapping

| Old Endpoint                        | New Endpoint                              | Notes                    |
|-------------------------------------|-------------------------------------------|--------------------------|
| `POST /fields`                      | `POST /api/v1/fields`                     | Enhanced model           |
| `GET /fields/{field_id}`            | `GET /api/v1/fields/{field_id}`           | Same                     |
| `GET /fields`                       | `GET /api/v1/fields`                      | Same                     |
| `PUT /fields/{field_id}`            | `PATCH /api/v1/fields/{field_id}`         | Changed to PATCH         |
| `DELETE /fields/{field_id}`         | `DELETE /api/v1/fields/{field_id}`        | Same                     |
| `POST /operations`                  | `POST /api/v1/fields/{field_id}/operations`| Nested under field       |
| `GET /operations`                   | `GET /api/v1/fields/{field_id}/operations` | Nested under field       |
| `POST /operations/{id}/complete`    | `PATCH /api/v1/operations/{id}`           | Generic update           |
| `GET /stats/tenant/{tenant_id}`     | `GET /api/v1/stats/tenant`                | Tenant from header       |

#### Code Migration Example

**Before (field-ops)**:
```python
import httpx

async def create_field(tenant_id: str, name: str, area_ha: float):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://field-ops:8080/fields",
            json={
                "tenant_id": tenant_id,
                "name": name,
                "area_hectares": area_ha
            }
        )
        return response.json()

async def create_operation(tenant_id: str, field_id: str, op_type: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://field-ops:8080/operations",
            json={
                "tenant_id": tenant_id,
                "field_id": field_id,
                "operation_type": op_type
            }
        )
        return response.json()
```

**After (field-management-service)**:
```typescript
// TypeScript/JavaScript example
import axios from 'axios';

async function createField(tenantId: string, name: string, areaHa: number) {
    const response = await axios.post(
        'http://field-management-service:3000/api/v1/fields',
        {
            name: name,
            areaHectares: areaHa
        },
        {
            headers: {
                'X-Tenant-Id': tenantId,
                'Content-Type': 'application/json'
            }
        }
    );
    return response.data;
}

async function createOperation(tenantId: string, fieldId: string, opType: string) {
    const response = await axios.post(
        `http://field-management-service:3000/api/v1/fields/${fieldId}/operations`,
        {
            operationType: opType
        },
        {
            headers: {
                'X-Tenant-Id': tenantId,
                'Content-Type': 'application/json'
            }
        }
    );
    return response.data;
}
```

#### Breaking Changes

1. **Port Change**: 8080 -> 3000
2. **Technology Change**: Python/FastAPI -> Node.js/NestJS
3. **API Prefix**: Added `/api/v1/` prefix
4. **Tenant Header**: Tenant ID moved to `X-Tenant-Id` header
5. **Nested Operations**: Operations are now nested under fields

---

### 6. field-core -> field-management-service

#### Overview

The `field-core` service provided crop profitability analysis. This functionality has been consolidated into `field-management-service` with enhanced financial insights.

#### Old Service Details

- **Port**: 8090
- **Base URL**: `http://field-core:8090`
- **Technology**: Python/FastAPI
- **Version**: 15.3.3

**Old Endpoints**:
```
GET  /healthz
GET  /readyz
GET  /v1/profitability/crop/{crop_season_id}
POST /v1/profitability/analyze
POST /v1/profitability/season
GET  /v1/profitability/compare
GET  /v1/profitability/break-even
GET  /v1/profitability/history/{field_id}/{crop_code}
GET  /v1/profitability/benchmarks/{crop_code}
GET  /v1/profitability/cost-breakdown/{crop_code}
GET  /v1/crops/list
GET  /v1/costs/categories
```

#### New Service Details

- **Port**: 3000
- **Base URL**: `http://field-management-service:3000`
- **Technology**: Node.js/NestJS with Prisma
- **Version**: 16.0.0

**New Endpoints**:
```
GET  /api/v1/analytics/profitability/{cropSeasonId}
POST /api/v1/analytics/profitability/analyze
POST /api/v1/analytics/profitability/season
GET  /api/v1/analytics/profitability/compare
GET  /api/v1/analytics/profitability/break-even
GET  /api/v1/analytics/profitability/history/{fieldId}/{cropCode}
GET  /api/v1/analytics/benchmarks/{cropCode}
GET  /api/v1/analytics/cost-breakdown/{cropCode}
GET  /api/v1/crops
GET  /api/v1/costs/categories
```

#### API Mapping

| Old Endpoint                                      | New Endpoint                                           |
|---------------------------------------------------|--------------------------------------------------------|
| `GET /v1/profitability/crop/{id}`                 | `GET /api/v1/analytics/profitability/{id}`             |
| `POST /v1/profitability/analyze`                  | `POST /api/v1/analytics/profitability/analyze`         |
| `POST /v1/profitability/season`                   | `POST /api/v1/analytics/profitability/season`          |
| `GET /v1/profitability/compare`                   | `GET /api/v1/analytics/profitability/compare`          |
| `GET /v1/profitability/break-even`                | `GET /api/v1/analytics/profitability/break-even`       |
| `GET /v1/profitability/history/{fid}/{crop}`      | `GET /api/v1/analytics/profitability/history/{fid}/{c}`|
| `GET /v1/profitability/benchmarks/{crop}`         | `GET /api/v1/analytics/benchmarks/{crop}`              |
| `GET /v1/profitability/cost-breakdown/{crop}`     | `GET /api/v1/analytics/cost-breakdown/{crop}`          |
| `GET /v1/crops/list`                              | `GET /api/v1/crops`                                    |
| `GET /v1/costs/categories`                        | `GET /api/v1/costs/categories`                         |

#### Breaking Changes

1. **Port Change**: 8090 -> 3000
2. **API Prefix**: Changed from `/v1/` to `/api/v1/`
3. **Path Structure**: `/profitability/` moved under `/analytics/`
4. **Tenant Header**: Required `X-Tenant-Id` header

---

### 7. field-service -> field-management-service

#### Overview

The `field-service` provided comprehensive field and boundary management with geospatial features. It has been consolidated into `field-management-service`.

#### Old Service Details

- **Port**: 8115 (originally 3000)
- **Base URL**: `http://field-service:8115`
- **Technology**: Python/FastAPI
- **Version**: 16.0.0

**Old Endpoints**:
```
GET  /health
GET  /healthz
GET  /readyz
POST /fields
GET  /fields/{field_id}
GET  /fields
PATCH /fields/{field_id}
DELETE /fields/{field_id}
PUT  /fields/{field_id}/boundary
GET  /fields/{field_id}/area
POST /fields/check-overlap
GET  /fields/{field_id}/export/kml
GET  /fields/{field_id}/export/geojson
POST /fields/{field_id}/crops
GET  /fields/{field_id}/crops/history
POST /fields/{field_id}/crops/current/close
POST /fields/{field_id}/zones
GET  /fields/{field_id}/zones
DELETE /zones/{zone_id}
GET  /fields/{field_id}/ndvi/history
POST /fields/{field_id}/ndvi
GET  /fields/{field_id}/stats
GET  /users/{user_id}/fields/stats
```

**Old Data Models**:
```python
class FieldCreate(BaseModel):
    tenant_id: str
    user_id: str
    name: str
    name_en: str | None = None
    location: GeoPoint
    boundary: PolygonBoundary | None = None
    area_hectares: float = Field(gt=0)
    soil_type: SoilType | None = None
    irrigation_source: IrrigationSource | None = None
    current_crop: str | None = None
    metadata: dict | None = None
```

#### New Service Details

- **Port**: 3000
- **Base URL**: `http://field-management-service:3000`
- **Technology**: Node.js/NestJS with Prisma
- **Version**: 16.0.0

**New Endpoints**:
```
GET  /healthz
GET  /readyz
POST /api/v1/fields
GET  /api/v1/fields/{fieldId}
GET  /api/v1/fields
PATCH /api/v1/fields/{fieldId}
DELETE /api/v1/fields/{fieldId}
PUT  /api/v1/fields/{fieldId}/boundary
GET  /api/v1/fields/{fieldId}/area
POST /api/v1/fields/check-overlap
GET  /api/v1/fields/{fieldId}/export/kml
GET  /api/v1/fields/{fieldId}/export/geojson
POST /api/v1/fields/{fieldId}/seasons
GET  /api/v1/fields/{fieldId}/seasons
POST /api/v1/fields/{fieldId}/seasons/current/close
POST /api/v1/fields/{fieldId}/zones
GET  /api/v1/fields/{fieldId}/zones
DELETE /api/v1/zones/{zoneId}
GET  /api/v1/fields/{fieldId}/ndvi/history
POST /api/v1/fields/{fieldId}/ndvi
GET  /api/v1/fields/{fieldId}/stats
GET  /api/v1/users/{userId}/fields/stats
```

#### API Mapping

| Old Endpoint                             | New Endpoint                                 | Notes                   |
|------------------------------------------|----------------------------------------------|-------------------------|
| `POST /fields`                           | `POST /api/v1/fields`                        | Added prefix            |
| `GET /fields/{field_id}`                 | `GET /api/v1/fields/{fieldId}`               | camelCase params        |
| `PUT /fields/{id}/boundary`              | `PUT /api/v1/fields/{id}/boundary`           | Same                    |
| `GET /fields/{id}/export/kml`            | `GET /api/v1/fields/{id}/export/kml`         | Same                    |
| `POST /fields/{id}/crops`                | `POST /api/v1/fields/{id}/seasons`           | Renamed to seasons      |
| `GET /fields/{id}/crops/history`         | `GET /api/v1/fields/{id}/seasons`            | Same endpoint           |
| `POST /fields/{id}/crops/current/close`  | `POST /api/v1/fields/{id}/seasons/current/close` | Same                |
| `POST /fields/{id}/zones`                | `POST /api/v1/fields/{id}/zones`             | Same                    |
| `DELETE /zones/{zone_id}`                | `DELETE /api/v1/zones/{zoneId}`              | camelCase params        |

#### Breaking Changes

1. **Port Change**: 8115 -> 3000
2. **API Prefix**: Added `/api/v1/` prefix
3. **Parameter Naming**: Changed from snake_case to camelCase
4. **Crop Seasons**: Renamed from `/crops` to `/seasons`
5. **Tenant Header**: Required `X-Tenant-Id` header

---

## Data Migration Steps

### General Migration Process

1. **Backup Existing Data**
   ```bash
   # Export data from old service
   pg_dump -h old-db-host -d sahool -t old_service_tables > backup.sql
   ```

2. **Transform Data**
   - Map old field names to new field names
   - Update foreign key references
   - Convert data formats as needed

3. **Import to New Service**
   ```bash
   # Import to new database
   psql -h new-db-host -d sahool -f transformed_data.sql
   ```

4. **Verify Migration**
   ```bash
   # Run verification queries
   SELECT COUNT(*) FROM new_fields;
   SELECT COUNT(*) FROM old_fields;
   ```

### Service-Specific Data Migration

#### Weather Data Migration

```sql
-- Migrate weather cache data
INSERT INTO weather_service.weather_cache (
    location_lat, location_lon, provider, data, cached_at
)
SELECT
    lat, lon, 'open-meteo', weather_data, timestamp
FROM weather_advanced.cache_entries;
```

#### Field Data Migration

```sql
-- Migrate fields from field-ops to field-management-service
INSERT INTO field_management.fields (
    id, tenant_id, name, area_hectares, geometry, created_at, updated_at
)
SELECT
    id, tenant_id, name, area_hectares,
    ST_GeomFromGeoJSON(geometry), created_at, updated_at
FROM field_ops.fields;
```

---

## Testing Migration

### Pre-Migration Testing

1. **Create Test Environment**
   ```bash
   make dev-test
   ```

2. **Run Compatibility Tests**
   ```bash
   pytest tests/migration/test_api_compatibility.py
   ```

3. **Verify Response Formats**
   ```bash
   python scripts/verify_response_formats.py
   ```

### Post-Migration Testing

1. **Smoke Tests**
   ```bash
   pytest tests/smoke/ -m migration
   ```

2. **Integration Tests**
   ```bash
   pytest tests/integration/ -k "new_service"
   ```

3. **Load Tests**
   ```bash
   locust -f tests/load/test_new_services.py
   ```

---

## Rollback Procedures

### Immediate Rollback

If issues are detected immediately after migration:

1. **Stop New Service Traffic**
   ```bash
   kubectl scale deployment new-service --replicas=0
   ```

2. **Restore Old Service**
   ```bash
   kubectl scale deployment old-service --replicas=3
   ```

3. **Update Kong Routes**
   ```bash
   curl -X PATCH http://kong:8001/services/service-name \
     -d "url=http://old-service:port"
   ```

### Data Rollback

If data corruption is detected:

1. **Restore from Backup**
   ```bash
   psql -h db-host -d sahool -f backup.sql
   ```

2. **Verify Data Integrity**
   ```bash
   python scripts/verify_data_integrity.py
   ```

---

## Support and Resources

### Documentation

- [API Gateway Documentation](./API_GATEWAY.md)
- [Service Registry](../governance/services.yaml)
<<<<<<< HEAD
- [Architecture Overview](./ARCHITECTURE.md)
=======
- [Architecture Overview](./ARCHITECTURE_DIAGRAMS.md)
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473

### Getting Help

- **Internal Support**: #sahool-platform Slack channel
- **Documentation Issues**: Create issue in sahool-docs repository
- **Emergency**: Contact platform-team@kafaat.com

### Migration Checklist

- [ ] Review deprecation headers in current responses
- [ ] Update API client libraries
- [ ] Migrate database schemas
- [ ] Update configuration files
- [ ] Test in staging environment
- [ ] Update monitoring dashboards
- [ ] Update documentation
- [ ] Communicate changes to consumers
- [ ] Schedule production migration
- [ ] Monitor post-migration metrics

---

_Last Updated: January 2026_
_Version: 16.0.0_
