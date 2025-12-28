# ⚠️ DEPRECATED - Use crop-intelligence-service instead

This service has been deprecated and merged into `crop-intelligence-service`.
Please update your references to use `crop-intelligence-service` on port 8095.

---


# Crop Health Service

**خدمة صحة المحاصيل - التشخيص الذكي للحقول الزراعية**

## Overview | نظرة عامة

Intelligent crop health diagnostics with zone-based analysis, vegetation index monitoring, and VRT (Variable Rate Technology) export for precision agriculture.

تشخيص ذكي لصحة المحاصيل مع تحليل قائم على المناطق ومراقبة مؤشرات الغطاء النباتي وتصدير VRT للزراعة الدقيقة.

## Port

```
8100
```

## Features | الميزات

### Zone Management | إدارة المناطق
- Create and manage field zones
- GeoJSON export
- Area calculations

### Observation Ingestion | استقبال الأرصاد
- Multi-source support (Sentinel-2, Drone, Planet, Landsat)
- Cloud coverage tracking
- Growth stage association

### Vegetation Indices | مؤشرات الغطاء النباتي
- NDVI (Normalized Difference Vegetation Index)
- EVI (Enhanced Vegetation Index)
- NDRE (Normalized Difference Red Edge)
- LCI (Leaf Chlorophyll Index)
- NDWI (Normalized Difference Water Index)
- SAVI (Soil-Adjusted Vegetation Index)

### Diagnosis Engine | محرك التشخيص
- Zone status classification (critical/warning/ok)
- Priority-based action recommendations
- Evidence-based decisions

### VRT Export | تصدير VRT
- Irrigation recommendations
- Fertilization rates
- Variable rate application maps

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Health check |
| GET | `/` | Service info |

### Zones
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/fields/{field_id}/zones` | Create zone |
| GET | `/api/v1/fields/{field_id}/zones` | List zones |
| GET | `/api/v1/fields/{field_id}/zones.geojson` | Export GeoJSON |

### Observations
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/fields/{field_id}/zones/{zone_id}/observations` | Ingest observation |
| GET | `/api/v1/fields/{field_id}/zones/{zone_id}/observations` | List observations |

### Diagnosis
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/fields/{field_id}/diagnosis?date=` | Full field diagnosis |
| POST | `/api/v1/diagnose` | Quick diagnosis (no save) |

### Timeline
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/fields/{field_id}/zones/{zone_id}/timeline?from=&to=` | Index timeline |

### VRT Export
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/fields/{field_id}/vrt?date=` | VRT GeoJSON export |

## Usage Examples | أمثلة الاستخدام

### Ingest Observation
```bash
curl -X POST http://localhost:8100/api/v1/fields/field_001/zones/zone_a/observations \
  -H "Content-Type: application/json" \
  -d '{
    "captured_at": "2025-12-23T10:00:00Z",
    "source": "sentinel-2",
    "growth_stage": "mid",
    "indices": {
      "ndvi": 0.72,
      "evi": 0.58,
      "ndre": 0.25,
      "lci": 0.30,
      "ndwi": -0.02,
      "savi": 0.60
    },
    "cloud_pct": 5.0
  }'
```

### Get Field Diagnosis
```bash
curl "http://localhost:8100/api/v1/fields/field_001/diagnosis?date=2025-12-23"
```

### Export VRT
```bash
curl "http://localhost:8100/api/v1/fields/field_001/vrt?date=2025-12-23&action_type=irrigation"
```

## Action Priorities

| Priority | Description | Response Window |
|----------|-------------|-----------------|
| P0 | Critical - immediate action | 24 hours |
| P1 | High - urgent attention | 48 hours |
| P2 | Medium - planned action | 1 week |
| P3 | Low - routine monitoring | 2 weeks |

## Growth Stages

- `early` - Early growth
- `mid` - Mid season
- `late` - Late season/maturity

## Dependencies

- FastAPI
- Pydantic
- PostgreSQL + PostGIS (planned)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8100` |
| `CDN_BASE_URL` | CDN for map layers | `https://cdn.sahool.io` |
| `CORS_ORIGINS` | Allowed CORS origins | - |
