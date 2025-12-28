# Crop Intelligence Service (Unified)

**خدمة ذكاء المحاصيل الموحدة**

> **Note**: This service consolidates `crop-health`, `crop-health-ai`, and `crop-growth-model` into a single unified service.

## Overview | نظرة عامة

Unified crop intelligence service providing health monitoring, disease diagnosis, growth simulation, and agricultural recommendations.

خدمة ذكاء المحاصيل الموحدة. توفر مراقبة الصحة وتشخيص الأمراض ومحاكاة النمو والتوصيات الزراعية.

## Port

```
8095
```

## Features | الميزات

### Health Monitoring | مراقبة الصحة (from crop-health)
- Zone-based field analysis (تحليل الحقول حسب المنطقة)
- Vegetation indices: NDVI, EVI, NDRE, LCI, NDWI, SAVI
- Zone observation management (إدارة ملاحظات المناطق)
- Diagnosis engine with recommendations (محرك التشخيص مع التوصيات)
- VRT (Variable Rate Technology) export

### Disease Diagnosis | تشخيص الأمراض (from crop-health-ai)
- Image-based disease detection (كشف الأمراض من الصور)
- AI-powered diagnosis (تشخيص بالذكاء الاصطناعي)
- Batch diagnosis support (دعم التشخيص الجماعي)
- Treatment recommendations (توصيات العلاج)
- Crop disease database with 90%+ accuracy

### Growth Simulation | محاكاة النمو (from crop-growth-model)
- Growth stage prediction (توقع مراحل النمو)
- Multiple models: DSSAT, AquaCrop, WOFOST
- Yield prediction (توقع الإنتاج)
- Harvest date estimation (تقدير تاريخ الحصاد)
- Water requirement calculations (حسابات متطلبات المياه)
- Scenario comparison (مقارنة السيناريوهات)

## API Endpoints

### Health Check
- `GET /healthz` - Service health status

### Zone Analysis
- `POST /zones/analyze` - Analyze field zones
- `GET /zones/{zone_id}/health` - Get zone health score
- `POST /zones/{zone_id}/observations` - Add observation

### Disease Diagnosis
- `POST /diagnose` - Diagnose from image
- `POST /diagnose/batch` - Batch diagnosis
- `GET /diseases` - List known diseases

### Growth Modeling
- `POST /growth/simulate` - Run growth simulation
- `GET /growth/stages/{field_id}` - Get growth stages
- `POST /growth/predict-yield` - Predict yield
- `POST /growth/predict-harvest` - Predict harvest date

### Recommendations
- `GET /recommendations/{field_id}` - Get field recommendations
- `POST /vrt/export` - Export VRT prescription

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8095 | Service port |
| `DATABASE_URL` | - | PostgreSQL connection |
| `REDIS_URL` | - | Redis for caching |
| `AI_MODEL_PATH` | - | Path to disease detection model |

## Migration from Previous Services

This service replaces:
- `crop-health` (Port 8100) - Zone analysis & observations
- `crop-health-ai` (Port 8095) - Disease diagnosis
- `crop-growth-model` (Port 8097) - Growth simulation

All functionality is now available in this unified service.

## Docker

```bash
docker build -t crop-intelligence-service .
docker run -p 8095:8095 crop-intelligence-service
```

## Development

```bash
cd apps/services/crop-intelligence-service
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8095
```
