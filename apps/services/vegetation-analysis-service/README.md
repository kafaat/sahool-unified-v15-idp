# Vegetation Analysis Service (Unified)

**خدمة تحليل الغطاء النباتي الموحدة**

> **Note**: This service consolidates `satellite-service`, `ndvi-processor`, `ndvi-engine`, and `lai-estimation` into a single unified service.

## Overview | نظرة عامة

Unified vegetation analysis service providing satellite imagery processing, NDVI calculations, and vegetation health monitoring.

خدمة تحليل الغطاء النباتي الموحدة. توفر معالجة صور الأقمار الصناعية وحسابات NDVI ومراقبة صحة النباتات.

## Port

```
8090
```

## Features | الميزات

### Satellite Imagery | صور الأقمار الصناعية (from satellite-service)
- Multi-source imagery: Sentinel-2, Landsat, MODIS, Planet
- RGB true color composites
- Tile generation for maps
- Historical imagery access

### Vegetation Indices | مؤشرات الغطاء النباتي (from ndvi-processor)
- NDVI (Normalized Difference Vegetation Index)
- EVI (Enhanced Vegetation Index)
- NDRE (Normalized Difference Red Edge)
- SAVI (Soil Adjusted Vegetation Index)
- NDWI (Normalized Difference Water Index)

### LAI Estimation | تقدير مؤشر مساحة الأوراق (from lai-estimation)
- Leaf Area Index calculations
- Canopy coverage estimation
- Biomass estimation

### Analysis Features | ميزات التحليل
- Time series analysis (تحليل السلاسل الزمنية)
- Anomaly detection (كشف الشذوذ)
- Trend calculation (حساب الاتجاهات)
- Zone statistics (إحصائيات المناطق)
- Field boundary analysis (تحليل حدود الحقول)

## API Endpoints

### Health Check
- `GET /healthz` - Service health status

### Satellite Imagery
- `GET /imagery/{field_id}` - Get field imagery
- `GET /imagery/{field_id}/tiles/{z}/{x}/{y}` - Get map tiles
- `GET /imagery/sources` - List available sources

### Vegetation Indices
- `GET /ndvi/{field_id}` - Current NDVI
- `GET /ndvi/{field_id}/timeseries` - NDVI time series
- `GET /indices/{field_id}` - All vegetation indices
- `POST /indices/calculate` - Calculate custom indices

### Analysis
- `GET /analysis/{field_id}/anomaly` - Anomaly detection
- `GET /analysis/{field_id}/trend` - Trend analysis
- `GET /analysis/{field_id}/stats` - Zone statistics
- `POST /analysis/compare` - Compare multiple fields

### LAI
- `GET /lai/{field_id}` - LAI estimation
- `GET /lai/{field_id}/timeseries` - LAI time series

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8090 | Service port |
| `DATABASE_URL` | - | PostgreSQL connection |
| `REDIS_URL` | - | Redis for caching |
| `SENTINEL_HUB_KEY` | - | Sentinel Hub API key |
| `PLANET_API_KEY` | - | Planet API key |

## Data Sources

1. **Sentinel-2** - 10m resolution, 5-day revisit (Free via Copernicus)
2. **Landsat 8/9** - 30m resolution, 16-day revisit (Free via USGS)
3. **MODIS** - 250m resolution, daily (Free via NASA)
4. **Planet** - 3m resolution, daily (Commercial)

## Migration from Previous Services

This service replaces:
- `satellite-service` (Port 8090) - Satellite imagery
- `ndvi-processor` (Port 8101) - NDVI calculations
- `ndvi-engine` (Port 8099) - NDVI analysis
- `lai-estimation` (Port 8100) - LAI calculations

All functionality is now available in this unified service.

## Docker

```bash
docker build -t vegetation-analysis-service .
docker run -p 8090:8090 vegetation-analysis-service
```

## Development

```bash
cd apps/services/vegetation-analysis-service
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8090
```
