# Terrain Core Service

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/kafaat/sahool)
[![Coverage](https://img.shields.io/badge/coverage-82%25-green)](https://github.com/kafaat/sahool)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

## خدمة تحليل التضاريس

> **Comprehensive terrain analysis service for agricultural land assessment using Digital Elevation Models (DEM), providing slope, aspect, flow analysis, and irrigation suitability mapping.**

> **خدمة شاملة لتحليل التضاريس لتقييم الأراضي الزراعية باستخدام نماذج الارتفاع الرقمية، وتوفر تحليل الميل والجانب والتدفق وخرائط ملاءمة الري.**

---

## Architecture | البنية المعمارية

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Terrain Core Service                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  DEM Ingest  │  │    Slope     │  │    Aspect    │  │  Curvature   │    │
│  │   Module     │  │   Analysis   │  │   Analysis   │  │   Analysis   │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │            │
│  ┌──────┴─────────────────┴─────────────────┴─────────────────┴──────┐     │
│  │                    Terrain Processing Engine                       │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │     │
│  │  │    GDAL     │  │  rasterio   │  │  richdem    │               │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘               │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                              │                                              │
│  ┌───────────────────────────┴───────────────────────────────────┐         │
│  │                     DEM Data Sources                           │         │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │         │
│  │  │Copernicus│  │   SRTM   │  │   ALOS   │  │  Local   │       │         │
│  │  │ GLO-30   │  │  30/90m  │  │  12.5m   │  │  Upload  │       │         │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Port | المنفذ

```
8160
```

---

## Features | الميزات

### DEM Data Sources | مصادر بيانات الارتفاعات

- **Copernicus DEM GLO-30/GLO-90**: Global 30m/90m coverage (European Space Agency)
- **NASA SRTM**: Shuttle Radar Topography Mission 30m/90m
- **ALOS PALSAR**: JAXA high-resolution 12.5m DEM
- **Local DEM**: User-uploaded GeoTIFF files

### Terrain Indicators | مؤشرات التضاريس

| Indicator | Description | Arabic | Use Case |
|-----------|-------------|--------|----------|
| **Slope** | Surface inclination | الميل | Irrigation method selection |
| **Aspect** | Slope direction | الجانب | Sun exposure, crop placement |
| **Flow Direction** | Water flow path | اتجاه التدفق | Drainage design |
| **Flow Accumulation** | Upstream area | تراكم التدفق | Stream detection |
| **TWI** | Topographic Wetness Index | مؤشر الرطوبة | Soil moisture prediction |
| **Plan Curvature** | Horizontal curvature | الانحناء الأفقي | Erosion risk |
| **Profile Curvature** | Vertical curvature | الانحناء الطولي | Water flow acceleration |
| **Contours** | Elevation contour lines | خطوط الكنتور | Field visualization |

### Analysis Methods | طرق التحليل

- **D8 Flow Direction**: Eight-direction pour point model
- **D-Infinity**: Tarboton's infinite flow model
- **Multiple Flow Direction (MFD)**: Distributed flow routing

---

## API Endpoints | نقاط النهاية

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/metrics` | GET | Prometheus metrics |

### Terrain Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/terrain/analyze` | POST | Full terrain analysis |
| `/api/v1/terrain/slope` | POST | Slope analysis only |
| `/api/v1/terrain/aspect` | POST | Aspect analysis only |
| `/api/v1/terrain/flow` | POST | Flow direction & accumulation |
| `/api/v1/terrain/twi` | POST | Topographic Wetness Index |
| `/api/v1/terrain/curvature` | POST | Curvature analysis |
| `/api/v1/terrain/contours` | POST | Contour generation |

### DEM Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/dem/sources` | GET | List available DEM sources |
| `/api/v1/dem/upload` | POST | Upload custom DEM file |
| `/api/v1/dem/fetch` | POST | Fetch DEM for bounding box |
| `/api/v1/dem/metadata/{field_id}` | GET | Get DEM metadata |

### Irrigation Suitability

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/terrain/irrigation-zones` | POST | Generate irrigation zones |
| `/api/v1/terrain/recommendations` | GET | Get terrain-based recommendations |

---

## Request/Response Examples | أمثلة الطلبات

### Full Terrain Analysis Request

```bash
curl -X POST "http://localhost:8160/api/v1/terrain/analyze" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "FIELD-003",
    "dem_source": "copernicus",
    "target_resolution_m": 30.0,
    "include_slope": true,
    "include_aspect": true,
    "include_flow_direction": true,
    "include_twi": true,
    "include_contours": true,
    "contour_interval_m": 5.0,
    "slope_unit": "degrees",
    "flow_method": "d8"
  }'
```

### Full Terrain Analysis Response

```json
{
  "field_id": "FIELD-003",
  "analysis_id": "terrain-550e8400-e29b",
  "status": "completed",
  "analyzed_at": "2026-01-31T10:30:00Z",
  "dem_metadata": {
    "source": "copernicus",
    "source_name": {
      "en": "Copernicus DEM GLO-30",
      "ar": "نموذج كوبرنيكوس للارتفاعات الرقمية"
    },
    "resolution_m": 30.0,
    "crs": "EPSG:32637",
    "vertical_datum": "EGM96"
  },
  "dem_statistics": {
    "min_elevation_m": 145.2,
    "max_elevation_m": 162.8,
    "mean_elevation_m": 153.4,
    "std_elevation_m": 4.2,
    "elevation_range_m": 17.6
  },
  "slope": {
    "unit": "degrees",
    "unit_name": {"en": "Degrees", "ar": "درجات"},
    "min_slope": 0.1,
    "max_slope": 8.5,
    "mean_slope": 2.3,
    "classification": {
      "flat": 35.2,
      "gentle": 48.5,
      "moderate": 14.8,
      "steep": 1.5
    }
  },
  "aspect": {
    "dominant_direction": "south",
    "dominant_direction_name": {"en": "South", "ar": "جنوب"},
    "distribution": {
      "north": 8.2,
      "northeast": 12.5,
      "east": 15.3,
      "southeast": 18.7,
      "south": 22.1,
      "southwest": 10.5,
      "west": 7.2,
      "northwest": 5.5
    }
  },
  "twi": {
    "name": {"en": "Topographic Wetness Index", "ar": "مؤشر الرطوبة الطبوغرافية"},
    "min_twi": 4.2,
    "max_twi": 18.5,
    "mean_twi": 8.7,
    "high_moisture_area_pct": 12.5,
    "interpretation": {
      "en": "Moderate drainage with some waterlogging risk areas",
      "ar": "تصريف معتدل مع بعض مناطق خطر التشبع بالماء"
    }
  },
  "terrain_category": "gentle",
  "terrain_category_name": {"en": "Gentle Slope", "ar": "ميل لطيف"},
  "irrigation_recommendations": [
    {
      "zone_id": "zone-1",
      "zone_name": {"en": "North Section", "ar": "القسم الشمالي"},
      "area_ha": 3.2,
      "mean_slope_pct": 1.5,
      "mean_twi": 9.2,
      "irrigation_suitability": "excellent",
      "recommended_method": {"en": "Center Pivot", "ar": "الري المحوري"},
      "water_retention_capacity": "high",
      "erosion_risk": "low"
    }
  ],
  "processing_time_ms": 2450
}
```

---

## Terrain Classification | تصنيف التضاريس

### Slope Categories

| Category | Slope (%) | Arabic | Irrigation Recommendation |
|----------|-----------|--------|---------------------------|
| **Flat** | 0-2% | مسطح | Surface/flood irrigation |
| **Gentle** | 2-5% | لطيف | Sprinkler/drip irrigation |
| **Moderate** | 5-10% | معتدل | Drip irrigation preferred |
| **Steep** | 10-20% | حاد | Drip only, terracing needed |
| **Very Steep** | >20% | حاد جداً | Not suitable for irrigation |

### Aspect Directions

| Direction | Degrees | Arabic | Agricultural Impact |
|-----------|---------|--------|---------------------|
| North | 337.5-22.5 | شمال | Cooler, less evaporation |
| East | 67.5-112.5 | شرق | Morning sun exposure |
| South | 157.5-202.5 | جنوب | Maximum sun exposure |
| West | 247.5-292.5 | غرب | Afternoon sun exposure |

---

## Environment Variables | متغيرات البيئة

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `PORT` | `8160` | Service port | No |
| `HOST` | `0.0.0.0` | Bind address | No |
| `ENVIRONMENT` | `development` | Environment | No |
| `DATABASE_URL` | - | PostgreSQL (PostGIS) connection | Yes |
| `REDIS_URL` | - | Redis for caching | Yes |
| `NATS_URL` | - | NATS server URL | Yes |
| `DEFAULT_DEM_SOURCE` | `copernicus` | Default DEM source | No |
| `COPERNICUS_API_URL` | ESA URL | Copernicus DEM API | No |
| `SRTM_API_URL` | USGS URL | NASA SRTM API | No |
| `ALOS_API_URL` | JAXA URL | ALOS World 3D API | No |
| `DEFAULT_RESOLUTION_M` | `30.0` | Default output resolution | No |
| `MAX_PROCESSING_AREA_KM2` | `1000.0` | Max processing area | No |
| `DEFAULT_CRS` | `EPSG:32637` | Default CRS (UTM 37N) | No |
| `RESAMPLING_METHOD` | `bilinear` | Resampling method | No |
| `CONTOUR_INTERVAL_M` | `5.0` | Contour interval | No |
| `FLOW_THRESHOLD` | `100` | Flow accumulation threshold | No |
| `TEMP_DIR` | `/tmp/terrain` | Temporary directory | No |
| `DEM_CACHE_DIR` | `/tmp/terrain/dem_cache` | DEM cache directory | No |
| `MAX_UPLOAD_SIZE_MB` | `500` | Max upload size | No |
| `S3_BUCKET` | - | S3 bucket for DEM storage | No |
| `AWS_REGION` | `me-south-1` | AWS region | No |
| `LOG_LEVEL` | `INFO` | Logging level | No |
| `CACHE_TTL_SECONDS` | `3600` | Cache TTL | No |

---

## Quick Start | البداية السريعة

### Prerequisites

- **GDAL** >= 3.6 with Python bindings
- **PostgreSQL** >= 14 with **PostGIS** >= 3.4
- Python 3.12+

### Local Development

```bash
# Navigate to service directory
cd apps/services/terrain-core-service

# Install system dependencies (Ubuntu/Debian)
sudo apt-get install -y gdal-bin libgdal-dev python3-gdal

# Install Python dependencies
pip install -r requirements.txt

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8160 --reload
```

### Docker

```bash
# Build image (includes GDAL)
docker build -t sahool/terrain-core-service .

# Run container
docker run -p 8160:8160 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/sahool \
  -e REDIS_URL=redis://localhost:6379 \
  -e NATS_URL=nats://localhost:4222 \
  -v /path/to/dem_cache:/tmp/terrain/dem_cache \
  sahool/terrain-core-service
```

---

## Dependencies | التبعيات

### Python Packages

- **GDAL** >= 3.6 - Geospatial data processing
- **rasterio** >= 1.3 - Raster I/O
- **richdem** >= 2.3 - Terrain analysis algorithms
- **shapely** >= 2.0 - Geometric operations
- **pyproj** >= 3.6 - Coordinate transformations
- **numpy** >= 1.24 - Numerical computing
- **FastAPI** >= 0.126.0 - Web framework

### System Requirements

- **GDAL** libraries and binaries
- **PROJ** library for coordinate transforms
- **GEOS** for geometric operations

---

## Events | الأحداث

### Produces

| Event | Description |
|-------|-------------|
| `TerrainAnalysisCompleted.v1` | Full terrain analysis completed |
| `SlopeAnalysisCompleted.v1` | Slope analysis completed |
| `TWICalculated.v1` | TWI calculation completed |
| `ContoursGenerated.v1` | Contour lines generated |

### Consumes

| Event | Description |
|-------|-------------|
| `FieldBoundaryCreated.v1` | Process terrain for new field |
| `FieldBoundaryUpdated.v1` | Re-process terrain on boundary change |
| `DEMUpdated.v1` | New DEM data available |

---

## Testing | الاختبار

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_terrain_analysis.py -v
```

---

## Troubleshooting | استكشاف الأخطاء

### GDAL Import Error

```bash
# Check GDAL installation
gdalinfo --version

# Reinstall with pip
pip install GDAL==$(gdal-config --version)
```

### DEM Download Failures

- Check network connectivity to DEM providers
- Verify API credentials for restricted datasets
- Check disk space in cache directory

### Memory Issues with Large DEMs

- Reduce processing area
- Use tile-based processing
- Increase available memory

---

## License | الترخيص

Proprietary - KAFAAT

---

**Version**: 16.0.0
**Last Updated**: January 2026
