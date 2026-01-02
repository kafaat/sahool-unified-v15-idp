# Field Health API Documentation
# توثيق واجهة صحة الحقل

## Overview | نظرة عامة

The Field Health API provides comprehensive analysis of agricultural field health based on multiple data sources including NDVI satellite imagery, IoT sensor data, and weather information.

توفر واجهة صحة الحقل تحليلاً شاملاً لصحة الحقول الزراعية بناءً على مصادر بيانات متعددة تشمل صور الأقمار الصناعية NDVI وبيانات أجهزة الاستشعار IoT ومعلومات الطقس.

---

## Endpoint | نقطة النهاية

```
POST /api/v1/field-health
```

**Port:** 8080 (field-ops service)

---

## Health Score Calculation | حساب درجة الصحة

The overall field health score (0-100) is calculated using weighted components:

يتم حساب درجة الصحة الإجمالية للحقل (0-100) باستخدام مكونات مرجحة:

| Component | Weight | Arabic |
|-----------|--------|--------|
| NDVI (Vegetation Index) | 40% | مؤشر الغطاء النباتي |
| Soil Moisture | 25% | رطوبة التربة |
| Weather Conditions | 20% | حالة الطقس |
| Sensor Anomaly Detection | 15% | كشف شذوذ الأجهزة |

**Formula:**
```
Overall Score = (NDVI × 0.40) + (Soil Moisture × 0.25) + (Weather × 0.20) + (Sensor × 0.15)
```

---

## Request Schema | مخطط الطلب

### FieldHealthRequest

```json
{
  "field_id": "string",           // معرف الحقل - Field identifier
  "crop_type": "string",          // نوع المحصول - Crop type (wheat, corn, rice, etc.)
  "sensor_data": {
    "soil_moisture": 0-100,       // رطوبة التربة - Soil moisture percentage
    "temperature": -50 to 60,     // درجة الحرارة - Temperature in Celsius
    "humidity": 0-100             // الرطوبة النسبية - Relative humidity percentage
  },
  "ndvi_data": {
    "ndvi_value": -1 to 1,        // قيمة NDVI - NDVI value
    "image_date": "YYYY-MM-DD",   // تاريخ الصورة - Image date (optional)
    "cloud_coverage": 0-100       // تغطية السحب - Cloud coverage % (optional)
  },
  "weather_data": {
    "precipitation": 0+,          // هطول الأمطار - Precipitation in mm
    "wind_speed": 0+,             // سرعة الرياح - Wind speed in km/h (optional)
    "forecast_days": 1-14         // أيام التنبؤ - Forecast days (default: 7)
  }
}
```

### Example Request

```json
{
  "field_id": "field-123-abc",
  "crop_type": "wheat",
  "sensor_data": {
    "soil_moisture": 28.5,
    "temperature": 22.3,
    "humidity": 65.0
  },
  "ndvi_data": {
    "ndvi_value": 0.52,
    "image_date": "2024-01-15",
    "cloud_coverage": 15.0
  },
  "weather_data": {
    "precipitation": 12.5,
    "wind_speed": 18.0,
    "forecast_days": 7
  }
}
```

---

## Response Schema | مخطط الاستجابة

### FieldHealthResponse

```json
{
  "field_id": "string",
  "crop_type": "string",
  "overall_health_score": 0-100,      // الدرجة الإجمالية - Overall score
  "health_status": "string",          // excellent|good|fair|poor|critical
  "health_status_ar": "string",       // ممتاز|جيد|مقبول|ضعيف|حرج

  // Component Scores - درجات المكونات
  "ndvi_score": 0-100,
  "soil_moisture_score": 0-100,
  "weather_score": 0-100,
  "sensor_anomaly_score": 0-100,

  // Risk Analysis - تحليل المخاطر
  "risk_factors": [
    {
      "type": "string",
      "severity": "low|medium|high|critical",
      "description_ar": "string",
      "description_en": "string",
      "impact_score": 0-100
    }
  ],

  // Recommendations - التوصيات
  "recommendations_ar": ["string"],
  "recommendations_en": ["string"],

  "analysis_timestamp": "ISO-8601",
  "metadata": {
    "ndvi_weight": 0.40,
    "soil_moisture_weight": 0.25,
    "weather_weight": 0.20,
    "sensor_anomaly_weight": 0.15,
    "total_risk_factors": 0,
    "critical_risks": 0,
    "high_risks": 0
  }
}
```

---

## Health Status Levels | مستويات الصحة

| Score Range | Status (EN) | Status (AR) | Description |
|-------------|-------------|-------------|-------------|
| 85-100 | Excellent | ممتاز | Optimal field conditions |
| 70-84 | Good | جيد | Healthy with minor concerns |
| 50-69 | Fair | مقبول | Requires attention |
| 30-49 | Poor | ضعيف | Needs intervention |
| 0-29 | Critical | حرج | Immediate action required |

---

## Risk Factor Types | أنواع عوامل الخطر

| Type | Arabic | Description |
|------|--------|-------------|
| `vegetation_stress` | إجهاد نباتي | Low NDVI indicating poor plant health |
| `drought` | جفاف | Low soil moisture requiring irrigation |
| `waterlogging` | غمر | Excessive soil moisture risking root rot |
| `heavy_rain` | أمطار غزيرة | High precipitation affecting operations |
| `strong_winds` | رياح قوية | High wind speeds risking crop damage |
| `sensor_anomaly` | شذوذ الأجهزة | Abnormal sensor readings |

---

## Supported Crop Types | أنواع المحاصيل المدعومة

The API supports crop-specific optimal ranges for soil moisture:

| Crop | Optimal Soil Moisture Range |
|------|----------------------------|
| Wheat (قمح) | 25-35% |
| Corn (ذرة) | 30-40% |
| Rice (أرز) | 60-80% |
| Tomato (طماطم) | 25-35% |
| Potato (بطاطس) | 30-40% |
| Cotton (قطن) | 20-30% |
| Default | 25-40% |

---

## Usage Examples | أمثلة الاستخدام

### Using curl

```bash
curl -X POST http://localhost:8080/api/v1/field-health \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field-001",
    "crop_type": "wheat",
    "sensor_data": {
      "soil_moisture": 30.0,
      "temperature": 22.0,
      "humidity": 65.0
    },
    "ndvi_data": {
      "ndvi_value": 0.65,
      "image_date": "2024-01-20",
      "cloud_coverage": 10.0
    },
    "weather_data": {
      "precipitation": 8.0,
      "wind_speed": 15.0,
      "forecast_days": 7
    }
  }'
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8080/api/v1/field-health",
    json={
        "field_id": "field-001",
        "crop_type": "wheat",
        "sensor_data": {
            "soil_moisture": 30.0,
            "temperature": 22.0,
            "humidity": 65.0
        },
        "ndvi_data": {
            "ndvi_value": 0.65,
            "image_date": "2024-01-20",
            "cloud_coverage": 10.0
        },
        "weather_data": {
            "precipitation": 8.0,
            "wind_speed": 15.0,
            "forecast_days": 7
        }
    }
)

result = response.json()
print(f"Health Score: {result['overall_health_score']}/100")
print(f"Status: {result['health_status_ar']}")
```

### Using JavaScript/TypeScript

```javascript
const response = await fetch('http://localhost:8080/api/v1/field-health', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    field_id: 'field-001',
    crop_type: 'wheat',
    sensor_data: {
      soil_moisture: 30.0,
      temperature: 22.0,
      humidity: 65.0
    },
    ndvi_data: {
      ndvi_value: 0.65,
      image_date: '2024-01-20',
      cloud_coverage: 10.0
    },
    weather_data: {
      precipitation: 8.0,
      wind_speed: 15.0,
      forecast_days: 7
    }
  })
});

const result = await response.json();
console.log(`Health Score: ${result.overall_health_score}/100`);
```

---

## Error Responses | استجابات الخطأ

### 400 Bad Request

Invalid input data:

```json
{
  "detail": "Invalid input data: soil_moisture must be between 0 and 100"
}
```

### 500 Internal Server Error

Server error during analysis:

```json
{
  "detail": "Internal server error during health analysis: ..."
}
```

---

## Testing | الاختبار

### Run Example Scripts

1. **Python Example:**
   ```bash
   cd apps/services/field-ops
   python3 examples/field_health_example.py
   ```

2. **Curl Example:**
   ```bash
   cd apps/services/field-ops
   ./examples/field_health_curl_example.sh
   ```

### Start the Service

```bash
# Using Docker Compose
docker-compose up field-ops

# Or run directly
cd apps/services/field-ops
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

---

## Integration Points | نقاط التكامل

The Field Health API can be integrated with:

1. **NDVI Processor Service** - For real-time NDVI data
2. **IoT Gateway** - For sensor data collection
3. **Weather Service** - For weather forecasts
4. **Alert Service** - For critical health notifications
5. **Field Management Dashboard** - For visualization

---

## Algorithm Details | تفاصيل الخوارزمية

### NDVI Score Calculation

```
NDVI < 0:        Score = 0          (Water/Non-vegetation)
0 ≤ NDVI < 0.2:  Score = 0-30       (Bare soil/Sparse vegetation)
0.2 ≤ NDVI < 0.4: Score = 30-60     (Moderate vegetation)
0.4 ≤ NDVI < 0.6: Score = 60-85     (Healthy vegetation)
NDVI ≥ 0.6:      Score = 85-100     (Very dense vegetation)
```

Adjusted for cloud coverage when > 30%.

### Soil Moisture Score

Based on crop-specific optimal ranges:
- **Optimal range:** Score = 100
- **Below optimal:** Linear decrease, severe penalty if < 50% of minimum
- **Above optimal:** Linear decrease, severe penalty if > 150% of maximum

### Weather Score

Starts at 100, deducted for:
- No precipitation: -15
- Heavy rain (>30mm): -10 to -25
- Strong winds (>30 km/h): -15 to -30

### Sensor Anomaly Detection

Checks for:
- Temperature outside reasonable range (-10°C to 50°C)
- Extreme humidity values
- Inconsistencies between air humidity and soil moisture

---

## File Structure | هيكل الملفات

```
apps/services/field-ops/
├── src/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── field_health.py         # 🆕 Field Health API
│   └── main.py                         # ✏️ Updated with router registration
├── examples/
│   ├── field_health_example.py         # 🆕 Python usage example
│   └── field_health_curl_example.sh    # 🆕 Curl usage example
├── FIELD_HEALTH_API.md                 # 🆕 This documentation
└── README.md
```

---

## Future Enhancements | التحسينات المستقبلية

- [ ] Machine learning-based anomaly detection
- [ ] Historical trend analysis
- [ ] Predictive health forecasting
- [ ] Multi-field comparative analysis
- [ ] Integration with pest detection systems
- [ ] Automated irrigation recommendations
- [ ] Crop-specific disease risk assessment

---

## Support | الدعم

For issues or questions:
- Service: field-ops
- Port: 8080
- Health Check: `GET /healthz`
- API Docs: `http://localhost:8080/docs`

---

**Version:** 1.0.0
**Last Updated:** 2024-01-20
**Service:** SAHOOL Field Operations v15.3.3
