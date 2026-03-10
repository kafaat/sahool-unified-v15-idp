# Vegetation Analysis Service

## Service Overview

| Property | Value |
|----------|-------|
| **Service Name** | vegetation-analysis-service |
| **Type** | Python / FastAPI |
| **Port** | 8090 |
| **Version** | 16.0.0 |
| **Status** | Active (Replaces deprecated satellite-service) |

### Description

The Vegetation Analysis Service is a comprehensive satellite imagery analysis microservice for the SAHOOL platform. It provides real-time vegetation health monitoring, crop phenology detection, soil moisture estimation, yield prediction, and precision agriculture capabilities through multi-satellite data integration.

**Arabic**: خدمة تحليل الغطاء النباتي - تحليل صور الأقمار الصناعية لمراقبة صحة المحاصيل

### Key Features

- Multi-satellite data integration (Sentinel-2, Sentinel-1 SAR, MODIS, Landsat)
- 18+ vegetation indices calculation (NDVI, EVI, LAI, NDWI, NDRE, etc.)
- Crop phenology detection with BBCH growth stage mapping
- Soil moisture estimation from Sentinel-1 SAR backscatter
- Variable Rate Application (VRA) prescription maps
- Field boundary detection and change monitoring
- Yield prediction with ML ensemble models
- Growing Degree Days (GDD) tracking
- Spray conditions advisory
- Cloud masking and interpolation
- Data export (GeoJSON, CSV, KML, ISOXML)

---

## Kong Gateway Configuration

| Route | Upstream | Strip Path |
|-------|----------|------------|
| `/api/v1/vegetation` | vegetation-analysis-service:8090 | true |
| `/vegetation` | vegetation-analysis-service:8090 | true |
| `/api/v1/satellite` | vegetation-analysis-service:8090 | true |
| `/satellite` | vegetation-analysis-service:8090 | true |
| `/api/v1/ndvi` | vegetation-analysis-service:8090 | true |
| `/ndvi` | vegetation-analysis-service:8090 | true |

---

## Dependencies

### Infrastructure Dependencies

| Service | Purpose | Required |
|---------|---------|----------|
| PostgreSQL | Data persistence | Optional |
| Redis | Caching layer (NDVI, analysis, timeseries) | Optional |
| NATS | Event publishing for real-time notifications | Optional |

### Python Dependencies

```
fastapi==0.126.0
starlette>=0.49.1
uvicorn[standard]>=0.30.0,<1.0.0
pydantic==2.9.2
httpx==0.28.1
python-dotenv==1.0.1
redis[hiredis]==5.0.1
numpy==1.26.4
```

### Optional Dependencies (for real satellite data)

- `sahool-eo` package (eo-learn integration)
- `sentinelhub` (Sentinel Hub API client)
- `eolearn` (Earth Observation processing)
- `s2cloudless` (Cloud detection)

---

## Environment Variables

### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | 8090 |
| `LOG_LEVEL` | Logging level | INFO |
| `ENVIRONMENT` | Runtime environment | development |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `USE_MULTI_PROVIDER` | Enable multi-satellite provider | true |
| `SENTINEL_HUB_CLIENT_ID` | Sentinel Hub OAuth client ID | - |
| `SENTINEL_HUB_CLIENT_SECRET` | Sentinel Hub OAuth secret | - |
| `NASA_EARTHDATA_USERNAME` | NASA Earthdata username | - |
| `NASA_EARTHDATA_PASSWORD` | NASA Earthdata password | - |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379/0 |
| `DATABASE_URL` | PostgreSQL connection URL | - |
| `NATS_URL` | NATS server URL | - |

### Missing/Unused Variables (Documented in docker-compose but not implemented)

| Variable | Status | Notes |
|----------|--------|-------|
| `PLANET_API_KEY` | **NOT IMPLEMENTED** | Planet provider not integrated |
| `PLANET_CLIENT_ID` | **NOT IMPLEMENTED** | Planet provider not integrated |

---

## API Endpoints

### Health Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness probe (checks providers, cache, SAR) |

---

### Core Analysis Endpoints

#### GET /v1/analyze/{field_id}

Comprehensive field vegetation analysis with NDVI, health score, and recommendations.

**Parameters:**
- `field_id` (path): Field identifier
- `lat` (query, required): Latitude (-90 to 90)
- `lon` (query, required): Longitude (-180 to 180)
- `satellite` (query): Satellite source (sentinel2, sentinel1, landsat8, modis, viirs)

**Response Schema:**
```json
{
  "field_id": "string",
  "analysis_date": "2024-01-15T10:30:00Z",
  "satellite": "sentinel-2",
  "indices": {
    "ndvi": 0.65,
    "ndwi": 0.35,
    "evi": 0.58,
    "savi": 0.52,
    "lai": 3.2,
    "ndmi": 0.28
  },
  "health_score": 78.5,
  "health_status": "good",
  "health_status_ar": "جيد",
  "anomalies": ["string"],
  "recommendations_ar": ["string"],
  "recommendations_en": ["string"],
  "imagery": {
    "acquisition_date": "2024-01-14",
    "cloud_cover_percent": 5.2,
    "scene_id": "string"
  }
}
```

---

#### POST /v1/analyze-with-action

Field analysis with ActionTemplate output for mobile app integration.

**Request Body:**
```json
{
  "field_id": "string",
  "farmer_id": "string",
  "tenant_id": "string",
  "latitude": 15.5,
  "longitude": 44.2,
  "start_date": "2024-01-01",
  "end_date": "2024-01-15",
  "cloud_cover_max": 20.0,
  "publish_event": true
}
```

**Response:** Analysis + ActionTemplate + TaskCard for mobile integration

---

#### GET /v1/timeseries/{field_id}

NDVI time series for trend analysis.

**Parameters:**
- `field_id` (path): Field identifier
- `days` (query): Number of days (default: 30, max: 365)
- `satellite` (query): Satellite source

**Response Schema:**
```json
{
  "field_id": "string",
  "start_date": "2024-01-01",
  "end_date": "2024-01-30",
  "data_points_count": 5,
  "timeseries": [
    {
      "date": "2024-01-05",
      "ndvi": 0.65,
      "ndwi": 0.35,
      "evi": 0.58,
      "cloud_cover": 5.2,
      "scene_id": "string"
    }
  ],
  "trend": "increasing",
  "average_ndvi": 0.62
}
```

---

### Vegetation Indices Endpoints

#### GET /v1/indices/{field_id}

Get all vegetation indices (18+ indices).

**Response includes:**
- Basic: NDVI, NDWI, EVI, SAVI, LAI, NDMI
- Chlorophyll: NDRE, CVI, MCARI, TCARI, SIPI
- Early Stress: GNDVI, VARI, GLI, GRVI
- Corrected: MSAVI, OSAVI, ARVI

---

#### GET /v1/indices/{field_id}/{index_name}

Get specific vegetation index with interpretation.

**Parameters:**
- `index_name` (path): ndvi, ndre, gndvi, mcari, etc.
- `crop_type` (query): wheat, sorghum, coffee, qat, etc.
- `growth_stage` (query): emergence, vegetative, reproductive, maturation

---

#### POST /v1/indices/interpret

Interpret multiple indices for specific crop and growth stage.

**Request Body:**
```json
{
  "field_id": "field123",
  "indices": {"ndvi": 0.65, "ndre": 0.28, "gndvi": 0.55},
  "crop_type": "wheat",
  "growth_stage": "reproductive"
}
```

---

#### GET /v1/indices/guide

Usage guide for vegetation indices by growth stage.

---

### Phenology Detection Endpoints

#### GET /v1/phenology/{field_id}

Detect current crop growth stage from NDVI time series.

**Parameters:**
- `crop_type` (query, required): wheat, sorghum, millet, tomato, etc.
- `planting_date` (query, required): Planting date (YYYY-MM-DD)
- `days` (query): Analysis period (default: 60)

**Response Schema:**
```json
{
  "field_id": "string",
  "crop_type": "wheat",
  "current_stage": {
    "id": "tillering",
    "name_ar": "التفريع",
    "name_en": "Tillering",
    "days_in_stage": 15,
    "stage_start_date": "2024-01-01"
  },
  "next_stage": {
    "id": "stem_elong",
    "name_ar": "استطالة الساق",
    "name_en": "Stem Elongation",
    "days_to_next_stage": 10
  },
  "season_progress": {
    "percent": 45.5,
    "sos_date": "2023-11-15",
    "pos_date": "2024-02-01",
    "eos_date": "2024-03-15",
    "estimated_harvest_date": "2024-03-20"
  },
  "confidence": 0.85,
  "recommendations_ar": ["string"],
  "recommendations_en": ["string"]
}
```

---

#### GET /v1/phenology/{field_id}/timeline

Get expected phenology timeline for crop planning.

---

#### GET /v1/phenology/recommendations/{crop_type}/{stage}

Get stage-specific recommendations.

---

#### GET /v1/phenology/crops

List all supported crops for phenology detection.

**Supported Crops:**
- Cereals: wheat, sorghum, millet, barley, corn
- Vegetables: tomato, potato, onion, pepper, cucumber
- Fruits: banana, mango, date_palm, grapes
- Cash crops: coffee, qat, cotton, sesame
- Fodder: alfalfa

---

#### POST /v1/phenology/{field_id}/analyze-with-action

Phenology analysis with ActionTemplate output for mobile app.

---

### SAR / Soil Moisture Endpoints

#### GET /v1/soil-moisture/{field_id}

Estimate soil moisture from Sentinel-1 SAR backscatter.

**Parameters:**
- `lat` (query, required): Latitude
- `lon` (query, required): Longitude
- `date` (query): Target date (YYYY-MM-DD)

**Response Schema:**
```json
{
  "field_id": "string",
  "timestamp": "2024-01-15T10:30:00Z",
  "soil_moisture": {
    "percent": 35.5,
    "volumetric_water_content": 0.16,
    "status": "Optimal - Good for Growth",
    "status_ar": "مثالي - جيد للنمو"
  },
  "sar_data": {
    "vv_backscatter_db": -12.5,
    "vh_backscatter_db": -19.8,
    "incidence_angle_deg": 38.5,
    "data_source": "sentinel-1"
  },
  "confidence": 0.85,
  "recommendation_ar": "string",
  "recommendation_en": "string"
}
```

---

#### GET /v1/irrigation-events/{field_id}

Detect irrigation events from soil moisture changes.

**Parameters:**
- `days` (query): Days to look back (default: 30, max: 90)

---

#### GET /v1/sar-timeseries/{field_id}

Time series of SAR backscatter and soil moisture.

**Parameters:**
- `start_date` (query, required): Start date (YYYY-MM-DD)
- `end_date` (query, required): End date (YYYY-MM-DD)
- `lat` (query): Field latitude
- `lon` (query): Field longitude

---

### Yield Prediction Endpoints

#### POST /v1/yield-prediction

Predict crop yield using ML ensemble model.

**Request Body:**
```json
{
  "field_id": "string",
  "crop_code": "WHEAT",
  "latitude": 15.5,
  "longitude": 44.2,
  "planting_date": "2023-11-15",
  "field_area_ha": 2.5,
  "ndvi_series": [0.3, 0.45, 0.55, 0.65, 0.72],
  "precipitation_mm": 250.0,
  "avg_temp_min": 15.0,
  "avg_temp_max": 28.0,
  "soil_moisture": 0.4
}
```

**Response Schema:**
```json
{
  "field_id": "string",
  "crop_code": "WHEAT",
  "crop_name_ar": "قمح",
  "crop_name_en": "Wheat",
  "predicted_yield_ton_ha": 4.5,
  "predicted_yield_total_ton": 11.25,
  "yield_range_min": 3.8,
  "yield_range_max": 5.2,
  "confidence": 0.82,
  "factors": {
    "ndvi_factor": 0.4,
    "gdd_factor": 0.3,
    "water_factor": 0.2,
    "soil_factor": 0.1
  },
  "comparison_to_average": 1.15,
  "recommendations_ar": ["string"],
  "recommendations_en": ["string"],
  "growth_stage": "ripening",
  "days_to_harvest": 25,
  "data_sources_used": ["sentinel-2_ndvi_timeseries", "estimated_weather"]
}
```

---

#### GET /v1/yield-history/{field_id}

Get historical yield predictions.

---

#### GET /v1/regional-yields/{governorate}

Get regional yield statistics by governorate.

---

### VRA (Variable Rate Application) Endpoints

#### POST /v1/vra/generate

Generate VRA prescription map.

**Request Body:**
```json
{
  "field_id": "string",
  "latitude": 15.5,
  "longitude": 44.2,
  "vra_type": "fertilizer",
  "target_rate": 100,
  "unit": "kg/ha",
  "num_zones": 3,
  "zone_method": "ndvi",
  "min_rate": 50,
  "max_rate": 150,
  "product_price_per_unit": 2.5,
  "notes": "string",
  "notes_ar": "string"
}
```

**VRA Types:** fertilizer, seed, lime, pesticide, irrigation

**Zone Methods:** ndvi, yield, soil, combined

---

#### GET /v1/vra/zones/{field_id}

Get management zones for a field.

---

#### GET /v1/vra/prescriptions/{field_id}

Get prescription history for a field.

---

#### GET /v1/vra/prescription/{prescription_id}

Get prescription details.

---

#### GET /v1/vra/export/{prescription_id}

Export prescription (formats: geojson, shapefile, isoxml).

---

#### DELETE /v1/vra/prescription/{prescription_id}

Delete a prescription.

---

#### GET /v1/vra/info

VRA capabilities and supported types.

---

### Field Boundary Endpoints

#### POST /v1/boundaries/detect

Detect field boundaries using NDVI edge detection.

**Parameters:**
- `lat` (query, required): Center latitude
- `lon` (query, required): Center longitude
- `radius_m` (query): Search radius in meters (default: 500)
- `date` (query): Date for imagery (ISO format)

---

#### POST /v1/boundaries/refine

Refine rough boundary by snapping to NDVI edges.

**Request Body:**
```json
{
  "coords": [[44.2, 15.5], [44.21, 15.5], [44.21, 15.51], [44.2, 15.51]],
  "buffer_m": 50
}
```

---

#### GET /v1/boundaries/{field_id}/changes

Detect boundary changes over time.

---

### Change Detection Endpoints

#### GET /v1/changes/{field_id}

Comprehensive change detection report.

**Parameters:**
- `lat` (query, required): Latitude
- `lon` (query, required): Longitude
- `start_date` (query, required): Start date (YYYY-MM-DD)
- `end_date` (query, required): End date (YYYY-MM-DD)
- `crop_type` (query): Crop type

**Change Types Detected:**
- vegetation_increase / vegetation_decrease
- water_stress / drought_stress
- flooding
- harvest / planting
- land_clearing
- crop_damage / pest_disease

---

#### GET /v1/changes/{field_id}/compare

Compare two specific dates.

---

#### GET /v1/changes/{field_id}/anomalies

Detect anomalies in recent time series.

---

### Cloud Masking Endpoints

#### GET /v1/cloud-cover/{field_id}

Analyze cloud cover for a location.

---

#### GET /v1/clear-observations/{field_id}

Find clear observations in date range.

---

#### GET /v1/best-observation/{field_id}

Find best observation near target date.

---

#### POST /v1/interpolate-cloudy

Interpolate cloudy observations using temporal neighbors.

**Methods:** linear, spline, previous

---

### Weather Integration Endpoints

#### GET /v1/weather/{field_id}

Get weather data for analysis context.

---

#### GET /v1/weather/{field_id}/forecast

Get weather forecast.

---

### GDD (Growing Degree Days) Endpoints

#### GET /v1/gdd/{field_id}

Calculate accumulated GDD.

---

#### GET /v1/gdd/{field_id}/forecast

GDD forecast for crop planning.

---

### Spray Advisory Endpoints

#### GET /v1/spray/{field_id}/conditions

Get spray application conditions.

---

#### GET /v1/spray/{field_id}/window

Find optimal spray window.

---

### Data Export Endpoints

#### GET /v1/export/analysis/{field_id}

Export analysis data.

**Formats:** geojson, csv, json, kml

---

#### GET /v1/export/timeseries/{field_id}

Export time series data.

**Formats:** csv, json, geojson

---

#### GET /v1/export/boundaries

Export field boundaries.

**Parameters:**
- `field_ids` (query, required): Comma-separated field IDs

**Formats:** geojson, json, kml

---

#### GET /v1/export/report/{field_id}

Export comprehensive field report.

**Report Types:** full, summary, changes

---

## NATS Events

### Published Events

| Event Type | Subject Pattern | Description |
|------------|----------------|-------------|
| `satellite.analysis_completed` | `sahool.{tenant_id}.satellite.analysis_completed` | Field analysis complete with ActionTemplate |
| `phenology.stage_detected` | `sahool.{tenant_id}.phenology.stage_detected` | Growth stage detection |

### Event Payload Schema

```json
{
  "event_type": "satellite.analysis_completed",
  "source_service": "satellite-service",
  "field_id": "string",
  "data": {
    "ndvi": 0.65,
    "health_score": 78.5,
    "health_status": "good",
    "anomalies": []
  },
  "action_template": {
    "action_id": "uuid",
    "action_type": "field_monitoring",
    "title_ar": "string",
    "title_en": "string",
    "urgency": "medium",
    "confidence": 0.85,
    "offline_executable": true
  },
  "priority": "medium",
  "farmer_id": "string",
  "tenant_id": "string"
}
```

### Subscribed Events

The service does not currently subscribe to external NATS events. It operates primarily as an event publisher.

---

## Satellite Data Providers

### Supported Providers

| Provider | Satellites | Auth Required | Status |
|----------|------------|---------------|--------|
| Sentinel Hub | Sentinel-2, Sentinel-1 | Yes (OAuth) | Configured |
| NASA Earthdata | MODIS, VIIRS | Yes (Basic) | Configured |
| Copernicus STAC | Sentinel-2, Sentinel-1 | No (Free) | Active |
| Simulated | All | No | Fallback |

### Provider Priority

1. Sentinel Hub (if credentials configured)
2. NASA Earthdata (if credentials configured)
3. Copernicus STAC (free, no auth)
4. Simulated data (always available fallback)

---

## Caching

### Redis Cache Configuration

| Data Type | TTL | Key Pattern |
|-----------|-----|-------------|
| NDVI Data | 24 hours | `satellite:ndvi:{field_id}:{date}:{satellite}` |
| Analysis Results | 12 hours | `satellite:analysis:{field_id}:{date}:{satellite}` |
| Imagery Metadata | 6 hours | `satellite:imagery:*` |
| Time Series | 1 hour | `satellite:timeseries:{field_id}:{days}:{satellite}` |
| Health Status | 30 minutes | `satellite:health:*` |

### Cache Operations

- Automatic invalidation on field update
- Non-blocking SCAN for key patterns
- Graceful degradation when Redis unavailable

---

## Source Files

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | Main FastAPI application with all endpoints | ~3900 |
| `multi_provider.py` | Multi-satellite provider integration | ~800 |
| `vegetation_indices.py` | 18+ vegetation index calculations | ~1200 |
| `phenology_detector.py` | Crop growth stage detection | ~1200 |
| `sar_processor.py` | Sentinel-1 SAR soil moisture | ~540 |
| `change_detector.py` | Agricultural change detection | ~1200 |
| `field_boundary_detector.py` | Field boundary detection | ~900 |
| `vra_generator.py` | VRA prescription generation | ~700 |
| `vra_endpoints.py` | VRA API endpoints | ~580 |
| `yield_predictor.py` | ML yield prediction | ~750 |
| `gdd_tracker.py` | Growing Degree Days calculation | ~1700 |
| `spray_advisor.py` | Spray conditions advisory | ~900 |
| `cloud_masking.py` | Cloud detection and masking | ~700 |
| `data_exporter.py` | GeoJSON/CSV/KML export | ~600 |
| `weather_integration.py` | Weather data integration | ~750 |
| `ndvi_timeseries.py` | NDVI time series analysis | ~1500 |
| `cache.py` | Redis caching layer | ~400 |
| `eo_integration.py` | eo-learn/sahool-eo integration | ~280 |

---

## Bugs, Issues, and Recommendations

### Critical Issues

1. **Planet API Not Implemented**
   - **Location**: docker-compose.yml, multi_provider.py
   - **Issue**: `PLANET_API_KEY` and `PLANET_CLIENT_ID` environment variables are documented in docker-compose but Planet provider is not implemented in `multi_provider.py`
   - **Recommendation**: Either implement PlanetProvider class or remove unused environment variables from docker-compose

### Medium Priority Issues

2. **Hardcoded Path in sys.path**
   - **Location**: main.py lines 211, 2758, 2867
   - **Issue**: `sys.path.insert(0, "/home/user/sahool-unified-v15-idp")` is hardcoded
   - **Recommendation**: Use relative imports or environment variable for path

3. **Random Data in Production Endpoints**
   - **Location**: main.py, yield_predictor.py
   - **Issue**: Several endpoints use `random.uniform()` for simulated data without clear production data paths
   - **Recommendation**: Add clear data source indicators and improve real data integration

4. **Missing Database Integration**
   - **Location**: Multiple files
   - **Issue**: Many endpoints that should persist data (prescriptions, yield history) use in-memory storage or return simulated data
   - **Recommendation**: Integrate with PostgreSQL for data persistence

### Low Priority Issues

5. **Inconsistent Error Handling**
   - **Location**: Throughout main.py
   - **Issue**: Some endpoints catch generic `Exception`, others use specific exceptions
   - **Recommendation**: Standardize error handling with custom exception classes

6. **Missing Rate Limiting**
   - **Issue**: No rate limiting on compute-intensive endpoints like `/v1/yield-prediction`
   - **Recommendation**: Add rate limiting via Kong or application-level middleware

7. **Test Coverage**
   - **Location**: tests/ directory
   - **Issue**: Limited test coverage for complex calculation modules
   - **Recommendation**: Add unit tests for vegetation_indices, phenology_detector, and yield_predictor

### Documentation Issues

8. **API Versioning**
   - **Issue**: All endpoints use `/v1/` but no v2 migration path documented
   - **Recommendation**: Document API versioning strategy

---

## Performance Considerations

- **Caching**: Redis caching reduces satellite API calls significantly
- **SAR Processing**: 6-day revisit time for Sentinel-1 data
- **Optical Data**: Cloud cover affects data availability
- **Batch Operations**: Export endpoints support bulk operations

---

## Security Notes

- **Authentication**: DELETE endpoints (`DELETE /v1/vra/prescription/{id}`) require JWT authentication via `get_current_user` dependency
- Satellite provider credentials stored in environment variables
- No direct database credential exposure
- NATS events include tenant_id for multi-tenancy isolation
- API supports authentication via Kong gateway
- Unified error handling via `shared.errors_py`

---

## Related Services

| Service | Relationship |
|---------|--------------|
| field-management-service | Provides field metadata |
| weather-service | Weather data for analysis context |
| indicators-service | Consumes vegetation indices |
| crop-intelligence-service | Uses phenology data |
| advisory-service | Receives recommendations |
| notification-service | Receives NATS events |
| mobile app | Receives ActionTemplates |

---

## Deprecation Notes

This service replaces the deprecated `satellite-service`. All routes previously served by satellite-service are now handled by vegetation-analysis-service through Kong gateway configuration.

---

*Last Updated: 2026-01-25*
*Generated for SAHOOL Platform v16.0.0*
