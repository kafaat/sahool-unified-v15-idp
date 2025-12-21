# Yield Engine - محرك الإنتاجية

## نظرة عامة | Overview

محرك التعلم الآلي لتوقع إنتاجية المحاصيل الزراعية في اليمن.

Machine learning engine for crop yield prediction in Yemen.

**Port:** 8098
**Version:** 15.4.0

---

## الميزات | Features

### التوقع | Prediction
| الميزة | Feature | الوصف |
|--------|---------|--------|
| توقع موسمي | Seasonal Forecast | توقع الإنتاج الموسمي |
| توقع مبكر | Early Prediction | توقع قبل الحصاد |
| سيناريوهات | Scenarios | ماذا لو؟ |
| عدم اليقين | Uncertainty | فترات الثقة |

### النماذج | Models
| النموذج | Model | الدقة |
|---------|-------|--------|
| Random Forest | RF | 88% |
| XGBoost | XGB | 91% |
| LSTM | LSTM | 89% |
| Ensemble | Ensemble | 93% |

---

## API Endpoints

### التوقع | Prediction

```http
# توقع الإنتاجية
POST /predict
{
    "field_id": "field-001",
    "crop_type": "wheat",
    "planting_date": "2024-01-15",
    "model": "ensemble"
}

Response:
{
    "field_id": "field-001",
    "prediction": {
        "yield_kg_ha": 3850,
        "confidence_interval": {
            "lower": 3400,
            "upper": 4300
        },
        "confidence_percent": 85
    },
    "harvest_date": {
        "expected": "2024-05-20",
        "range": ["2024-05-15", "2024-05-25"]
    },
    "factors": {
        "weather_impact": "positive",
        "soil_quality": "good",
        "water_availability": "adequate"
    },
    "model": {
        "name": "ensemble",
        "version": "3.2"
    }
}

# توقع متعدد الحقول
POST /predict/batch
{
    "field_ids": ["field-001", "field-002", "field-003"],
    "crop_type": "wheat"
}
```

### السلسلة الزمنية | Time Series

```http
# تطور التوقع
GET /fields/{field_id}/yield/timeseries?season=2024

Response:
{
    "field_id": "field-001",
    "season": "2024",
    "predictions": [
        {"date": "2024-01-20", "days_after_planting": 5, "yield_kg_ha": 3200, "confidence": 0.60},
        {"date": "2024-02-20", "days_after_planting": 35, "yield_kg_ha": 3500, "confidence": 0.72},
        {"date": "2024-03-20", "days_after_planting": 65, "yield_kg_ha": 3750, "confidence": 0.82},
        {"date": "2024-04-20", "days_after_planting": 95, "yield_kg_ha": 3850, "confidence": 0.90}
    ],
    "final_prediction": 3850,
    "actual_yield": null
}
```

### السيناريوهات | Scenarios

```http
# تحليل سيناريوهات
POST /scenarios
{
    "field_id": "field-001",
    "base_scenario": "current",
    "variations": [
        {
            "name": "جفاف خفيف",
            "rainfall_reduction_percent": 20
        },
        {
            "name": "زيادة الري",
            "irrigation_increase_percent": 30
        },
        {
            "name": "تحسين التسميد",
            "fertilizer_optimization": true
        }
    ]
}

Response:
{
    "field_id": "field-001",
    "base_yield_kg_ha": 3850,
    "scenarios": [
        {
            "name": "جفاف خفيف",
            "yield_kg_ha": 3200,
            "change_percent": -17,
            "risk_level": "medium"
        },
        {
            "name": "زيادة الري",
            "yield_kg_ha": 4200,
            "change_percent": 9,
            "cost_increase_sar": 500
        },
        {
            "name": "تحسين التسميد",
            "yield_kg_ha": 4100,
            "change_percent": 6,
            "cost_increase_sar": 300
        }
    ]
}
```

### العوامل المؤثرة | Factors

```http
# أهمية العوامل
GET /fields/{field_id}/yield/factors

Response:
{
    "field_id": "field-001",
    "factors": [
        {"name": "rainfall_mm", "importance": 0.25, "current_value": 250, "optimal_range": [300, 400]},
        {"name": "temperature_avg", "importance": 0.18, "current_value": 22, "optimal_range": [18, 25]},
        {"name": "ndvi_peak", "importance": 0.15, "current_value": 0.78, "optimal_range": [0.7, 0.85]},
        {"name": "soil_moisture", "importance": 0.12, "current_value": 42, "optimal_range": [35, 55]},
        {"name": "nitrogen_kg_ha", "importance": 0.10, "current_value": 120, "optimal_range": [100, 150]}
    ],
    "limiting_factors": ["rainfall_mm"],
    "improvement_potential_percent": 15
}
```

### المقارنة | Benchmarking

```http
# مقارنة إقليمية
GET /fields/{field_id}/yield/benchmark

Response:
{
    "field_id": "field-001",
    "predicted_yield_kg_ha": 3850,
    "benchmarks": {
        "field_historical_avg": 3200,
        "regional_avg": 3400,
        "national_avg": 3100,
        "top_10_percent": 4500
    },
    "rankings": {
        "regional_percentile": 78,
        "national_percentile": 82
    },
    "gap_analysis": {
        "vs_top_performers": -650,
        "achievable_improvement_kg_ha": 400
    }
}
```

### التقارير | Reports

```http
# تقرير التوقع
GET /fields/{field_id}/yield/report?format=pdf

# تقرير موسمي
GET /reports/seasonal?region=sanaa&crop=wheat&season=2024
```

---

## نماذج البيانات | Data Models

### YieldPrediction
```json
{
    "id": "pred-001",
    "field_id": "field-001",
    "crop_type": "wheat",
    "season": "2024_winter",
    "prediction_date": "2024-03-15",
    "days_after_planting": 60,
    "prediction": {
        "yield_kg_ha": 3850,
        "yield_total_kg": 20020,
        "confidence_interval": {
            "p10": 3200,
            "p50": 3850,
            "p90": 4400
        },
        "confidence_percent": 85
    },
    "model": {
        "name": "ensemble",
        "version": "3.2",
        "features_used": 45
    },
    "inputs": {
        "ndvi_current": 0.72,
        "lai_current": 3.2,
        "cumulative_gdd": 1250,
        "cumulative_rainfall_mm": 180,
        "soil_moisture_avg": 42
    }
}
```

### SeasonalForecast
```json
{
    "region": "صنعاء",
    "crop_type": "wheat",
    "season": "2024_winter",
    "forecast_date": "2024-03-01",
    "summary": {
        "total_area_ha": 15000,
        "predicted_production_tons": 52500,
        "avg_yield_kg_ha": 3500,
        "vs_last_season_percent": 8
    },
    "distribution": {
        "excellent": {"percent": 15, "yield_range": [4000, 5000]},
        "good": {"percent": 45, "yield_range": [3500, 4000]},
        "average": {"percent": 30, "yield_range": [3000, 3500]},
        "poor": {"percent": 10, "yield_range": [2000, 3000]}
    }
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8098
HOST=0.0.0.0
LOG_LEVEL=INFO

# قاعدة البيانات
DATABASE_URL=postgresql://...

# النماذج
MODEL_PATH=/models
DEFAULT_MODEL=ensemble
PREDICTION_INTERVAL_DAYS=7

# خدمات خارجية
WEATHER_SERVICE_URL=http://weather-advanced:8092
SATELLITE_SERVICE_URL=http://satellite-service:8090
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "yield-engine",
    "version": "15.4.0",
    "models": {
        "ensemble": "loaded",
        "rf": "loaded",
        "xgboost": "loaded"
    }
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
