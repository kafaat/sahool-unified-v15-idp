# ⚠️ DEPRECATED - Use advisory-service instead

This service has been deprecated and merged into `advisory-service`.
Please update your references to use `advisory-service` on port 8093.

---


# Agro Advisor Service

**المستشار الزراعي - تشخيص الأمراض وتخطيط التسميد**

## Overview | نظرة عامة

Agro Advisor provides intelligent agricultural advisory services including disease diagnosis, nutrient assessment, and fertilizer planning for Yemen agriculture.

خدمة المستشار الزراعي توفر استشارات زراعية ذكية تشمل تشخيص الأمراض وتقييم المغذيات وتخطيط التسميد للزراعة اليمنية.

## Port

```
8095
```

## Features | الميزات

### Disease Diagnosis | تشخيص الأمراض
- Image-based disease assessment
- Symptom-based diagnosis
- Crop-specific disease database
- Treatment recommendations

### Nutrient Assessment | تقييم المغذيات
- NDVI-based deficiency detection
- Visual symptom analysis
- Soil fertility evaluation

### Fertilizer Planning | تخطيط التسميد
- Growth stage-based plans
- Field size calculations
- Irrigation type adjustments

## API Endpoints

### Health
| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Health check |

### Disease
| Method | Path | Description |
|--------|------|-------------|
| POST | `/disease/assess` | Assess disease from image |
| POST | `/disease/symptoms` | Assess from symptoms |
| GET | `/disease/search?q=` | Search diseases |
| GET | `/disease/crop/{crop}` | Get crop diseases |
| GET | `/disease/{disease_id}` | Get disease info |

### Nutrient
| Method | Path | Description |
|--------|------|-------------|
| POST | `/nutrient/ndvi` | Assess from NDVI |
| POST | `/nutrient/visual` | Assess from visual indicators |
| GET | `/nutrient/{deficiency_id}` | Get deficiency info |

### Fertilizer
| Method | Path | Description |
|--------|------|-------------|
| POST | `/fertilizer/plan` | Generate fertilizer plan |
| GET | `/fertilizer/{fertilizer_id}` | Get fertilizer info |
| GET | `/fertilizer/nutrient/{nutrient}` | Get fertilizers by nutrient |

### Crops
| Method | Path | Description |
|--------|------|-------------|
| GET | `/crops` | List supported crops |
| GET | `/crops/{crop}/stages` | Get growth stages |
| GET | `/crops/{crop}/requirements` | Get nutrient requirements |

## Usage Examples | أمثلة الاستخدام

### Diagnose Disease from Symptoms
```bash
curl -X POST http://localhost:8095/disease/symptoms \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "field_id": "field_001",
    "crop": "wheat",
    "symptoms": ["yellow_leaves", "wilting"],
    "lang": "ar"
  }'
```

### Generate Fertilizer Plan
```bash
curl -X POST http://localhost:8095/fertilizer/plan \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant_001",
    "field_id": "field_001",
    "crop": "wheat",
    "stage": "vegetative",
    "field_size_ha": 5.0,
    "soil_fertility": "medium",
    "irrigation_type": "drip"
  }'
```

## Dependencies

- FastAPI
- Pydantic
- NATS (for event publishing)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8095` |
| `NATS_URL` | NATS server URL | - |

## Events Published

- `agro.recommendation.created` - Disease/pest recommendation
- `agro.nutrient.assessment` - Nutrient deficiency assessment
- `agro.fertilizer.plan` - Fertilizer plan generated
