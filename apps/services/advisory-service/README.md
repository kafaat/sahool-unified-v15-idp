# Advisory Service (Unified)

**خدمة الاستشارات الزراعية الموحدة**

> **Note**: This service consolidates `agro-advisor` and `fertilizer-advisor` into a single unified service.

## Overview | نظرة عامة

Unified agricultural advisory service providing disease diagnosis, nutrient assessment, fertilizer planning, and crop recommendations.

خدمة الاستشارات الزراعية الموحدة. توفر تشخيص الأمراض وتقييم المغذيات وتخطيط التسميد وتوصيات المحاصيل.

## Port

```
8093
```

## Features | الميزات

### Disease Diagnosis | تشخيص الأمراض (from agro-advisor)

- Image-based disease detection (كشف الأمراض من الصور)
- Symptom-based diagnosis (تشخيص حسب الأعراض)
- Treatment recommendations (توصيات العلاج)
- Disease database for Yemen crops

### Nutrient Assessment | تقييم المغذيات (from agro-advisor)

- Soil nutrient analysis (تحليل مغذيات التربة)
- NDVI-based health assessment
- Deficiency detection (كشف النقص)
- Micronutrient recommendations

### Fertilizer Planning | تخطيط التسميد (from fertilizer-advisor)

- Soil analysis integration (تكامل تحليل التربة)
- Nutrient requirements calculation (حساب متطلبات المغذيات)
- Fertilizer recommendations (توصيات الأسمدة)
- Application scheduling (جدولة التطبيق)
- Cost estimation (تقدير التكلفة)
- NPK optimization

### Crop Recommendations | توصيات المحاصيل

- Seasonal planting advice
- Variety selection
- Rotation planning
- Yemen-specific recommendations

## API Endpoints

### Health Check

- `GET /healthz` - Service health status

### Disease Diagnosis

- `POST /diagnose` - Diagnose from image/symptoms
- `GET /diseases` - List known diseases
- `GET /diseases/{disease_id}` - Disease details
- `GET /treatments/{disease_id}` - Treatment options

### Nutrient Assessment

- `POST /nutrients/assess` - Assess nutrient status
- `GET /nutrients/{field_id}` - Field nutrient profile
- `POST /nutrients/deficiency` - Detect deficiencies

### Fertilizer Planning

- `POST /fertilizer/plan` - Create fertilizer plan
- `GET /fertilizer/schedule/{field_id}` - Get schedule
- `POST /fertilizer/calculate` - Calculate requirements
- `GET /fertilizer/cost/{plan_id}` - Cost estimation
- `GET /fertilizer/products` - Available products

### Recommendations

- `GET /recommendations/{field_id}` - Field recommendations
- `POST /recommendations/seasonal` - Seasonal advice

## Environment Variables

| Variable              | Default | Description           |
| --------------------- | ------- | --------------------- |
| `PORT`                | 8093    | Service port          |
| `DATABASE_URL`        | -       | PostgreSQL connection |
| `REDIS_URL`           | -       | Redis for caching     |
| `WEATHER_SERVICE_URL` | -       | Weather service URL   |

## Migration from Previous Services

This service replaces:

- `agro-advisor` (Port 8095) - Disease diagnosis & nutrients
- `fertilizer-advisor` (Port 8093) - Fertilizer planning

All functionality is now available in this unified service.

## Docker

```bash
docker build -t advisory-service .
docker run -p 8093:8093 advisory-service
```

## Development

```bash
cd apps/services/advisory-service
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 8093
```
