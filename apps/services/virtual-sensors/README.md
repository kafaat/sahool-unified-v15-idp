# Virtual Sensors - المستشعرات الافتراضية

## نظرة عامة | Overview

خدمة المستشعرات الافتراضية لتقدير القياسات الزراعية باستخدام النماذج والأقمار الصناعية.

Virtual sensors service for estimating agricultural measurements using models and satellite data.

**Port:** 8096
**Version:** 15.4.0

---

## الميزات | Features

### المستشعرات المتاحة | Available Sensors

| المستشعر         | Sensor        | الوصف                |
| ---------------- | ------------- | -------------------- |
| رطوبة التربة     | Soil Moisture | تقدير من NDWI والطقس |
| درجة حرارة السطح | Surface Temp  | من الأقمار الحرارية  |
| الإجهاد المائي   | Water Stress  | مؤشر الإجهاد         |
| الكتلة الحيوية   | Biomass       | تقدير الكتلة الخضراء |
| النتروجين        | Nitrogen      | محتوى النيتروجين     |
| الكلوروفيل       | Chlorophyll   | محتوى اليخضور        |

### مصادر البيانات | Data Sources

| المصدر       | Source     | البيانات               |
| ------------ | ---------- | ---------------------- |
| Sentinel-2   | Sentinel-2 | NDVI, NDWI             |
| Landsat      | Landsat    | حرارة السطح            |
| SMAP         | SMAP       | رطوبة التربة           |
| بيانات الطقس | Weather    | درجات الحرارة، الرطوبة |

---

## API Endpoints

### القراءات | Readings

```http
# قراءات المستشعر الافتراضي
GET /fields/{field_id}/virtual-sensors/{sensor_type}

Response:
{
    "field_id": "field-001",
    "sensor_type": "soil_moisture",
    "timestamp": "2024-01-15T10:00:00Z",
    "reading": {
        "value": 42.5,
        "unit": "percent",
        "confidence": 0.85
    },
    "source": {
        "model": "smi_ndwi",
        "inputs": ["sentinel-2", "weather"]
    },
    "interpretation": {
        "status": "adequate",
        "threshold_low": 30,
        "threshold_high": 60
    }
}

# جميع المستشعرات
GET /fields/{field_id}/virtual-sensors

Response:
{
    "field_id": "field-001",
    "timestamp": "2024-01-15T10:00:00Z",
    "sensors": {
        "soil_moisture": {"value": 42.5, "unit": "%", "status": "adequate"},
        "surface_temperature": {"value": 28.5, "unit": "°C", "status": "normal"},
        "water_stress": {"value": 0.15, "unit": "index", "status": "low"},
        "biomass": {"value": 3500, "unit": "kg/ha", "status": "good"},
        "chlorophyll": {"value": 45, "unit": "SPAD", "status": "healthy"}
    }
}
```

### السلاسل الزمنية | Time Series

```http
# سلسلة زمنية
GET /fields/{field_id}/virtual-sensors/{sensor_type}/timeseries?start=2024-01-01&end=2024-01-31

Response:
{
    "field_id": "field-001",
    "sensor_type": "soil_moisture",
    "period": {
        "start": "2024-01-01",
        "end": "2024-01-31"
    },
    "data": [
        {"date": "2024-01-01", "value": 45.2, "confidence": 0.82},
        {"date": "2024-01-05", "value": 38.5, "confidence": 0.88},
        {"date": "2024-01-10", "value": 52.1, "confidence": 0.85}
    ],
    "statistics": {
        "mean": 45.3,
        "min": 32.1,
        "max": 58.4,
        "trend": "stable"
    }
}
```

### خرائط | Maps

```http
# خريطة المستشعر
GET /fields/{field_id}/virtual-sensors/{sensor_type}/map?date=2024-01-15

Response:
{
    "field_id": "field-001",
    "sensor_type": "soil_moisture",
    "date": "2024-01-15",
    "map": {
        "format": "geotiff",
        "url": "https://...",
        "resolution_m": 10
    },
    "zones": [
        {"zone_id": "north", "value": 48.5, "area_percent": 40},
        {"zone_id": "south", "value": 38.2, "area_percent": 60}
    ]
}
```

### المعايرة | Calibration

```http
# إضافة قياس مرجعي
POST /fields/{field_id}/virtual-sensors/{sensor_type}/calibration
{
    "measurement_date": "2024-01-15",
    "location": {"lat": 15.35, "lng": 44.15},
    "measured_value": 44.0,
    "method": "tdr_probe",
    "depth_cm": 30
}

# نتائج المعايرة
GET /fields/{field_id}/virtual-sensors/{sensor_type}/calibration/results

Response:
{
    "sensor_type": "soil_moisture",
    "calibration": {
        "n_points": 15,
        "rmse": 4.2,
        "mae": 3.5,
        "r_squared": 0.78,
        "bias": -1.2
    },
    "status": "good",
    "last_calibration": "2024-01-15"
}
```

### التنبيهات | Alerts

```http
# إعداد تنبيه
POST /fields/{field_id}/virtual-sensors/{sensor_type}/alerts
{
    "condition": {
        "operator": "lt",
        "value": 30
    },
    "severity": "high",
    "message": "رطوبة التربة منخفضة - يلزم الري"
}

# جلب التنبيهات النشطة
GET /fields/{field_id}/virtual-sensors/alerts?status=active
```

### المقارنة | Comparison

```http
# مقارنة بين حقول
POST /virtual-sensors/compare
{
    "sensor_type": "soil_moisture",
    "field_ids": ["field-001", "field-002", "field-003"],
    "date": "2024-01-15"
}

Response:
{
    "sensor_type": "soil_moisture",
    "date": "2024-01-15",
    "comparison": [
        {"field_id": "field-001", "value": 42.5, "rank": 2},
        {"field_id": "field-002", "value": 55.2, "rank": 1},
        {"field_id": "field-003", "value": 35.8, "rank": 3}
    ],
    "regional_average": 44.5
}
```

---

## نماذج البيانات | Data Models

### VirtualSensorReading

```json
{
  "id": "read-001",
  "field_id": "field-001",
  "sensor_type": "soil_moisture",
  "timestamp": "2024-01-15T10:00:00Z",
  "reading": {
    "value": 42.5,
    "unit": "percent",
    "precision": 2
  },
  "model": {
    "name": "smi_ndwi_weather",
    "version": "2.1",
    "confidence": 0.85
  },
  "inputs": {
    "ndwi": 0.35,
    "temperature_c": 25.5,
    "humidity_percent": 45,
    "days_since_rain": 3
  },
  "quality": {
    "data_completeness": 0.95,
    "cloud_free": true
  }
}
```

### CalibrationPoint

```json
{
  "id": "cal-001",
  "field_id": "field-001",
  "sensor_type": "soil_moisture",
  "measurement_date": "2024-01-15",
  "location": {
    "lat": 15.35,
    "lng": 44.15,
    "depth_cm": 30
  },
  "measured_value": 44.0,
  "predicted_value": 42.5,
  "error": -1.5,
  "method": "tdr_probe",
  "operator_id": "user-001"
}
```

---

## متغيرات البيئة | Environment Variables

```env
# الخادم
PORT=8096
HOST=0.0.0.0

# قاعدة البيانات
DATABASE_URL=postgresql://...

# خدمات خارجية
SATELLITE_SERVICE_URL=http://satellite-service:8090
WEATHER_SERVICE_URL=http://weather-advanced:8092

# النماذج
MODEL_UPDATE_INTERVAL_HOURS=6
```

---

## Health Check

```http
GET /healthz

Response:
{
    "status": "healthy",
    "service": "virtual-sensors",
    "version": "15.4.0",
    "models_loaded": 6
}
```

---

## الترخيص | License

Proprietary - KAFAAT © 2024
