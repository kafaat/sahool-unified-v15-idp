# ⚠️ DEPRECATED - Use vegetation-analysis-service instead

This service has been deprecated and merged into `vegetation-analysis-service`.
Please update your references to use `vegetation-analysis-service` on port 8090.

---

# LAI Estimation - تقدير مؤشر مساحة الورقة

## نظرة عامة | Overview

خدمة تقدير مؤشر مساحة الورقة (LAI) للمحاصيل باستخدام صور الأقمار الصناعية والنماذج الإحصائية.

Leaf Area Index (LAI) estimation service using satellite imagery and statistical models.

**Port:** 8099
**Version:** 15.4.0

---

## الميزات | Features

### مصادر البيانات | Data Sources

| المصدر         | Source             | الدقة  |
| -------------- | ------------------ | ------ |
| Sentinel-2     | Sentinel-2         | 10-20m |
| Landsat        | Landsat            | 30m    |
| صور طائرات     | Drone Images       | 1-5cm  |
| قياسات ميدانية | Field Measurements | مرجعية |

### النماذج | Models

| النموذج  | Model     | الوصف                  |
| -------- | --------- | ---------------------- |
| تجريبي   | Empirical | علاقات إحصائية مع NDVI |
| فيزيائي  | Physical  | نماذج انتقال الإشعاع   |
| تعلم آلي | ML        | شبكات عصبية            |

---

## API Endpoints

### تقدير LAI | LAI Estimation

```http
# الحصول على LAI الحالي
GET /fields/{field_id}/lai/current

Response:
{
    "field_id": "field-001",
    "date": "2024-01-15",
    "lai": {
        "mean": 3.2,
        "min": 1.5,
        "max": 4.8,
        "std": 0.6
    },
    "source": "sentinel-2",
    "model": "empirical_ndvi",
    "quality": {
        "confidence": 0.85,
        "cloud_cover_percent": 5
    },
    "interpretation": {
        "status": "good",
        "growth_stage": "vegetative",
        "recommendation": "الغطاء النباتي جيد"
    }
}

# سلسلة زمنية
GET /fields/{field_id}/lai/timeseries?start=2024-01-01&end=2024-01-31

# مقارنة بين النماذج
GET /fields/{field_id}/lai/models-comparison
```

### الخرائط | Maps

```http
# خريطة LAI
GET /fields/{field_id}/lai/map?date=2024-01-15&format=geotiff

# خريطة الفروقات
GET /fields/{field_id}/lai/change-map?date1=2024-01-01&date2=2024-01-15
```

### التحليل | Analysis

```http
# تحليل LAI بالمناطق
GET /fields/{field_id}/lai/zones-analysis

Response:
{
    "field_id": "field-001",
    "date": "2024-01-15",
    "zones": [
        {
            "zone_id": "zone-001",
            "name": "الشمال",
            "lai_mean": 3.8,
            "lai_class": "high",
            "area_percent": 40
        },
        {
            "zone_id": "zone-002",
            "name": "الجنوب",
            "lai_mean": 2.5,
            "lai_class": "moderate",
            "area_percent": 60
        }
    ],
    "variability_index": 0.32
}

# تحليل الاتجاه
GET /fields/{field_id}/lai/trend?period=90d

Response:
{
    "field_id": "field-001",
    "period": "90d",
    "trend": {
        "direction": "increasing",
        "slope": 0.02,
        "r_squared": 0.85
    },
    "peak": {
        "date": "2024-03-15",
        "value": 4.5,
        "expected": true
    }
}
```

### المعايرة | Calibration

```http
# إضافة قياس ميداني
POST /fields/{field_id}/lai/measurements
{
    "measurement_date": "2024-01-15",
    "location": {
        "lat": 15.35,
        "lng": 44.15
    },
    "lai_value": 3.4,
    "method": "ceptometer",
    "operator": "محمد علي"
}

# قياسات ميدانية
GET /fields/{field_id}/lai/measurements?start=2024-01-01

# تقييم دقة النموذج
GET /fields/{field_id}/lai/validation

Response:
{
    "field_id": "field-001",
    "model": "empirical_ndvi",
    "validation": {
        "n_measurements": 15,
        "rmse": 0.42,
        "mae": 0.35,
        "r_squared": 0.82,
        "bias": -0.05
    },
    "recommendation": "النموذج مناسب للاستخدام"
}
```

### العلاقة مع المؤشرات | Index Relations

```http
# علاقة LAI-NDVI
GET /fields/{field_id}/lai/ndvi-relation

Response:
{
    "field_id": "field-001",
    "relation": {
        "equation": "LAI = 4.5 * NDVI + 0.3",
        "r_squared": 0.78,
        "valid_ndvi_range": [0.2, 0.9]
    },
    "calibration_points": 25
}
```

---

## نماذج البيانات | Data Models

### LAIEstimate

```json
{
    "id": "lai-001",
    "field_id": "field-001",
    "date": "2024-01-15",
    "source": {
        "type": "sentinel-2",
        "scene_id": "S2A_20240115",
        "cloud_cover_percent": 5
    },
    "model": {
        "name": "empirical_ndvi",
        "version": "2.1",
        "parameters": {
            "a": 4.5,
            "b": 0.3
        }
    },
    "results": {
        "mean": 3.2,
        "median": 3.1,
        "std": 0.6,
        "min": 1.5,
        "max": 4.8,
        "histogram": [...]
    },
    "quality": {
        "valid_pixels_percent": 95,
        "confidence": 0.85
    }
}
```

### FieldMeasurement

```json
{
  "id": "meas-001",
  "field_id": "field-001",
  "measurement_date": "2024-01-15",
  "location": {
    "lat": 15.35,
    "lng": 44.15
  },
  "lai_value": 3.4,
  "method": "ceptometer",
  "instrument": "AccuPAR LP-80",
  "conditions": {
    "time": "10:30",
    "sky_condition": "clear",
    "solar_elevation": 55
  },
  "operator_id": "user-001",
  "notes": "قياس في منتصف الحقل",
  "created_at": "2024-01-15T10:35:00Z"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8099
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...

# خدمات خارجية
SATELLITE_SERVICE_URL=http://satellite-service:8090

# النماذج
DEFAULT_MODEL=empirical_ndvi
ENABLE_ML_MODEL=true
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "lai-estimation",
    "version": "15.4.0"
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
