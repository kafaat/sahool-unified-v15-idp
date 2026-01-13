# ⚠️ DEPRECATED - Use crop-intelligence-service instead

This service has been deprecated and merged into `crop-intelligence-service`.
Please update your references to use `crop-intelligence-service` on port 8095.

---

# Crop Growth Model - نموذج نمو المحاصيل

## نظرة عامة | Overview

خدمة محاكاة ونمذجة نمو المحاصيل باستخدام نماذج زراعية متقدمة.

Crop growth simulation and modeling service using advanced agricultural models.

**Port:** 8097
**Version:** 15.4.0

---

## الميزات | Features

### النماذج | Models

| النموذج  | Model    | الوصف               |
| -------- | -------- | ------------------- |
| DSSAT    | DSSAT    | نموذج محاكاة شامل   |
| AquaCrop | AquaCrop | نموذج FAO للإنتاجية |
| WOFOST   | WOFOST   | نموذج أوروبي        |
| Custom   | Custom   | نماذج مخصصة لليمن   |

### المحاصيل المدعومة | Supported Crops

- القمح (Wheat)
- الذرة (Corn/Sorghum)
- البن (Coffee)
- القات (Qat)
- الخضروات (Vegetables)
- الفواكه (Fruits)

---

## API Endpoints

### المحاكاة | Simulation

```http
# تشغيل محاكاة
POST /simulation/run
{
    "field_id": "field-001",
    "crop_type": "wheat",
    "model": "aquacrop",
    "planting_date": "2024-01-15",
    "parameters": {
        "variety": "local_yemen",
        "irrigation_method": "drip",
        "fertilizer_regime": "standard"
    },
    "weather_scenario": "normal"
}

# حالة المحاكاة
GET /simulation/{simulation_id}/status

# نتائج المحاكاة
GET /simulation/{simulation_id}/results
```

### مراحل النمو | Growth Stages

```http
# مراحل النمو الحالية
GET /fields/{field_id}/growth-stage

# تاريخ مراحل النمو
GET /fields/{field_id}/growth-history

Response:
{
    "field_id": "field-001",
    "current_stage": {
        "name": "التفريع",
        "name_en": "Tillering",
        "code": "V3",
        "days_in_stage": 12,
        "progress_percent": 60
    },
    "next_stage": {
        "name": "الاستطالة",
        "name_en": "Stem Elongation",
        "expected_date": "2024-02-01"
    }
}
```

### التوقعات | Predictions

```http
# توقع الإنتاجية
GET /fields/{field_id}/yield-prediction

# توقع موعد الحصاد
GET /fields/{field_id}/harvest-prediction

# توقع الاحتياجات المائية
GET /fields/{field_id}/water-requirements
{
    "period_days": 30
}
```

### السيناريوهات | Scenarios

```http
# مقارنة سيناريوهات
POST /scenarios/compare
{
    "field_id": "field-001",
    "scenarios": [
        {
            "name": "الوضع الحالي",
            "irrigation": "current",
            "fertilizer": "current"
        },
        {
            "name": "زيادة الري",
            "irrigation": "increased_20",
            "fertilizer": "current"
        },
        {
            "name": "تحسين التسميد",
            "irrigation": "current",
            "fertilizer": "optimized"
        }
    ]
}

Response:
{
    "comparison": [
        {
            "scenario": "الوضع الحالي",
            "predicted_yield": 3.2,
            "water_usage": 4500,
            "cost": 50000
        },
        {
            "scenario": "زيادة الري",
            "predicted_yield": 3.8,
            "water_usage": 5400,
            "cost": 55000
        }
    ]
}
```

---

## نماذج البيانات | Data Models

### SimulationResult

```json
{
  "id": "sim-001",
  "field_id": "field-001",
  "model": "aquacrop",
  "status": "completed",
  "parameters": {
    "crop_type": "wheat",
    "planting_date": "2024-01-15",
    "variety": "local_yemen"
  },
  "results": {
    "predicted_yield_kg_ha": 3500,
    "harvest_date": "2024-05-20",
    "total_water_mm": 450,
    "total_nitrogen_kg_ha": 120,
    "biomass_kg_ha": 8500
  },
  "daily_outputs": [
    {
      "day": 1,
      "date": "2024-01-15",
      "lai": 0.1,
      "biomass": 50,
      "root_depth": 0.05,
      "soil_water": 85
    }
  ],
  "created_at": "2024-01-14T10:00:00Z",
  "completed_at": "2024-01-14T10:02:30Z"
}
```

### GrowthStage

```json
{
  "code": "V3",
  "name": "التفريع",
  "name_en": "Tillering",
  "description": "تكون الفروع الجانبية",
  "typical_duration_days": 20,
  "key_indicators": ["عدد الفروع: 3-5", "ارتفاع النبات: 15-20 سم"],
  "management_tips": [
    "تطبيق الدفعة الأولى من النيتروجين",
    "مراقبة الآفات المبكرة"
  ]
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8097
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...

# خدمات خارجية
WEATHER_SERVICE_URL=http://weather-advanced:8092
SATELLITE_SERVICE_URL=http://satellite-service:8090

# النماذج
DEFAULT_MODEL=aquacrop
MAX_SIMULATION_DAYS=365
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "crop-growth-model",
    "version": "15.4.0",
    "models_loaded": ["aquacrop", "dssat", "wofost"]
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
