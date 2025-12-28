# ⚠️ DEPRECATED - Use vegetation-analysis-service instead

This service has been deprecated and merged into `vegetation-analysis-service`.
Please update your references to use `vegetation-analysis-service` on port 8090.

---


# NDVI Engine Service

**محرك NDVI - حوسبة الاستشعار عن بعد**

## Overview | نظرة عامة

Remote sensing NDVI computation and vegetation analysis engine. Processes satellite imagery to calculate vegetation indices and detect crop health anomalies.

محرك حوسبة NDVI والتحليل النباتي للاستشعار عن بعد. يعالج صور الأقمار الصناعية لحساب مؤشرات الغطاء النباتي واكتشاف الشذوذ في صحة المحاصيل.

## Port

```
8097
```

## Features | الميزات

### NDVI Computation | حساب NDVI
- Sentinel-2 data processing
- Mock data for testing
- Historical analysis

### Vegetation Indices | مؤشرات الغطاء النباتي
- NDVI (Normalized Difference Vegetation Index)
- EVI (Enhanced Vegetation Index)
- NDRE (Normalized Difference Red Edge)
- NDWI (Normalized Difference Water Index)

### Zone Analysis | تحليل المناطق
- Field zone segmentation
- Stress detection
- Growth stage classification

### Anomaly Detection | اكتشاف الشذوذ
- Sudden NDVI drops
- Pattern recognition
- Trend analysis

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Health check |

### Computation
| Method | Path | Description |
|--------|------|-------------|
| POST | `/compute` | Compute NDVI from coordinates |
| POST | `/compute/sentinel` | Compute from Sentinel-2 |
| POST | `/compute/mock` | Compute with mock data |

### Analysis
| Method | Path | Description |
|--------|------|-------------|
| POST | `/analyze/zones` | Analyze field zones |
| POST | `/analyze/anomalies` | Detect anomalies |
| GET | `/classify/{ndvi}` | Classify NDVI health |

### Indices
| Method | Path | Description |
|--------|------|-------------|
| POST | `/indices/all` | Calculate all vegetation indices |
| GET | `/indices/reference` | Get reference values |

## Usage Examples | أمثلة الاستخدام

### Compute NDVI
```bash
curl -X POST http://localhost:8097/compute \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "field_id": "field_001",
    "coordinates": {
      "type": "Polygon",
      "coordinates": [[[44.0, 15.0], [44.1, 15.0], [44.1, 15.1], [44.0, 15.1], [44.0, 15.0]]]
    },
    "date": "2025-12-20"
  }'
```

### Analyze Zones
```bash
curl -X POST http://localhost:8097/analyze/zones \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field_001",
    "zones": ["zone_a", "zone_b", "zone_c"],
    "ndvi_values": [0.72, 0.58, 0.35]
  }'
```

### Classify NDVI
```bash
curl http://localhost:8097/classify/0.65
```

## NDVI Classification

| Range | Category | Arabic | Color |
|-------|----------|--------|-------|
| < 0.0 | Non-vegetation | غير نباتي | Blue |
| 0.0 - 0.2 | Bare soil | تربة جرداء | Brown |
| 0.2 - 0.4 | Stressed | إجهاد | Orange |
| 0.4 - 0.6 | Moderate | متوسط | Yellow |
| 0.6 - 0.8 | Healthy | صحي | Light Green |
| > 0.8 | Very Healthy | ممتاز | Dark Green |

## Response Format

### NDVI Computation Result
```json
{
  "field_id": "field_001",
  "date": "2025-12-20",
  "ndvi": {
    "mean": 0.65,
    "min": 0.42,
    "max": 0.78,
    "std": 0.08
  },
  "classification": "healthy",
  "zones": [...],
  "anomalies": [],
  "computed_at": "2025-12-23T10:00:00Z"
}
```

## Dependencies

- FastAPI
- NumPy
- NATS
- Sentinel Hub SDK (optional)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8097` |
| `NATS_URL` | NATS server URL | - |
| `SENTINEL_CLIENT_ID` | Sentinel Hub client ID | - |
| `SENTINEL_CLIENT_SECRET` | Sentinel Hub secret | - |
| `USE_MOCK_DATA` | Use mock data | `false` |

## Events Published

- `ndvi.computed` - NDVI computation complete
- `ndvi.anomaly` - Anomaly detected
- `ndvi.alert` - Critical NDVI drop alert
