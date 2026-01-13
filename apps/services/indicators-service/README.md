# Indicators Service - خدمة المؤشرات

## نظرة عامة | Overview

خدمة حساب وتحليل المؤشرات الزراعية ومؤشرات أداء الحقول.

Agricultural indicators calculation and field performance analytics service.

**Port:** 8091
**Version:** 15.4.0

---

## الميزات | Features

### مؤشرات الغطاء النباتي | Vegetation Indices

| المؤشر | Index | الوصف                             |
| ------ | ----- | --------------------------------- |
| NDVI   | NDVI  | مؤشر الاختلاف النباتي             |
| EVI    | EVI   | مؤشر الغطاء النباتي المحسن        |
| SAVI   | SAVI  | مؤشر الغطاء النباتي المعدل للتربة |
| NDWI   | NDWI  | مؤشر الماء                        |
| LAI    | LAI   | مؤشر مساحة الورقة                 |

### مؤشرات الأداء | Performance Indicators

| المؤشر       | Indicator | الوصف          |
| ------------ | --------- | -------------- |
| إنتاجية      | Yield     | كفاءة الإنتاج  |
| كفاءة المياه | WUE       | استخدام المياه |
| صحة المحصول  | Health    | صحة النباتات   |
| نمو          | Growth    | معدل النمو     |

---

## API Endpoints

### مؤشرات الغطاء النباتي | Vegetation Indices

```http
# المؤشرات الحالية
GET /fields/{field_id}/indices/current

Response:
{
    "field_id": "field-001",
    "date": "2024-01-15",
    "indices": {
        "ndvi": {
            "value": 0.72,
            "status": "healthy",
            "change_7d": 0.05
        },
        "evi": {
            "value": 0.65,
            "status": "good"
        },
        "savi": {
            "value": 0.68,
            "status": "good"
        },
        "ndwi": {
            "value": 0.35,
            "status": "adequate"
        }
    },
    "overall_health_score": 78
}

# سلسلة زمنية
GET /fields/{field_id}/indices/timeseries?index=ndvi&start_date=2024-01-01&end_date=2024-01-31

# مقارنة بين حقول
POST /indices/compare
{
    "field_ids": ["field-001", "field-002", "field-003"],
    "indices": ["ndvi", "evi"],
    "date": "2024-01-15"
}
```

### مؤشرات الأداء | Performance Indicators

```http
# أداء الحقل
GET /fields/{field_id}/performance

Response:
{
    "field_id": "field-001",
    "season": "2024_winter",
    "indicators": {
        "yield_efficiency": {
            "value": 85,
            "benchmark": 80,
            "status": "above_average"
        },
        "water_use_efficiency": {
            "value": 1.2,
            "unit": "kg/m3",
            "benchmark": 1.0
        },
        "input_efficiency": {
            "fertilizer_roi": 3.5,
            "pesticide_effectiveness": 92
        }
    }
}

# تقييم الموسم
GET /fields/{field_id}/seasons/{season_id}/evaluation
```

### تحليل المناطق | Zone Analysis

```http
# تحليل المناطق بالمؤشرات
GET /fields/{field_id}/zones/analysis

Response:
{
    "field_id": "field-001",
    "zones": [
        {
            "zone_id": "zone-001",
            "name": "المنطقة الشمالية",
            "area_percent": 35,
            "ndvi": 0.78,
            "status": "excellent"
        },
        {
            "zone_id": "zone-002",
            "name": "المنطقة الجنوبية",
            "area_percent": 65,
            "ndvi": 0.65,
            "status": "needs_attention"
        }
    ],
    "recommendations": [
        {
            "zone": "zone-002",
            "action": "زيادة الري",
            "priority": "high"
        }
    ]
}
```

### الإنذارات | Alerts

```http
# إنشاء قاعدة إنذار
POST /alerts/rules
{
    "field_id": "field-001",
    "indicator": "ndvi",
    "condition": {
        "operator": "lt",
        "value": 0.5
    },
    "alert_config": {
        "severity": "high",
        "message": "انخفاض حاد في NDVI"
    }
}

# جلب الإنذارات
GET /alerts?field_id=field-001&status=active
```

### التقارير | Reports

```http
# تقرير شامل
GET /fields/{field_id}/report?type=monthly&month=2024-01

# تصدير البيانات
GET /fields/{field_id}/export?format=csv&indices=ndvi,evi&period=90d
```

---

## نماذج البيانات | Data Models

### VegetationIndices

```json
{
  "field_id": "field-001",
  "timestamp": "2024-01-15T10:00:00Z",
  "source": "sentinel-2",
  "indices": {
    "ndvi": {
      "mean": 0.72,
      "min": 0.45,
      "max": 0.85,
      "std": 0.08
    },
    "evi": {
      "mean": 0.65,
      "min": 0.4,
      "max": 0.78
    }
  },
  "quality": {
    "cloud_cover_percent": 5,
    "valid_pixels_percent": 95
  }
}
```

### PerformanceMetrics

```json
{
  "field_id": "field-001",
  "season": "2024_winter",
  "metrics": {
    "yield_kg_ha": 3800,
    "water_used_m3_ha": 4500,
    "wue_kg_m3": 0.84,
    "nitrogen_efficiency": 75,
    "cost_per_kg_sar": 1.2,
    "profit_sar_ha": 8500
  },
  "rankings": {
    "regional_percentile": 82,
    "national_percentile": 75
  }
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8091
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...
REDIS_URL=redis://redis:6379
NATS_URL=nats://nats:4222

# خدمات خارجية
SATELLITE_SERVICE_URL=http://satellite-service:8090
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "indicators-service",
    "version": "15.4.0"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
