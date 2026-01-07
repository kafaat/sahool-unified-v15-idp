# SAHOOL AI/ML API Documentation

OpenAPI 3.0 specifications for SAHOOL's AI/ML and Analysis services.

## Overview

This directory contains comprehensive OpenAPI/Swagger documentation for SAHOOL's agricultural AI and remote sensing APIs.

### API Specifications

1. **[ai-services.yaml](./ai-services.yaml)** - AI/ML Services API
   - Crop Intelligence & Disease Detection
   - Fertilizer Advisor & NPK Recommendations
   - Yield Prediction with ML Models

2. **[analysis-services.yaml](./analysis-services.yaml)** - Analysis Services API
   - NDVI Analysis & Vegetation Monitoring
   - Satellite Imagery (Sentinel-2, Landsat, MODIS)
   - LAI Estimation & Time Series Analysis

## Quick Start

### Viewing the Documentation

#### Option 1: Swagger UI (Recommended)

```bash
# Install swagger-ui
npm install -g swagger-ui-watcher

# View AI Services API
swagger-ui-watcher docs/api/openapi/ai-services.yaml

# View Analysis Services API
swagger-ui-watcher docs/api/openapi/analysis-services.yaml
```

Open your browser to `http://localhost:8000`

#### Option 2: Redoc

```bash
# Install redoc-cli
npm install -g redoc-cli

# Generate HTML documentation
redoc-cli bundle docs/api/openapi/ai-services.yaml -o ai-services.html
redoc-cli bundle docs/api/openapi/analysis-services.yaml -o analysis-services.html
```

#### Option 3: Online Swagger Editor

1. Go to https://editor.swagger.io/
2. File → Import file → Select the YAML file

### Generating Client SDKs

#### Python Client

```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate Python client for AI Services
openapi-generator-cli generate \
  -i docs/api/openapi/ai-services.yaml \
  -g python \
  -o clients/python/sahool-ai-client \
  --additional-properties=packageName=sahool_ai

# Generate Python client for Analysis Services
openapi-generator-cli generate \
  -i docs/api/openapi/analysis-services.yaml \
  -g python \
  -o clients/python/sahool-analysis-client \
  --additional-properties=packageName=sahool_analysis
```

#### JavaScript/TypeScript Client

```bash
# Generate TypeScript client for AI Services
openapi-generator-cli generate \
  -i docs/api/openapi/ai-services.yaml \
  -g typescript-axios \
  -o clients/typescript/sahool-ai-client

# Generate TypeScript client for Analysis Services
openapi-generator-cli generate \
  -i docs/api/openapi/analysis-services.yaml \
  -g typescript-axios \
  -o clients/typescript/sahool-analysis-client
```

#### Java Client

```bash
openapi-generator-cli generate \
  -i docs/api/openapi/ai-services.yaml \
  -g java \
  -o clients/java/sahool-ai-client \
  --additional-properties=groupId=io.sahool,artifactId=sahool-ai-client
```

## API Services

### 1. AI Services API

**Base URL**: `https://api.sahool.io/v1`

#### Crop Intelligence
- Disease detection using deep learning
- Crop health diagnostics
- Zone-based field analysis
- VRT export for precision agriculture

**Key Endpoints**:
- `POST /crop-intelligence/disease-detection` - Detect diseases from images
- `GET /crop-intelligence/fields/{field_id}/diagnosis` - Complete field diagnosis
- `POST /crop-intelligence/fields/{field_id}/zones/{zone_id}/observations` - Submit observations

#### Fertilizer Advisor
- NPK recommendations
- Soil analysis interpretation
- Crop-specific fertilization plans
- Nutrient deficiency diagnosis

**Key Endpoints**:
- `POST /fertilizer/recommend` - Get fertilizer recommendations
- `POST /fertilizer/soil-analysis/interpret` - Interpret soil test results
- `GET /fertilizer/deficiency-symptoms/{crop}` - Get deficiency information

#### Yield Prediction
- ML-powered yield forecasting
- Revenue estimation
- Weather and soil integration
- 30+ Yemen crops supported

**Key Endpoints**:
- `POST /yield/predict` - Predict crop yield
- `GET /yield/crops` - List supported crops
- `GET /yield/price/{crop_type}` - Get current prices

### 2. Analysis Services API

**Base URL**: `https://api.sahool.io/v1`

#### NDVI Analysis
- Vegetation health monitoring
- Anomaly detection
- Zone-based analysis
- Statistical trend analysis

**Key Endpoints**:
- `POST /ndvi/compute` - Compute NDVI for field
- `POST /ndvi/anomaly` - Detect NDVI anomalies
- `POST /ndvi/zones` - Analyze NDVI zones

#### Vegetation Analysis
- 17+ vegetation indices (NDVI, EVI, SAVI, LAI, NDRE, etc.)
- Chlorophyll and nitrogen assessment
- Water stress detection
- Crop-specific interpretation

**Key Endpoints**:
- `POST /vegetation/indices` - Calculate all indices
- `POST /vegetation/interpret` - Interpret index values

#### Satellite Imagery
- Multi-source support (Sentinel-2, Landsat-8/9, MODIS)
- Automatic cloud filtering
- Band-level data access
- Temporal compositing

**Key Endpoints**:
- `POST /satellite/imagery` - Acquire satellite imagery
- `POST /satellite/analyze` - Complete field analysis
- `GET /satellite/sources` - List available sources

#### LAI Estimation
- Leaf Area Index calculation
- Growth monitoring
- Canopy development tracking
- Time series analysis

**Key Endpoints**:
- `POST /lai/estimate` - Estimate LAI from indices
- `POST /lai/timeseries` - Get LAI time series

#### Time Series
- Historical vegetation data
- Multi-index time series
- Trend analysis
- Data export (CSV, GeoJSON, NetCDF)

**Key Endpoints**:
- `POST /timeseries/vegetation` - Get vegetation time series
- `POST /timeseries/export` - Export data
- `POST /timeseries/compare` - Compare multiple fields

## Authentication

All API endpoints require authentication using JWT Bearer tokens.

### Getting a Token

```bash
# Login to get access token
curl -X POST https://api.sahool.io/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "your-password"
  }'
```

### Using the Token

```bash
# Include token in Authorization header
curl -X GET https://api.sahool.io/v1/crop-intelligence/fields/field_123/diagnosis?date=2025-12-14 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Rate Limits

### AI Services
- **Analysis Endpoints**: 100 requests/minute per user
- **Prediction Endpoints**: 50 requests/minute per user
- **Batch Operations**: 1000 requests/hour per tenant

### Analysis Services
- **Real-time Analysis**: 50 requests/minute per user
- **Time Series (Cached)**: 500 requests/minute per user
- **Data Export**: 20 requests/minute per user

## Error Handling

All APIs use standard HTTP status codes and return errors in this format:

```json
{
  "error": "INVALID_REQUEST",
  "message": "Invalid crop type specified",
  "details": {
    "field": "crop_type",
    "allowed_values": ["wheat", "tomato", "corn", ...]
  }
}
```

### Common Error Codes

- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable

## Async Job Handling

Long-running ML operations (e.g., disease detection on large images) return a job ID:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "created_at": "2025-12-14T10:00:00Z"
}
```

Poll for job status:

```bash
curl -X GET https://api.sahool.io/v1/jobs/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Examples

### Example 1: Get Field Diagnosis

```bash
curl -X GET "https://api.sahool.io/v1/crop-intelligence/fields/field_123/diagnosis?date=2025-12-14" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

### Example 2: Get Fertilizer Recommendations

```bash
curl -X POST https://api.sahool.io/v1/fertilizer/recommend \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field_123",
    "crop": "tomato",
    "growth_stage": "flowering",
    "area_hectares": 2.5,
    "soil_type": "loamy",
    "target_yield_kg_ha": 40000
  }'
```

### Example 3: Predict Crop Yield

```bash
curl -X POST https://api.sahool.io/v1/yield/predict \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field_123",
    "area_hectares": 5.0,
    "crop_type": "wheat",
    "avg_rainfall": 450,
    "avg_temperature": 20,
    "soil_quality": "good",
    "irrigation_type": "drip"
  }'
```

### Example 4: Calculate Vegetation Indices

```bash
curl -X POST https://api.sahool.io/v1/vegetation/indices \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "red": 0.08,
    "nir": 0.45,
    "blue": 0.05,
    "green": 0.06,
    "swir": 0.15
  }'
```

### Example 5: Get NDVI Time Series

```bash
curl -X POST https://api.sahool.io/v1/timeseries/vegetation \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field_123",
    "start_date": "2025-01-01",
    "end_date": "2025-12-14",
    "indices": ["ndvi", "evi", "lai"],
    "interval": "weekly"
  }'
```

## Validation

Validate your OpenAPI specs:

```bash
# Install validator
npm install -g @apidevtools/swagger-cli

# Validate specs
swagger-cli validate docs/api/openapi/ai-services.yaml
swagger-cli validate docs/api/openapi/analysis-services.yaml
```

## Testing

### Using Postman

1. Import the OpenAPI spec into Postman:
   - Click "Import" → "Upload Files"
   - Select the YAML file
   - Postman will create a collection with all endpoints

2. Set up environment variables:
   - `base_url`: `https://api.sahool.io/v1`
   - `access_token`: Your JWT token

### Using curl

See the examples above.

### Using Python

```python
import requests

# Setup
base_url = "https://api.sahool.io/v1"
token = "YOUR_ACCESS_TOKEN"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Get field diagnosis
response = requests.get(
    f"{base_url}/crop-intelligence/fields/field_123/diagnosis",
    headers=headers,
    params={"date": "2025-12-14"}
)
diagnosis = response.json()
print(f"Critical zones: {diagnosis['summary']['zones_critical']}")

# Predict yield
response = requests.post(
    f"{base_url}/yield/predict",
    headers=headers,
    json={
        "field_id": "field_123",
        "area_hectares": 5.0,
        "crop_type": "tomato",
        "avg_rainfall": 450,
        "avg_temperature": 24,
        "soil_quality": "good",
        "irrigation_type": "drip"
    }
)
prediction = response.json()
print(f"Predicted yield: {prediction['predicted_yield_tons']} tons")
print(f"Revenue: ${prediction['estimated_revenue_usd']:,.2f}")
```

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (Kong)                        │
│                  https://api.sahool.io                       │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────────┐              ┌──────────────────────┐
│   AI Services API    │              │ Analysis Services API│
│   (Port 8080)        │              │   (Port 8090)        │
└──────────────────────┘              └──────────────────────┘
        │                                       │
        │                                       │
   ┌────┴────┐                          ┌──────┴──────┐
   │         │                          │             │
   ▼         ▼                          ▼             ▼
┌────────┐ ┌─────────┐         ┌─────────┐    ┌──────────┐
│  Crop  │ │Fertilizer│         │  NDVI   │    │Satellite │
│Intell. │ │ Advisor  │         │ Engine  │    │ Service  │
│  :8095 │ │  :8093   │         │  :8097  │    │  :8090   │
└────────┘ └─────────┘         └─────────┘    └──────────┘
     │           │                    │              │
     ▼           ▼                    ▼              ▼
┌────────┐ ┌─────────┐         ┌─────────┐    ┌──────────┐
│ Yield  │ │  Soil   │         │  Veg.   │    │   LAI    │
│ Engine │ │Analysis │         │Analysis │    │Estimator │
│  :8098 │ │         │         │         │    │          │
└────────┘ └─────────┘         └─────────┘    └──────────┘
```

## Support

For API support and questions:
- Email: support@sahool.io
- Documentation: https://docs.sahool.io
- GitHub Issues: https://github.com/sahool/platform/issues

## License

Proprietary - Copyright (c) 2025 SAHOOL Platform
