# Hydrology Service

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/kafaat/sahool)
[![Coverage](https://img.shields.io/badge/coverage-80%25-green)](https://github.com/kafaat/sahool)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

## خدمة الهيدرولوجيا

> **Comprehensive hydrology analysis service for agricultural water management, providing drainage network analysis, wetness mapping, depression detection, stream delineation, and watershed analysis.**

> **خدمة شاملة للتحليل الهيدرولوجي لإدارة المياه الزراعية، توفر تحليل شبكة التصريف وخرائط الرطوبة واكتشاف المنخفضات وتحديد المجاري المائية وتحليل أحواض التجميع.**

---

## Architecture | البنية المعمارية

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Hydrology Service                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Drainage   │  │   Wetness   │  │ Depression  │  │    Basin    │        │
│  │  Network    │  │  Analysis   │  │  Detection  │  │ Delineation │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │               │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐        │
│  │                   Hydrology Processing Engine                   │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                              │                                             │
│  ┌───────────────────────────┴───────────────────────────────────┐        │
│  │                    External Services                           │        │
│  │  ┌───────────────────┐  ┌───────────────────┐                 │        │
│  │  │ Terrain Core      │  │ Weather Service   │                 │        │
│  │  │ Service (DEM)     │  │ (Rainfall Data)   │                 │        │
│  │  └───────────────────┘  └───────────────────┘                 │        │
│  └────────────────────────────────────────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Port | المنفذ

```
8165
```

---

## Features | الميزات

### Drainage Network Analysis | تحليل شبكة التصريف

- Drainage pattern classification (dendritic, parallel, trellis, etc.)
- Bifurcation ratio calculation
- Drainage density computation
- Stream segment analysis
- Main channel identification

### Wetness Analysis | تحليل الرطوبة

- Topographic Wetness Index (TWI) mapping
- Wetness zone classification (6 levels)
- Waterlogging prediction
- Irrigation efficiency scoring
- Mitigation recommendations (bilingual)

### Depression Detection | اكتشاف المنخفضات

- Sink identification and mapping
- Volume and area calculation
- Depth analysis
- Risk level assessment
- Drainage recommendations

### Stream Network | شبكة المجاري المائية

- Strahler stream ordering (1-6+)
- Stream length computation
- Upstream area calculation
- Perennial/ephemeral classification

### Basin/Watershed Delineation | تحديد أحواض التجميع

- Sub-basin identification
- Pour point analysis
- Time of concentration calculation
- Runoff coefficient estimation
- Morphometric parameters

---

## API Endpoints | نقاط النهاية

### Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/healthz` | GET | Kubernetes liveness probe |
| `/readyz` | GET | Kubernetes readiness probe |
| `/metrics` | GET | Prometheus metrics |

### Full Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/hydrology/analyze` | POST | Full hydrology analysis |
| `/api/v1/hydrology/summary/{field_id}` | GET | Get analysis summary |

### Drainage Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/drainage/network` | POST | Analyze drainage network |
| `/api/v1/drainage/pattern/{field_id}` | GET | Get drainage pattern |
| `/api/v1/drainage/density/{field_id}` | GET | Get drainage density |

### Wetness Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/wetness/analyze` | POST | Wetness zone analysis |
| `/api/v1/wetness/predict-waterlogging` | POST | Predict waterlogging risk |
| `/api/v1/wetness/zones/{field_id}` | GET | Get wetness zones |

### Depression Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/depressions/detect` | POST | Detect depressions |
| `/api/v1/depressions/volume/{field_id}` | GET | Get total depression volume |
| `/api/v1/depressions/{field_id}` | GET | List depressions with risk |

### Stream Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/streams/detect` | POST | Detect stream network |
| `/api/v1/streams/{field_id}` | GET | Get stream network |
| `/api/v1/streams/order/{field_id}` | GET | Get streams by order |

### Basin Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/basins/delineate` | POST | Delineate watersheds |
| `/api/v1/basins/{field_id}` | GET | Get basin information |
| `/api/v1/basins/runoff/{field_id}` | GET | Get runoff coefficient |

---

## Request/Response Examples | أمثلة الطلبات

### Full Hydrology Analysis Request

```bash
curl -X POST "http://localhost:8165/api/v1/hydrology/analyze" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "FIELD-003",
    "tenant_id": "FARM-001",
    "dem_source": "srtm",
    "resolution_m": 30.0,
    "include_rainfall": true,
    "rainfall_period_days": 30
  }'
```

### Full Hydrology Analysis Response

```json
{
  "success": true,
  "data": {
    "field_id": "FIELD-003",
    "tenant_id": "FARM-001",
    "analyzed_at": "2026-01-31T10:30:00Z",
    "dem_source": "srtm",
    "resolution_m": 30.0,
    "field_area_ha": 8.5,
    "mean_elevation_m": 153.4,
    "elevation_range_m": 17.6,
    "mean_slope_percent": 2.3,
    "drainage": {
      "field_id": "FIELD-003",
      "total_length_m": 1250.5,
      "drainage_density": 147.1,
      "main_channel_length_m": 320.5,
      "bifurcation_ratio": 3.8,
      "pattern": "dendritic",
      "pattern_ar": "شجيري",
      "segments": [...]
    },
    "wetness": {
      "field_id": "FIELD-003",
      "total_area_ha": 8.5,
      "twi_mean": 8.7,
      "twi_std": 2.3,
      "dominant_level": "moderate",
      "dominant_level_ar": "معتدل",
      "zones": [
        {
          "zone_id": "zone-1",
          "level": "wet",
          "level_ar": "رطب",
          "area_ha": 1.2,
          "percentage": 14.1,
          "twi_mean": 12.5,
          "recommendations_ar": ["تجنب الري الزائد", "تحسين التصريف"],
          "recommendations_en": ["Avoid over-irrigation", "Improve drainage"]
        }
      ],
      "waterlogging_prediction": {
        "rainfall_mm": 50.0,
        "risk_level": "medium",
        "risk_level_ar": "متوسط",
        "affected_area_ha": 0.8,
        "affected_percentage": 9.4,
        "time_to_drain_hours": 24.0,
        "mitigation_ar": ["حفر قنوات تصريف مؤقتة"],
        "mitigation_en": ["Dig temporary drainage channels"]
      },
      "irrigation_efficiency_score": 78.5
    },
    "depressions": {
      "field_id": "FIELD-003",
      "total_depressions": 5,
      "total_volume_m3": 45.2,
      "total_area_sqm": 320.5,
      "field_area_ha": 8.5,
      "depressions_percentage": 0.38,
      "high_risk_count": 1,
      "critical_count": 0,
      "summary_ar": "تم اكتشاف 5 منخفضات بحجم إجمالي 45.2 متر مكعب",
      "summary_en": "Detected 5 depressions with total volume 45.2 m³"
    },
    "streams": {
      "field_id": "FIELD-003",
      "total_streams": 12,
      "total_length_m": 1250.5,
      "max_order": 3,
      "streams_by_order": {"1": 8, "2": 3, "3": 1},
      "main_stream_length_m": 320.5
    },
    "basins": {
      "field_id": "FIELD-003",
      "total_basins": 3,
      "total_area_ha": 8.5,
      "main_basin_area_ha": 5.2,
      "mean_elevation_m": 153.4,
      "relief_m": 17.6,
      "elongation_ratio": 0.72,
      "circularity_ratio": 0.65,
      "runoff_coefficient": 0.35
    },
    "flood_risk_level": "low",
    "flood_risk_level_ar": "منخفض",
    "drainage_quality_score": 85.2,
    "recommendations_ar": [
      "جودة التصريف جيدة للزراعة",
      "مراقبة المنطقة عالية الرطوبة في الجزء الشمالي",
      "معالجة المنخفض ذو الخطورة العالية قبل موسم الأمطار"
    ],
    "recommendations_en": [
      "Good drainage quality for agriculture",
      "Monitor high wetness area in north section",
      "Address high-risk depression before rainy season"
    ]
  },
  "processing_time_ms": 3250
}
```

---

## Wetness Levels | مستويات الرطوبة

| Level | TWI Range | Arabic | Management Action |
|-------|-----------|--------|-------------------|
| **Very Dry** | < 4 | جاف جداً | Increase irrigation |
| **Dry** | 4-6 | جاف | Monitor soil moisture |
| **Moderate** | 6-9 | معتدل | Optimal for most crops |
| **Wet** | 9-12 | رطب | Reduce irrigation |
| **Very Wet** | 12-15 | رطب جداً | Improve drainage |
| **Waterlogged** | > 15 | مشبع بالماء | Critical drainage needed |

---

## Drainage Patterns | أنماط التصريف

| Pattern | Arabic | Description |
|---------|--------|-------------|
| **Dendritic** | شجيري | Tree-like, uniform geology |
| **Parallel** | متوازي | Steep uniform slopes |
| **Trellis** | شبكي | Folded sedimentary rocks |
| **Rectangular** | مستطيل | Jointed/fractured rock |
| **Radial** | شعاعي | Around volcanic cones |
| **Centripetal** | مركزي | Toward central depression |
| **Deranged** | مشوش | Glaciated areas |

---

## Depression Risk Levels | مستويات خطر المنخفضات

| Level | Arabic | Criteria | Action |
|-------|--------|----------|--------|
| **Low** | منخفض | Depth < 20cm, drains < 6h | Monitor |
| **Medium** | متوسط | Depth 20-50cm, drains 6-24h | Improve drainage |
| **High** | مرتفع | Depth 50-100cm, drains 24-72h | Fill or drain |
| **Critical** | حرج | Depth > 100cm, drains > 72h | Immediate action |

---

## Environment Variables | متغيرات البيئة

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `PORT` | `8165` | Service port | No |
| `HOST` | `0.0.0.0` | Bind address | No |
| `ENVIRONMENT` | `development` | Environment | No |
| `DATABASE_URL` | - | PostgreSQL connection | Yes |
| `NATS_URL` | - | NATS server URL | Yes |
| `TERRAIN_SERVICE_URL` | `http://terrain-core-service:8160` | Terrain service URL | No |
| `WEATHER_SERVICE_URL` | `http://weather-service:8092` | Weather service URL | No |
| `DEFAULT_DEM_RESOLUTION` | `30.0` | Default DEM resolution (m) | No |
| `FLOW_ACCUMULATION_THRESHOLD` | `100` | Stream detection threshold | No |
| `DEPRESSION_FILL_MAX_DEPTH` | `2.0` | Max depression fill depth (m) | No |
| `WETNESS_INDEX_HIGH_THRESHOLD` | `12.0` | High wetness TWI threshold | No |
| `BASIN_AREA_MIN_HECTARES` | `0.5` | Minimum basin area (ha) | No |
| `CACHE_TTL_SECONDS` | `3600` | Cache TTL | No |
| `LOG_LEVEL` | `INFO` | Logging level | No |

---

## Integration with Other Services | التكامل مع الخدمات الأخرى

### Terrain Core Service

```
hydrology-service --> terrain-core-service
                  |
                  +-- GET /api/v1/terrain/flow
                  +-- GET /api/v1/terrain/twi
                  +-- GET /api/v1/dem/metadata
```

The hydrology service depends on terrain-core-service for:
- DEM data and flow direction analysis
- TWI (Topographic Wetness Index) calculations
- Slope and elevation data

### Weather Service

```
hydrology-service --> weather-service
                  |
                  +-- GET /api/v1/weather/rainfall/{field_id}
                  +-- GET /api/v1/weather/forecast/{field_id}
```

Weather data is used for:
- Rainfall-based waterlogging predictions
- Time-to-drain calculations
- Flood risk assessment

---

## Quick Start | البداية السريعة

### Local Development

```bash
# Navigate to service directory
cd apps/services/hydrology-service

# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn src.main:app --host 0.0.0.0 --port 8165 --reload
```

### Docker

```bash
# Build image
docker build -t sahool/hydrology-service .

# Run container
docker run -p 8165:8165 \
  -e DATABASE_URL=postgresql://user:pass@localhost:5432/sahool \
  -e NATS_URL=nats://localhost:4222 \
  -e TERRAIN_SERVICE_URL=http://terrain-core-service:8160 \
  -e WEATHER_SERVICE_URL=http://weather-service:8092 \
  sahool/hydrology-service
```

---

## Events | الأحداث

### Produces

| Event | Description |
|-------|-------------|
| `HydrologyAnalysisCompleted.v1` | Full hydrology analysis completed |
| `WaterloggingAlert.v1` | High waterlogging risk detected |
| `DepressionDetected.v1` | Critical depression identified |
| `DrainageQualityAssessed.v1` | Drainage quality score calculated |

### Consumes

| Event | Description |
|-------|-------------|
| `FieldCreated.v1` | Analyze hydrology for new field |
| `TerrainAnalysisCompleted.v1` | Process with new terrain data |
| `WeatherForecastReady.v1` | Update waterlogging predictions |
| `RainfallRecorded.v1` | Update predictions with actual rainfall |

---

## Testing | الاختبار

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_drainage.py -v
```

---

## Troubleshooting | استكشاف الأخطاء

### Terrain Service Unavailable

```
Error: Connection refused to terrain-core-service
```

- Verify terrain-core-service is running
- Check TERRAIN_SERVICE_URL environment variable
- Test connectivity: `curl http://terrain-core-service:8160/healthz`

### Slow Analysis

- Large fields may take longer; consider tiling
- Check DEM resolution (higher = slower)
- Verify database connection pooling

### Memory Issues

- Reduce analysis resolution
- Process sub-basins separately
- Increase container memory limits

---

## License | الترخيص

Proprietary - KAFAAT

---

**Version**: 16.0.0
**Last Updated**: January 2026
