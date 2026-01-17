# ⚠️ DEPRECATED - Use yield-prediction-service instead

This service has been deprecated and merged into `yield-prediction-service`.
Please update your references to use `yield-prediction-service` on port 8103.

---

# Yield Prediction - توقع الإنتاجية

## نظرة عامة | Overview

خدمة توقع إنتاجية المحاصيل باستخدام البيانات التاريخية ونماذج التعلم الآلي.

Crop yield prediction service using historical data and machine learning models.

**Port:** 8103
**Version:** 15.4.0

---

## الميزات | Features

### أنواع التوقع | Prediction Types

| النوع       | Type         | الوصف                 |
| ----------- | ------------ | --------------------- |
| توقع فردي   | Single Field | توقع لحقل واحد        |
| توقع إقليمي | Regional     | توقع للمنطقة          |
| توقع وطني   | National     | توقع على مستوى الدولة |
| توقع مقارن  | Comparative  | مقارنة بين سيناريوهات |

### المحاصيل المدعومة | Supported Crops

| المحصول | Crop    | دقة النموذج |
| ------- | ------- | ----------- |
| القمح   | Wheat   | 92%         |
| الذرة   | Sorghum | 89%         |
| البن    | Coffee  | 87%         |
| الطماطم | Tomato  | 91%         |
| البصل   | Onion   | 88%         |

---

## API Endpoints

### التوقع الفردي | Single Prediction

```http
# توقع إنتاجية حقل
POST /predict/field
{
    "field_id": "field-001",
    "crop_type": "wheat",
    "variety": "local",
    "planting_date": "2024-01-15",
    "expected_harvest": "2024-05-20"
}

Response:
{
    "prediction_id": "pred-001",
    "field_id": "field-001",
    "crop_type": "wheat",
    "prediction": {
        "yield_kg_ha": 3750,
        "total_yield_kg": 19500,
        "confidence": 0.88,
        "range": {
            "min": 3200,
            "max": 4300
        }
    },
    "comparison": {
        "vs_historical_avg": "+12%",
        "vs_regional_avg": "+8%"
    },
    "key_factors": [
        {"factor": "rainfall", "impact": "positive", "contribution": 0.25},
        {"factor": "temperature", "impact": "neutral", "contribution": 0.15},
        {"factor": "soil_quality", "impact": "positive", "contribution": 0.20}
    ]
}
```

### التوقع الإقليمي | Regional Prediction

```http
# توقع إنتاجية منطقة
POST /predict/region
{
    "region": "صنعاء",
    "crop_type": "wheat",
    "season": "2024_winter"
}

Response:
{
    "region": "صنعاء",
    "crop_type": "wheat",
    "season": "2024_winter",
    "prediction": {
        "total_area_ha": 12500,
        "avg_yield_kg_ha": 3450,
        "total_production_tons": 43125,
        "confidence": 0.82
    },
    "breakdown": {
        "districts": [
            {
                "name": "بني حشيش",
                "area_ha": 3500,
                "avg_yield": 3800,
                "production_tons": 13300
            },
            {
                "name": "سنحان",
                "area_ha": 2800,
                "avg_yield": 3200,
                "production_tons": 8960
            }
        ]
    },
    "risks": [
        {"type": "drought", "probability": 0.15, "impact": "medium"},
        {"type": "pest", "probability": 0.10, "impact": "low"}
    ]
}
```

### التوقع التاريخي | Historical Comparison

```http
# مقارنة تاريخية
GET /predict/historical/{field_id}

Response:
{
    "field_id": "field-001",
    "historical_data": [
        {"season": "2021", "crop": "wheat", "actual_yield": 3200, "predicted_yield": 3150},
        {"season": "2022", "crop": "wheat", "actual_yield": 3450, "predicted_yield": 3400},
        {"season": "2023", "crop": "wheat", "actual_yield": 3600, "predicted_yield": 3550}
    ],
    "model_accuracy": {
        "mae": 85,
        "rmse": 102,
        "mape": 2.8
    },
    "trend": "increasing",
    "avg_growth_rate": 6.2
}
```

### تحسين الإنتاجية | Yield Optimization

```http
# توصيات لتحسين الإنتاجية
POST /optimize
{
    "field_id": "field-001",
    "current_prediction": 3750,
    "target_yield": 4500
}

Response:
{
    "field_id": "field-001",
    "current_prediction": 3750,
    "target_yield": 4500,
    "gap": 750,
    "achievable": true,
    "recommendations": [
        {
            "action": "increase_nitrogen",
            "current": 100,
            "recommended": 130,
            "unit": "kg/ha",
            "expected_gain": 300,
            "cost_sar": 450
        },
        {
            "action": "optimize_irrigation",
            "current_efficiency": 75,
            "target_efficiency": 90,
            "expected_gain": 250,
            "cost_sar": 1200
        },
        {
            "action": "pest_prevention",
            "expected_gain": 200,
            "cost_sar": 300
        }
    ],
    "total_expected_gain": 750,
    "total_cost_sar": 1950,
    "roi_percent": 285
}
```

### تقارير الموسم | Season Reports

```http
# تقرير موسمي
GET /reports/season?crop=wheat&season=2024&region=sanaa

# تقرير مقارن
GET /reports/comparison?field_id=field-001&seasons=2022,2023,2024
```

### التنبؤ بالمخاطر | Risk Forecasting

```http
# تنبؤ المخاطر
GET /predict/risks/{field_id}

Response:
{
    "field_id": "field-001",
    "crop_type": "wheat",
    "risks": [
        {
            "type": "weather",
            "subtype": "drought",
            "probability": 0.25,
            "impact_yield_percent": -15,
            "period": "March-April",
            "mitigation": "زيادة الري في الفترة الحرجة"
        },
        {
            "type": "pest",
            "subtype": "aphids",
            "probability": 0.20,
            "impact_yield_percent": -10,
            "period": "February",
            "mitigation": "رش وقائي مبكر"
        },
        {
            "type": "disease",
            "subtype": "rust",
            "probability": 0.15,
            "impact_yield_percent": -20,
            "period": "March",
            "mitigation": "مراقبة وعلاج مبكر"
        }
    ],
    "overall_risk_score": 0.35,
    "risk_adjusted_yield": 3200
}
```

---

## نماذج البيانات | Data Models

### FieldPrediction

```json
{
  "id": "pred-001",
  "field_id": "field-001",
  "crop_type": "wheat",
  "season": "2024_winter",
  "planting_date": "2024-01-15",
  "prediction_date": "2024-03-01",
  "prediction": {
    "yield_kg_ha": 3750,
    "total_yield_kg": 19500,
    "area_ha": 5.2,
    "confidence": 0.88
  },
  "model": {
    "name": "yield_rf_v3",
    "version": "3.1.0"
  },
  "inputs": {
    "weather_data": true,
    "satellite_data": true,
    "soil_data": true,
    "historical_data": true
  },
  "created_at": "2024-03-01T10:00:00Z"
}
```

### RegionalForecast

```json
{
  "id": "forecast-001",
  "region": "صنعاء",
  "crop_type": "wheat",
  "season": "2024_winter",
  "forecast_date": "2024-03-01",
  "summary": {
    "total_area_ha": 12500,
    "avg_yield_kg_ha": 3450,
    "total_production_tons": 43125
  },
  "confidence": 0.82,
  "vs_last_season": {
    "area_change": "+5%",
    "yield_change": "+8%",
    "production_change": "+13%"
  },
  "updated_at": "2024-03-01T12:00:00Z"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8103
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...

# النماذج
MODEL_PATH=/models/yield
DEFAULT_MODEL=ensemble_v3

# خدمات خارجية
WEATHER_SERVICE_URL=http://weather-advanced:8092
SATELLITE_SERVICE_URL=http://satellite-service:8090
YIELD_ENGINE_URL=http://yield-engine:8098
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "yield-prediction",
    "version": "15.4.0"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
